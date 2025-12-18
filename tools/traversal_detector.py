from __future__ import annotations

import ast
from typing import Optional


class TraversalDetector:
    """Classifies traversal algorithms using simple structural heuristics."""

    def classify_function(self, func: ast.FunctionDef) -> Optional[str]:
        uses_queue = any(self._is_queue_call(n) for n in ast.walk(func))
        uses_stack = any(self._is_stack_pattern(n) for n in ast.walk(func))
        uses_pq = any(self._is_priority_queue(n) for n in ast.walk(func))
        if uses_pq:
            return "astar"
        if uses_queue:
            return "bfs"
        if uses_stack or self._is_recursive(func):
            return "dfs"
        return None

    def is_safe(self, traversal_type: str, shared_state: list[str], mutable_globals: list[str]) -> bool:
        if shared_state or mutable_globals:
            return False
        return traversal_type in {"bfs", "dfs", "astar"}

    def _is_queue_call(self, node: ast.AST) -> bool:
        # Heuristic for BFS: look for deque() creation or popleft usage
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
