"""End-to-end CLI for drafting and revision pipeline slices."""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from tools.artifacts import (
    ArtifactStore,
    Checkpoint,
    ClauseMap,
    MatterManifest,
    Outline,
    PlaceholderRegistry,
    TermRegistry,
    schemas,
)
from tools.artifacts.store import next_available_path
from tools.parsing.docx_parser import block_text, parse_docx
from tools.revision.level_b import write_level_b_artifacts
from tools.validation.runner import run_validation


ROOT = Path(__file__).resolve().parents[2]
DOCX_GENERATOR = ROOT / ".claude/skills/output-formatter/scripts/docx-generator.py"


def run_draft(request_path: Path, *, output_base: Path | None = None) -> dict[str, Any]:
    request = _read_json(request_path)
    store = ArtifactStore(output_base=output_base)
    output_root = _output_root(store)
    artifact_paths: dict[str, str] = {}
    document_id = request.get("documentId") or schemas.new_document_id()

    try:
        manifest = _manifest_from_request(request, document_id=document_id)
        manifest_path = store.write_artifact(manifest)
        artifact_paths["manifest"] = str(manifest_path)

        content = _draft_markdown(request)
        outline = _outline_from_markdown(content, document_id=document_id, fallback_title=request.get("title", "Draft"))
        clause_map = _clause_map_from_outline(outline)
        placeholders = _placeholder_registry(content, document_id=document_id)
        registry = TermRegistry(documentId=document_id, terms=())
        written = store.write_many([outline, clause_map, placeholders, registry])
        artifact_paths.update({key: str(path) for key, path in written.items()})

        draft_path = store.next_document_output_path(_filename(request, suffix="_draft", ext="md"))
        draft_path.write_text(content, encoding="utf-8")
        artifact_paths["draft"] = str(draft_path)
        _write_checkpoint(
            store,
            document_id=document_id,
            step="D3",
            status="completed",
            artifact_paths=artifact_paths,
            last_successful_step="D3",
            next_resume_step="D4",
        )

        report = run_validation(draft_path, manifest_path=manifest_path, placeholder_registry_path=written["placeholder_registry"])
        report_path = store.write_artifact(report)
        artifact_paths["validation_report"] = str(report_path)
        if report["blocking"]:
            return _fail(
                store,
                document_id=document_id,
                command="draft",
                failed_step="D4",
                next_resume_step="D3",
                artifact_paths=artifact_paths,
                message="validation blocked rendering",
                validation_report=report,
            )

        docx_path = store.next_document_output_path(_filename(request, suffix="", ext="docx"))
        _render_docx(
            draft_path,
            docx_path,
            target_language=manifest.targetLanguage,
            jurisdiction=manifest.jurisdiction,
            document_type=manifest.documentType,
        )
        artifact_paths["rendered_output"] = str(docx_path)
        summary = _success(
            store,
            document_id=document_id,
            command="draft",
            completed_step="D6",
            artifact_paths=artifact_paths,
            validation_report=report,
        )
        summary_path = _write_delivery_summary(output_root, summary)
        summary["deliverySummaryPath"] = str(summary_path)
        return summary
    except Exception as exc:
        return _fail(
            store,
            document_id=document_id,
            command="draft",
            failed_step="unknown",
            next_resume_step="D1",
            artifact_paths=artifact_paths,
            message=str(exc),
        )


