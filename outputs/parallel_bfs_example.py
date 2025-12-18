from collections import deque

# Sample graph for BFS
GRAPH = {
    "A": ["B", "C"],
    "B": ["D", "E"],
    "C": ["F"],
    "D": [],
    "E": ["F"],
    "F": [],
}

START_NODE = "A"


def bfs_traversal(graph, start):
    visited = set([start])
    order = []
    queue = deque([start])
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order


# Alias expected by detector (optional)
traverse = bfs_traversal



def parallel_bfs_traversal(graph, start):
    '''Parallel BFS using thread workers for neighbor expansion.'''
    from concurrent.futures import ThreadPoolExecutor

    visited = set()
    order = []
    frontier = [start]
    visited.add(start)
    with ThreadPoolExecutor() as ex:
        while frontier:
            order.extend(frontier)
            tasks = list(frontier)

            def expand(node):
                return [nbr for nbr in graph.get(node, []) if nbr not in visited]

            results = ex.map(expand, tasks)
            next_frontier = []
            for node, neighbors in zip(tasks, results):
                for nbr in neighbors:
                    if nbr not in visited:
                        visited.add(nbr)
                        next_frontier.append(nbr)
            frontier = next_frontier
    return order

