import networkx as nx
import os

class CodeAnalyzer:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def detect_dead_code(self):
        """
        Identifies dead code using reachability analysis.
        Dead code consists of methods that are NOT reachable from "Entry Points".
        Entry Points:
        - Methods triggered by UI (TRIGGERS edges)
        - Methods explicitly named "Main" or "Sub Main"
        """
        # 1. Identify Entry Points
        entry_points = set()
        
        # Nodes target of TRIGGERS (UI events)
        for u, v, d in self.graph.edges(data=True):
            if d.get('type') == 'TRIGGERS':
                entry_points.add(v)
        
        # Common VB6/Argentum entry points
        # We iterate through all nodes and add them if they match the criteria
        for n, d in self.graph.nodes(data=True):
            node_type = d.get('type')
            node_name_lower = n.split(':')[-1].lower() if ':' in n else n.lower()

            if node_type == 'UIControl':
                entry_points.add(n)
            elif node_type == 'Method':
                # Methods named Main (case-insensitive)
                if node_name_lower == "main":
                    entry_points.add(n)
                # Network/Protocol handlers, Events (Form_, Class_, Timer_), and Interface implementations
                elif (node_name_lower.startswith('handle') or 
                      node_name_lower.startswith('event') or 
                      '_' in node_name_lower or 
                      node_name_lower in ['onserverrecv', 'receive', 'eventosockread', 'senddata']):
                    entry_points.add(n)

        # 2. Perform reachability analysis (BFS/DFS)
        reachable_nodes = set()
        for ep in entry_points:
            if ep in self.graph:
                reachable_nodes.add(ep)
                reachable_nodes.update(nx.descendants(self.graph, ep))

        # 3. Dead methods are Methods NOT in reachable_nodes
        all_methods = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'Method']
        dead_methods = [m for m in all_methods if m not in reachable_nodes]
        
        return dead_methods

    def detect_god_objects(self, top_n=10):
        """
        Los top 10 métodos/archivos usando el algoritmo de centralidad nx.pagerank()
        o evaluando los out-degree (que llaman a demasiadas cosas).
        Usaremos PageRank para una métrica más profesional de 'importancia' o 'complejidad'.
        """
        try:
            pagerank = nx.pagerank(self.graph)
            # Ordenar por valor de pagerank descendente
            sorted_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
            
            # Filtrar solo Archivos y Métodos para God Objects
            god_objects = []
            for node, score in sorted_nodes:
                ntype = self.graph.nodes[node].get('type')
                if ntype in ('File', 'Method'):
                    god_objects.append({"node": node, "type": ntype, "score": round(score, 4)})
                if len(god_objects) >= top_n:
                    break
            return god_objects
        except Exception as e:
            return [{"error": f"Error calculando PageRank: {str(e)}"}]

    def detect_circular_dependencies(self):
        """
        Detección de ciclos a nivel de Archivos usando nx.simple_cycles().
        Primero colapsamos el grafo a nivel de archivos.
        """
        file_graph = nx.DiGraph()
        files = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'File']
        file_graph.add_nodes_from(files)

        for u, v, d in self.graph.edges(data=True):
            if d.get('type') in ('CALLS', 'USES'):
                # Extraer el archivo de origen y destino
                # u y v pueden ser Method, Variable o File
                file_u = u.split(':')[0] if ':' in u else u
                file_v = v.split(':')[0] if ':' in v else v

                if file_u in files and file_v in files and file_u != file_v:
                    file_graph.add_edge(file_u, file_v)

        try:
            # Use Strongly Connected Components to find groups of files that are all reachable from each other
            sccs = list(nx.strongly_connected_components(file_graph))
            # Filter only components with more than 1 node (actual cycles)
            cycles = [list(component) for component in sccs if len(component) > 1]
            # Sort by size descending
            cycles.sort(key=len, reverse=True)
            return cycles
        except Exception as e:
            return [[f"Error detectando componentes: {str(e)}"]]

    def get_analysis_summary(self):
        return {
            "dead_code": self.detect_dead_code(),
            "god_objects": self.detect_god_objects(),
            "circular_dependencies": self.detect_circular_dependencies()
        }

if __name__ == "__main__":
    # Test rápido si se ejecuta directamente
    import sys
    if len(sys.argv) > 1:
        g = nx.read_graphml(sys.argv[1])
        analyzer = CodeAnalyzer(g)
        print(analyzer.get_analysis_summary())
