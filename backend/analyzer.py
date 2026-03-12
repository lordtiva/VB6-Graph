import networkx as nx
import os

class CodeAnalyzer:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def detect_dead_code(self):
        """
        Nodos tipo 'Method' con in-degree = 0 (que no sean llamados por nadie) 
        y que no tengan aristas entrantes de tipo 'TRIGGERS' (UI).
        En nuestro grafo, un método siempre tiene una arista 'CONTAINS' desde su archivo.
        Por lo tanto, buscamos métodos que SOLO tengan la arista 'CONTAINS'.
        """
        dead_methods = []
        methods = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'Method']
        
        for method in methods:
            # Buscamos aristas entrantes que no sean 'CONTAINS'
            incoming_calls = [u for u, v, d in self.graph.in_edges(method, data=True) 
                             if d.get('type') in ('CALLS', 'TRIGGERS')]
            
            if not incoming_calls:
                dead_methods.append(method)
        
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

        from itertools import islice
        try:
            # simple_cycles can be exponential, so we limit to the first 50 results
            cycles = list(islice(nx.simple_cycles(file_graph), 50))
            return cycles
        except Exception as e:
            return [[f"Error detectando ciclos: {str(e)}"]]

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
