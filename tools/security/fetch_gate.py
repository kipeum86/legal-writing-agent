"""Sanitize content fetched from web / MCP / RAG before agents reason about it."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from tools.security.sanitizer import sanitize, wrap_untrusted, write_audit


@dataclass(frozen=True)
class FetchSanitizationResult:
    wrapped: str
    match_count: int
    is_clean: bool
    audit_path: Optional[Path]


def sanitize_fetched(
    text: str,
    *,
    source: str,
    url: str,
    audit_dir: Optional[Path] = None,
) -> FetchSanitizationResult:
    result = sanitize(text)
    wrapped = wrap_untrusted(result.wrapped_text, source=source, path=url)

    audit_path: Optional[Path] = None
    if audit_dir is not None:
        from hashlib import sha1

        digest = sha1(url.encode("utf-8")).hexdigest()[:12]
        audit_path = audit_dir / f"fetch-{digest}.audit.json"
        write_audit(result, source_path=url, audit_path=audit_path)

    return FetchSanitizationResult(
        wrapped=wrapped,
        match_count=result.match_count,
        is_clean=result.is_clean,
        audit_path=audit_path,
    )
