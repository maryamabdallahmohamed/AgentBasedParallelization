import heapq
import random
import time

def generate_weighted_graph(nodes=200, density=0.1):
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

def dijkstra_traversal(graph, start):
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    
    while pq:
        current_dist, current_node = heapq.heappop(pq)

        if current_dist > distances[current_node]:
            continue
        
        # Simulate Work
        time.sleep(0.0005)

        for neighbor, weight in graph.get(current_node, {}).items():
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    
    return distances