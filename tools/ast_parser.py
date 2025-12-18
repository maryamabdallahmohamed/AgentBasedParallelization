from __future__ import annotations

import ast
from pathlib import Path


class ASTParser:
    """Thin wrapper around ast.parse to allow swapping implementations."""

    def parse_file(self, path: Path) -> ast.AST:
        source = path.read_text(encoding="utf-8")
        return ast.parse(source, filename=str(path))
