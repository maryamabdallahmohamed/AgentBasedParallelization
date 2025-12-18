from __future__ import annotations

import importlib.util
import time
from pathlib import Path
from types import ModuleType
from typing import Any, Callable


class ExecutionSandbox:
    """Loads transformed modules and executes traversal functions safely."""

    def __init__(self, use_processes: bool, max_workers: int, timeout_s: float | None) -> None:
        self.use_processes = use_processes
        self.max_workers = max_workers
        self.timeout_s = timeout_s

    def run_function(self, file_path: Path, func_name: str) -> tuple[Any, float]:
        module = self._load_module(file_path)
        func: Callable[..., Any] = getattr(module, func_name)
        start = time.perf_counter()
        # Examples expect (graph, start, [goal, heuristic])
        graph = getattr(module, "GRAPH", None)
        start_node = getattr(module, "START_NODE", None)
        goal = getattr(module, "GOAL_NODE", None)
        heuristic = getattr(module, "heuristic", None)
        if goal is not None and heuristic:
            output = func(graph, start_node, goal, heuristic)
        else:
            output = func(graph, start_node)
        elapsed = time.perf_counter() - start
        return output, elapsed

    def _load_module(self, file_path: Path) -> ModuleType:
        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from {file_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
