from pyvis.network import Network
import networkx as nx
from parser import VB6Parser

def export_graph(graph, output_path="visualizacion.html"):
    """Exports a NetworkX graph to an interactive HTML file using PyVis."""
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", directed=True)
    
    # Configure physics for better layout
    net.force_atlas_2based()

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

if __name__ == "__main__":
    import sys
    parser = VB6Parser()
    path = sys.argv[1] if len(sys.argv) > 1 else "sample_project"
    parser.parse_project(path)
    export_graph(parser.get_graph())
