"""Level B revision artifact generation.

Phase 1-8 intentionally does not promise native Word tracked changes. This
module produces the supported substitute: a clean copy, a unified redline diff,
and a section-level change-map that can be validated deterministically.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from tools.artifacts import schemas
from tools.artifacts.store import next_available_path


TRACKING_LEVEL = "level-b"
SectionRange = tuple[str, int, int]


@dataclass(frozen=True)
class LevelBArtifactPaths:
    clean_output: Path
    redline_output: Path
    change_map: Path

    def to_payload(self) -> dict[str, str]:
        return {
            "cleanOutput": str(self.clean_output),
            "redlineOutput": str(self.redline_output),
            "changeMap": str(self.change_map),
        }


def write_level_b_artifacts(
    original_path: str | Path,
    revised_path: str | Path,
    output_dir: str | Path,
    *,
    document_id: str | None = None,
    source_instruction: str = "",
) -> LevelBArtifactPaths:
    """Write clean/redline/change-map artifacts without overwriting old files."""
    original = Path(original_path)
    revised = Path(revised_path)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    if not original.is_file():
        raise FileNotFoundError(f"original file not found: {original}")
    if not revised.is_file():
        raise FileNotFoundError(f"revised file not found: {revised}")

    original_lines = _read_document_lines(original)
    revised_lines = _read_document_lines(revised)
    base_name = _safe_stem(revised)
    artifact_paths = LevelBArtifactPaths(
        clean_output=_next_kind_path(destination, base_name, "clean", revised.suffix or ".txt"),
        redline_output=_next_kind_path(destination, base_name, "redline", ".diff"),
        change_map=next_available_path(_change_map_base_path(destination)),
    )

    shutil.copy2(revised, artifact_paths.clean_output)
    artifact_paths.redline_output.write_text(
        _unified_diff(original_lines, revised_lines, original, revised),
        encoding="utf-8",
    )
    change_map = build_change_map(
        original_lines,
        revised_lines,
        document_id=document_id,
        source_instruction=source_instruction,
        original_path=original,
        revised_path=revised,
        artifact_paths=artifact_paths,
    )
    artifact_paths.change_map.write_text(
        json.dumps(change_map, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return artifact_paths


def build_change_map(
    original_lines: Sequence[str],
    revised_lines: Sequence[str],
    *,
    document_id: str | None = None,
    source_instruction: str = "",
    original_path: str | Path | None = None,
    revised_path: str | Path | None = None,
    artifact_paths: LevelBArtifactPaths | None = None,
) -> dict[str, Any]:
    """Build the canonical section-level Level B change-map payload."""
    resolved_document_id = document_id or schemas.new_document_id()
    sections = _section_ranges(original_lines, revised_lines)
    matcher = difflib.SequenceMatcher(a=list(original_lines), b=list(revised_lines), autojunk=False)

    changes: list[dict[str, Any]] = []
    counts = {"added": 0, "deleted": 0, "modified": 0}
    for tag, left_start, left_end, right_start, right_end in matcher.get_opcodes():
        if tag == "equal":
            continue
        if tag == "replace":
            shared = min(left_end - left_start, right_end - right_start)
            if shared:
                _append_change(
                    changes,
                    counts,
                    sections,
                    "modify",
                    original_lines[left_start : left_start + shared],
                    revised_lines[right_start : right_start + shared],
                    left_start,
                    right_start,
                    source_instruction,
                )
            if right_start + shared < right_end:
                _append_change(
                    changes,
                    counts,
                    sections,
                    "insert",
                    (),
                    revised_lines[right_start + shared : right_end],
                    left_start + shared,
                    right_start + shared,
                    source_instruction,
                )
            if left_start + shared < left_end:
                _append_change(
                    changes,
                    counts,
                    sections,
                    "delete",
                    original_lines[left_start + shared : left_end],
                    (),
                    left_start + shared,
                    right_start + shared,
                    source_instruction,
                )
            continue

        change_type = _change_type(tag)
        _append_change(
            changes,
            counts,
            sections,
            change_type,
            original_lines[left_start:left_end],
            revised_lines[right_start:right_end],
            left_start,
            right_start,
            source_instruction,
        )

    payload: dict[str, Any] = {
        "documentId": resolved_document_id,
        "schemaVersion": schemas.SCHEMA_VERSION,
        # Future-proofing field: Phase 1-8 supports only level-b artifacts.
        "trackingLevel": TRACKING_LEVEL,
        "nativeTrackedChanges": False,
        "changes": changes,
        "summary": counts,
        "status": "pass",
    }
    if original_path is not None:
        payload["originalFile"] = str(original_path)
    if revised_path is not None:
        payload["revisedFile"] = str(revised_path)
    if artifact_paths is not None:
        payload.update(artifact_paths.to_payload())
    return payload


def _read_document_lines(path: Path) -> list[str]:
    if path.suffix.lower() == ".docx":
        from tools.parsing.docx_parser import block_text, parse_docx

        parsed = parse_docx(path)
        return [block_text(block) for block in parsed.profile["blocks"] if block_text(block)]
    return path.read_text(encoding="utf-8").splitlines()


def _unified_diff(original_lines: Sequence[str], revised_lines: Sequence[str], original: Path, revised: Path) -> str:
    lines = list(
        difflib.unified_diff(
            list(original_lines),
            list(revised_lines),
            fromfile=str(original),
            tofile=str(revised),
            lineterm="",
        )
    )
    if not lines:
        return ""
    return "\n".join(lines) + "\n"


def _append_change(
    changes: list[dict[str, Any]],
    counts: dict[str, int],
    sections: dict[str, list[SectionRange]],
    change_type: str,
    original_chunk: Sequence[str],
    revised_chunk: Sequence[str],
    original_index: int,
    revised_index: int,
    source_instruction: str,
) -> None:
    counts[_summary_key(change_type)] += 1
    changes.append(
        {
            "id": f"c{len(changes) + 1}",
            "sectionId": _section_id_for_change(sections, original_index, revised_index),
            "type": change_type,
            "original": "\n".join(original_chunk),
            "revised": "\n".join(revised_chunk),
            "reason": _reason(source_instruction),
            "sourceInstruction": source_instruction,
        }
    )


def _safe_stem(path: Path) -> str:
    stem = path.stem.strip() or "document"
    return re.sub(r"[^0-9A-Za-z가-힣._-]+", "-", stem).strip("-") or "document"


def _next_kind_path(output_dir: Path, base_name: str, kind: str, suffix: str) -> Path:
    for version in range(1, 10000):
        candidate = output_dir / f"{base_name}_{kind}_v{version}{suffix}"
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"could not find available {kind} output path in {output_dir}")


def _change_map_base_path(output_dir: Path) -> Path:
    if output_dir.name == "documents":
        return output_dir.parent / "change-map.json"
    return output_dir / "change-map.json"


def _change_type(opcode: str) -> str:
    if opcode == "insert":
        return "insert"
    if opcode == "delete":
        return "delete"
    return "modify"


def _summary_key(change_type: str) -> str:
    if change_type == "insert":
        return "added"
    if change_type == "delete":
        return "deleted"
    return "modified"


def _reason(source_instruction: str) -> str:
    if source_instruction:
        return f"per user instruction: {source_instruction}"
    return "per revision diff"


def _section_ranges(original_lines: Sequence[str], revised_lines: Sequence[str]) -> dict[str, list[SectionRange]]:
    return {
        "original": _ranges_for_lines(original_lines),
        "revised": _ranges_for_lines(revised_lines),
    }


def _ranges_for_lines(lines: Sequence[str]) -> list[SectionRange]:
    open_ranges: list[tuple[str, int, int | None]] = [("document", 0, None)]
    next_index = 1
    for index, line in enumerate(lines):
        if not _looks_like_heading(line):
            continue
        if open_ranges:
            previous_section, start, _ = open_ranges[-1]
            open_ranges[-1] = (previous_section, start, index - 1)
        open_ranges.append((f"s{next_index}", index, None))
        next_index += 1
    final_index = max(len(lines) - 1, 0)
    section_id, start, end = open_ranges[-1]
    if end is None:
        open_ranges[-1] = (section_id, start, final_index)
    return [(section_id, start, end if end is not None else final_index) for section_id, start, end in open_ranges]


def _looks_like_heading(line: str) -> bool:
    text = line.strip()
    if not text or len(text) > 140:
        return False
    patterns = (
        r"^#{1,6}\s+\S",
        r"^제\s*\d+\s*[편장절관]\b",
        r"^제\s*\d+\s*조(?:의\s*\d+)?(?:\s*\([^)]+\))?",
        r"^[IVXLC]+\.\s+\S",
        r"^\d+(?:\.\d+)*[.)]\s+\S",
    )
    return any(re.match(pattern, text) for pattern in patterns)


def _section_id_for_change(
    sections: dict[str, list[SectionRange]],
    original_index: int,
    revised_index: int,
) -> str:
    if original_index >= 0:
        section_id = _section_at(sections["original"], original_index)
        if section_id != "document":
            return section_id
    return _section_at(sections["revised"], revised_index)


def _section_at(ranges: Sequence[SectionRange], index: int) -> str:
    if not ranges:
        return "document"
    bounded_index = max(index, 0)
    for section_id, start, end in reversed(ranges):
        if bounded_index >= start and bounded_index <= end:
            return section_id
    return ranges[0][0]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tools.revision.level_b",
        description="Write Level B revision artifacts: clean copy, redline diff, and change-map.",
    )
    parser.add_argument("original", type=Path, help="original document path")
    parser.add_argument("revised", type=Path, help="revised document path")
    parser.add_argument("output_dir", type=Path, help="directory for clean/redline outputs")
    parser.add_argument("--document-id", help="documentId to store in change-map")
    parser.add_argument("--source-instruction", default="", help="user revision instruction for change reasons")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = write_level_b_artifacts(
        args.original,
        args.revised,
        args.output_dir,
        document_id=args.document_id,
        source_instruction=args.source_instruction,
    )
    print(json.dumps(paths.to_payload(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