def run_revise(input_path: Path, instructions_path: Path, *, output_base: Path | None = None) -> dict[str, Any]:
    store = ArtifactStore(output_base=output_base)
    output_root = _output_root(store)
    artifact_paths: dict[str, str] = {}
    document_id = schemas.new_document_id()

    try:
        instructions = instructions_path.read_text(encoding="utf-8")
        original_text = _read_source_document(input_path)
        revised_markdown = _revision_markdown(original_text, instructions, title=input_path.stem)

        manifest = MatterManifest(
            documentId=document_id,
            documentType="general",
            supportLevel="full",
            targetLanguage=_detect_language(revised_markdown),
            jurisdiction="korea" if _detect_language(revised_markdown) == "ko" else "international",
            authorityPacketProvided=True,
            skeletonOnly=False,
            step="R1",
        )
        manifest_path = store.write_artifact(manifest)
        artifact_paths["manifest"] = str(manifest_path)

        original_md = store.next_document_output_path(_slug(input_path.stem) + "_original_v1.md")
        original_md.write_text(original_text, encoding="utf-8")
        revised_md = store.next_document_output_path(_slug(input_path.stem) + "_revised_v1.md")
        revised_md.write_text(revised_markdown, encoding="utf-8")
        artifact_paths["original"] = str(original_md)
        artifact_paths["draft"] = str(revised_md)

        outline = _outline_from_markdown(revised_markdown, document_id=document_id, fallback_title=input_path.stem)
        clause_map = _clause_map_from_outline(outline)
        placeholders = _placeholder_registry(revised_markdown, document_id=document_id)
        registry = TermRegistry(documentId=document_id, terms=())
        written = store.write_many([outline, clause_map, placeholders, registry])
        artifact_paths.update({key: str(path) for key, path in written.items()})

        report = run_validation(revised_md, manifest_path=manifest_path, placeholder_registry_path=written["placeholder_registry"])
        report_path = store.write_artifact(report)
        artifact_paths["validation_report"] = str(report_path)
        if report["blocking"]:
            return _fail(
                store,
                document_id=document_id,
                command="revise",
                failed_step="R5",
                next_resume_step="R4",
                artifact_paths=artifact_paths,
                message="validation blocked rendering",
                validation_report=report,
            )

        docx_path = store.next_document_output_path(_slug(input_path.stem) + "_revised_v1.docx")
        _render_docx(
            revised_md,
            docx_path,
            target_language=manifest.targetLanguage,
            jurisdiction=manifest.jurisdiction,
            document_type=manifest.documentType,
        )
        artifact_paths["rendered_output"] = str(docx_path)
        level_b_paths = write_level_b_artifacts(
            original_md,
            revised_md,
            docx_path.parent,
            document_id=document_id,
            source_instruction=instructions.strip(),
        )
        artifact_paths.update(level_b_paths.to_payload())

        summary = _success(
            store,
            document_id=document_id,
            command="revise",
            completed_step="R7",
            artifact_paths=artifact_paths,
            validation_report=report,
        )
        summary_path = _write_delivery_summary(output_root, summary)
        summary["deliverySummaryPath"] = str(summary_path)
        return summary
    except Exception as exc:
        return _fail(
            store,
            document_id=document_id,
            command="revise",
            failed_step="unknown",
            next_resume_step="R1",
            artifact_paths=artifact_paths,
            message=str(exc),
        )


def _manifest_from_request(request: dict[str, Any], *, document_id: str) -> MatterManifest:
    support_level = request.get("supportLevel", "full")
    authority_provided = bool(request.get("authorityPacketProvided", support_level == "full"))
    skeleton_only = bool(request.get("skeletonOnly", support_level == "conditional" and not authority_provided))
    return MatterManifest(
        documentId=document_id,
        documentType=request.get("documentType", "general"),
        supportLevel=support_level,
        targetLanguage=request.get("targetLanguage", _detect_language(_request_text(request))),
        jurisdiction=request.get("jurisdiction", "korea"),
        governingLaw=request.get("governingLaw", ""),
        parties=tuple(request.get("parties", ())),
        reviewIntensity=request.get("reviewIntensity", "light"),
        outputFormat=request.get("outputFormat", "docx"),
        houseStyle=request.get("houseStyle"),
        authorityPacketProvided=authority_provided,
        skeletonOnly=skeleton_only,
        authorityChunks=tuple(request.get("authorityChunks", ())),
        pageSize=request.get("pageSize", "a4"),
        step="D1",
    )


def _draft_markdown(request: dict[str, Any]) -> str:
    if request.get("content"):
        return str(request["content"]).strip() + "\n"

    title = request.get("title", "Draft")
    lines = [f"# {title}", ""]
    for section in request.get("sections", []):
        heading = section.get("heading") or section.get("title")
        body = section.get("body", "")
        if heading:
            lines.extend([f"## {heading}", ""])
        if body:
            lines.extend([str(body).strip(), ""])
    if len(lines) <= 2:
        lines.extend(["[Drafting Gap: no draft content supplied]", ""])
    return "\n".join(lines).strip() + "\n"


