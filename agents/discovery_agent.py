from __future__ import annotations

from pathlib import Path

from core.models import DiscoveryResult
from tools.codebase_scanner import CodebaseScanner


class CodeDiscoveryAgent:
    """Scans a directory to find candidate traversal functions."""

    def __init__(self) -> None:
        self.scanner = CodebaseScanner()

    def discover(self, target_dir: Path) -> DiscoveryResult:
        return self.scanner.scan_for_traversals(target_dir)
