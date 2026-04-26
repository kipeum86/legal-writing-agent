"""Helpers for deterministic DOCX rendering assertions.

DOCX files are zip archives containing XML parts. Direct binary comparisons are
not stable because Word-processing tools can add run IDs, timestamps, and other
dynamic metadata. These helpers compare the document structure that matters for
the current renderer baseline.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree


WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

_DYNAMIC_ATTRS = (
    "rsid",
    "paraId",
    "textId",
    "durableId",
    "docId",
)


def read_docx_part(docx_path: Path, part_name: str) -> str:
    """Read a raw XML part from a DOCX archive."""
    with zipfile.ZipFile(docx_path) as archive:
        return archive.read(part_name).decode("utf-8")


def normalize_docx_xml(xml: str) -> str:
    """Remove unstable XML attributes and whitespace noise from a DOCX XML part."""
    normalized = xml
    for attr in _DYNAMIC_ATTRS:
        normalized = re.sub(rf'\s[\w:]*{attr}[\w]*="[^"]*"', "", normalized)
    normalized = re.sub(r">\s+<", "><", normalized)
    return normalized.strip()


def normalized_docx_part(docx_path: Path, part_name: str = "word/document.xml") -> str:
    """Return a normalized XML part from a DOCX archive."""
    return normalize_docx_xml(read_docx_part(docx_path, part_name))


def docx_paragraph_texts(docx_path: Path, *, include_empty: bool = False) -> list[str]:
    """Extract paragraph texts from ``word/document.xml`` in document order."""
    root = ElementTree.fromstring(read_docx_part(docx_path, "word/document.xml"))
    paragraphs: list[str] = []
    for paragraph in root.findall(".//w:p", WORD_NS):
        texts = [node.text or "" for node in paragraph.findall(".//w:t", WORD_NS)]
        value = "".join(texts)
        if include_empty or value:
            paragraphs.append(value)
    return paragraphs


def docx_table_count(docx_path: Path) -> int:
    """Count real DOCX table elements in ``word/document.xml``."""
    root = ElementTree.fromstring(read_docx_part(docx_path, "word/document.xml"))
    return len(root.findall(".//w:tbl", WORD_NS))


def docx_table_texts(docx_path: Path) -> list[list[list[str]]]:
    """Extract all DOCX tables as table -> row -> cell text."""
    root = ElementTree.fromstring(read_docx_part(docx_path, "word/document.xml"))
    tables: list[list[list[str]]] = []
    for table in root.findall(".//w:tbl", WORD_NS):
        rows: list[list[str]] = []
        for row in table.findall("./w:tr", WORD_NS):
            cells: list[str] = []
            for cell in row.findall("./w:tc", WORD_NS):
                texts = [node.text or "" for node in cell.findall(".//w:t", WORD_NS)]
                cells.append("".join(texts))
            rows.append(cells)
        tables.append(rows)
    return tables


def docx_paragraph_styles(docx_path: Path) -> list[tuple[str, str | None]]:
    """Return paragraph text with its style id in document order."""
    root = ElementTree.fromstring(read_docx_part(docx_path, "word/document.xml"))
    values: list[tuple[str, str | None]] = []
    for paragraph in root.findall(".//w:p", WORD_NS):
        texts = [node.text or "" for node in paragraph.findall(".//w:t", WORD_NS)]
        style = paragraph.find("./w:pPr/w:pStyle", WORD_NS)
        style_id = style.attrib.get(f"{{{WORD_NS['w']}}}val") if style is not None else None
        values.append(("".join(texts), style_id))
    return values


def docx_run_flags(docx_path: Path) -> list[tuple[str, bool, bool]]:
    """Return run text with bold/italic flags in document order."""
    root = ElementTree.fromstring(read_docx_part(docx_path, "word/document.xml"))
    values: list[tuple[str, bool, bool]] = []
    for run in root.findall(".//w:r", WORD_NS):
        texts = [node.text or "" for node in run.findall("./w:t", WORD_NS)]
        if not texts:
            continue
        rpr = run.find("./w:rPr", WORD_NS)
        bold = rpr is not None and _flag_enabled(rpr.find("./w:b", WORD_NS))
        italic = rpr is not None and _flag_enabled(rpr.find("./w:i", WORD_NS))
        values.append(("".join(texts), bold, italic))
    return values


def _flag_enabled(element: ElementTree.Element | None) -> bool:
    if element is None:
        return False
    value = element.attrib.get(f"{{{WORD_NS['w']}}}val")
    return value not in {"0", "false", "False"}
