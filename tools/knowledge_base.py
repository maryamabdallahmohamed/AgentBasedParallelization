from __future__ import annotations

from typing import Dict


class ParallelizationKnowledgeBase:
    """Encodes heuristic strategies per traversal type."""

    def __init__(self) -> None:
        self.rules: Dict[str, str] = {
            "bfs": "threads",
            "dfs": "threads",
            "astar": "processes",
        }

    def get_default_strategy(self, traversal_type: str) -> str:
        return self.rules.get(traversal_type, "sequential")
