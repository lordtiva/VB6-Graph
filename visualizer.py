from pyvis.network import Network
import networkx as nx
from parser import VB6Parser

def export_graph(graph, output_path="visualizacion.html"):
    """Exports a NetworkX graph to an interactive HTML file using PyVis."""
    net = Network(height="100vh", width="100%", bgcolor="#222222", font_color="white", directed=True)
    
    # Configuración de alto rendimiento para grafos masivos (>1000 nodos)
    net.set_options("""
    var options = {
      "nodes": {
        "shape": "dot",
        "size": 10
      },
      "edges": {
        "smooth": false,
        "arrows": {
          "to": {
            "enabled": true,
            "scaleFactor": 0.5
          }
        }
      },
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -30000,
          "centralGravity": 0.3,
          "springLength": 95,
          "springConstant": 0.04,
          "damping": 0.09,
          "avoidOverlap": 0
        },
        "stabilization": {
          "enabled": true,
          "iterations": 1000,
          "updateInterval": 100,
          "onlyDynamicEdges": false,
          "fit": true
        }
      }
    }
    """)

    # Define colors for different node types
    color_map = {
        "Project": "#ff4d4d",    # Red
        "File": "#4da6ff",       # Blue
        "Method": "#5cd65c",     # Green
        "Variable": "#ffa31a",   # Orange
        "UIControl": "#c266ff"   # Purple
    }

    # Add nodes
    for n, d in graph.nodes(data=True):
        ntype = d.get('type', 'Unknown')
        label = d.get('label', n)
        color = color_map.get(ntype, "#999999")
        net.add_node(n, label=label, color=color, title=f"Type: {ntype}\nID: {n}")

    # Add edges
    edge_colors = {
        "CONTAINS": "#888888",
        "CALLS": "#ffffff",
        "USES": "#ffa31a",
        "TRIGGERS": "#c266ff"
    }

    for u, v, d in graph.edges(data=True):
        etype = d.get('type', 'Unknown')
        color = edge_colors.get(etype, "#555555")
        net.add_edge(u, v, color=color, title=etype)

    # Save visualization
    net.save_graph(output_path)
    print(f"Visualization saved to {output_path}")

def export_for_gephi(graph, output_path="visualizacion.graphml"):
    """Exporta el grafo a un formato estándar para abrir en Gephi"""
    # NetworkX soporta GraphML nativamente
    nx.write_graphml(graph, output_path)
    print(f"Grafo exportado para Gephi en: {output_path}")

if __name__ == "__main__":
    import sys
    import os
    path = sys.argv[1] if len(sys.argv) > 1 else "sample_project"
    
    # Derive project name from directory
    project_name = os.path.basename(path.rstrip(os.sep))
    
    parser = VB6Parser(project_name=project_name)
    parser.parse_project(path)
    
    graph = parser.get_graph()
    export_graph(graph, output_path=f"{project_name}.html")
    export_for_gephi(graph, output_path=f"{project_name}.graphml")
