import os
import sqlite3
import networkx as nx
import sys
import re
import concurrent.futures
import multiprocessing
import threading

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import set_db_name, get_db_name, get_node_code
from antlr_parser_wrapper import AntlrParserWrapper

# Reuse regex logic from parser.py
def _extract_variables_regex(content):
    var_pattern = re.compile(r'^\s*(?:Public|Global|Dim)\s+\b([a-zA-Z0-9_]+)\b', re.IGNORECASE)
    reserved = {'to', 'for', 'if', 'then', 'else', 'while', 'step', 'each', 'in', 'next', 'select', 'case'}
    vars_found = []
    for line in content.splitlines():
        if re.search(r'^\s*(?:Public|Private|Friend|Static)?\s*(?:Sub|Function|Property)', line, re.IGNORECASE):
            break
        if line.strip().startswith("'") or line.strip().upper().startswith("REM "):
            continue
        match = var_pattern.search(line)
        if match:
            var_name = match.group(1)
            if var_name.lower() not in reserved:
                vars_found.append({"name": var_name, "content": line})
    return vars_found

def _extract_methods_regex(content):
    method_pattern = re.compile(
        r'^\s*(?:(?:Public|Private|Friend)\s+)?(?:Static\s+)?(?:Sub|Function|Property\s+(?:Get|Let|Set))\s+\b([a-zA-Z0-9_]+)\b',
        re.IGNORECASE
    )
    lines = content.splitlines()
    methods_found = []
    current_method = None
    method_body = []
    start_line = 0
    
    for i, line in enumerate(lines, 1):
        if not current_method and not (line.strip().startswith("'") or line.strip().upper().startswith("REM ")):
            match = method_pattern.search(line)
            if match:
                current_method = match.group(1)
                method_body = [line]
                start_line = i
                continue
        
        if current_method:
            method_body.append(line)
            if re.search(r'^\s*End\s+(?:Sub|Function|Property)', line, re.IGNORECASE):
                methods_found.append({
                    "name": current_method,
                    "content": "\n".join(method_body),
                    "start": start_line,
                    "end": i
                })
                current_method = None
                method_body = []
    return methods_found

def _reparse_worker(file_name, content):
    """Worker function with timeout protection and regex fallback."""
    res = {
        "file_name": file_name,
        "variables": [],
        "methods": [],
        "calls": [],
        "antlr_success": False
    }
    
    # Try ANTLR
    result_container = {}
    def _antlr_task():
        try:
            parser = AntlrParserWrapper()
            result_container["result"] = parser.parse_content(content)
        except Exception as e:
            result_container["error"] = e
    
    t = threading.Thread(target=_antlr_task, daemon=True)
    t.start()
    t.join(timeout=30) # Faster timeout for reconstruction
    
    if not t.is_alive() and "error" not in result_container and "result" in result_container:
        antlr_res = result_container["result"]
        res["variables"] = antlr_res.get("variables", [])
        res["methods"] = antlr_res.get("methods", [])
        res["antlr_success"] = True
    
    # Fallback to Regex if ANTLR fails
    if not res["antlr_success"]:
        res["variables"] = _extract_variables_regex(content)
        res["methods"] = _extract_methods_regex(content)
        
    return res

