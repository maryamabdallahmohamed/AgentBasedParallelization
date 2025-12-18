from __future__ import annotations

from typing import List

from core.models import ExecutionResult, TransformationResult
from tools.execution_sandbox import ExecutionSandbox
from tools.correctness_validator import CorrectnessValidator
from tools.profiler_tool import ProfilerTool


class ExecutionValidationAgent:
    """Runs sequential and parallel versions, validates correctness, and collects metrics."""

    def __init__(self, use_processes: bool, max_workers: int, timeout_s: float | None) -> None:
        self.sandbox = ExecutionSandbox(use_processes=use_processes, max_workers=max_workers, timeout_s=timeout_s)
        self.validator = CorrectnessValidator()
        self.profiler = ProfilerTool()

    def run_all(self, transformations: List[TransformationResult]) -> ExecutionResult:
        metrics = []
        for t in transformations:
            seq_output, seq_time = self.sandbox.run_function(
                t.output_file, t.candidate.function_name
            )
            par_output, par_time = self.sandbox.run_function(
                t.output_file, t.parallel_function_name
            )
            correct = self.validator.compare_outputs(seq_output, par_output)
            speedup = self.profiler.compute_speedup(seq_time, par_time)
            metrics.append(self.profiler.build_metrics(t, seq_time, par_time, speedup, correct))
        return ExecutionResult(metrics=metrics)
