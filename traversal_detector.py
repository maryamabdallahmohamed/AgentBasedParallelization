from __future__ import annotations

import ast
from typing import Optional


class TraversalDetector:
    """Classifies traversal algorithms using structural heuristics."""

    def classify_function(self, func: ast.FunctionDef) -> Optional[str]:
        # FIX: Ignore helper functions like 'generate_graph'
        if "generate" in func.name:
            return None

        # Walk the tree once to gather features
        nodes = list(ast.walk(func))
        
        uses_queue = any(self._is_queue_call(n) for n in nodes)
        uses_stack = any(self._is_stack_pattern(n) for n in nodes)
        uses_pq = any(self._is_priority_queue(n) for n in nodes)
        is_nested = self._is_nested_loop(func)

        # Distinguish A* from Dijkstra: A* usually has a 'heuristic' argument or variable
        has_heuristic = any(
            (isinstance(n, ast.arg) and "heuristic" in n.arg) or
            (isinstance(n, ast.Name) and "heuristic" in n.id)
            for n in nodes
        )

        if uses_pq:
            return "astar" if has_heuristic else "dijkstra"
        if uses_queue:
            return "bfs"
        if is_nested and self._has_relaxation_pattern(nodes):
             return "bellman_ford"
        if uses_stack or self._is_recursive(func):
            return "dfs"
        return None

    def is_safe(self, traversal_type: str, shared_state: list[str], mutable_globals: list[str]) -> bool:
        # Ignore uppercase globals (constants like GRAPH)
        dangerous_globals = [g for g in mutable_globals if not g.isupper()]
        
        if shared_state or dangerous_globals:
            return False
        return traversal_type in {"bfs", "dfs", "astar", "dijkstra", "bellman_ford"}

    def _is_queue_call(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Attribute) and node.attr == "popleft":
            return True
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "deque":
            return True
        return False

    def _is_stack_pattern(self, node: ast.AST) -> bool:
        return isinstance(node, ast.Attribute) and node.attr in {"append", "pop"}

    def _is_priority_queue(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"heappush", "heappop"}:
            return True
        if isinstance(node, ast.Attribute) and node.attr in {"heappush", "heappop"}:
            return True
        return False

    def _is_recursive(self, func: ast.FunctionDef) -> bool:
        for node in ast.walk(func):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == func.name:
                return True
        return False

    def _is_nested_loop(self, func: ast.FunctionDef) -> bool:
        for node in ast.walk(func):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if child is not node and isinstance(child, (ast.For, ast.While)):
                        return True
        return False

    def _has_relaxation_pattern(self, nodes: list[ast.AST]) -> bool:
        for node in nodes:
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                if "dist" in node.id or "distance" in node.id:
                    return True
        return False