from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.artifacts import schemas
from tools.revision.level_b import build_change_map, write_level_b_artifacts


ROOT = Path(__file__).resolve().parents[2]


def test_write_level_b_artifacts_creates_clean_redline_and_change_map(tmp_path: Path) -> None:
    original = tmp_path / "opinion.txt"
    revised = tmp_path / "opinion_revised.txt"
    output_dir = tmp_path / "output" / "documents"
    original.write_text(
        "1. Issue\nOriginal argument.\n2. Conclusion\nOriginal conclusion.\nClosing marker.\n",
        encoding="utf-8",
    )
    revised.write_text(
        "1. Issue\nStrengthened argument.\n2. Conclusion\nRevised conclusion.\nNew final sentence.\nClosing marker.\n",
        encoding="utf-8",
    )

    paths = write_level_b_artifacts(
        original,
        revised,
        output_dir,
        document_id="doc-revision",
        source_instruction="strengthen issue and rewrite conclusion",
    )

    assert paths.clean_output.name == "opinion_revised_clean_v1.txt"
    assert paths.redline_output.name == "opinion_revised_redline_v1.diff"
    assert paths.change_map == tmp_path / "output" / "change-map.json"
    assert paths.clean_output.read_text(encoding="utf-8") == revised.read_text(encoding="utf-8")
    assert f"--- {original}" in paths.redline_output.read_text(encoding="utf-8")
    assert f"+++ {revised}" in paths.redline_output.read_text(encoding="utf-8")

    change_map = json.loads(paths.change_map.read_text(encoding="utf-8"))
    assert change_map["schemaVersion"] == schemas.SCHEMA_VERSION
    assert change_map["trackingLevel"] == "level-b"
    assert change_map["nativeTrackedChanges"] is False
    assert change_map["documentId"] == "doc-revision"
    assert change_map["cleanOutput"] == str(paths.clean_output)
    assert change_map["redlineOutput"] == str(paths.redline_output)
    assert change_map["changeMap"] == str(paths.change_map)
    assert all(change["sectionId"].startswith("s") for change in change_map["changes"])
    assert any(change["type"] == "modify" for change in change_map["changes"])
    assert any(change["type"] == "insert" for change in change_map["changes"])
    assert change_map["summary"] == _summary_from_changes(change_map["changes"])


def test_level_b_artifacts_do_not_overwrite_existing_outputs(tmp_path: Path) -> None:
    original = tmp_path / "draft.md"
    revised = tmp_path / "draft.md.revised"
    output_dir = tmp_path / "artifacts"
    original.write_text("# Title\n\nold\n", encoding="utf-8")
    revised.write_text("# Title\n\nnew\n", encoding="utf-8")

    first = write_level_b_artifacts(original, revised, output_dir, document_id="doc-1")
    second = write_level_b_artifacts(original, revised, output_dir, document_id="doc-1")

    assert first.clean_output.name == "draft.md_clean_v1.revised"
    assert second.clean_output.name == "draft.md_clean_v2.revised"
    assert first.redline_output.name == "draft.md_redline_v1.diff"
    assert second.redline_output.name == "draft.md_redline_v2.diff"
    assert first.change_map.name == "change-map.json"
    assert second.change_map.name == "change-map.v2.json"
    assert first.change_map != second.change_map
    assert second.change_map.exists()


def test_build_change_map_summary_matches_change_objects() -> None:
    change_map = build_change_map(
        ["1. Background", "A", "B", "3. Removed", "gone"],
        ["1. Background", "A revised", "B", "2. Added", "new"],
        document_id="doc-map",
    )

    assert change_map["trackingLevel"] == "level-b"
    assert change_map["nativeTrackedChanges"] is False
    assert change_map["summary"] == _summary_from_changes(change_map["changes"])
    assert {change["type"] for change in change_map["changes"]} <= {"insert", "delete", "modify"}
    assert all("sourceInstruction" in change for change in change_map["changes"])


def test_level_b_cli_emits_artifact_paths(tmp_path: Path) -> None:
    original = tmp_path / "before.txt"
    revised = tmp_path / "after.txt"
    output_dir = tmp_path / "out"
    original.write_text("1. Issue\nold\n", encoding="utf-8")
    revised.write_text("1. Issue\nnew\n", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.revision.level_b",
            str(original),
            str(revised),
            str(output_dir),
            "--document-id",
            "doc-cli",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert Path(payload["cleanOutput"]).exists()
    assert Path(payload["redlineOutput"]).exists()
    assert Path(payload["changeMap"]).exists()
    assert json.loads(Path(payload["changeMap"]).read_text(encoding="utf-8"))["documentId"] == "doc-cli"


def _summary_from_changes(changes: list[dict[str, str]]) -> dict[str, int]:
    summary = {"added": 0, "deleted": 0, "modified": 0}
    for change in changes:
        if change["type"] == "insert":
            summary["added"] += 1
        elif change["type"] == "delete":
            summary["deleted"] += 1
        else:
            summary["modified"] += 1
    return summary
