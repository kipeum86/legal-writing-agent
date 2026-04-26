"""DOCX structure extractor for revision intake.

The parser preserves document order across paragraphs and tables, extracts a
minimal heading tree, records numbering candidates, and seeds the Phase 2
`Outline` and `ClauseMap` artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from tools.artifacts import schemas

try:
    from docx import Document
    from docx.document import Document as DocxDocument
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    from docx.table import Table
    from docx.text.paragraph import Paragraph
except ImportError as exc:  # pragma: no cover - exercised only when dependency is absent
    print(f"Error: python-docx is required: {exc}", file=sys.stderr)
    raise


PARSER_VERSION = "tools.parsing.docx_parser.v1"


@dataclass(frozen=True)
class DocxParseResult:
    profile: dict[str, Any]
    outline: schemas.Outline
    clause_map: schemas.ClauseMap

    def to_payload(self) -> dict[str, Any]:
        return {
            "profile": self.profile,
            "outline": schemas.artifact_to_payload(self.outline),
            "clauseMap": schemas.artifact_to_payload(self.clause_map),
        }


def parse_docx(path: str | Path, *, document_id: str | None = None) -> DocxParseResult:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"DOCX file not found: {source}")

    resolved_document_id = document_id or schemas.new_document_id()
    file_sha = _sha256_bytes(source.read_bytes())
    document = Document(str(source))
    blocks = extract_blocks(document)
    heading_tree = build_heading_tree(blocks)
    extracted_text = "\n".join(block_text(block) for block in blocks if block_text(block))
    extracted_text_sha = _sha256_text(extracted_text)

    profile = {
        "schemaVersion": schemas.SCHEMA_VERSION,
        "parserVersion": PARSER_VERSION,
        "documentId": resolved_document_id,
        "sourcePath": str(source),
        "sourceSha256": file_sha,
        "extractedTextSha256": extracted_text_sha,
        "blockCount": len(blocks),
        "blocks": blocks,
        "headingTree": heading_tree,
    }
    provenance = (
        schemas.SourceProvenance(
            sourceType="input",
            path=str(source),
            sha256=file_sha,
            trusted=False,
        ),
    )
    outline = build_outline(profile, source_provenance=provenance)
    clause_map = build_clause_map(profile, source_provenance=provenance)
    return DocxParseResult(profile=profile, outline=outline, clause_map=clause_map)


def extract_blocks(document: DocxDocument) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for index, item in enumerate(iter_block_items(document)):
        if isinstance(item, Paragraph):
            block = paragraph_block(item, index)
        else:
            block = table_block(item, index)
        blocks.append(block)
    return blocks


def iter_block_items(document: DocxDocument) -> Iterable[Paragraph | Table]:
    for child in document.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)


def paragraph_block(paragraph: Paragraph, index: int) -> dict[str, Any]:
    text = paragraph.text.strip()
    style_name = paragraph.style.name if paragraph.style is not None else ""
    style_id = paragraph.style.style_id if paragraph.style is not None else ""
    heading_level = infer_heading_level(text, style_name)
    numbering = infer_numbering(paragraph, text, style_name)

    return {
        "id": f"b{index + 1}",
        "type": "paragraph",
        "blockIndex": index,
        "text": text,
        "textHash": _sha256_text(text),
        "styleName": style_name,
        "styleId": style_id,
        "headingLevel": heading_level,
        "numberingCandidate": numbering,
    }


def table_block(table: Table, index: int) -> dict[str, Any]:
    rows: list[list[str]] = []
    for row in table.rows:
        rows.append([_cell_text(cell) for cell in row.cells])
    flat_text = "\n".join("\t".join(row) for row in rows)
    return {
        "id": f"b{index + 1}",
        "type": "table",
        "blockIndex": index,
        "rows": rows,
        "text": flat_text,
        "textHash": _sha256_text(flat_text),
        "rowCount": len(rows),
        "columnCount": max((len(row) for row in rows), default=0),
    }


def _cell_text(cell) -> str:
    return "\n".join(paragraph.text.strip() for paragraph in cell.paragraphs if paragraph.text.strip())


def infer_heading_level(text: str, style_name: str) -> int | None:
    style = style_name.strip().lower()
    match = re.search(r"(?:heading|제목)\s*(\d+)", style)
    if match:
        return min(int(match.group(1)), 6)

    if not text:
        return None
    if re.match(r"^제\s*\d+\s*[편장]\b", text):
        return 1
    if re.match(r"^제\s*\d+\s*[절관]\b", text):
        return 2
    if re.match(r"^제\s*\d+\s*조(?:의\s*\d+)?(?:\s*\([^)]+\))?\s*$", text):
        return 3
    if re.match(r"^[IVXLC]+\.\s+\S", text) and len(text) <= 120:
        return 1
    if re.match(r"^\d+(?:\.\d+)*[.)]\s+\S", text) and len(text) <= 120 and "list" not in style:
        return 2
    return None


def infer_numbering(paragraph: Paragraph, text: str, style_name: str) -> dict[str, Any] | None:
    style = style_name.strip().lower()
    has_num_pr = paragraph._p.pPr is not None and paragraph._p.pPr.numPr is not None

    candidates: list[tuple[str, re.Pattern[str]]] = [
        ("korean_article", re.compile(r"^제\s*\d+\s*조(?:의\s*\d+)?")),
        ("korean_chapter", re.compile(r"^제\s*\d+\s*[편장절관]\b")),
        ("decimal", re.compile(r"^\d+(?:\.\d+)*[.)]\s+")),
        ("parenthetical", re.compile(r"^\([0-9A-Za-z가-힣]+\)\s+")),
        ("bullet", re.compile(r"^[\-*+•·]\s+")),
        ("roman", re.compile(r"^[IVXLC]+\.\s+")),
    ]
    pattern_kind = None
    for kind, pattern in candidates:
        if pattern.match(text):
            pattern_kind = kind
            break

    if not has_num_pr and pattern_kind is None and "list" not in style:
        return None

    return {
        "hasNumberingProperties": has_num_pr,
        "styleName": style_name,
        "pattern": pattern_kind,
        "isListStyle": "list" in style,
    }


def build_heading_tree(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    stack: list[dict[str, Any]] = []
    for block in blocks:
        level = block.get("headingLevel")
        if not level:
            continue
        while stack and stack[-1]["level"] >= level:
            stack.pop()
        section_id = f"s{len(headings) + 1}"
        parent_id = stack[-1]["sectionId"] if stack else None
        node = {
            "sectionId": section_id,
            "title": block.get("text", ""),
            "level": level,
            "blockId": block["id"],
            "blockIndex": block["blockIndex"],
            "parentId": parent_id,
        }
        headings.append(node)
        stack.append(node)
    return headings


def build_outline(
    profile: dict[str, Any],
    *,
    source_provenance: tuple[schemas.SourceProvenance, ...] = (),
) -> schemas.Outline:
    sections = tuple(
        {
            "sectionId": node["sectionId"],
            "title": node["title"],
            "level": node["level"],
            "parentId": node["parentId"],
            "sourceBlockId": node["blockId"],
            "sourceBlockIndex": node["blockIndex"],
        }
        for node in profile["headingTree"]
    )
    title = sections[0]["title"] if sections else Path(profile["sourcePath"]).stem
    return schemas.Outline(
        documentId=profile["documentId"],
        title=title,
        sections=sections,
        sourceProvenance=source_provenance,
    )


def build_clause_map(
    profile: dict[str, Any],
    *,
    source_provenance: tuple[schemas.SourceProvenance, ...] = (),
) -> schemas.ClauseMap:
    blocks = profile["blocks"]
    headings = profile["headingTree"]
    if not headings:
        text_hash = _range_hash(blocks, 0, len(blocks) - 1)
        clauses = (
            {
                "sectionId": "s1",
                "title": Path(profile["sourcePath"]).stem,
                "level": 1,
                "startBlockIndex": 0,
                "endBlockIndex": max(len(blocks) - 1, 0),
                "sourceTextHash": text_hash,
                "kind": "document",
            },
        )
        return schemas.ClauseMap(
            documentId=profile["documentId"],
            clauses=clauses,
            sourceProvenance=source_provenance,
        )

    clauses: list[dict[str, Any]] = []
    for index, node in enumerate(headings):
        start = node["blockIndex"]
        end = len(blocks) - 1
        for later in headings[index + 1 :]:
            if later["level"] <= node["level"]:
                end = later["blockIndex"] - 1
                break
        clauses.append(
            {
                "sectionId": node["sectionId"],
                "title": node["title"],
                "level": node["level"],
                "parentId": node["parentId"],
                "startBlockIndex": start,
                "endBlockIndex": end,
                "sourceTextHash": _range_hash(blocks, start, end),
                "kind": "heading",
            }
        )
    return schemas.ClauseMap(
        documentId=profile["documentId"],
        clauses=tuple(clauses),
        sourceProvenance=source_provenance,
    )


def block_text(block: dict[str, Any]) -> str:
    if block["type"] == "table":
        return block.get("text", "")
    return block.get("text", "")


def _range_hash(blocks: list[dict[str, Any]], start: int, end: int) -> str:
    if not blocks:
        return _sha256_text("")
    bounded_start = max(start, 0)
    bounded_end = min(end, len(blocks) - 1)
    text = "\n".join(block_text(blocks[index]) for index in range(bounded_start, bounded_end + 1))
    return _sha256_text(text)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tools.parsing.docx_parser",
        description="Extract a structured profile, outline, and clause-map seed from a DOCX file.",
    )
    parser.add_argument("docx", type=Path, help="DOCX file to parse")
    parser.add_argument("--document-id", help="existing documentId to attach to artifacts")
    parser.add_argument("--out", type=Path, help="write combined parser payload JSON")
    parser.add_argument("--profile-out", type=Path, help="write only document profile JSON")
    parser.add_argument("--outline-out", type=Path, help="write outline artifact JSON")
    parser.add_argument("--clause-map-out", type=Path, help="write clause-map artifact JSON")
    return parser


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = parse_docx(args.docx, document_id=args.document_id)
    payload = result.to_payload()

    if args.out:
        _write_json(args.out, payload)
    if args.profile_out:
        _write_json(args.profile_out, result.profile)
    if args.outline_out:
        _write_json(args.outline_out, schemas.artifact_to_payload(result.outline))
    if args.clause_map_out:
        _write_json(args.clause_map_out, schemas.artifact_to_payload(result.clause_map))

    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
