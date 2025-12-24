from __future__ import annotations
import time
import tracemalloc
from core.models import ExecutionMetrics, TransformationResult


class ProfilerTool:
    """Computes speedup, memory overhead, and CPU utilization metrics."""

    def compute_speedup(self, seq_time: float, par_time: float) -> float:
        if par_time <= 0:
            return float("inf")
        return seq_time / par_time

    def measure_execution(self, func, *args, **kwargs):
        """Runs a function and returns (result, wall_time, cpu_time, peak_memory_mb)."""
        tracemalloc.start()
        start_wall = time.time()
        start_cpu = time.process_time()
        
        try:
            result = func(*args, **kwargs)
        finally:
            end_wall = time.time()
            end_cpu = time.process_time()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

        wall_time = end_wall - start_wall
        cpu_time = end_cpu - start_cpu
        peak_mb = peak / (1024 * 1024)
        
        return result, wall_time, cpu_time, peak_mb

    def build_metrics(
        self,
        transformation: TransformationResult,
        seq_metrics: tuple, # (wall, cpu, mem)
        par_metrics: tuple, # (wall, cpu, mem)
        correct: bool,
    ) -> ExecutionMetrics:
        
        seq_wall, seq_cpu, seq_mem = seq_metrics
        par_wall, par_cpu, par_mem = par_metrics
        
        speedup = self.compute_speedup(seq_wall, par_wall)
        
        # CPU Util = CPU Time / Wall Time * 100 (Can be >100% for multi-core)
        cpu_util = (par_cpu / par_wall * 100) if par_wall > 0 else 0.0

        return ExecutionMetrics(
            candidate=transformation.candidate,
            sequential_time_s=seq_wall,
            parallel_time_s=par_wall,
            speedup=speedup,
            correct=correct,
            details={
                "seq_memory_mb": round(seq_mem, 2),
                "par_memory_mb": round(par_mem, 2),
                "cpu_utilization_pct": round(cpu_util, 2),
                "mem_overhead_pct": round(((par_mem - seq_mem) / seq_mem * 100), 2) if seq_mem > 0 else 0
            },
        )