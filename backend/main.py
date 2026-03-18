import typer
import os
import networkx as nx
from typing import Optional
import uvicorn

# Importaciones locales (asumiendo que estamos en la carpeta backend o la agregamos al path)
from parser import VB6Parser
from analyzer import CodeAnalyzer
import db
from graph_utils import sanitize_graph_for_graphml

app = typer.Typer(help="VB6-Graph CLI: Herramienta de análisis de código heredado.")
# Definir la ruta de salida relativa a la raíz del proyecto
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(os.path.dirname(BACKEND_DIR), "output")

def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

@app.command()
def parse(directory: str = typer.Argument(..., help="Directorio del proyecto VB6 a parsear")):
    """Ejecuta el parser existente y guarda en BD y GraphML."""
    if not os.path.exists(directory):
        typer.echo(f"Error: El directorio {directory} no existe.")
        raise typer.Exit(code=1)

    ensure_output_dir()
    project_name = os.path.basename(directory.rstrip(os.sep))
    typer.echo(f"[*] Iniciando parseo del proyecto: {project_name}")
    
    # Configure DB path in output directory
    db_path = os.path.join(OUTPUT_DIR, f"{project_name}.db")
    db.set_db_name(db_path)
    
    parser = VB6Parser(project_name=db_path)
    parser.parse_project(directory)
    
    graph = parser.get_graph()
    graph_path = os.path.join(OUTPUT_DIR, f"{project_name}.graphml")
    graph = sanitize_graph_for_graphml(graph)
    nx.write_graphml(graph, graph_path)
    
    typer.echo(f"[+] Parseo completado.")
    typer.echo(f"[+] Base de datos actualizada: {db_path}")
    typer.echo(f"[+] Grafo guardado en: {graph_path}")

@app.command()
def analyze(graph_file: Optional[str] = typer.Option(None, help="Archivo .graphml a analizar")):
    """Corre los algoritmos de NetworkX para detectar Deuda Técnica."""
    ensure_output_dir()
    if not graph_file:
        # Intentar buscar el último .graphml generado en el directorio de salida o actual
        search_dirs = [OUTPUT_DIR, '.']
        graph_files = []
        for d in search_dirs:
            if os.path.exists(d):
                graph_files.extend([os.path.join(d, f) for f in os.listdir(d) if f.endswith('.graphml')])
        
        if not graph_files:
            typer.echo("Error: No se encontró ningún archivo .graphml. Ejecuta 'parse' primero.")
            raise typer.Exit(code=1)
        
        # Sort by modification time
        graph_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        graph_file = graph_files[0]

    typer.echo(f"[*] Analizando grafo: {graph_file}")
    graph = nx.read_graphml(graph_file)
    analyzer = CodeAnalyzer(graph)
    results = analyzer.get_analysis_summary()

    # Save detailed report
    import json
    report_name = os.path.basename(graph_file).replace('.graphml', '_analysis.json')
    report_path = os.path.join(OUTPUT_DIR, report_name)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)

    typer.echo("\n=== RESULTADOS DEL ANÁLISIS ===")
    
    typer.echo(f"\n[!] Dead Code ({len(results['dead_code'])} métodos):")
    for m in results['dead_code'][:10]: typer.echo(f"  - {m}")
    if len(results['dead_code']) > 10: typer.echo(f"  ... y {len(results['dead_code'])-10} más.")

    typer.echo(f"\n[!] God Objects (Top 10):")
    for go in results['god_objects']:
        if "error" in go:
            typer.echo(f"  - Error: {go['error']}")
        else:
            typer.echo(f"  - {go['node']} ({go['type']}): {go['score']}")

    typer.echo(f"\n[!] Dependencias Circulares ({len(results['circular_dependencies'])} ciclos):")
    for cycle in results['circular_dependencies'][:5]:
        typer.echo(f"  - {' -> '.join(cycle)}")
    if len(results['circular_dependencies']) > 5: typer.echo(f"  ... y {len(results['circular_dependencies'])-5} más.")
    
    if 'metrics' in results:
        typer.echo("\n[!] Métricas Arquitectónicas (Top Inestabilidad):")
        # Sort files by instability descending
        sorted_metrics = sorted(results['metrics'].items(), key=lambda x: x[1]['instability'], reverse=True)
        for f, m in sorted_metrics[:5]:
            typer.echo(f"  - {f}: I={m['instability']} (Ca={m['afferent']}, Ce={m['efferent']})")

    typer.echo(f"\n[+] Reporte completo guardado en: {report_path}")

@app.command()
def ui(port: int = typer.Option(8000, help="Puerto para el servidor FastAPI")):
    """Levanta el servidor FastAPI para el Dashboard Web."""
    typer.echo(f"[*] Iniciando servidor FastAPI en puerto {port}...")
    
    # Ensure we are in the backend directory context for imports inside api.py
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        import api
        uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True)
    except Exception as e:
        typer.echo(f"Error levantando UI: {e}")

@app.command()
def mcp(project_path: str = typer.Argument("sample_project", help="Proyecto a cargar en MCP")):
    """Levanta el servidor MCP existente."""
    typer.echo(f"[*] Iniciando servidor MCP con proyecto: {project_path}")
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    mcp_script = os.path.join(backend_dir, "mcp_server.py")
    
    import sys
    import subprocess
    # Use normalized paths for Windows
    try:
        subprocess.run([sys.executable, mcp_script, project_path])
    except KeyboardInterrupt:
        typer.echo("\n[*] Servidor MCP detenido.")

@app.command()
def inspect(project_path: str = typer.Argument("sample_project", help="Proyecto a cargar en MCP Inspector")):
    """Lanza el MCP Inspector para probar las herramientas manualmente."""
    import os
    import sys
    import subprocess
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    normalized_project_path = os.path.abspath(os.path.join(project_root, project_path)).replace('\\', '/')
    
    # Normalize paths to forward slashes for npx/node compatibility on Windows
    python_exe = sys.executable.replace('\\', '/')
    mcp_script = os.path.join(backend_dir, "mcp_server.py").replace('\\', '/')
    
    typer.echo(f"[*] Lanzando MCP Inspector para: {normalized_project_path}")
    typer.echo(f"[*] Si es la primera vez, se descargará el inspector. Revisa tu navegador.")
    
    # Run npx using shell=True for Windows command resolution
    cmd = f'npx @modelcontextprotocol/inspector "{python_exe}" "{mcp_script}" "{normalized_project_path}"'
    subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    app()
