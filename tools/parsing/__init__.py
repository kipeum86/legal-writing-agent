"""Structured document parsers."""
from __future__ import annotations

from tools.parsing.docx_parser import (
    DocxParseResult,
    build_clause_map,
    build_outline,
    parse_docx,
)

__all__ = [
    "DocxParseResult",
    "build_clause_map",
    "build_outline",
    "parse_docx",
]