def reconstruct_graph(db_path):
    project_name = os.path.basename(db_path).replace('.db', '')
    set_db_name(db_path)
    
    print(f"[*] Reconstructing graph from: {db_path}")
    graph = nx.DiGraph()
    graph.add_node(project_name, type="Project", label=project_name)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all nodes
    cursor.execute("SELECT node_id, node_type, file_path, code_content FROM code_nodes")
    all_nodes = cursor.fetchall()
    
    # Phase 1: Re-identify nodes and structure
    print(f"[*] Found {len(all_nodes)} nodes in database.")
    
    # Store file content for fallback regex
    file_contents = {}
    for node_id, node_type, file_path, content in all_nodes:
        if node_type == "File":
            file_contents[node_id] = content
            # Re-add File node
            loc = len(content.splitlines())
            graph.add_node(node_id, type="File", label=node_id, loc=loc)
            graph.add_edge(project_name, node_id, type="CONTAINS")
        elif node_type == "UIControl":
            graph.add_node(node_id, type="UIControl", label=node_id.split(':')[-1], loc=1)
            file_name = node_id.split(':')[0]
            graph.add_edge(file_name, node_id, type="CONTAINS")

    # Phase 2: Re-parse files to find CALL_PENDING and scopes IN PARALLEL
    print(f"[*] Re-parsing {len(file_contents)} files with ANTLR to recover ASG metadata using {multiprocessing.cpu_count()} cores...")
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = {executor.submit(_reparse_worker, fname, content): fname for fname, content in file_contents.items()}
        
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            res = future.result()
            file_name = res["file_name"]
            
            if "error" in res:
                print(f"    [{i}/{len(file_contents)}] Error in {file_name}: {res['error']}")
                continue
                
            print(f"    [{i}/{len(file_contents)}] Processing: {file_name}")
            
            # Add Variables
            for var in res["variables"]:
                var_name = var["name"]
                var_id = f"{file_name}:{var_name}"
                graph.add_node(var_id, type="Variable", label=var_name, loc=1)
                graph.add_edge(file_name, var_id, type="CONTAINS")
                
            # Add Methods
            for method in res["methods"]:
                method_name = method["name"]
                method_id = f"{file_name}:{method_name}"
                loc = (method["end"] - method["start"] + 1) if "end" in method else 1
                
                # ASG Metadata - Convert to string for GraphML compatibility
                locals_str = ",".join([l.lower() for l in method.get("locals", [])])
                params_str = ",".join([p.lower() for p in method.get("parameters", [])])
                
                graph.add_node(
                    method_id, 
                    type="Method", 
                    label=method_name, 
                    loc=loc,
                    locals=locals_str,
                    parameters=params_str
                )
                graph.add_edge(file_name, method_id, type="CONTAINS")
                
                # Recover Pendings
                if "calls" in method:
                    for target in method["calls"]:
                        graph.add_edge(method_id, target, type="CALL_PENDING")

    # Phase 3: Build Relationships
    print("[*] Building relationships (ASG resolution)...")
    
    methods = [n for n, d in graph.nodes(data=True) if d.get('type') == 'Method']
    variables = [n for n, d in graph.nodes(data=True) if d.get('type') == 'Variable']
    controls = [n for n, d in graph.nodes(data=True) if d.get('type') == 'UIControl']
    
    method_map = {m.split(':')[-1].lower(): m for m in methods}
    variable_map = {v.split(':')[-1].lower(): v for v in variables}
    
    for method_id in methods:
        pending_edges = [(u, v) for u, v, d in graph.out_edges(method_id, data=True) if d.get('type') == 'CALL_PENDING']
        if pending_edges:
            method_data = graph.nodes[method_id]
            # Convert back to set for logic
            local_names = set(method_data.get('locals', "").split(",")) if method_data.get('locals') else set()
            param_names = set(method_data.get('parameters', "").split(",")) if method_data.get('parameters') else set()
            
            for u, target_name in pending_edges:
                target_key = target_name.lower()
                
                if target_key in local_names or target_key in param_names:
                    continue
                    
                if target_key in method_map:
                    graph.add_edge(method_id, method_map[target_key], type="CALLS")
                elif target_key in variable_map:
                    graph.add_edge(method_id, variable_map[target_key], type="USES")
                elif "." in target_key:
                    parts = target_key.split(".")
                    obj_name = parts[0]
                    member_name = parts[-1]
                    found_qualified = False
                    
                    for m_id in methods:
                        m_file, m_name = m_id.split(":", 1) if ":" in m_id else ("", m_id)
                        m_file_base = m_file.split(".")[0].lower()
                        if m_file_base == obj_name and m_name.lower() == member_name:
                            graph.add_edge(method_id, m_id, type="CALLS")
                            found_qualified = True
                            break
                    
                    if not found_qualified:
                        for v_id in variables:
                            v_file, v_name = v_id.split(":", 1) if ":" in v_id else ("", v_id)
                            v_file_base = v_file.split(".")[0].lower()
                            if v_file_base == obj_name and v_name.lower() == member_name:
                                graph.add_edge(method_id, v_id, type="USES")
                                found_qualified = True
                                break
                    
                    if not found_qualified:
                        if member_name in method_map:
                            graph.add_edge(method_id, method_map[member_name], type="CALLS")
                        elif member_name in variable_map:
                            graph.add_edge(method_id, variable_map[member_name], type="USES")
            
            for u, v in pending_edges:
                graph.remove_edge(u, v)

    # TRIGGERS
    methods_by_file = {}
    for m_id in methods:
        f_name = m_id.split(':')[0]
        if f_name not in methods_by_file:
            methods_by_file[f_name] = []
        methods_by_file[f_name].append(m_id)

    for control_id in controls:
        if ':' not in control_id: continue
        file_name, control_name = control_id.split(':')
        methods_in_file = methods_by_file.get(file_name, [])
        prefix = f"{file_name}:{control_name}_".lower()
        for m_id in methods_in_file:
            if m_id.lower().startswith(prefix):
                graph.add_edge(control_id, m_id, type="TRIGGERS")

    # SAVE GRAPHML
    output_path = db_path.replace('.db', '.graphml')
    print(f"[*] Saving graph to: {output_path}")
    nx.write_graphml(graph, output_path)
    print("[*] DONE!")
    conn.close()

if __name__ == "__main__":
    db = sys.argv[1] if len(sys.argv) > 1 else "output/argentum-online-server.db"
    reconstruct_graph(db)
