"""Gate between markitdown-converted markdown and the library/grade-* placement step.

- Scan with tools.security.sanitizer.
- If clean -> return wrapped_text unchanged (no <escape> tags inserted, because
  there were no matches).
- If matches -> write original file + audit JSON to library/inbox/_failed/,
  raise IngestQuarantined so the caller can surface to the user.
- Emit a per-file audit sidecar regardless of outcome.
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from tools.security.sanitizer import sanitize, write_audit, wrap_untrusted


class IngestQuarantined(Exception):
    def __init__(self, audit_path: Path, match_count: int) -> None:
        super().__init__(f"ingest quarantined: {match_count} injection patterns matched")
        self.audit_path = audit_path
        self.match_count = match_count


@dataclass(frozen=True)
class GateOutcome:
    accepted_path: Path
    audit_path: Path


def run_gate(
    converted_md_path: Path,
    *,
    audit_dir: Path,
    quarantine_dir: Path = Path("library/inbox/_failed"),
    wrap_with_untrusted_tag: bool = False,
) -> GateOutcome:
    text = converted_md_path.read_text(encoding="utf-8")
    result = sanitize(text)

    audit_file = audit_dir / f"{converted_md_path.stem}.audit.json"
    write_audit(result, source_path=str(converted_md_path), audit_path=audit_file)

    if not result.is_clean:
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        target = quarantine_dir / converted_md_path.name
        shutil.move(str(converted_md_path), str(target))
        raise IngestQuarantined(audit_path=audit_file, match_count=result.match_count)

    if wrap_with_untrusted_tag:
        converted_md_path.write_text(
            wrap_untrusted(result.wrapped_text, source="ingest", path=str(converted_md_path)),
            encoding="utf-8",
        )
    return GateOutcome(accepted_path=converted_md_path, audit_path=audit_file)
