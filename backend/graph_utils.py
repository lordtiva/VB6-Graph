def sanitize_graph_for_graphml(graph):
    """
    GraphML export in NetworkX doesn't support list/dict attributes.
    This function converts any non-scalar attribute to a string.
    """
    for n, d in graph.nodes(data=True):
        for k, v in d.items():
            if isinstance(v, (list, dict, set)):
                graph.nodes[n][k] = str(v)
    for u, v, d in graph.edges(data=True):
        for k, val in d.items():
            if isinstance(val, (list, dict, set)):
                graph[u][v][k] = str(val)
    return graph
