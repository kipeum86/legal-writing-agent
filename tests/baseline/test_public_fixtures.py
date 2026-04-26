from __future__ import annotations

import json
import re
from pathlib import Path

from tools.artifacts.schemas import ARTIFACT_TYPES, ENUMS


ROOT = Path(__file__).resolve().parents[2]
PUBLIC_FIXTURES = ROOT / "tests" / "fixtures" / "public"
BASELINE_RUNNER = ROOT / "scripts" / "run-baseline-tests.sh"

EXPECTED_FIXTURE_COUNT = 10
REQUIRED_ARTIFACT_TYPES = {
    "manifest",
    "outline",
    "clause_map",
    "term_registry",
    "placeholder_registry",
    "validation_report",
}
SENSITIVE_PATTERNS = (
    re.compile(r"\b\d{6}-\d{7}\b"),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
)


def _fixture_dirs() -> list[Path]:
    return sorted(path for path in PUBLIC_FIXTURES.iterdir() if path.is_dir())


def _metadata(path: Path) -> dict[str, object]:
    return json.loads((path / "metadata.json").read_text(encoding="utf-8"))


def test_public_fixture_set_has_ten_representative_inputs() -> None:
    fixtures = _fixture_dirs()

    assert len(fixtures) == EXPECTED_FIXTURE_COUNT
    assert {path.name for path in fixtures} == {
        "en_general_compliance_note",
        "en_regulatory_skeleton",
        "en_uk_advisory_authority",
        "en_us_advisory_authority",
        "ko_advisory_no_authority",
        "ko_board_resolution_simple",
        "ko_internal_policy_conditional",
        "ko_litigation_skeleton",
        "ko_minutes_simple",
        "table_heavy_document",
    }


def test_public_fixtures_are_synthetic_and_schema_described() -> None:
    for fixture in _fixture_dirs():
        metadata = _metadata(fixture)
        input_path = fixture / "input.md"
        assert input_path.exists(), fixture
        input_text = input_path.read_text(encoding="utf-8")

        assert metadata["id"] == fixture.name
        assert metadata["synthetic"] is True
        assert metadata["containsSensitiveData"] is False
        assert isinstance(metadata["authorityPacketProvided"], bool)
        assert metadata["language"] in ENUMS["targetLanguage"]
        assert metadata["documentType"] in ENUMS["documentType"]
        assert metadata["supportLevel"] in ENUMS["supportLevel"]
        assert metadata["expectedValidationStatus"] in {"passed", "failed"}
        assert set(metadata["expectedArtifactTypes"]) == REQUIRED_ARTIFACT_TYPES
        assert set(metadata["expectedArtifactTypes"]).issubset(ARTIFACT_TYPES)
        assert len(input_text.strip()) > 80
        assert not any(pattern.search(input_text) for pattern in SENSITIVE_PATTERNS)


def test_baseline_runner_executes_security_rendering_validation_and_fixture_checks() -> None:
    content = BASELINE_RUNNER.read_text(encoding="utf-8")

    assert "tests/security" in content
    assert "tests/baseline" in content
    assert "tests/rendering" in content
    assert "tests/validation" in content
