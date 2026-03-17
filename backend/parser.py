import os
import re
import networkx as nx
from db import init_db, save_node, set_db_name
import sqlite3
import concurrent.futures
import multiprocessing

try:
    from antlr_parser_wrapper import AntlrParserWrapper
except ImportError:
    AntlrParserWrapper = None

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

def _extract_ui_controls_regex(content):
    control_pattern = re.compile(r'^\s*Begin\s+\b[a-zA-Z0-9_.]+\b\s+\b([a-zA-Z0-9_]+)\b', re.IGNORECASE)
    controls_found = []
    for line in content.splitlines():
        match = control_pattern.search(line)
        if match:
            controls_found.append(match.group(1))
    return controls_found

def _parse_file_worker(file_path):
    file_name = os.path.basename(file_path)
    try:
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
    except Exception as e:
        return {"error": str(e), "file_path": file_path}

    res = {
        "file_path": file_path,
        "file_name": file_name,
        "content": content,
        "lines_count": len(content.splitlines()),
        "methods": [],
        "variables": [],
        "ui_controls": [],
        "antlr_success": False
    }

    # Try ANTLR
    if AntlrParserWrapper:
        import threading
        
        result_container = {}
        def _antlr_task():
            try:
                result_container["result"] = AntlrParserWrapper().parse_file(file_path)
            except Exception as e:
                result_container["error"] = e
        
        t = threading.Thread(target=_antlr_task, daemon=True)
        t.start()
        t.join(timeout=600)  # Standardized 10 min timeout
        
        if t.is_alive():
            print(f"    [!] ANTLR timed out for {file_name}. Falling back to regex.")
            res["antlr_success"] = False
        else:
            if "error" in result_container:
                res["antlr_success"] = False
            else:
                antlr_res = result_container.get("result", {})
                res["methods"] = antlr_res.get("methods", [])
                res["variables"] = antlr_res.get("variables", [])
                res["antlr_success"] = True
                
                # 'False Success' Detection
                if len(res["methods"]) == 0 and len(res["variables"]) == 0 and res["lines_count"] > 10:
                    res["antlr_success"] = False
    
    # Fallback to Regex if ANTLR failed or not available
    if not res["antlr_success"]:
        res["variables"] = _extract_variables_regex(content)
        res["methods"] = _extract_methods_regex(content)
    
    # UI Controls
    if file_path.lower().endswith('.frm'):
        res["ui_controls"] = _extract_ui_controls_regex(content)
        
    return res

