"""Filesystem store for versioned pipeline artifacts."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

import tools.artifacts.schemas as schemas
from tools.artifacts.schemas import SchemaValidationError
from tools.security import paths


KIND_TO_DIR = {
    "manifest": paths.manifests_dir,
    "outline": paths.outlines_dir,
    "clause_map": paths.clause_maps_dir,
    "term_registry": paths.term_registries_dir,
    "placeholder_registry": paths.placeholders_dir,
    "validation_report": paths.validation_reports_dir,
    "checkpoint": paths.checkpoints_dir,
    "schema_error": paths.schema_errors_dir,
}


def next_available_path(path: Path) -> Path:
    """Return a non-existing path by appending .vN before the suffix."""
    if not path.exists():
        return path

    for version in range(2, 10000):
        candidate = path.with_name(f"{path.stem}.v{version}{path.suffix}")
        if not candidate.exists():
            return candidate

    raise FileExistsError(f"could not find available versioned path for {path}")


class ArtifactStore:
    """Write and read JSON artifacts under the resolved output directory."""

    def __init__(self, *, output_base: Path | None = None) -> None:
        self.output_base = output_base

    def write_artifact(self, artifact: Any, *, overwrite: bool = False) -> Path:
        payload = schemas.validate_artifact(artifact)
        target = self.path_for(payload["artifactType"], payload["documentId"])
        if not overwrite:
            target = next_available_path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return target

    def write_many(self, artifacts: Iterable[Any], *, overwrite: bool = False) -> dict[str, Path]:
        payloads = [schemas.validate_artifact(artifact) for artifact in artifacts]
        document_ids = {payload["documentId"] for payload in payloads}
        if len(document_ids) != 1:
            raise SchemaValidationError(
                f"all artifacts in one write_many call must share documentId, got {sorted(document_ids)}"
            )

        written: dict[str, Path] = {}
        for payload in payloads:
            written[payload["artifactType"]] = self.write_artifact(payload, overwrite=overwrite)
        return written

    def read_artifact(self, path: Path, *, expected_type: str | None = None) -> dict[str, Any]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return schemas.validate_artifact(payload, expected_type=expected_type)

    def read_latest(self, artifact_type: str, document_id: str) -> dict[str, Any]:
        candidates = self._versions_for(artifact_type, document_id)
        if not candidates:
            raise FileNotFoundError(f"no {artifact_type} artifact for documentId {document_id}")
        return self.read_artifact(candidates[-1], expected_type=artifact_type)

    def path_for(self, artifact_type: str, document_id: str) -> Path:
        if artifact_type not in KIND_TO_DIR:
            raise SchemaValidationError(f"unknown artifactType: {artifact_type}")
        directory = self._dir_for(artifact_type)
        return directory / f"{document_id}.json"

    def artifact_paths(self, document_id: str) -> dict[str, Path]:
        found: dict[str, Path] = {}
        for artifact_type in KIND_TO_DIR:
            versions = self._versions_for(artifact_type, document_id)
            if versions:
                found[artifact_type] = versions[-1]
        return found

    def next_document_output_path(self, filename: str) -> Path:
        target = self._output_dir() / "documents" / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        return next_available_path(target)

    def _dir_for(self, artifact_type: str) -> Path:
        if self.output_base is None:
            return KIND_TO_DIR[artifact_type]()
        relative_name = KIND_TO_DIR[artifact_type]().name
        return self.output_base / relative_name

    def _output_dir(self) -> Path:
        if self.output_base is None:
            return paths.output_dir()
        return self.output_base

    def _versions_for(self, artifact_type: str, document_id: str) -> list[Path]:
        directory = self._dir_for(artifact_type)
        if not directory.exists():
            return []
        pattern = re.compile(rf"^{re.escape(document_id)}(?:\.v(?P<version>\d+))?\.json$")
        candidates: list[tuple[int, Path]] = []
        for path in directory.glob(f"{document_id}*.json"):
            match = pattern.match(path.name)
            if match:
                version = int(match.group("version") or "1")
                candidates.append((version, path))
        return [path for _, path in sorted(candidates, key=lambda item: item[0])]
