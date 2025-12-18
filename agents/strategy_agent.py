from __future__ import annotations

from core.models import AnalysisResult, StrategyResult
from tools.knowledge_base import ParallelizationKnowledgeBase
from tools.strategy_selector import StrategySelector


class ParallelizationStrategyAgent:
    """Chooses a parallelization approach per traversal candidate."""

    def __init__(self) -> None:
        self.kb = ParallelizationKnowledgeBase()
        self.selector = StrategySelector(self.kb)

    def select_strategies(self, analysis: AnalysisResult) -> StrategyResult:
        return self.selector.select(analysis)
