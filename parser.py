import os
import re
import networkx as nx
from db import init_db, save_node
import sqlite3

class VB6Parser:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.project_path = None
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
        project_name = os.path.basename(vbp_file)
        self.graph.add_node(project_name, type="Project", label=project_name)
        save_node(project_name, "Project", vbp_file, "")

        # Phase 1: Identify all nodes
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file.lower().endswith(('.bas', '.cls', '.frm')):
                    self.parse_file(file_path, project_name)
        
        # Phase 2: Build Relationships (CALLS, USES, TRIGGERS)
        self.build_relationships()

    def build_relationships(self):
        """Iterates over stored methods to find calls and uses."""
        # Get all methods from the graph
        methods = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'Method']
        variables = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'Variable']
        controls = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'UIControl']

        # Pre-calculate method and variable names for faster lookup
        method_names = {m.split(':')[-1]: m for m in methods}
        variable_names = {v.split(':')[-1]: v for v in variables}

        for method_id in methods:
            code = self.get_stored_code(method_id)
            if not code: continue

            # Detect CALLS
            for m_name, m_id in method_names.items():
                if m_id == method_id: continue # Don't call yourself
                # Regex for method call (not a definition)
                # Word boundary, name, and either ( or space/newline
                if re.search(rf'\b{m_name}\b', code, re.IGNORECASE):
                    # verify it's not the definition line
                    lines = code.splitlines()
                    for line in lines[1:]: # Skip the first line which is the definition
                        if re.search(rf'\b{m_name}\b', line, re.IGNORECASE):
                            self.graph.add_edge(method_id, m_id, type="CALLS")
                            break

            # Detect USES (Variables)
            for v_name, v_id in variable_names.items():
                if re.search(rf'\b{v_name}\b', code, re.IGNORECASE):
                    self.graph.add_edge(method_id, v_id, type="USES")

        # Detect TRIGGERS (UI Control -> Method)
        # Usually Name_Event (e.g., btnGuardar_Click)
        for control_id in controls:
            control_name = control_id.split(':')[-1]
            file_name = control_id.split(':')[0]
            # Look for methods in the same file starting with control_name_
            for method_id in methods:
                if method_id.startswith(f"{file_name}:{control_name}_"):
                    self.graph.add_edge(control_id, method_id, type="TRIGGERS")

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
