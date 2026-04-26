from __future__ import annotations

import os
from pathlib import Path


def _base() -> Path:
    override = os.environ.get("LEGAL_AGENT_PRIVATE_DIR")
    if override:
        return Path(override).expanduser()
    return Path(__file__).resolve().parents[2]


def input_dir() -> Path:
    return _base() / "input"


def output_dir() -> Path:
    return _base() / "output"


def documents_dir() -> Path:
    return output_dir() / "documents"


def manifests_dir() -> Path:
    return output_dir() / "manifests"


def manifest_dir() -> Path:
    return manifests_dir()


def clause_maps_dir() -> Path:
    return output_dir() / "clause-maps"


def outlines_dir() -> Path:
    return output_dir() / "outlines"


def placeholders_dir() -> Path:
    return output_dir() / "placeholders"


def term_registries_dir() -> Path:
    return output_dir() / "term-registries"


def validation_reports_dir() -> Path:
    return output_dir() / "validation-reports"


def checkpoints_dir() -> Path:
    return output_dir() / "checkpoints"


def schema_errors_dir() -> Path:
    return output_dir() / "schema-errors"


def checkpoint_path() -> Path:
    return output_dir() / "checkpoint.json"


def change_map_path() -> Path:
    return output_dir() / "change-map.json"


def outline_path() -> Path:
    return output_dir() / "outline.json"


def codex_quality_audit_prompt_path() -> Path:
    return output_dir() / "codex-quality-audit-prompt.md"


def describe_runtime_io() -> str:
    override = os.environ.get("LEGAL_AGENT_PRIVATE_DIR")
    if override:
        return f"{Path(override).expanduser()} (LEGAL_AGENT_PRIVATE_DIR)"
    return f"{_base()} (repo fallback)"
