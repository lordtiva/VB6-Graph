import os
import networkx as nx
import igraph as ig
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any

# Local imports
import db
from analyzer import CodeAnalyzer

app = FastAPI(title="VB6-Graph API")

# Setup CORS for React frontend (Vite defaults to localhost:5173 or 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all. Be more restrictive in production.
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for the graph to avoid reloading on every request
_cached_graph: Dict[str, Any] = {"name": None, "graph": None}

def load_latest_graph():
    """Finds and loads the most recent .graphml file, and updates DB path."""
    global _cached_graph
    
    # Check output directory, then current, then parent, then parent's output
    locations = ['output', '../output', '.', '..']
    graph_file_path = None
    
    for loc in locations:
        if not os.path.exists(loc):
            continue
        files = [os.path.join(loc, f) for f in os.listdir(loc) if f.endswith('.graphml')]
        if files:
            # Sort by modification time to get the latest
            files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            graph_file_path = files[0]
            break
            
    if not graph_file_path:
        raise HTTPException(status_code=404, detail="No .graphml files found. Run 'parse' first.")
    
    # Update DB name to match the graph file (ProjectName.db)
    db_path = graph_file_path.replace('.graphml', '.db')
    if os.path.exists(db_path):
        db.set_db_name(db_path)
    
    if _cached_graph["name"] != graph_file_path:
        graph = nx.read_graphml(graph_file_path)
        _cached_graph["name"] = graph_file_path
        _cached_graph["graph"] = graph
        
    return _cached_graph["graph"]

@app.get("/api/graph")
def get_graph():
    """Returns the graph in Sigma.js/Graphology compatible format."""
    try:
        graph = load_latest_graph()
        analyzer = CodeAnalyzer(graph)
        communities = analyzer.detect_communities()
        
        # Calculate layout using igraph for 10x speedup and better math
        print(f"[*] Calculating high-performance layout for {len(graph.nodes)} nodes...")
        
        # Convert NetworkX graph to igraph
        node_list = list(graph.nodes())
        node_index = {node: i for i, node in enumerate(node_list)}
        
        # Filter edges to ensure both nodes exist in the node_list
        edges = []
        for u, v in graph.edges():
            if u in node_index and v in node_index:
                edges.append((node_index[u], node_index[v]))
        
        g_ig = ig.Graph(len(node_list), edges, directed=True)
        
        # Use Fruchterman-Reingold layout (C-optimized)
        layt = g_ig.layout_fruchterman_reingold(niter=1000)
        
        # Normalize coordinates to [-1, 1] for consistent frontend scaling
        coords = list(zip(*layt)) # [[x1, x2...], [y1, y2...]]
        if coords:
            min_x, max_x = min(coords[0]), max(coords[0])
            min_y, max_y = min(coords[1]), max(coords[1])
            range_x = (max_x - min_x) if max_x != min_x else 1
            range_y = (max_y - min_y) if max_y != min_y else 1

            pos = {node_list[i]: (
                (layt[i][0] - min_x) / range_x * 2 - 1,
                (layt[i][1] - min_y) / range_y * 2 - 1
            ) for i in range(len(node_list))}
        else:
            pos = {node: [0, 0] for node in node_list}

        print(f"[*] Layout calculated for {len(pos)} nodes.")
        
        # Format for Sigma.js/Graphology
        nodes = []
        for n, d in graph.nodes(data=True):
            nx_pos = pos.get(n, [0, 0])
            nodes.append({
                "key": n,
                "attributes": {
                    "label": d.get("label", n),
                    "type": d.get("type", "Unknown"),
                    "loc": d.get("loc", 1),
                    "size": d.get("size", 5),
                    "community": communities.get(n, -1),
                    "x": nx_pos[0] * 1000, 
                    "y": nx_pos[1] * 1000
                }
            })
            
        edges_out = []
        for u, v, d in graph.edges(data=True):
            edges_out.append({
                "source": u,
                "target": v,
                "attributes": {
                    "type": d.get("type", "Unknown")
                }
            })
            
        print(f"[*] Returning {len(nodes)} nodes and {len(edges_out)} edges.")
        return {"nodes": nodes, "edges": edges_out}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/code/{node_id:path}")
def get_code(node_id: str):
    """Retrieves code content from SQLite."""
    code = db.get_node_code(node_id)
    if not code:
        raise HTTPException(status_code=404, detail=f"Code for node {node_id} not found.")
    return {"node_id": node_id, "code": code}

@app.get("/api/analysis")
def get_analysis():
    """Runs the CodeAnalyzer and returns the report."""
    try:
        graph = load_latest_graph()
        analyzer = CodeAnalyzer(graph)
        return analyzer.get_analysis_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/impact/{node_id:path}")
def get_impact(node_id: str):
    """Calculates the impact of modifying a specific node (Blast Radius)."""
    try:
        graph = load_latest_graph()
        analyzer = CodeAnalyzer(graph)
        return analyzer.get_impact_analysis(node_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"msg": "VB6-Graph API is running. Use /api/graph, /api/code/{id}, or /api/analysis"}
