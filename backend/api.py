import os
import networkx as nx
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
        
        # Format for Sigma.js/Graphology
        nodes = []
        for n, d in graph.nodes(data=True):
            nodes.append({
                "key": n,
                "attributes": {
                    "label": d.get("label", n),
                    "type": d.get("type", "Unknown"),
                    "loc": d.get("loc", 1),
                    # Add visualization attributes (can be customized by frontend)
                    "size": d.get("size", 5),
                    # We'll let the frontend decide colors, but we can hint
                    "x": 0, "y": 0 # Position will be calculated by layout
                }
            })
            
        edges = []
        for u, v, d in graph.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "attributes": {
                    "type": d.get("type", "Unknown")
                }
            })
            
        return {"nodes": nodes, "edges": edges}
    except Exception as e:
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

@app.get("/")
def read_root():
    return {"msg": "VB6-Graph API is running. Use /api/graph, /api/code/{id}, or /api/analysis"}
