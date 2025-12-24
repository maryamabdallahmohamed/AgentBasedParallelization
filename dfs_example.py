import random
import time

def generate_graph(nodes=200, density=0.1):
    g = {str(i): [] for i in range(nodes)}
    for i in range(nodes):
        if i + 1 < nodes: 
            g[str(i)].append(str(i+1))
        for j in range(nodes):
            if i != j and random.random() < density: 
                g[str(i)].append(str(j))
    return g

GRAPH = generate_graph()
START_NODE = "0"


def dfs_traversal(graph, start):
    # Using Iterative DFS is safer for large graphs (avoids RecursionError)
    visited = set()
    order = []
    stack = [start]
    
    while stack:
        node = stack.pop()
        
        if node not in visited:
            # SIMULATED WORK: 0.5ms per node
            time.sleep(0.0005)
            
            visited.add(node)
            order.append(node)
            
            # Add neighbors to stack
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    stack.append(neighbor)
    return order