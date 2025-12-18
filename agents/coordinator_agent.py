from __future__ import annotations

from pathlib import Path
from typing import List

from core.models import (
    AnalysisResult,
    DiscoveryResult,
    ExecutionResult,
    OrchestratorConfig,
    PipelineContext,
    StrategyResult,
    TransformationResult,
)
from agents.discovery_agent import CodeDiscoveryAgent
from agents.analysis_agent import ProgramAnalysisAgent
from agents.strategy_agent import ParallelizationStrategyAgent
from agents.transformation_agent import CodeTransformationAgent
from agents.execution_agent import ExecutionValidationAgent


class CoordinatorAgent:
    """Orchestrates the end-to-end pipeline across all agents."""

    def __init__(self, config: OrchestratorConfig) -> None:
        self.config = config
        self.context = PipelineContext(
            target_dir=config.target_dir,
            output_dir=config.output_dir,
        )
        self.discovery_agent = CodeDiscoveryAgent()
        self.analysis_agent = ProgramAnalysisAgent()
        self.strategy_agent = ParallelizationStrategyAgent()
        self.transformation_agent = CodeTransformationAgent(output_dir=config.output_dir)
        self.execution_agent = ExecutionValidationAgent(
            use_processes=config.use_processes,
            max_workers=config.max_workers,
            timeout_s=config.timeout_s,
        )

    def run(self) -> PipelineContext:
        self.context.discovery = self._discover()
        self.context.analysis = self._analyze()
        self.context.strategy = self._plan()
        self.context.transformations = self._transform()
        self.context.execution = self._execute()
        return self.context

    def _discover(self) -> DiscoveryResult:
        return self.discovery_agent.discover(self.context.target_dir)

    def _analyze(self) -> AnalysisResult:
        if not self.context.discovery:
            return AnalysisResult()
        return self.analysis_agent.analyze(self.context.discovery)

    def _plan(self) -> StrategyResult:
        if not self.context.analysis:
            return StrategyResult()
        return self.strategy_agent.select_strategies(self.context.analysis)

    def _transform(self) -> List[TransformationResult]:
        if not self.context.strategy:
            return []
        return self.transformation_agent.rewrite_all(self.context.strategy)

    def _execute(self) -> ExecutionResult:
        if not self.context.transformations:
            return ExecutionResult()
        return self.execution_agent.run_all(self.context.transformations)