def _revision_markdown(original_text: str, instructions: str, *, title: str) -> str:
    return (
        f"# Revised {title}\n\n"
        f"{original_text.strip()}\n\n"
        "## Revision Instructions Applied\n\n"
        f"{instructions.strip()}\n"
    )


def _outline_from_markdown(content: str, *, document_id: str, fallback_title: str) -> Outline:
    sections: list[dict[str, Any]] = []
    for index, line in enumerate(content.splitlines()):
        match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if not match:
            continue
        section_id = f"s{len(sections) + 1}"
        sections.append(
            {
                "sectionId": section_id,
                "title": match.group(2).strip(),
                "level": min(len(match.group(1)), 6),
                "sourceLine": index + 1,
            }
        )
    if not sections:
        sections.append({"sectionId": "s1", "title": fallback_title, "level": 1, "sourceLine": 1})
    return Outline(documentId=document_id, title=sections[0]["title"], sections=tuple(sections))


def _clause_map_from_outline(outline: Outline) -> ClauseMap:
    clauses = []
    for section in outline.sections:
        clauses.append(
            {
                "sectionId": section["sectionId"],
                "title": section["title"],
                "level": section["level"],
                "sourceLine": section.get("sourceLine"),
                "kind": "heading",
            }
        )
    return ClauseMap(documentId=outline.documentId, clauses=tuple(clauses))


PLACEHOLDER_RE = re.compile(r"\[(?:Citation needed: [^\]]+|Authority needed: [^\]]+|Argument: [^\]]+|Factual basis needed|Counsel conclusion needed: [^\]]+|Counsel certainty needed: [^\]]+|Counsel risk assessment needed: [^\]]+|Convention Note: [^\]]+|Drafting Gap: [^\]]+|Insert [^\]]+|[^\]]+ needed)\]")


def _placeholder_registry(content: str, *, document_id: str) -> PlaceholderRegistry:
    placeholders = []
    for index, match in enumerate(PLACEHOLDER_RE.finditer(content), start=1):
        placeholders.append(
            {
                "id": f"p{index}",
                "type": _placeholder_type(match.group(0)),
                "text": match.group(0),
                "resolved": False,
            }
        )
    return PlaceholderRegistry(documentId=document_id, placeholders=tuple(placeholders))


def _placeholder_type(text: str) -> str:
    if "Citation needed" in text:
        return "citation"
    if "Authority needed" in text:
        return "authority"
    if "Counsel" in text:
        return "counsel"
    return "drafting"


def _read_source_document(input_path: Path) -> str:
    if input_path.suffix.lower() == ".docx":
        parsed = parse_docx(input_path)
        return "\n".join(block_text(block) for block in parsed.profile["blocks"] if block_text(block))
    return input_path.read_text(encoding="utf-8")


def _render_docx(
    input_path: Path,
    output_path: Path,
    *,
    target_language: str,
    jurisdiction: str,
    document_type: str,
) -> None:
    generator = _load_docx_generator()
    with contextlib.redirect_stdout(io.StringIO()):
        generator.generate_docx(
            str(input_path),
            str(output_path),
            lang=target_language,
            jurisdiction="intl" if jurisdiction == "international" else jurisdiction,
            document_type=document_type,
            classification="Confidential - AI-Generated Draft",
        )


