from __future__ import annotations

from core.models import ExecutionMetrics, TransformationResult


class ProfilerTool:
    """Computes simple speedup metrics."""

    def compute_speedup(self, seq_time: float, par_time: float) -> float:
        if par_time <= 0:
            return float("inf")
        return seq_time / par_time

    def build_metrics(
        self,
        transformation: TransformationResult,
        seq_time: float,
        par_time: float,
        speedup: float,
        correct: bool,
    ) -> ExecutionMetrics:
        return ExecutionMetrics(
            candidate=transformation.candidate,
            sequential_time_s=seq_time,
            parallel_time_s=par_time,
            speedup=speedup,
            correct=correct,
            details={},
        )
