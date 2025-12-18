from __future__ import annotations

from typing import Any


class CorrectnessValidator:
    """Compares outputs from sequential and parallel executions."""

    def compare_outputs(self, sequential_out: Any, parallel_out: Any) -> bool:
        return sequential_out == parallel_out
