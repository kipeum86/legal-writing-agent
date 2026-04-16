"""Sanitize fetched, ingested, or loaded content for prompt-injection patterns.

Stdlib only. Wraps matches with <escape>…</escape>. Writes an audit JSON
sidecar describing every match (pattern name, category, line range, snippet).

CLI entry point (see tools/security/cli.py — added in Task 6):
    python -m tools.security.sanitizer <input_file> --out <output_file> --audit <audit.json>
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from tools.security.patterns import ALL_PATTERNS, InjectionPattern


ESCAPE_OPEN = "<escape>"
ESCAPE_CLOSE = "</escape>"
UNTRUSTED_OPEN = '<untrusted_content source="{source}" path="{path}">'
UNTRUSTED_CLOSE = "</untrusted_content>"


@dataclass(frozen=True)
class Match:
    pattern_name: str
    category: str
    language: str
    description: str
    start: int
    end: int
    line: int
    snippet: str


@dataclass(frozen=True)
class SanitizationResult:
    sanitized_text: str
    wrapped_text: str
    matches: tuple[Match, ...]
    input_sha256: str

    @property
    def match_count(self) -> int:
        return len(self.matches)

    @property
    def is_clean(self) -> bool:
        return self.match_count == 0


def _line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _snippet(text: str, start: int, end: int, radius: int = 40) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    return text[left:right].replace("\n", "\\n")


def _collect_matches(text: str, patterns: Iterable[InjectionPattern]) -> list[Match]:
    """Find all non-overlapping matches across patterns, sorted by start offset."""
    found: list[Match] = []
    for pat in patterns:
        for match in pat.regex.finditer(text):
            found.append(
                Match(
                    pattern_name=pat.name,
                    category=pat.category,
                    language=pat.language,
                    description=pat.description,
                    start=match.start(),
                    end=match.end(),
                    line=_line_of(text, match.start()),
                    snippet=_snippet(text, match.start(), match.end()),
                )
            )
    found.sort(key=lambda item: (item.start, -item.end))

    deduped: list[Match] = []
    cursor = -1
    for item in found:
        if item.start >= cursor:
            deduped.append(item)
            cursor = item.end
    return deduped


def _wrap_matches(text: str, matches: list[Match]) -> str:
    """Insert <escape> tags around each match region without mutating content."""
    if not matches:
        return text

    chunks: list[str] = []
    cursor = 0
    for match in matches:
        chunks.append(text[cursor:match.start])
        chunks.append(ESCAPE_OPEN)
        chunks.append(text[match.start:match.end])
        chunks.append(ESCAPE_CLOSE)
        cursor = match.end
    chunks.append(text[cursor:])
    return "".join(chunks)


def sanitize(text: str, *, patterns: Iterable[InjectionPattern] = ALL_PATTERNS) -> SanitizationResult:
    matches = _collect_matches(text, patterns)
    wrapped = _wrap_matches(text, matches)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return SanitizationResult(
        sanitized_text=text,
        wrapped_text=wrapped,
        matches=tuple(matches),
        input_sha256=digest,
    )


def wrap_untrusted(sanitized_body: str, *, source: str, path: str) -> str:
    """Wrap an already-sanitized body in the outer untrusted_content tag."""
    open_tag = UNTRUSTED_OPEN.format(
        source=_escape_attr(source),
        path=_escape_attr(path),
    )
    return f"{open_tag}\n{sanitized_body}\n{UNTRUSTED_CLOSE}\n"


def _escape_attr(value: str) -> str:
    return value.replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def write_audit(result: SanitizationResult, *, source_path: str, audit_path: Path) -> None:
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_path": source_path,
        "input_sha256": result.input_sha256,
        "match_count": result.match_count,
        "is_clean": result.is_clean,
        "matches": [asdict(match) for match in result.matches],
    }
    audit_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
