"""Schema migration hooks for artifact payloads."""
from __future__ import annotations

from typing import Any

from tools.artifacts.schemas import SCHEMA_VERSION, SchemaValidationError


def migrate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a payload upgraded to the current schema version.

    Version 1.0 is the first persisted artifact schema, so there is no real
    migration yet. Keeping this hook explicit gives future schema changes a
    stable place to live without teaching callers about historical versions.
    """
    version = payload.get("schemaVersion")
    if version == SCHEMA_VERSION:
        return dict(payload)
    raise SchemaValidationError(f"no migration path from schemaVersion {version!r} to {SCHEMA_VERSION!r}")
