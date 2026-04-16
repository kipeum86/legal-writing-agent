from __future__ import annotations

import os
from pathlib import Path

import pytest

from tools.security import paths


def test_defaults_to_repo_root(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LEGAL_AGENT_PRIVATE_DIR", raising=False)
    base = paths._base()
    assert (base / "CLAUDE.md").exists(), f"fallback did not resolve to repo root: {base}"


def test_env_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("LEGAL_AGENT_PRIVATE_DIR", str(tmp_path))
    assert paths._base() == tmp_path
    assert paths.input_dir() == tmp_path / "input"
    assert paths.output_dir() == tmp_path / "output"
    assert paths.manifest_dir() == tmp_path / "output" / "manifests"


def test_expanduser(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LEGAL_AGENT_PRIVATE_DIR", "~/legal-agent-test")
    expected = Path(os.path.expanduser("~/legal-agent-test"))
    assert paths._base() == expected
