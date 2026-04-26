from __future__ import annotations

from pathlib import Path

import pytest

from tools.artifacts import (
    ArtifactStore,
    Checkpoint,
    ClauseMap,
    MatterManifest,
    Outline,
    PlaceholderRegistry,
    SchemaValidationError,
    TermRegistry,
    ValidationReport,
    next_available_path,
)
from tools.artifacts import schemas


def test_write_many_links_artifacts_by_document_id(tmp_path: Path) -> None:
    store = ArtifactStore(output_base=tmp_path)
    document_id = schemas.new_document_id()

    written = store.write_many(
        [
            MatterManifest(documentId=document_id),
            Outline(documentId=document_id, title="Outline", sections=()),
            ClauseMap(documentId=document_id, clauses=()),
            TermRegistry(documentId=document_id, terms=()),
            PlaceholderRegistry(documentId=document_id, placeholders=()),
            ValidationReport(documentId=document_id, status="pending", findings=()),
            Checkpoint(documentId=document_id, step="D1", status="completed", artifactPaths={}),
        ]
    )

    assert set(written) == {
        "manifest",
        "outline",
        "clause_map",
        "term_registry",
        "placeholder_registry",
        "validation_report",
        "checkpoint",
    }
    assert all(path.exists() for path in written.values())
    assert store.read_latest("manifest", document_id)["documentId"] == document_id
    assert store.read_latest("checkpoint", document_id)["documentId"] == document_id


def test_write_many_rejects_mismatched_document_ids(tmp_path: Path) -> None:
    store = ArtifactStore(output_base=tmp_path)

    with pytest.raises(SchemaValidationError, match="must share documentId"):
        store.write_many(
            [
                MatterManifest(documentId="doc-a"),
                Outline(documentId="doc-b", title="Outline", sections=()),
            ]
        )


def test_artifact_write_does_not_overwrite_existing_file(tmp_path: Path) -> None:
    store = ArtifactStore(output_base=tmp_path)
    document_id = schemas.new_document_id()

    first = store.write_artifact(MatterManifest(documentId=document_id))
    second = store.write_artifact(MatterManifest(documentId=document_id, step="D2"))

    assert first.name == f"{document_id}.json"
    assert second.name == f"{document_id}.v2.json"
    assert first.read_text(encoding="utf-8") != second.read_text(encoding="utf-8")
    assert store.read_latest("manifest", document_id)["step"] == "D2"


def test_next_available_document_output_path_does_not_overwrite(tmp_path: Path) -> None:
    store = ArtifactStore(output_base=tmp_path)
    first = store.next_document_output_path("draft.docx")
    first.write_text("existing", encoding="utf-8")

    second = store.next_document_output_path("draft.docx")

    assert second.name == "draft.v2.docx"
    assert not second.exists()


def test_next_available_path_versions_before_suffix(tmp_path: Path) -> None:
    target = tmp_path / "report.json"
    target.write_text("one", encoding="utf-8")
    (tmp_path / "report.v2.json").write_text("two", encoding="utf-8")

    assert next_available_path(target).name == "report.v3.json"


def test_default_store_uses_legal_agent_private_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("LEGAL_AGENT_PRIVATE_DIR", str(tmp_path))
    store = ArtifactStore()
    document_id = schemas.new_document_id()

    path = store.write_artifact(MatterManifest(documentId=document_id))

    assert path == tmp_path / "output" / "manifests" / f"{document_id}.json"
    assert path.exists()


def test_read_artifact_validates_expected_type(tmp_path: Path) -> None:
    store = ArtifactStore(output_base=tmp_path)
    path = store.write_artifact(MatterManifest())

    with pytest.raises(SchemaValidationError, match="artifactType must be 'checkpoint'"):
        store.read_artifact(path, expected_type="checkpoint")
