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
                strategy = self.kb.get_default_strategy(artifact.candidate.traversal_type)
                rationale = f"default for {artifact.candidate.traversal_type}"
            decisions.append(
                StrategyDecision(
                    candidate=artifact.candidate,
                    strategy=strategy,
                    rationale=rationale,
                )
            )
        return StrategyResult(decisions=decisions)