class VB6Parser:
    def __init__(self, project_name=None):
        self.graph = nx.DiGraph()
        self.project_path = None
        if project_name:
            set_db_name(project_name)
        init_db()
        
        self.antlr_parser = AntlrParserWrapper() if AntlrParserWrapper else None

        # Persistent connection for batch parsing
        from db import get_connection
        self.conn = get_connection()
        self.nodes_saved_count = 0

    def find_vbp(self, directory):
        """Finds the .vbp file in the given directory."""
        for file in os.listdir(directory):
            if file.lower().endswith('.vbp'):
                self.project_path = os.path.join(directory, file)
                return self.project_path
        return None

    def parse_project(self, directory):
        """Main entry point to parse a VB6 project."""
        vbp_file = self.find_vbp(directory)
        if not vbp_file:
            print(f"No .vbp file found in {directory}")
            return

        # Add Project Node
        project_name = os.path.basename(directory.rstrip(os.sep))
        
        print(f"[*] Analyzing Project: {project_name}")
        self.graph.add_node(project_name, type="Project", label=project_name)
        self._save_node_batched(project_name, "Project", vbp_file, "")

        # Phase 1: Identify all nodes
        files_to_parse = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.bas', '.cls', '.frm')):
                    files_to_parse.append(os.path.join(root, file))
        
        total_files = len(files_to_parse)
        print(f"[*] Found {total_files} files to parse.")
        print(f"[*] Starting parallel parsing using {multiprocessing.cpu_count()} cores...")
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            futures = {executor.submit(_parse_file_worker, fp): fp for fp in files_to_parse}
            
            for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
                res = future.result()
                if "error" in res:
                    print(f"    [{i}/{total_files}] Error parsing {os.path.basename(res['file_path'])}: {res['error']}")
                    continue
                
                file_name = res["file_name"]
                file_path = res["file_path"]
                
                print(f"    [{i}/{total_files}] Processing results: {file_name}")
                
                # Update Graph and DB (Sequential)
                self.graph.add_node(file_name, type="File", label=file_name, loc=res["lines_count"])
                self.graph.add_edge(project_name, file_name, type="CONTAINS")
                self._save_node_batched(file_name, "File", file_path, res["content"])
                
                # Add Variables
                for var in res["variables"]:
                    var_name = var["name"]
                    var_id = f"{file_name}:{var_name}"
                    self.graph.add_node(var_id, type="Variable", label=var_name, loc=1)
                    self.graph.add_edge(file_name, var_id, type="CONTAINS")
                    content = var.get("content", f"Public/Private {var_name}")
                    self._save_node_batched(var_id, "Variable", file_path, content)

                # Add Methods
                for method in res["methods"]:
                    method_name = method["name"]
                    method_id = f"{file_name}:{method_name}"
                    loc = (method["end"] - method["start"] + 1) if "end" in method else 1
                    self.graph.add_node(method_id, type="Method", label=method_name, loc=loc)
                    self.graph.add_edge(file_name, method_id, type="CONTAINS")
                    self._save_node_batched(method_id, "Method", file_path, method["content"])
                    
                    if "calls" in method:
                        for target in method["calls"]:
                            self.graph.add_edge(method_id, target, type="CALL_PENDING")

                # Add UI Controls
                for control_name in res["ui_controls"]:
                    control_id = f"{file_name}:{control_name}"
                    self.graph.add_node(control_id, type="UIControl", label=control_name, loc=1)
                    self.graph.add_edge(file_name, control_id, type="CONTAINS")
                    self._save_node_batched(control_id, "UIControl", file_path, f"Begin {control_name}")

        # Phase 2: Build Relationships (CALLS, USES, TRIGGERS)
        print("[*] Building relationships (this may take a while)...")
        self.build_relationships()
        
        # Final commit and close
        self.conn.commit()
        self.conn.close()

    def build_relationships(self):
        """Iterates over stored methods to find calls and uses."""
        # Get all methods from the graph
        methods = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'Method']
        variables = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'Variable']
        controls = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'UIControl']

        print(f"    - Building lookup maps for {len(methods)} methods and {len(variables)} variables...")
        # Map simple name to full node_id
        method_map = {m.split(':')[-1].lower(): m for m in methods}
        variable_map = {v.split(':')[-1].lower(): v for v in variables}
        
        # Keyword list for fast intersection
        method_keywords = set(method_map.keys())
        variable_keywords = set(variable_map.keys())

        print(f"    - Processing ANTLR findings and fallback regex analysis...")
        for i, method_id in enumerate(methods, 1):
            if i % 500 == 0:
                print(f"    - Progress: {i}/{len(methods)} methods analyzed.")
            
            # Resolve CALL_PENDING edges from ANTLR
            pending_edges = [(u, v) for u, v, d in self.graph.out_edges(method_id, data=True) if d.get('type') == 'CALL_PENDING']
            if pending_edges:
                for u, target_name in pending_edges:
                    target_key = target_name.lower()
                    if target_key in method_map:
                        self.graph.add_edge(method_id, method_map[target_key], type="CALLS")
                    elif target_key in variable_map:
                        self.graph.add_edge(method_id, variable_map[target_key], type="USES")
                
                # Remove pending edges
                for u, v in pending_edges:
                    self.graph.remove_edge(u, v)
                
                # We can skip regex scan for this method if we have ANTLR results
                continue

            # Fallback to Regex for methods not handled by ANTLR
            code = self.get_stored_code(method_id)
            if not code: continue

            # Strip VB6 comments
            code_lines = []
            for line in code.splitlines():
                clean_line = re.split(r"\'|\b[rR][eE][mM]\b", line)[0]
                code_lines.append(clean_line)
            
            clean_code = "\n".join(code_lines)
            tokens = set(re.findall(r'\b[a-zA-Z0-9_]+\b', clean_code.lower()))
            method_name_simple = method_id.split(':')[-1].lower()
            if method_name_simple in tokens:
                tokens.remove(method_name_simple)

            found_methods = tokens.intersection(method_keywords)
            for m_key in found_methods:
                self.graph.add_edge(method_id, method_map[m_key], type="CALLS")

            found_vars = tokens.intersection(variable_keywords)
            for v_key in found_vars:
                self.graph.add_edge(method_id, variable_map[v_key], type="USES")

        # Detect TRIGGERS (UI Control -> Method)
        print(f"    - Linking {len(controls)} UI controls to event handlers...")
        
        # Optimization: group methods by file to avoid O(N*M) search
        methods_by_file = {}
        for m_id in methods:
            f_name = m_id.split(':')[0]
            if f_name not in methods_by_file:
                methods_by_file[f_name] = []
            methods_by_file[f_name].append(m_id)

        for control_id in controls:
            parts = control_id.split(':')
            file_name = parts[0]
            control_name = parts[-1]
            
            # Look for methods in the same file starting with control_name_
            methods_in_file = methods_by_file.get(file_name, [])
            prefix = f"{file_name}:{control_name}_".lower()
            for m_id in methods_in_file:
                if m_id.lower().startswith(prefix):
                    self.graph.add_edge(control_id, m_id, type="TRIGGERS")

        # Phase 3: Tag External Nodes
        # Any node that was created as a target of a call but was never defined in a file
        print(f"    - Tagging external dependencies...")
        for n, d in self.graph.nodes(data=True):
            if 'type' not in d:
                self.graph.nodes[n]['type'] = 'External'
                if 'label' not in d:
                    self.graph.nodes[n]['label'] = n.split(':')[-1] # Simple name
                    self.graph.nodes[n]['loc'] = 0

    def get_stored_code(self, node_id):
        # Helper to get code from SQLite via db.py
        from db import get_node_code
        return get_node_code(node_id)
    
    def _save_node_batched(self, node_id, node_type, file_path, code_content):
        """Internal helper to save nodes with periodic commits."""
        save_node(node_id, node_type, file_path, code_content, conn=self.conn)
        self.nodes_saved_count += 1
        if self.nodes_saved_count % 100 == 0:
            self.conn.commit()
            # print(f"    - Batched commit: {self.nodes_saved_count} nodes saved.") # Removed for less verbose output

    def parse_file(self, file_path, project_name):
        file_name = os.path.basename(file_path)
        file_type = "File"
        
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
            
        lines_count = len(content.splitlines())
        self.graph.add_node(file_name, type=file_type, label=file_name, loc=lines_count)
        self.graph.add_edge(project_name, file_name, type="CONTAINS")
        
        self._save_node_batched(file_name, file_type, file_path, content)
        
        antlr_success = False
        if self.antlr_parser:
            try:
                # Use robust ANTLR parser
                result = self.antlr_parser.parse_file(file_path)
                
                # Add Variables
                for var in result["variables"]:
                    var_name = var["name"]
                    var_id = f"{file_name}:{var_name}"
                    self.graph.add_node(var_id, type="Variable", label=var_name, loc=1)
                    self.graph.add_edge(file_name, var_id, type="CONTAINS")
                    # We don't have the original line but we saved the file content
                    self._save_node_batched(var_id, "Variable", file_path, f"Public/Private {var_name}")

                # Add Methods
                for method in result["methods"]:
                    method_name = method["name"]
                    method_id = f"{file_name}:{method_name}"
                    loc = method["end"] - method["start"] + 1
                    self.graph.add_node(method_id, type="Method", label=method_name, loc=loc)
                    self.graph.add_edge(file_name, method_id, type="CONTAINS")
                    self._save_node_batched(method_id, "Method", file_path, method["content"])
                    
                    # Store direct calls found by ANTLR (already qualified by context)
                    for target in method["calls"]:
                        # We will link these in build_relationships to ensure nodes exist
                        self.graph.add_edge(method_id, target, type="CALL_PENDING")

                antlr_success = True
            except Exception as e:
                print(f"    [!] ANTLR failed for {file_name}: {e}. Falling back to regex.")

        if not antlr_success:
            # Fallback to legacy regex extraction
            self.extract_variables(content, file_name, file_path)
            self.extract_methods(content, file_name, file_path)
        
        # UI controls are still handled via regex for now as they are simple and reliable in frm headers
        if file_path.lower().endswith('.frm'):
            self.extract_ui_controls(content, file_name, file_path)

    def extract_variables(self, content, file_name, file_path):
        # Public | Global | Dim (at module level)
        # Using \b and ^\s* for precission
        var_pattern = re.compile(r'^\s*(?:Public|Global|Dim)\s+\b([a-zA-Z0-9_]+)\b', re.IGNORECASE)
        reserved = {'to', 'for', 'if', 'then', 'else', 'while', 'step', 'each', 'in', 'next', 'select', 'case'}
        
        for line in content.splitlines():
            # Stop if we find a method
            if re.search(r'^\s*(?:Public|Private|Friend|Static)?\s*(?:Sub|Function|Property)', line, re.IGNORECASE):
                break
            # Skip comments
            if line.strip().startswith("'") or line.strip().upper().startswith("REM "):
                continue

            match = var_pattern.search(line)
            if match:
                var_name = match.group(1)
                if var_name.lower() in reserved: continue
                var_id = f"{file_name}:{var_name}"
                self.graph.add_node(var_id, type="Variable", label=var_name, loc=1)
                self.graph.add_edge(file_name, var_id, type="CONTAINS")
                self._save_node_batched(var_id, "Variable", file_path, line)

    def extract_methods(self, content, file_name, file_path):
        # Regex for methods: Sub, Function, Property (Enforce start of line)
        method_pattern = re.compile(
            r'^\s*(?:(?:Public|Private|Friend)\s+)?(?:Static\s+)?(?:Sub|Function|Property\s+(?:Get|Let|Set))\s+\b([a-zA-Z0-9_]+)\b',
            re.IGNORECASE
        )
        reserved = {'to', 'for', 'if', 'then', 'else', 'while', 'step', 'each', 'in', 'next', 'select', 'case'}
        
        lines = content.splitlines()
        current_method = None
        method_body = []
        
        for line in lines:
            # Only match if we're not currently in a method or if the line is not a comment
            if not current_method and not (line.strip().startswith("'") or line.strip().upper().startswith("REM ")):
                match = method_pattern.search(line)
                if match:
                    method_name = match.group(1)
                    if method_name.lower() not in reserved:
                        current_method = method_name
                        method_body = [line]
                        continue

            if current_method:
                method_body.append(line)
                if re.search(r'^\s*End\s+(Sub|Function|Property)', line, re.IGNORECASE):
                    method_id = f"{file_name}:{current_method}"
                    loc = len(method_body)
                    self.graph.add_node(method_id, type="Method", label=current_method, loc=loc)
                    self.graph.add_edge(file_name, method_id, type="CONTAINS")
                    self._save_node_batched(method_id, "Method", file_path, "\n".join(method_body))
                    current_method = None
                    method_body = []

    def extract_ui_controls(self, content, file_name, file_path):
        # Begin VB.CommandButton btnGuardar
        control_pattern = re.compile(r'Begin\s+([a-zA-Z0-9_.]+)\s+([a-zA-Z0-9_]+)', re.IGNORECASE)
        
        lines = content.splitlines()
        for line in lines:
            match = control_pattern.search(line)
            if match:
                control_type = match.group(1)
                control_name = match.group(2)
                control_id = f"{file_name}:{control_name}"
                
                self.graph.add_node(control_id, type="UIControl", label=f"{control_name} ({control_type})")
                self.graph.add_edge(file_name, control_id, type="CONTAINS")
                self._save_node_batched(control_id, "UIControl", file_path, line)

    def get_graph(self):
        return self.graph

if __name__ == "__main__":
    import sys
    parser = VB6Parser()
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    parser.parse_project(path)
    print(f"Nodes: {parser.graph.number_of_nodes()}")
    print(f"Edges: {parser.graph.number_of_edges()}")
    
    # Print relationship counts
    rels = {}
    for _, _, d in parser.graph.edges(data=True):
        rtype = d.get('type', 'Unknown')
        rels[rtype] = rels.get(rtype, 0) + 1
    print(f"Relationships: {rels}")
