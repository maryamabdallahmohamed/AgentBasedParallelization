from __future__ import annotations

import argparse
from pathlib import Path

from agents.coordinator_agent import CoordinatorAgent
from core.models import OrchestratorConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automatic traversal parallelization")
    parser.add_argument("--target", type=Path, default=Path("examples"), help="Directory to scan for traversals")
    parser.add_argument("--output", type=Path, default=Path("outputs"), help="Directory to write transformed files")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum workers for parallel execution")
    parser.add_argument("--processes", action="store_true", help="Use processes instead of threads for execution")
    parser.add_argument("--timeout", type=float, default=None, help="Optional timeout per run")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = OrchestratorConfig(
        target_dir=args.target,
        output_dir=args.output,
        max_workers=args.max_workers,
        use_processes=args.processes,
        timeout_s=args.timeout,
    )
    coordinator = CoordinatorAgent(config)
    context = coordinator.run()

    print("=== Discovery ===")
    for c in context.discovery.candidates if context.discovery else []:
        print(f"- {c.traversal_type.upper()} in {c.file_path}::{c.function_name} @ line {c.lineno}")

    print("\n=== Analysis ===")
    for a in context.analysis.artifacts if context.analysis else []:
        print(f"- {a.candidate.function_name}: safe={a.safe_to_parallelize} shared={a.shared_state_variables} globals={a.mutable_globals}")

    print("\n=== Strategy ===")
    for s in context.strategy.decisions if context.strategy else []:
        print(f"- {s.candidate.function_name}: {s.strategy} ({s.rationale})")

    print("\n=== Transformation ===")
    for t in context.transformations:
        print(f"- {t.candidate.function_name} -> {t.output_file} ({t.message})")

    print("\n=== Execution ===")
    for m in context.execution.metrics if context.execution else []:
        print(
            f"- {m.candidate.function_name}: seq={m.sequential_time_s:.6f}s "
            f"par={m.parallel_time_s:.6f}s speedup={m.speedup:.2f} correct={m.correct}"
        )


if __name__ == "__main__":
    main()
