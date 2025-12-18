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
        except Exception as exc:  # pragma: no cover - defensive
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
        if traversal == "bfs":
            return dedent(
                f"""
                def {parallel_func_name}(graph, start):
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
                """
            )
        if traversal == "dfs":
            return dedent(
                f"""
                def {parallel_func_name}(graph, start):
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
                """
            )
        if traversal == "astar":
            return dedent(
                f"""
                def {parallel_func_name}(graph, start, goal, heuristic):
                    '''Conservative A*: delegates to sequential implementation for correctness.'''
                    return {decision.candidate.function_name}(graph, start, goal, heuristic)
                """
            )
        return dedent(
            f"""
            def {parallel_func_name}(*args, **kwargs):
                return {decision.candidate.function_name}(*args, **kwargs)
            """
        )
