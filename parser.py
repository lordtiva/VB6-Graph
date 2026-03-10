import os
import re
import networkx as nx
from db import init_db, save_node, set_db_name
import sqlite3

class VB6Parser:
    def __init__(self, project_name=None):
        self.graph = nx.DiGraph()
        self.project_path = None
        if project_name:
            set_db_name(project_name)
        init_db()

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
        set_db_name(project_name)
        init_db()
        
        print(f"[*] Analyzing Project: {project_name}")
        self.graph.add_node(project_name, type="Project", label=project_name)
        save_node(project_name, "Project", vbp_file, "")

        # Phase 1: Identify all nodes
        files_to_parse = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.bas', '.cls', '.frm')):
                    files_to_parse.append(os.path.join(root, file))
        
        total_files = len(files_to_parse)
        print(f"[*] Found {total_files} files to parse.")
        
        for i, file_path in enumerate(files_to_parse, 1):
            print(f"    [{i}/{total_files}] Parsing: {os.path.basename(file_path)}")
            self.parse_file(file_path, project_name)
        
        # Phase 2: Build Relationships (CALLS, USES, TRIGGERS)
        print("[*] Building relationships (this may take a while)...")
        self.build_relationships()

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

        print(f"    - Analyzing {len(methods)} methods bodies...")
        for i, method_id in enumerate(methods, 1):
            if i % 500 == 0:
                print(f"    - Progress: {i}/{len(methods)} methods analyzed.")
                
            code = self.get_stored_code(method_id)
            if not code: continue

            # Tokenize code simply (alphanumeric + underscore)
            tokens = set(re.findall(r'\b[a-zA-Z0-9_]+\b', code.lower()))
            
            # Skip the first token if it's the method name itself (definition)
            method_name_simple = method_id.split(':')[-1].lower()
            if method_name_simple in tokens:
                tokens.remove(method_name_simple)

            # Find intersection with known methods
            found_methods = tokens.intersection(method_keywords)
            for m_key in found_methods:
                self.graph.add_edge(method_id, method_map[m_key], type="CALLS")

            # Find intersection with known variables
            found_vars = tokens.intersection(variable_keywords)
            for v_key in found_vars:
                # To be safe, verify it's not a local variable or param? 
                # (Standard VB6 regex approach is simplified as requested)
                self.graph.add_edge(method_id, variable_map[v_key], type="USES")

        # Detect TRIGGERS (UI Control -> Method)
        print(f"    - Linking {len(controls)} UI controls to event handlers...")
        for control_id in controls:
            parts = control_id.split(':')
            file_name = parts[0]
            control_name = parts[-1]
            
            # Look for methods in the same file starting with control_name_
            prefix = f"{file_name}:{control_name}_".lower()
            for m_id in methods:
                if m_id.lower().startswith(prefix):
                    self.graph.add_edge(control_id, m_id, type="TRIGGERS")

    def get_stored_code(self, node_id):
        # Helper to get code from SQLite via db.py
        from db import get_node_code
        return get_node_code(node_id)

    def parse_file(self, file_path, project_name):
        file_name = os.path.basename(file_path)
        file_type = "File"
        self.graph.add_node(file_name, type=file_type, label=file_name)
        self.graph.add_edge(project_name, file_name, type="CONTAINS")
        
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
        
        save_node(file_name, file_type, file_path, content)
        
        # Extract Globals/Public variables (Phase 2 Variable node)
        self.extract_variables(content, file_name, file_path)
        
        # Extract Methods
        self.extract_methods(content, file_name, file_path)
        
        # Extract UI Controls (only for .frm)
        if file_path.lower().endswith('.frm'):
            self.extract_ui_controls(content, file_name, file_path)

    def extract_variables(self, content, file_name, file_path):
        # Public | Global | Dim (at module level)
        # Simplification: we only look at the header before first Sub/Function
        header = content.splitlines()
        var_pattern = re.compile(r'^(?:Public|Global|Dim)\s+([a-zA-Z0-9_]+)', re.IGNORECASE)
        
        for line in header:
            # Stop if we find a method
            if re.search(r'(?:Sub|Function|Property)', line, re.IGNORECASE):
                break
            match = var_pattern.search(line)
            if match:
                var_name = match.group(1)
                var_id = f"{file_name}:{var_name}"
                self.graph.add_node(var_id, type="Variable", label=var_name)
                self.graph.add_edge(file_name, var_id, type="CONTAINS")
                save_node(var_id, "Variable", file_path, line)

    def extract_methods(self, content, file_name, file_path):
        # Regex for methods: Sub, Function, Property
        method_pattern = re.compile(
            r'(?:(?:Public|Private|Friend)\s+)?(?:Static\s+)?(?:Sub|Function|Property\s+(?:Get|Let|Set))\s+([a-zA-Z0-9_]+)',
            re.IGNORECASE
        )
        
        lines = content.splitlines()
        current_method = None
        method_body = []
        
        for line in lines:
            match = method_pattern.search(line)
            if match and not current_method:
                current_method = match.group(1)
                method_body = [line]
            elif current_method:
                method_body.append(line)
                if re.search(r'End\s+(Sub|Function|Property)', line, re.IGNORECASE):
                    method_id = f"{file_name}:{current_method}"
                    self.graph.add_node(method_id, type="Method", label=current_method)
                    self.graph.add_edge(file_name, method_id, type="CONTAINS")
                    save_node(method_id, "Method", file_path, "\n".join(method_body))
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
                save_node(control_id, "UIControl", file_path, line)

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
