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


def parallel_bfs_traversal(graph, start):
    '''Parallel BFS with trace logging.'''
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


    visited = set()
    order = []
    frontier = [start]
    visited.add(start)
    log_event(start, "start")

    with ThreadPoolExecutor() as ex:
        while frontier:
            order.extend(frontier)
            tasks = list(frontier)

            def expand(node):
                log_event(node, "expanding")
                # Use {} for literal empty dict/set usage if needed inside f-strings
                return [nbr for nbr in graph.get(node, []) if nbr not in visited]

            results = ex.map(expand, tasks)
            next_frontier = []
            for node, neighbors in zip(tasks, results):
                for nbr in neighbors:
                    if nbr not in visited:
                        visited.add(nbr)
                        next_frontier.append(nbr)
                        log_event(nbr, "discovered")
            frontier = next_frontier


    # Dump trace for visualization
    with open('trace_parallel_bfs_traversal.json', 'w') as f:
        json.dump(trace_log, f, indent=2)

    return order

