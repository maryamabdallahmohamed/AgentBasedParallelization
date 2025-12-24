from collections import deque
import random
import time

# Generate a larger graph so we can measure performance
def generate_graph(nodes=200, density=0.1):
    g = {str(i): [] for i in range(nodes)}
    for i in range(nodes):
        # Ensure some connectivity
        if i + 1 < nodes: 
            g[str(i)].append(str(i+1))
        # Add random edges
        for j in range(nodes):
            if i != j and random.random() < density: 
                g[str(i)].append(str(j))
    return g

# Use a generated graph instead of a tiny manual one
GRAPH = generate_graph()
START_NODE = "0"


def bfs_traversal(graph, start):
    visited = set([start])
    order = []
    queue = deque([start])
    while queue:
        node = queue.popleft()
        order.append(node)
        
        # SIMULATED WORK: 0.5ms per node 
        # (This allows parallel threads to actually speed things up)
        time.sleep(0.0005)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order