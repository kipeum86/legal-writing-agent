from __future__ import annotations

import json
from pathlib import Path

from tools.artifacts import schemas
from tools.validation.runner import run_validation


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = ROOT / "tests" / "fixtures" / "validation" / "current-validator-snapshots.json"


def _write_manifest(
    tmp_path: Path,
    *,
    document_id: str | None = None,
    jurisdiction: str = "us",
    target_language: str = "en",
    review_intensity: str = "standard",
) -> Path:
    manifest = schemas.MatterManifest(
        documentId=document_id or schemas.new_document_id(),
        documentType="general",
        supportLevel="full",
        targetLanguage=target_language,
        jurisdiction=jurisdiction,
        reviewIntensity=review_intensity,
    )
    path = tmp_path / "output" / "manifests" / f"{manifest.documentId}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(schemas.artifact_to_payload(manifest), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def _write_placeholder_registry(tmp_path: Path, document_id: str, placeholders: list[str]) -> Path:
    registry = schemas.PlaceholderRegistry(
        documentId=document_id,
        placeholders=tuple(
            {"id": f"p{index}", "type": "authority", "text": text, "resolved": False}
            for index, text in enumerate(placeholders, start=1)
        ),
    )
    path = tmp_path / "output" / "placeholders" / f"{document_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(schemas.artifact_to_payload(registry), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def _projection(report: dict[str, object]) -> dict[str, object]:
    findings = report["findings"]
    assert isinstance(findings, list)
    return {
        "status": report["status"],
        "blocking": report["blocking"],
        "renderAllowed": report["renderAllowed"],
        "reviewIntensity": report["reviewIntensity"],
        "summary": report["summary"],
        "findingValidators": [finding["validator"] for finding in findings],
        "blockingValidators": [finding["validator"] for finding in findings if finding["blocking"]],
    }


def test_current_validator_result_snapshots(tmp_path: Path) -> None:
    expected = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))

    clean = tmp_path / "clean.md"
    clean.write_text(
        "# Memorandum\n\n"
        "This memorandum records the supplied factual background. "
        "The document preserves a neutral drafting posture.\n",
        encoding="utf-8",
    )

    numbering = tmp_path / "numbering.md"
    numbering.write_text(
        "# 의견서\n\n"
        "제1조(목적) 본 문서는 검토 목적을 기재한다.\n"
        "제3조(시행일) 본 문서는 작성일 현재 적용한다.\n",
        encoding="utf-8",
    )

    placeholder = "[Authority needed: governing statute]"
    tracked = tmp_path / "tracked-placeholder.md"
    tracked.write_text(f"# Memorandum\n\n{placeholder}\n", encoding="utf-8")
    tracked_document_id = schemas.new_document_id()

    actual = {
        "clean_en_general": _projection(
            run_validation(clean, manifest_path=_write_manifest(tmp_path / "clean"))
        ),
        "ko_numbering_gap": _projection(
            run_validation(
                numbering,
                manifest_path=_write_manifest(
                    tmp_path / "numbering",
                    jurisdiction="korea",
                    target_language="ko",
                    review_intensity="light",
                ),
            )
        ),
        "tracked_placeholder": _projection(
            run_validation(
                tracked,
                manifest_path=_write_manifest(tmp_path / "tracked", document_id=tracked_document_id),
                placeholder_registry_path=_write_placeholder_registry(
                    tmp_path / "tracked",
                    tracked_document_id,
                    [placeholder],
                ),
                validators=(),
            )
        ),
    }

    assert actual == expected
