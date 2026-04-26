from __future__ import annotations

import pytest

from tools.artifacts import schemas
from tools.artifacts.migrations import migrate_payload


def test_manifest_schema_includes_version_and_trust_metadata() -> None:
    manifest = schemas.MatterManifest(
        documentType="advisory",
        supportLevel="conditional",
        authorityPacketProvided=False,
        skeletonOnly=True,
        sourceProvenance=(
            schemas.SourceProvenance(sourceType="input", path="input/request.md", trusted=False),
        ),
    )

    payload = schemas.validate_artifact(manifest, expected_type="manifest")

    assert payload["schemaVersion"] == schemas.SCHEMA_VERSION
    assert payload["artifactType"] == "manifest"
    assert payload["sanitized"] is True
    assert payload["sanitizerVersion"] == schemas.SANITIZER_VERSION
    assert payload["sourceProvenance"][0]["sourceType"] == "input"
    assert payload["authorityChunks"] == []
    assert payload["safeInference"] == []
    assert payload["unsafeInference"] == []


def test_all_phase_two_artifacts_validate_with_same_document_id() -> None:
    document_id = schemas.new_document_id()
    artifacts = [
        schemas.MatterManifest(documentId=document_id),
        schemas.Outline(documentId=document_id, title="Test", sections=()),
        schemas.ClauseMap(documentId=document_id, clauses=()),
        schemas.TermRegistry(documentId=document_id, terms=()),
        schemas.PlaceholderRegistry(documentId=document_id, placeholders=()),
        schemas.ValidationReport(documentId=document_id, status="pending", findings=()),
        schemas.Checkpoint(documentId=document_id, step="D1", status="completed", artifactPaths={}),
    ]

    for artifact in artifacts:
        payload = schemas.validate_artifact(artifact)
        assert payload["schemaVersion"] == schemas.SCHEMA_VERSION
        assert payload["documentId"] == document_id


def test_schema_mismatch_returns_clear_error() -> None:
    manifest = schemas.artifact_to_payload(schemas.MatterManifest())
    manifest["schemaVersion"] = "0.9"

    with pytest.raises(schemas.SchemaValidationError, match="schemaVersion must be '1.0'"):
        schemas.validate_artifact(manifest)


def test_invalid_manifest_enum_is_rejected() -> None:
    manifest = schemas.artifact_to_payload(schemas.MatterManifest())
    manifest["supportLevel"] = "mixed"

    with pytest.raises(schemas.SchemaValidationError, match="supportLevel"):
        schemas.validate_artifact(manifest)


def test_schema_error_artifact_records_llm_fallback_errors() -> None:
    document_id = schemas.new_document_id()
    artifact = schemas.make_schema_error_artifact(
        document_id=document_id,
        step="D1",
        errors=(schemas.SchemaError(field="documentType", message="unknown enum"),),
        raw_artifact={"documentType": "memo-ish"},
    )

    payload = schemas.validate_artifact(artifact, expected_type="schema_error")

    assert payload["documentId"] == document_id
    assert payload["errors"][0]["field"] == "documentType"
    assert payload["rawArtifact"]["documentType"] == "memo-ish"
    assert schemas.MAX_SCHEMA_RETRIES == 2


def test_current_schema_migration_is_identity_copy() -> None:
    payload = schemas.artifact_to_payload(schemas.MatterManifest())
    migrated = migrate_payload(payload)

    assert migrated == payload
    assert migrated is not payload


def test_unknown_schema_version_has_no_silent_migration() -> None:
    payload = schemas.artifact_to_payload(schemas.MatterManifest())
    payload["schemaVersion"] = "2099.0"

    with pytest.raises(schemas.SchemaValidationError, match="no migration path"):
        migrate_payload(payload)
