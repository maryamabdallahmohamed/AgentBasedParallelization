from __future__ import annotations

import ast
from typing import List

from core.models import AnalysisArtifact, TraversalCandidate


class DependencyAnalyzer:
    """Finds mutable globals and shared state heuristically."""

    def find_mutable_globals(self, tree: ast.AST) -> List[str]:
        mutable_globals: List[str] = []
        for node in tree.body if isinstance(tree, ast.Module) else []:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        mutable_globals.append(target.id)
        return mutable_globals

    def find_shared_state(self, tree: ast.AST, function_name: str) -> List[str]:
        shared: List[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                for inner in ast.walk(node):
                    if isinstance(inner, ast.Global):
                        shared.extend(inner.names)
        return list(sorted(set(shared)))

    def build_artifact(
        self,
        candidate: TraversalCandidate,
        shared_state: List[str],
        mutable_globals: List[str],
        safe: bool,
    ) -> AnalysisArtifact:
        return AnalysisArtifact(
            candidate=candidate,
            shared_state_variables=shared_state,
            mutable_globals=mutable_globals,
            safe_to_parallelize=safe,
            notes="unsafe due to shared state" if not safe else "",
        )
