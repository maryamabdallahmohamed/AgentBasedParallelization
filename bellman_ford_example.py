import random
import time

def generate_weighted_graph(nodes=50, density=0.2):
    g = {str(i): {} for i in range(nodes)}
    for i in range(nodes):
        if i + 1 < nodes: 
            g[str(i)][str(i+1)] = random.randint(1, 10)
        for j in range(nodes):
            if i != j and random.random() < density: 
                g[str(i)][str(j)] = random.randint(1, 10)
    return g

GRAPH = generate_weighted_graph()
START_NODE = "0"

def bellman_ford_traversal(graph, start):
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    vertices = list(graph.keys())
    
    # Simulate work so parallel threads are useful
    WORK_DELAY = 0.0005

    for _ in range(len(vertices) - 1):
        # Simulate Chunk Work
        time.sleep(WORK_DELAY * 10) 
        
        for u in graph:
            for v, w in graph[u].items():
                if distances[u] + w < distances[v]:
                    distances[v] = distances[u] + w
                    
    return distances