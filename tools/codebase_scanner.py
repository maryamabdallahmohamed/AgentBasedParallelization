from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable, List

from core.models import DiscoveryResult, TraversalCandidate
from tools.traversal_detector import TraversalDetector


class CodebaseScanner:
    """Walks a directory and collects traversal function candidates."""

    def __init__(self) -> None:
        self.detector = TraversalDetector()

    def scan_for_traversals(self, target_dir: Path) -> DiscoveryResult:
        candidates: List[TraversalCandidate] = []
        for file_path in self._iter_py_files(target_dir):
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            for node in getattr(tree, "body", []):  # only top-level functions
                if isinstance(node, ast.FunctionDef):
                    traversal_type = self.detector.classify_function(node)
                    if traversal_type:
                        candidates.append(
                            TraversalCandidate(
                                file_path=file_path,
                                function_name=node.name,
                                traversal_type=traversal_type,
                                lineno=node.lineno,
                            )
                        )
        return DiscoveryResult(candidates=candidates)

    def _iter_py_files(self, base: Path) -> Iterable[Path]:
        for path in base.rglob("*.py"):
            if path.name.startswith("__"):
                continue
            yield path