def _load_docx_generator():
    spec = importlib.util.spec_from_file_location("pipeline_docx_generator", DOCX_GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load DOCX generator: {DOCX_GENERATOR}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _success(
    store: ArtifactStore,
    *,
    document_id: str,
    command: str,
    completed_step: str,
    artifact_paths: dict[str, str],
    validation_report: dict[str, Any],
) -> dict[str, Any]:
    checkpoint_path = _write_checkpoint(
        store,
        document_id=document_id,
        step=completed_step,
        status="completed",
        artifact_paths=artifact_paths,
        last_successful_step=completed_step,
        next_resume_step=None,
    )
    return {
        "status": "completed",
        "command": command,
        "documentId": document_id,
        "completedStep": completed_step,
        "nextResumeStep": None,
        "artifactPaths": artifact_paths,
        "validation": {
            "status": validation_report["status"],
            "blocking": validation_report["blocking"],
            "summary": validation_report["summary"],
        },
        "checkpointPath": str(checkpoint_path),
    }


def _fail(
    store: ArtifactStore,
    *,
    document_id: str,
    command: str,
    failed_step: str,
    next_resume_step: str,
    artifact_paths: dict[str, str],
    message: str,
    validation_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    checkpoint_path = _write_checkpoint(
        store,
        document_id=document_id,
        step=failed_step,
        status="failed",
        artifact_paths=artifact_paths,
        last_successful_step=_previous_step(failed_step),
        next_resume_step=next_resume_step,
        error=message,
    )
    summary = {
        "status": "failed",
        "command": command,
        "documentId": document_id,
        "failedStep": failed_step,
        "lastSuccessfulStep": _previous_step(failed_step),
        "nextResumeStep": next_resume_step,
        "message": message,
        "artifactPaths": artifact_paths,
        "checkpointPath": str(checkpoint_path),
    }
    if validation_report is not None:
        summary["validation"] = {
            "status": validation_report["status"],
            "blocking": validation_report["blocking"],
            "summary": validation_report["summary"],
        }
    _write_delivery_summary(_output_root(store), summary)
    return summary


def _write_checkpoint(
    store: ArtifactStore,
    *,
    document_id: str,
    step: str,
    status: str,
    artifact_paths: dict[str, str],
    last_successful_step: str | None,
    next_resume_step: str | None,
    error: str | None = None,
) -> Path:
    checkpoint = schemas.artifact_to_payload(
        Checkpoint(documentId=document_id, step=step, status=status, artifactPaths=artifact_paths)
    )
    checkpoint["lastSuccessfulStep"] = last_successful_step
    checkpoint["nextResumeStep"] = next_resume_step
    if error:
        checkpoint["error"] = error
    return store.write_artifact(checkpoint, overwrite=False)


def _write_delivery_summary(output_root: Path, summary: dict[str, Any]) -> Path:
    path = next_available_path(output_root / "delivery-summary.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _output_root(store: ArtifactStore) -> Path:
    return store.output_base if store.output_base is not None else ROOT / "output"


def _filename(request: dict[str, Any], *, suffix: str, ext: str) -> str:
    date = request.get("date", "20260426")
    document_type = request.get("documentType", "general")
    description = _slug(request.get("description") or request.get("title") or "document")
    return f"{date}_{document_type}_{description}{suffix}_v1.{ext}"


def _slug(value: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z가-힣._-]+", "-", str(value).strip().lower()).strip("-")
    return slug or "document"


def _detect_language(text: str) -> str:
    return "ko" if re.search(r"[가-힣]", text) else "en"


def _request_text(request: dict[str, Any]) -> str:
    if request.get("content"):
        return str(request["content"])
    return " ".join(str(section.get("body", "")) for section in request.get("sections", []))


def _previous_step(step: str) -> str | None:
    order = ["D1", "D2", "D3", "D4", "D5", "D6", "R1", "R2", "R3", "R4", "R5", "R6", "R7"]
    if step not in order:
        return None
    index = order.index(step)
    return order[index - 1] if index > 0 else None


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("request JSON must be an object")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tools.pipeline", description="Run drafting or revision pipeline.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    draft = subparsers.add_parser("draft", help="run D1-D6 from a request JSON")
    draft.add_argument("--request", type=Path, required=True)
    draft.add_argument("--output-base", type=Path, help="override output directory")

    revise = subparsers.add_parser("revise", help="run R1-R7 from an input document and instructions")
    revise.add_argument("--input", type=Path, required=True)
    revise.add_argument("--instructions", type=Path, required=True)
    revise.add_argument("--output-base", type=Path, help="override output directory")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "draft":
        summary = run_draft(args.request, output_base=args.output_base)
    else:
        summary = run_revise(args.input, args.instructions, output_base=args.output_base)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if summary["status"] == "failed" else 0
