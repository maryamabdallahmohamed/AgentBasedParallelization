from __future__ import annotations

import importlib.util
import sys
from typing import List, Any

try:
    from core.models import ExecutionResult, ExecutionMetrics, TransformationResult
except ImportError:
    from core.models import ExecutionMetrics, TransformationResult
    class ExecutionResult:
        def __init__(self, metrics): self.metrics = metrics

from tools.profiler_tool import ProfilerTool


class ExecutionValidationAgent:
    """
    Loads transformed code, executes both sequential and parallel versions,
    and captures performance metrics using the ProfilerTool.
    """

    def __init__(self, use_processes: bool = False, max_workers: int = 1, timeout_s: float | None = None) -> None:
        self.profiler = ProfilerTool()

    def run_all(self, transformations: List[TransformationResult]) -> ExecutionResult:
        metrics_list = []
        print(f"\n--- Starting Execution & Validation ({len(transformations)} files) ---")
        
        for t in transformations:
            if not t.success:
                print(f"Skipping {t.candidate.function_name} (Transformation failed)")
                continue

            try:
                module = self._load_module(t.output_file)
                
                if not hasattr(module, "GRAPH") or not hasattr(module, "START_NODE"):
                    print(f"Skipping {t.candidate.function_name}: Missing GRAPH/START_NODE")
                    continue
                
                graph = getattr(module, "GRAPH")
                start = getattr(module, "START_NODE")

                original_func = getattr(module, t.candidate.function_name)
                parallel_func = getattr(module, t.parallel_function_name)

                print(f"Running validation for: {t.candidate.function_name}...", end=" ", flush=True)

                seq_result, seq_wall, seq_cpu, seq_mem = self.profiler.measure_execution(
                    original_func, graph, start
                )

                par_result, par_wall, par_cpu, par_mem = self.profiler.measure_execution(
                    parallel_func, graph, start
                )

                # FIX: Relaxed Correctness Check
                # Parallel DFS returns different order, so we compare SETS of visited nodes.
                if isinstance(seq_result, list) and isinstance(par_result, list):
                    # Convert to string to safely sort mixed types if necessary
                    correct = sorted(map(str, seq_result)) == sorted(map(str, par_result))
                else:
                    correct = (seq_result == par_result)
                
                status_msg = "PASSED" if correct else "FAILED"
                print(f"{status_msg}")

                if not correct:
                    print(f"   -> Output mismatch!")

                seq_metrics = (seq_wall, seq_cpu, seq_mem)
                par_metrics = (par_wall, par_cpu, par_mem)

                metric = self.profiler.build_metrics(
                    transformation=t,
                    seq_metrics=seq_metrics,
                    par_metrics=par_metrics,
                    correct=correct
                )
                metrics_list.append(metric)

            except Exception as e:
                print(f"ERROR executing {t.candidate.function_name}: {e}")

        return ExecutionResult(metrics=metrics_list)

    def _load_module(self, path: Any):
        module_name = path.stem
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec for {path}")
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module