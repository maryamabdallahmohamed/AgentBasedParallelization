# Sample graph for DFS
GRAPH = {
    1: [2, 3],
    2: [4],
    3: [5, 6],
    4: [],
    5: [],
    6: [],
}

START_NODE = 1


def dfs_traversal(graph, start):
    visited = set()
    order = []

    def dfs(node):
        visited.add(node)
        order.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)

    dfs(start)
    return order


traverse = dfs_traversal



def parallel_dfs_traversal(graph, start):
    '''Parallel-ish DFS: expands neighbors in a thread pool while preserving stack order.'''
    from concurrent.futures import ThreadPoolExecutor

    visited = set()
    order = []
    stack = [start]
    with ThreadPoolExecutor() as ex:
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            order.append(node)

            def expand(n):
                return [nbr for nbr in graph.get(n, []) if nbr not in visited]

            neighbors = list(ex.map(expand, [node]))[0]
            for nbr in reversed(neighbors):
                stack.append(nbr)
    return order

