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


def parallel_bellman_ford_traversal(graph, start):
    '''Parallel Bellman-Ford: Parallelizes edge relaxation.'''
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
    vertices = list(graph.keys())

    # Flatten edges for parallel processing: (u, v, weight)
    all_edges = []
    for u in graph:
        for v, w in graph[u].items():
            all_edges.append((u, v, w))

    num_workers = 4
    chunk_size = max(1, len(all_edges) // num_workers)
    chunks = [all_edges[i:i + chunk_size] for i in range(0, len(all_edges), chunk_size)]

    def relax_chunk(edge_chunk):
        local_change = False
        for u, v, w in edge_chunk:
            if distances[u] + w < distances[v]:
                distances[v] = distances[u] + w
                local_change = True
                log_event(v, "relaxed")
        return local_change

    with ThreadPoolExecutor(max_workers=num_workers) as ex:
        for i in range(len(vertices) - 1):
            # Safe F-string nesting: escape inner braces
            log_event(f"iter_{i}", "iteration_start")

            # Run relaxation in parallel chunks
            results = list(ex.map(relax_chunk, chunks))
            if not any(results):
                break


    # Dump trace for visualization
    with open('trace_parallel_bellman_ford_traversal.json', 'w') as f:
        json.dump(trace_log, f, indent=2)

    return distances

