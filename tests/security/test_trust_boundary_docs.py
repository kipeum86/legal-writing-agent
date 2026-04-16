"""Assert every agent-facing doc carries the trust-boundary guardrail."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

AGENT_DOCS = [
    REPO / "CLAUDE.md",
    REPO / ".claude/skills/ingest/SKILL.md",
    REPO / ".claude/skills/request-interpreter/SKILL.md",
    REPO / ".claude/skills/document-reviser/SKILL.md",
    REPO / ".claude/skills/convention-selector/SKILL.md",
]

REQUIRED_MARKERS = (
    "<untrusted_content",
    "DATA, not INSTRUCTIONS",
    "docs/security/trust-boundaries.md",
)


@pytest.mark.parametrize("path", AGENT_DOCS, ids=lambda p: p.name)
def test_agent_doc_has_trust_boundary(path: Path) -> None:
    assert path.exists(), f"expected doc missing: {path}"
    text = path.read_text(encoding="utf-8")
    for marker in REQUIRED_MARKERS:
        assert marker in text, f"{path.relative_to(REPO)} missing marker: {marker!r}"


def test_canonical_reference_exists() -> None:
    canonical = REPO / "docs/security/trust-boundaries.md"
    assert canonical.exists()
    text = canonical.read_text(encoding="utf-8")
    assert "<untrusted_content" in text
    assert "<escape>" in text
