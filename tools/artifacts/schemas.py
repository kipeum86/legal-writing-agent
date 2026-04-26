"""Schema definitions and validation for versioned pipeline artifacts.

The artifact layer intentionally stays stdlib-only. These dataclasses are not a
full persistence model; they are the narrow wire format that lets pipeline steps
exchange state without relying on chat history.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


SCHEMA_VERSION = "1.0"
SANITIZER_VERSION = "tools.security.sanitizer.v1"
MAX_SCHEMA_RETRIES = 2

ARTIFACT_TYPES = {
    "manifest",
    "outline",
    "clause_map",
    "term_registry",
    "placeholder_registry",
    "validation_report",
    "checkpoint",
    "schema_error",
}

REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "manifest": (
        "documentId",
        "documentType",
        "supportLevel",
        "targetLanguage",
        "jurisdiction",
        "authorityPacketProvided",
        "skeletonOnly",
    ),
    "outline": ("documentId", "title", "sections"),
    "clause_map": ("documentId", "clauses"),
    "term_registry": ("documentId", "terms"),
    "placeholder_registry": ("documentId", "placeholders"),
    "validation_report": ("documentId", "status", "findings"),
    "checkpoint": ("documentId", "step", "status", "artifactPaths"),
    "schema_error": ("documentId", "step", "errors"),
}

ENUMS: dict[str, set[str]] = {
    "documentType": {"advisory", "corporate", "litigation", "regulatory", "general"},
    "supportLevel": {"full", "conditional"},
    "targetLanguage": {"ko", "en"},
    "reviewIntensity": {"light", "standard", "thorough"},
    "outputFormat": {"docx", "pdf", "md", "txt"},
    "pageSize": {"a4", "us-letter"},
    "validationStatus": {"pending", "passed", "failed"},
    "checkpointStatus": {"pending", "in_progress", "completed", "failed"},
}


class SchemaValidationError(ValueError):
    """Raised when an artifact payload does not match the current schema."""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_document_id() -> str:
    return str(uuid4())


@dataclass(frozen=True)
class SourceProvenance:
    sourceType: str
    path: str
    sha256: str | None = None
    trusted: bool = False


@dataclass(frozen=True)
class SchemaError:
    field: str
    message: str
    rawValue: str | None = None


@dataclass(frozen=True)
class MatterManifest:
    documentId: str = field(default_factory=new_document_id)
    documentType: str = "general"
    supportLevel: str = "full"
    targetLanguage: str = "ko"
    jurisdiction: str = "korea"
    governingLaw: str = ""
    parties: tuple[dict[str, Any], ...] = ()
    reviewIntensity: str = "standard"
    outputFormat: str = "docx"
    houseStyle: str | None = None
    authorityPacketProvided: bool = False
    skeletonOnly: bool = False
    authorityChunks: tuple[dict[str, Any], ...] = ()
    safeInference: tuple[dict[str, Any], ...] = ()
    unsafeInference: tuple[dict[str, Any], ...] = ()
    pageSize: str = "a4"
    step: str = "D1"
    sessionContext: dict[str, Any] = field(
        default_factory=lambda: {
            "priorDocumentId": None,
            "inheritedTerms": False,
            "inheritedParties": False,
        }
    )
    schemaVersion: str = SCHEMA_VERSION
    artifactType: str = "manifest"
    createdAt: str = field(default_factory=now_iso)
    updatedAt: str = field(default_factory=now_iso)
    sanitized: bool = True
    sanitizerVersion: str = SANITIZER_VERSION
    sourceProvenance: tuple[SourceProvenance, ...] = ()
    schemaErrors: tuple[SchemaError, ...] = ()


@dataclass(frozen=True)
class Outline:
    documentId: str
    title: str
    sections: tuple[dict[str, Any], ...]
    schemaVersion: str = SCHEMA_VERSION
    artifactType: str = "outline"
    createdAt: str = field(default_factory=now_iso)
    updatedAt: str = field(default_factory=now_iso)
    sanitized: bool = True
    sanitizerVersion: str = SANITIZER_VERSION
    sourceProvenance: tuple[SourceProvenance, ...] = ()
    schemaErrors: tuple[SchemaError, ...] = ()


@dataclass(frozen=True)
class ClauseMap:
    documentId: str
    clauses: tuple[dict[str, Any], ...]
    schemaVersion: str = SCHEMA_VERSION
    artifactType: str = "clause_map"
    createdAt: str = field(default_factory=now_iso)
    updatedAt: str = field(default_factory=now_iso)
    sanitized: bool = True
    sanitizerVersion: str = SANITIZER_VERSION
    sourceProvenance: tuple[SourceProvenance, ...] = ()
    schemaErrors: tuple[SchemaError, ...] = ()


@dataclass(frozen=True)
class TermRegistry:
    documentId: str
    terms: tuple[dict[str, Any], ...]
    schemaVersion: str = SCHEMA_VERSION
    artifactType: str = "term_registry"
    createdAt: str = field(default_factory=now_iso)
    updatedAt: str = field(default_factory=now_iso)
    sanitized: bool = True
    sanitizerVersion: str = SANITIZER_VERSION
    sourceProvenance: tuple[SourceProvenance, ...] = ()
    schemaErrors: tuple[SchemaError, ...] = ()


@dataclass(frozen=True)
class PlaceholderRegistry:
    documentId: str
    placeholders: tuple[dict[str, Any], ...]
    schemaVersion: str = SCHEMA_VERSION
    artifactType: str = "placeholder_registry"
    createdAt: str = field(default_factory=now_iso)
    updatedAt: str = field(default_factory=now_iso)
    sanitized: bool = True
    sanitizerVersion: str = SANITIZER_VERSION
    sourceProvenance: tuple[SourceProvenance, ...] = ()
    schemaErrors: tuple[SchemaError, ...] = ()


@dataclass(frozen=True)
class ValidationReport:
    documentId: str
    status: str = "pending"
    findings: tuple[dict[str, Any], ...] = ()
    blocking: bool = False
    renderAllowed: bool = True
    documentPath: str = ""
    manifestPath: str | None = None
    reviewIntensity: str = "standard"
    checks: tuple[dict[str, Any], ...] = ()
    summary: dict[str, Any] = field(default_factory=dict)
    schemaVersion: str = SCHEMA_VERSION
    artifactType: str = "validation_report"
    createdAt: str = field(default_factory=now_iso)
    updatedAt: str = field(default_factory=now_iso)
    sanitized: bool = True
    sanitizerVersion: str = SANITIZER_VERSION
    sourceProvenance: tuple[SourceProvenance, ...] = ()
    schemaErrors: tuple[SchemaError, ...] = ()


@dataclass(frozen=True)
class Checkpoint:
    documentId: str
    step: str
    status: str
    artifactPaths: dict[str, str]
    schemaVersion: str = SCHEMA_VERSION
    artifactType: str = "checkpoint"
    createdAt: str = field(default_factory=now_iso)
    updatedAt: str = field(default_factory=now_iso)
    sanitized: bool = True
    sanitizerVersion: str = SANITIZER_VERSION
    sourceProvenance: tuple[SourceProvenance, ...] = ()
    schemaErrors: tuple[SchemaError, ...] = ()


@dataclass(frozen=True)
class SchemaErrorArtifact:
    documentId: str
    step: str
    errors: tuple[SchemaError, ...]
    rawArtifact: dict[str, Any] | None = None
    schemaVersion: str = SCHEMA_VERSION
    artifactType: str = "schema_error"
    createdAt: str = field(default_factory=now_iso)
    updatedAt: str = field(default_factory=now_iso)
    sanitized: bool = True
    sanitizerVersion: str = SANITIZER_VERSION
    sourceProvenance: tuple[SourceProvenance, ...] = ()
    schemaErrors: tuple[SchemaError, ...] = ()


def artifact_to_payload(artifact: Any) -> dict[str, Any]:
    if is_dataclass(artifact):
        return _json_ready(asdict(artifact))
    if isinstance(artifact, dict):
        return _json_ready(dict(artifact))
    raise SchemaValidationError(f"artifact must be a dataclass or dict, got {type(artifact).__name__}")


def _json_ready(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    return value


def validate_artifact(artifact: Any, *, expected_type: str | None = None) -> dict[str, Any]:
    payload = artifact_to_payload(artifact)
    errors: list[str] = []

    if payload.get("schemaVersion") != SCHEMA_VERSION:
        errors.append(
            f"schemaVersion must be {SCHEMA_VERSION!r}, got {payload.get('schemaVersion')!r}"
        )

    artifact_type = payload.get("artifactType")
    if artifact_type not in ARTIFACT_TYPES:
        errors.append(f"artifactType must be one of {sorted(ARTIFACT_TYPES)}, got {artifact_type!r}")
    elif expected_type is not None and artifact_type != expected_type:
        errors.append(f"artifactType must be {expected_type!r}, got {artifact_type!r}")

    if not isinstance(payload.get("documentId"), str) or not payload.get("documentId"):
        errors.append("documentId must be a non-empty string")

    for field_name in ("createdAt", "updatedAt"):
        if not isinstance(payload.get(field_name), str) or not payload.get(field_name):
            errors.append(f"{field_name} must be a non-empty ISO timestamp string")

    if not isinstance(payload.get("sanitized"), bool):
        errors.append("sanitized must be a boolean")
    if not isinstance(payload.get("sanitizerVersion"), str) or not payload.get("sanitizerVersion"):
        errors.append("sanitizerVersion must be a non-empty string")
    if not isinstance(payload.get("sourceProvenance"), list):
        errors.append("sourceProvenance must be a list")

    if artifact_type in REQUIRED_FIELDS:
        for field_name in REQUIRED_FIELDS[artifact_type]:
            if field_name not in payload:
                errors.append(f"{field_name} is required for {artifact_type}")

    _validate_specific(payload, errors)

    if errors:
        raise SchemaValidationError("; ".join(errors))
    return payload


def _validate_specific(payload: dict[str, Any], errors: list[str]) -> None:
    artifact_type = payload.get("artifactType")

    if artifact_type == "manifest":
        _enum(payload, "documentType", ENUMS["documentType"], errors)
        _enum(payload, "supportLevel", ENUMS["supportLevel"], errors)
        _enum(payload, "targetLanguage", ENUMS["targetLanguage"], errors)
        _enum(payload, "reviewIntensity", ENUMS["reviewIntensity"], errors)
        _enum(payload, "outputFormat", ENUMS["outputFormat"], errors)
        _enum(payload, "pageSize", ENUMS["pageSize"], errors)
        for field_name in ("authorityPacketProvided", "skeletonOnly"):
            if not isinstance(payload.get(field_name), bool):
                errors.append(f"{field_name} must be a boolean")
        for field_name in ("parties", "safeInference", "unsafeInference", "authorityChunks"):
            if not isinstance(payload.get(field_name), list):
                errors.append(f"{field_name} must be a list")
        if not isinstance(payload.get("sessionContext"), dict):
            errors.append("sessionContext must be an object")

    if artifact_type == "validation_report":
        _enum(payload, "status", ENUMS["validationStatus"], errors)
        _enum(payload, "reviewIntensity", ENUMS["reviewIntensity"], errors)
        if not isinstance(payload.get("findings"), list):
            errors.append("findings must be a list")
        if not isinstance(payload.get("blocking"), bool):
            errors.append("blocking must be a boolean")
        if not isinstance(payload.get("renderAllowed"), bool):
            errors.append("renderAllowed must be a boolean")
        if not isinstance(payload.get("checks"), list):
            errors.append("checks must be a list")
        if not isinstance(payload.get("summary"), dict):
            errors.append("summary must be an object")

    if artifact_type == "checkpoint":
        _enum(payload, "status", ENUMS["checkpointStatus"], errors)
        if not isinstance(payload.get("artifactPaths"), dict):
            errors.append("artifactPaths must be an object")

    for list_field in ("sections", "clauses", "terms", "placeholders", "errors"):
        if list_field in payload and not isinstance(payload[list_field], list):
            errors.append(f"{list_field} must be a list")


def _enum(payload: dict[str, Any], field_name: str, allowed: set[str], errors: list[str]) -> None:
    value = payload.get(field_name)
    if value not in allowed:
        errors.append(f"{field_name} must be one of {sorted(allowed)}, got {value!r}")


def make_schema_error_artifact(
    *,
    document_id: str,
    step: str,
    errors: tuple[SchemaError, ...],
    raw_artifact: dict[str, Any] | None = None,
) -> SchemaErrorArtifact:
    return SchemaErrorArtifact(
        documentId=document_id,
        step=step,
        errors=errors,
        rawArtifact=raw_artifact,
    )
