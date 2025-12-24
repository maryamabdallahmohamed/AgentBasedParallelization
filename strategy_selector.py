from __future__ import annotations

from core.models import AnalysisResult, StrategyDecision, StrategyResult
from tools.knowledge_base import ParallelizationKnowledgeBase


class StrategySelector:
    """Maps analysis artifacts to concrete parallelization strategies."""

    def __init__(self, kb: ParallelizationKnowledgeBase) -> None:
        self.kb = kb

    def select(self, analysis: AnalysisResult) -> StrategyResult:
        decisions = []
        for artifact in analysis.artifacts:
            if not artifact.safe_to_parallelize:
                strategy = "sequential"
                rationale = "unsafe shared state"
            else:
                # Basic mapping logic
                t_type = artifact.candidate.traversal_type
                if t_type in ["bfs", "dfs", "dijkstra", "bellman_ford"]:
                    strategy = "threaded" # Standard threads for IO/simple graph tasks
                    rationale = f"threading for {t_type}"
                elif t_type == "astar":
                    strategy = "sequential" # A* hard to parallelize safely auto-magically
                    rationale = "A* complexity requires manual tuning"
                else:
                    strategy = "sequential"
                    rationale = "unknown type"

            decisions.append(
                StrategyDecision(
                    candidate=artifact.candidate,
                    strategy=strategy,
                    rationale=rationale,
                )
            )
        return StrategyResult(decisions=decisions)