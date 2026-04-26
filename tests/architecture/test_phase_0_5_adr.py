from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "architecture" / "adr" / "0003-phase-0-5-runtime-measurements.md"


def test_phase_0_5_adr_records_required_decisions() -> None:
    text = ADR.read_text(encoding="utf-8")

    assert "Status: Accepted" in text
    assert "deterministic single-pipeline router" in text
    assert "character-count thresholds" in text
    assert "Level B only" in text
    assert "explicit context plans" in text


def test_phase_0_5_adr_records_runtime_measurements() -> None:
    text = ADR.read_text(encoding="utf-8")

    assert "15,128" in text
    assert "22,781" in text
    assert "18,141" in text
    assert "`tiktoken` | No" in text
    assert "`tokenizers` | No" in text
    assert "python-docx` | Available, version 1.2.0" in text
    assert "ko-korea-opinion" in text
