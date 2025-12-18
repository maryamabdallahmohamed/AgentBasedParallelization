from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple


@dataclass
class TraversalCandidate:
    file_path: Path
    function_name: str
    traversal_type: str  # bfs | dfs | astar
    lineno: int


@dataclass
class DiscoveryResult:
    candidates: List[TraversalCandidate] = field(default_factory=list)


@dataclass
class AnalysisArtifact:
    candidate: TraversalCandidate
    shared_state_variables: List[str]
    mutable_globals: List[str]
    safe_to_parallelize: bool
    notes: str = ""


@dataclass
class AnalysisResult:
    artifacts: List[AnalysisArtifact] = field(default_factory=list)


@dataclass
class StrategyDecision:
    candidate: TraversalCandidate
    strategy: str  # threads | processes | sequential
    rationale: str


@dataclass
class StrategyResult:
    decisions: List[StrategyDecision] = field(default_factory=list)


@dataclass
class TransformationResult:
    candidate: TraversalCandidate
    output_file: Path
    parallel_function_name: str
    success: bool
    message: str = ""


@dataclass
class ExecutionMetrics:
    candidate: TraversalCandidate
    sequential_time_s: float
    parallel_time_s: float
    speedup: float
    correct: bool
    details: Dict[str, float] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    metrics: List[ExecutionMetrics] = field(default_factory=list)


@dataclass
class PipelineContext:
    target_dir: Path
    output_dir: Path
    discovery: Optional[DiscoveryResult] = None
    analysis: Optional[AnalysisResult] = None
    strategy: Optional[StrategyResult] = None
    transformations: List[TransformationResult] = field(default_factory=list)
    execution: Optional[ExecutionResult] = None


@dataclass
class OrchestratorConfig:
    target_dir: Path
    output_dir: Path
    max_workers: int = 4
    use_processes: bool = False
    timeout_s: Optional[float] = None
