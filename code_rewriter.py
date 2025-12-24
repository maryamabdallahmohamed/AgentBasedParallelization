from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from core.models import StrategyDecision, TransformationResult


class CodeRewriter:
    """Creates parallel variants of traversal functions and writes them to the output directory."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def rewrite(self, decision: StrategyDecision) -> TransformationResult:
        src_path = decision.candidate.file_path
        try:
            source = src_path.read_text(encoding="utf-8")
            parallel_func_name = f"parallel_{decision.candidate.function_name}"
            template = self._render_template(decision, parallel_func_name)
            new_source = f"{source}\n\n{template}\n"
            output_file = self._output_path(src_path)
            output_file.write_text(new_source, encoding="utf-8")
            return TransformationResult(
                candidate=decision.candidate,
                output_file=output_file,
                parallel_function_name=parallel_func_name,
                success=True,
                message=f"Wrote {output_file}",
            )
        except Exception as exc: 
            return TransformationResult(
                candidate=decision.candidate,
                output_file=src_path,
                parallel_function_name=decision.candidate.function_name,
                success=False,
                message=str(exc),
            )

    def _output_path(self, src_path: Path) -> Path:
        return self.output_dir / f"parallel_{src_path.name}"

    def _render_template(self, decision: StrategyDecision, parallel_func_name: str) -> str:
        traversal = decision.candidate.traversal_type
        
        # Helper to generate trace logging code
        # Note: Braces here are fine because this is a standard string, not an f-string
        trace_setup = """
    import time, threading, json
    trace_log = []
    def log_event(node, action):
        trace_log.append({
            "time": time.time(),
            "thread": threading.get_ident(),
            "node": str(node),
            "action": action
        })
        """
        
        trace_dump = f"""
    # Dump trace for visualization
    with open('trace_{parallel_func_name}.json', 'w') as f:
        json.dump(trace_log, f, indent=2)
        """

        if traversal == "bfs":
            return dedent(f"""
def {parallel_func_name}(graph, start):
    '''Parallel BFS with trace logging.'''
    from concurrent.futures import ThreadPoolExecutor
    {trace_setup}

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
                # Use {{}} for literal empty dict/set usage if needed inside f-strings
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
    
    {trace_dump}
    return order
            """)

        if traversal == "dfs":
            return dedent(f"""
def {parallel_func_name}(graph, start):
    '''Parallel-ish DFS with trace logging.'''
    from concurrent.futures import ThreadPoolExecutor
    {trace_setup}

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
            log_event(node, "visit")

            def expand(n):
                return [nbr for nbr in graph.get(n, []) if nbr not in visited]

            # Parallel lookahead for neighbors (just for workload distribution demo)
            neighbors = list(ex.map(expand, [node]))[0]
            for nbr in reversed(neighbors):
                stack.append(nbr)
    
    {trace_dump}
    return order
            """)

        if traversal == "dijkstra":
            # FIX: Double braces {{}} for empty dict literal in graph.get
            return dedent(f"""
def {parallel_func_name}(graph, start):
    '''Parallel Dijkstra: Parallelizes neighbor cost calculation.'''
    import heapq
    from concurrent.futures import ThreadPoolExecutor
    {trace_setup}

    distances = {{node: float('infinity') for node in graph}}
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

            # FIX IS HERE: {{}} becomes {{}} in output
            neighbors = graph.get(current_node, {{}}).items()
            
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
            
    {trace_dump}
    return distances
            """)

        if traversal == "bellman_ford":
            return dedent(f"""
def {parallel_func_name}(graph, start):
    '''Parallel Bellman-Ford: Parallelizes edge relaxation.'''
    from concurrent.futures import ThreadPoolExecutor
    {trace_setup}
    
    distances = {{node: float('infinity') for node in graph}}
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
            log_event(f"iter_{{i}}", "iteration_start")
            
            # Run relaxation in parallel chunks
            results = list(ex.map(relax_chunk, chunks))
            if not any(results):
                break
                
    {trace_dump}
    return distances
            """)

        # Fallback for A* or others
        return dedent(f"""
def {parallel_func_name}(*args, **kwargs):
    '''Delegating wrapper (unsafe to auto-parallelize).'''
    return {decision.candidate.function_name}(*args, **kwargs)
        """)