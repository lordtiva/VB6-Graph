import networkx as nx
import igraph as ig
import os

def calculate_3d_layout(graph: nx.DiGraph, iterations=1000):
    """
    Calculates a 3D layout for the graph using igraph's Fruchterman-Reingold algorithm.
    Returns the graph with x, y, z attributes added to nodes.
    """
    if not graph.nodes:
        return graph

    print(f"[*] Calculating high-performance 3D layout for {len(graph.nodes)} nodes...")
    
    # 1. Convert to igraph for speed
    node_list = list(graph.nodes())
    node_index = {node: i for i, node in enumerate(node_list)}
    
    edges = []
    for u, v in graph.edges():
        if u in node_index and v in node_index:
            edges.append((node_index[u], node_index[v]))
    
    g_ig = ig.Graph(len(node_list), edges, directed=True)
    
    # 2. Compute layout
    print(f"[*] Computing 3D cloud ({iterations} iterations)...")
    layt = g_ig.layout_fruchterman_reingold(dim=3, niter=iterations)
    
    # 3. Normalize coordinates to [-1, 1] range
    coords = list(zip(*layt))
    if coords:
        min_x, max_x = min(coords[0]), max(coords[0])
        min_y, max_y = min(coords[1]), max(coords[1])
        min_z, max_z = min(coords[2]), max(coords[2])
        range_x = (max_x - min_x) or 1
        range_y = (max_y - min_y) or 1
        range_z = (max_z - min_z) or 1

        # If the graph is mostly flat in Z, scale it up a bit for better 3D feel
        z_scale_fix = 2.0 if range_z < 0.1 * range_x else 1.0

        for i, node in enumerate(node_list):
            nx_x = ((layt[i][0] - min_x) / range_x * 2 - 1) * 1000
            nx_y = ((layt[i][1] - min_y) / range_y * 2 - 1) * 1000
            nx_z = (((layt[i][2] - min_z) / range_z * 2 - 1) * z_scale_fix) * 1000
            
            graph.nodes[node]['x'] = nx_x
            graph.nodes[node]['y'] = nx_y
            graph.nodes[node]['z'] = nx_z
    else:
        for node in node_list:
            graph.nodes[node]['x'] = 0
            graph.nodes[node]['y'] = 0
            graph.nodes[node]['z'] = 0

    print(f"[*] 3D Layout calculated and normalized.")
    return graph
