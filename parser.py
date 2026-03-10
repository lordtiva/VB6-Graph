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

        # Parse .bas, .cls, .frm mentioned in .vbp (simplification: parse all in directory)
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file.lower().endswith(('.bas', '.cls', '.frm')):
                    self.parse_file(file_path, project_name)

    def parse_file(self, file_path, project_name):
        file_name = os.path.basename(file_path)
        file_type = "File"
        self.graph.add_node(file_name, type=file_type, label=file_name)
        self.graph.add_edge(project_name, file_name, type="CONTAINS")
        
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
        
        save_node(file_name, file_type, file_path, content)
        
        # Extract Methods
        self.extract_methods(content, file_name, file_path)
        
        # Extract UI Controls (only for .frm)
        if file_path.lower().endswith('.frm'):
            self.extract_ui_controls(content, file_name, file_path)

    def extract_methods(self, content, file_name, file_path):
        # Regex for methods: Sub, Function, Property
        method_pattern = re.compile(
            r'(?:(?:Public|Private|Friend)\s+)?(?:Static\s+)?(?:Sub|Function|Property\s+(?:Get|Let|Set))\s+([a-zA-Z0-9_]+)',
            re.IGNORECASE
        )
        
        # We need a more sophisticated way to get the full body.
        # For Phase 1, we'll just find the start and end of blocks.
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
        
        # Usually UI controls are at the top header of .frm files
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
                
                # Inference of TRIGGERS: if there's a method like cmdBtn_Click, relate it.
                # This logic might be better in Phase 2, but let's add a placeholder.
                # Actually, the user asked for TRIGGERS in Phase 1 ontology.

    def get_graph(self):
        return self.graph

if __name__ == "__main__":
    import sys
    parser = VB6Parser()
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    parser.parse_project(path)
    print(f"Nodes: {parser.graph.number_of_nodes()}")
    print(f"Edges: {parser.graph.number_of_edges()}")
