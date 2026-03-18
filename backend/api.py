import os
import sys
import networkx as nx
import igraph as ig
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any

# Ensure we can import local modules when running from outside
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

# Global cache for heavy calculations
_cache = {
    "file_path": None,
    "mtime": 0,
    "graph": None,
    "nodes": None,
    "edges": None,
    "analysis": None,
    "communities": None
}

def load_latest_graph():
    """Finds and loads the most recent .graphml file, and updates DB path."""
    global _cache
    
    locations = ['output', '../output', '.', '..']
    graph_file_path = None
    
    for loc in locations:
        if not os.path.exists(loc):
            continue
        files = [os.path.join(loc, f) for f in os.listdir(loc) if f.endswith('.graphml')]
        if files:
            files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            graph_file_path = files[0]
            break
            
    if not graph_file_path:
        raise HTTPException(status_code=404, detail="No .graphml files found. Run 'parse' first.")
    
    current_mtime = os.path.getmtime(graph_file_path)
    
    # If file or modification time changed, reload everything
    if _cache["file_path"] != graph_file_path or _cache["mtime"] != current_mtime:
        print(f"[*] NEW GRAPH LOADING: {graph_file_path} (mtime: {current_mtime})")
        # Load graph first into a temp variable to avoid serving half-loaded data
        new_graph = nx.read_graphml(graph_file_path)
        
        # Now update cache atomically
        _cache.update({
            "file_path": graph_file_path,
            "mtime": current_mtime,
            "graph": new_graph,
            "nodes": None,
            "edges": None,
            "analysis": None,
            "communities": None
        })
        
        db_path = graph_file_path.replace('.graphml', '.db')
        if os.path.exists(db_path):
            db.set_db_name(db_path)
    
    return _cache["graph"]

@app.get("/api/graph")
def get_graph():
    """Returns the graph with cached layout."""
    global _cache
    try:
        graph = load_latest_graph()
        
        # If we have cached nodes/edges, return them immediately
        if _cache["nodes"] is not None:
            print("[cache] Serving graph from cache")
            return {"nodes": _cache["nodes"], "edges": _cache["edges"]}

        print("[cache] Cache miss for graph, calculating layout...")
        analyzer = CodeAnalyzer(graph)
        communities = analyzer.detect_communities()
        _cache["communities"] = communities
        
        # Calculate layout
        print(f"[*] Calculating high-performance layout for {len(graph.nodes)} nodes...")
        node_list = list(graph.nodes())
        node_index = {node: i for i, node in enumerate(node_list)}
        
        edges = []
        for u, v in graph.edges():
            if u in node_index and v in node_index:
                edges.append((node_index[u], node_index[v]))
        
        g_ig = ig.Graph(len(node_list), edges, directed=True)
        print(f"[*] Computing 3D cloud (1000 iterations)...")
        layt = g_ig.layout_fruchterman_reingold(dim=3, niter=1000)
        
        coords = list(zip(*layt))
        if coords:
            min_x, max_x = min(coords[0]), max(coords[0])
            min_y, max_y = min(coords[1]), max(coords[1])
            min_z, max_z = min(coords[2]), max(coords[2])
            range_x = (max_x - min_x) or 1
            range_y = (max_y - min_y) or 1
            range_z = (max_z - min_z) or 1

            z_scale_fix = 2.0 if range_z < 0.1 * range_x else 1.0

            pos = {node_list[i]: (
                (layt[i][0] - min_x) / range_x * 2 - 1,
                (layt[i][1] - min_y) / range_y * 2 - 1,
                ((layt[i][2] - min_z) / range_z * 2 - 1) * z_scale_fix
            ) for i in range(len(node_list))}
        else:
            pos = {node: [0, 0, 0] for node in node_list}

        print(f"[*] 3D Layout calculated for {len(pos)} nodes.")
        
        # Format nodes and edges
        nodes = []
        for n, d in graph.nodes(data=True):
            nx_pos = pos.get(n, [0, 0, 0])
            nodes.append({
                "key": n,
                "attributes": {
                    "label": d.get("label", n),
                    "type": d.get("type", "Unknown"),
                    "loc": d.get("loc", 1),
                    "size": d.get("size", 5),
                    "community": communities.get(n, -1),
                    "x": nx_pos[0] * 1000, 
                    "y": nx_pos[1] * 1000,
                    "z": nx_pos[2] * 1000
                }
            })
            
        edges_out = [{"source": u, "target": v, "attributes": {"type": d.get("type", "Unknown")}} 
                   for u, v, d in graph.edges(data=True)]
            
        print(f"[*] 3D Layout and formatting complete.")
        _cache["nodes"] = nodes
        _cache["edges"] = edges_out
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
    """Returns the cached report."""
    global _cache
    try:
        graph = load_latest_graph()
        if _cache["analysis"] is not None:
            print("[cache] Serving analysis from cache")
            return _cache["analysis"]

        print("[cache] Cache miss for analysis, running CodeAnalyzer...")
        analyzer = CodeAnalyzer(graph)
        result = analyzer.get_analysis_summary()
        
        # Inject cached communities if available
        if _cache["communities"]:
            result["communities"] = _cache["communities"]
            
        _cache["analysis"] = result
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
