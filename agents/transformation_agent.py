from __future__ import annotations

from pathlib import Path
from typing import List

from core.models import StrategyResult, TransformationResult
from tools.code_rewriter import CodeRewriter


class CodeTransformationAgent:
    """Rewrites traversal functions into parallelized variants."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.rewriter = CodeRewriter(output_dir=output_dir)

    def rewrite_all(self, strategy: StrategyResult) -> List[TransformationResult]:
        results: List[TransformationResult] = []
        for decision in strategy.decisions:
            result = self.rewriter.rewrite(decision)
            results.append(result)
        return results
