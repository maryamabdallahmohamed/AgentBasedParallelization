from __future__ import annotations

from core.models import AnalysisResult, DiscoveryResult
from tools.ast_parser import ASTParser
from tools.dependency_analyzer import DependencyAnalyzer
from tools.traversal_detector import TraversalDetector


class ProgramAnalysisAgent:
    """Parses code, builds lightweight dependency info, and checks traversal safety."""

    def __init__(self) -> None:
        self.parser = ASTParser()
        self.dependency_analyzer = DependencyAnalyzer()
        self.traversal_detector = TraversalDetector()

    def analyze(self, discovery: DiscoveryResult) -> AnalysisResult:
        artifacts = []
        for candidate in discovery.candidates:
            tree = self.parser.parse_file(candidate.file_path)
            globals_mutable = self.dependency_analyzer.find_mutable_globals(tree)
            shared_vars = self.dependency_analyzer.find_shared_state(tree, candidate.function_name)
            safe = self.traversal_detector.is_safe(candidate.traversal_type, shared_vars, globals_mutable)
            artifacts.append(
                self.dependency_analyzer.build_artifact(
                    candidate=candidate,
                    shared_state=shared_vars,
                    mutable_globals=globals_mutable,
                    safe=safe,
                )
            )
        return AnalysisResult(artifacts=artifacts)
