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


def parallel_dijkstra_traversal(graph, start):
    '''Parallel Dijkstra: Parallelizes neighbor cost calculation.'''
    import heapq
    from concurrent.futures import ThreadPoolExecutor

    import time, threading, json
    trace_log = []
    def log_event(node, action):
        trace_log.append({
            "time": time.time(),
            "thread": threading.get_ident(),
            "node": str(node),
            "action": action
        })


    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    pq = [(0, start)]

    # Thread lock for shared distances dict
    lock = threading.Lock()

    with ThreadPoolExecutor() as ex:
        while pq:
            current_dist, current_node = heapq.heappop(pq)

            if current_dist > distances[current_node]:
                continue

            log_event(current_node, "visit")

            # FIX IS HERE: {} becomes {} in output
            neighbors = graph.get(current_node, {}).items()

            def process_neighbor(item):
                neighbor, weight = item
                distance = current_dist + weight
                updated = False
                with lock:
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        heapq.heappush(pq, (distance, neighbor))
                        updated = True
                if updated:
                    log_event(neighbor, "update_dist")

            # Map neighbor processing to threads
            list(ex.map(process_neighbor, neighbors))


    # Dump trace for visualization
    with open('trace_parallel_dijkstra_traversal.json', 'w') as f:
        json.dump(trace_log, f, indent=2)

    return distances

