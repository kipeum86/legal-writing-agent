from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.artifacts import schemas
from tools.validation.runner import is_blocking, run_validation


ROOT = Path(__file__).resolve().parents[2]
FALSE_POSITIVE_LABELS = ROOT / "tests" / "fixtures" / "validation" / "false-positive-labels.json"


def write_manifest(
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


def write_placeholder_registry(tmp_path: Path, document_id: str, placeholders: list[str]) -> Path:
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


def test_severity_intensity_blocking_matrix() -> None:
    assert is_blocking("critical", "light")
    assert not is_blocking("major", "light")
    assert not is_blocking("minor", "light")

    assert is_blocking("critical", "standard")
    assert is_blocking("major", "standard")
    assert not is_blocking("minor", "standard")

    assert is_blocking("critical", "thorough")
    assert is_blocking("major", "thorough")
    assert is_blocking("minor", "thorough")


def test_runner_passes_clean_draft(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text(
        "# Memorandum\n\n"
        "This memorandum records the supplied factual background. "
        "The document preserves a neutral drafting posture.\n",
        encoding="utf-8",
    )
    manifest = write_manifest(tmp_path)

    report = run_validation(draft, manifest_path=manifest)

    assert report["status"] == "passed"
    assert report["blocking"] is False
    assert report["renderAllowed"] is True
    assert {check["validator"] for check in report["checks"]} == {
        "numbering",
        "cross_reference",
        "register",
        "term",
        "citation",
        "placeholder_registry",
    }


def test_critical_numbering_issue_blocks_rendering(tmp_path: Path) -> None:
    draft = tmp_path / "numbering.md"
    draft.write_text(
        "# 의견서\n\n"
        "제1조(목적) 본 문서는 검토 목적을 기재한다.\n"
        "제3조(시행일) 본 문서는 작성일 현재 적용한다.\n",
        encoding="utf-8",
    )
    manifest = write_manifest(tmp_path, jurisdiction="korea", target_language="ko", review_intensity="light")

    report = run_validation(draft, manifest_path=manifest)

    assert report["status"] == "failed"
    assert report["blocking"] is True
    assert report["renderAllowed"] is False
    assert any(
        finding["validator"] == "numbering" and finding["severity"] == "critical"
        for finding in report["findings"]
    )


def test_malformed_korean_citation_blocks_rendering(tmp_path: Path) -> None:
    draft = tmp_path / "citation.md"
    draft.write_text(
        "# 의견서\n\n"
        "대법원 2023 선고 2022다12345 판결에 관한 사용자 제공 문구를 정리한다.\n",
        encoding="utf-8",
    )
    manifest = write_manifest(tmp_path, jurisdiction="korea", target_language="ko")

    report = run_validation(draft, manifest_path=manifest)

    assert report["status"] == "failed"
    assert any(
        finding["validator"] == "citation" and finding["severity"] == "critical"
        for finding in report["findings"]
    )


def test_untracked_placeholder_blocks_rendering(tmp_path: Path) -> None:
    draft = tmp_path / "placeholder.md"
    draft.write_text(
        "# Memorandum\n\n"
        "[Authority needed: governing statute]\n",
        encoding="utf-8",
    )
    manifest = write_manifest(tmp_path)

    report = run_validation(draft, manifest_path=manifest)

    assert report["status"] == "failed"
    assert any(
        finding["validator"] == "placeholder_registry"
        and finding["type"] in {"placeholder_registry_missing", "placeholder_untracked"}
        and finding["blocking"]
        for finding in report["findings"]
    )


def test_tracked_placeholder_passes_placeholder_gate(tmp_path: Path) -> None:
    document_id = schemas.new_document_id()
    draft = tmp_path / "placeholder.md"
    placeholder = "[Authority needed: governing statute]"
    draft.write_text(f"# Memorandum\n\n{placeholder}\n", encoding="utf-8")
    manifest = write_manifest(tmp_path, document_id=document_id)
    registry = write_placeholder_registry(tmp_path, document_id, [placeholder])

    report = run_validation(draft, manifest_path=manifest, placeholder_registry_path=registry)

    assert not any(
        finding["validator"] == "placeholder_registry" and finding["blocking"]
        for finding in report["findings"]
    )


def test_markdown_footnote_tokens_are_not_placeholder_gaps(tmp_path: Path) -> None:
    draft = tmp_path / "footnote.md"
    draft.write_text(
        "# Memorandum\n\n"
        "The supplied sentence includes a footnote candidate.[^1]\n\n"
        "[^1]: This is preserved for renderer conversion.\n",
        encoding="utf-8",
    )
    manifest = write_manifest(tmp_path)

    report = run_validation(draft, manifest_path=manifest, validators=())

    assert report["status"] == "passed"
    assert not any(finding["validator"] == "placeholder_registry" for finding in report["findings"])


def test_false_positive_labels_suppress_blocking_findings(tmp_path: Path) -> None:
    draft = tmp_path / "false-positive.md"
    draft.write_text(
        "# Memorandum\n\n"
        "The quoted phrase is kind of preserved for this fixture.\n",
        encoding="utf-8",
    )
    manifest = write_manifest(tmp_path)

    report = run_validation(
        draft,
        manifest_path=manifest,
        false_positive_labels_path=FALSE_POSITIVE_LABELS,
    )

    suppressed = [finding for finding in report["findings"] if finding.get("suppressed")]
    assert suppressed
    assert all(not finding["blocking"] for finding in suppressed)
    assert report["renderAllowed"] is True


def test_runner_cli_emits_single_json_report(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text("# Memorandum\n\nThis document records supplied facts.\n", encoding="utf-8")
    manifest = write_manifest(tmp_path)
    out = tmp_path / "report.json"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.validation.runner",
            str(draft),
            "--manifest",
            str(manifest),
            "--out",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    stdout_report = json.loads(completed.stdout)
    file_report = json.loads(out.read_text(encoding="utf-8"))
    assert stdout_report["artifactType"] == "validation_report"
    assert stdout_report == file_report
