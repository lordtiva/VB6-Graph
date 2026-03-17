from mcp.server.fastmcp import FastMCP
import networkx as nx
from parser import VB6Parser
from db import get_node_code
import os

# Initialize MCP Server
mcp = FastMCP("VB6-Graph-Server")

# Global instances
parser = None
graph = None

def load_project(path):
    global graph, parser
    project_name = os.path.basename(path.rstrip(os.sep))
    
    # Ensure output directory is always in the project root
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    output_dir = os.path.join(project_root, "output")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Use descriptive name in output directory
    db_path = os.path.join(output_dir, f"{project_name}.db")
    graph_path = os.path.join(output_dir, f"{project_name}.graphml")

    from db import set_db_name
    set_db_name(db_path)

    if os.path.exists(graph_path) and os.path.exists(db_path):
        print(f"[*] Loading existing graph and DB for: {project_name}")
        graph = nx.read_graphml(graph_path)
        # Initialize parser to handle the DB correctly but don't re-parse
        parser = VB6Parser(project_name=db_path)
    else:
        print(f"[*] Parsing project: {project_name}")
        parser = VB6Parser(project_name=db_path)
        parser.parse_project(path)
        graph = parser.get_graph()
        # Save graph for next time
        nx.write_graphml(graph, graph_path)

@mcp.tool()
def get_project_structure():
    """Returns the list of main files and their types extracted from the project."""
    if graph is None: return "Project not loaded."
    files = [n for n, d in graph.nodes(data=True) if d.get('type') == 'File']
    result = []
    for f in files:
        result.append({
            "name": f,
            "type": graph.nodes[f].get('type'),
            "methods": [n.split(':')[-1] for n in graph.neighbors(f) if graph.nodes[n].get('type') == 'Method']
        })
    return result

@mcp.tool()
def switch_project(project_path: str):
    """
    Switches the active VB6 project being analyzed. 
    Use this to load a different project directory without restarting the server.
    """
    try:
        load_project(project_path)
        return f"Successfully switched to project at: {project_path}"
    except Exception as e:
        return f"Error switching project: {str(e)}"

@mcp.tool()
def get_method_dependencies(method_name: str):
    """
    Returns what methods 'method_name' calls and what methods call it.
    Provide the method name (e.g., 'Add' or 'Form1:Add').
    """
    if graph is None: return "No project loaded. Please use switch_project first."
    
    # Find the node_id that ends with method_name or is exactly method_name
    target_node = None
    for n, d in graph.nodes(data=True):
        if d.get('type') == 'Method' and (n == method_name or n.endswith(f":{method_name}")):
            target_node = n
            break
    
    if not target_node:
        return f"Method '{method_name}' not found."

    # Calls (descendants with type=CALLS)
    calls = [v for u, v, d in graph.out_edges(target_node, data=True) if d.get('type') == 'CALLS']
    called_by = [u for u, v, d in graph.in_edges(target_node, data=True) if d.get('type') == 'CALLS']

    return {
        "method_id": target_node,
        "calls": [c.split(':')[-1] for c in calls],
        "called_by": [cb.split(':')[-1] for cb in called_by]
    }

@mcp.tool()
def get_source_code(node_id: str):
    """Returns the exact source code for a given node_id (File, Method, Variable, or UIControl)."""
    if graph is None: return "No project loaded. Please use switch_project first."
    
    # If node_id doesn't match exactly, try to find it
    actual_node = node_id
    if node_id not in graph.nodes:
        for n in graph.nodes:
            if n.endswith(f":{node_id}"):
                actual_node = n
                break
    
    code = get_node_code(actual_node)
    if code:
        return {"node_id": actual_node, "code": code}
    return f"Source code for '{node_id}' not found."

@mcp.tool()
def trace_ui_event(form_name: str, control_name: str):
    """Finds the method triggered by a specific UI control on a form."""
    if graph is None: return "No project loaded. Please use switch_project first."
    
    control_id = f"{form_name}.frm:{control_name}"
    if control_id not in graph.nodes:
        # Try without .frm
        control_id = f"{form_name}:{control_name}"

    if control_id not in graph.nodes:
        return f"Control '{control_name}' on '{form_name}' not found."

    # Find TRIGGERS edges
    triggered_methods = [v for u, v, d in graph.out_edges(control_id, data=True) if d.get('type') == 'TRIGGERS']
    
    return {
        "control_id": control_id,
        "triggers": [m.split(':')[-1] for m in triggered_methods]
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        load_project(path)
    else:
        print("[!] Started without initial project. Use switch_project to load one.")
    try:
        mcp.run()
    except (KeyboardInterrupt, SystemExit):
        # Graceful exit without traceback
        pass
