import networkx as nx
import os

class CodeAnalyzer:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def detect_dead_code(self):
        """
        Identifies dead code using reachability analysis.
        Enhanced for VB6/Argentum Online specific patterns.
        """
        # 1. Identify Entry Points
        entry_points = set()
        
        # Nodes target of TRIGGERS (UI events) are entry points
        for u, v, d in self.graph.edges(data=True):
            if d.get('type') == 'TRIGGERS':
                entry_points.add(v)
        
        # Common VB6/Argentum entry points
        for n, d in self.graph.nodes(data=True):
            node_type = d.get('type')
            node_name = n.split(':')[-1] if ':' in n else n
            node_name_lower = node_name.lower()
            file_name = n.split(':')[0].lower() if ':' in n else ""

            if node_type == 'UIControl':
                entry_points.add(n)
            elif node_type == 'Method':
                # VB6/Argentum well-known entry points
                if node_name_lower in ("main", "sub main", "form_load", "class_initialize", "class_terminate", "timer_timer"):
                    entry_points.add(n)
                
                # Protocol and Network handlers (Critical for Argentum)
                elif (node_name_lower.startswith('handle') or 
                      node_name_lower.startswith('incomingdata') or
                      node_name_lower.startswith('protocol_') or
                      node_name_lower in ['onserverrecv', 'receive', 'eventosockread', 'senddata', 'server_main']):
                    entry_points.add(n)
                
                # Public methods in .bas (Modules) are often entry points for the whole system
                elif file_name.endswith('.bas') and not node_name_lower.startswith('_'):
                    # To be conservative, we treat all public .bas methods as alive 
                    # unless we are sure they are internally scoped (not the case in simple VB6)
                    entry_points.add(n)

        # 2. Perform reachability analysis (BFS/DFS)
        reachable_nodes = set()
        for ep in entry_points:
            if ep in self.graph:
                if ep not in reachable_nodes:
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

    def detect_communities(self):
        """
        Detección de "Comunidades" (Microservicios ocultos) usando el algoritmo de Louvain.
        Requiere un grafo no dirigido.
        """
        try:
            # Louvain requires an undirected graph
            undirected_graph = self.graph.to_undirected()
            communities = nx.community.louvain_communities(undirected_graph)
            
            # Map each node to a community ID
            node_to_community = {}
            for i, community in enumerate(communities):
                for node in community:
                    node_to_community[node] = i
            
            print(f"[*] Detected {len(communities)} communities in graph.")
            return node_to_community
        except Exception as e:
            print(f"Error detectando comunidades: {str(e)}")
            return {}
    def get_impact_analysis(self, node_id):
        """
        Calculates the "Blast Radius" of modifying a node.
        Categorizes impact into Direct (immediate users) and Indirect (recursive users).
        """
        if node_id not in self.graph:
            return {"error": f"Node {node_id} not found."}
            
        ntype = self.graph.nodes[node_id].get('type', 'Unknown')
        
        # Start set of nodes to analyze
        targets = {node_id}
        
        # If it's a File, anyone depending on its members is also impacted
        if ntype == 'File':
            members = [v for u, v, d in self.graph.out_edges(node_id, data=True) 
                       if d.get('type') in ('CONTAINS', 'Method', 'Variable', 'UIControl')]
            targets.update(members)

        direct_impacted = set()
        for t in targets:
            if t in self.graph:
                # Predecessors are immediate callers/users
                direct_impacted.update(self.graph.predecessors(t))
        
        # Indirect impact: ancestors that are NOT direct predecessors
        all_impacted = set()
        for t in targets:
            if t in self.graph:
                all_impacted.update(nx.ancestors(self.graph, t))
        
        # Clean up: remove self and project node
        all_impacted -= targets
        all_impacted.discard(os.path.basename(node_id.split(':')[0])) # Approximate Project name
        
        indirect_impacted = all_impacted - direct_impacted

        def categorize(node_set):
            res = {"files": [], "methods": [], "ui_controls": [], "external": [], "other": 0}
            for node in node_set:
                t = self.graph.nodes[node].get('type', 'Unknown')
                if t == 'File': res["files"].append(node)
                elif t == 'Method': res["methods"].append(node)
                elif t == 'UIControl': res["ui_controls"].append(node)
                elif t == 'External': res["external"].append(node)
                elif t != 'Project': res["other"] += 1
            return res

        direct_categorized = categorize(direct_impacted)
        indirect_categorized = categorize(indirect_impacted)
                
        return {
            "node_id": node_id,
            "direct_impact_count": len(direct_impacted),
            "indirect_impact_count": len(indirect_impacted),
            "direct": direct_categorized,
            "indirect": indirect_categorized
        }

    def calculate_architectural_metrics(self):
        """
        Calcula métricas de calidad arquitectónica por archivo.
        - Ca (Afferent Coupling): Cuántos archivos externos dependen de este.
        - Ce (Efferent Coupling): De cuántos archivos externos depende este.
        - I (Instability): Ce / (Ca + Ce). 0 = Estable, 1 = Inestable.
        """
        metrics = {}
        files = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'File']
        
        # Colapsar a grafo de archivos
        file_graph = nx.DiGraph()
        file_graph.add_nodes_from(files)
        for u, v, d in self.graph.edges(data=True):
            if d.get('type') in ('CALLS', 'USES'):
                file_u = u.split(':')[0] if ':' in u else u
                file_v = v.split(':')[0] if ':' in v else v
                if file_u in files and file_v in files and file_u != file_v:
                    file_graph.add_edge(file_u, file_v)

        for f in files:
            ce = file_graph.out_degree(f)
            ca = file_graph.in_degree(f)
            instability = round(ce / (ca + ce), 2) if (ca + ce) > 0 else 0
            metrics[f] = {
                "afferent": ca,
                "efferent": ce,
                "instability": instability
            }
        
        return metrics

    def get_analysis_summary(self):
        return {
            "dead_code": self.detect_dead_code(),
            "god_objects": self.detect_god_objects(),
            "circular_dependencies": self.detect_circular_dependencies(),
            "communities": self.detect_communities(),
            "metrics": self.calculate_architectural_metrics()
        }

if __name__ == "__main__":
    # Test rápido si se ejecuta directamente
    import sys
    if len(sys.argv) > 1:
        g = nx.read_graphml(sys.argv[1])
        analyzer = CodeAnalyzer(g)
        print(analyzer.get_analysis_summary())
