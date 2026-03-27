#!/usr/bin/env python3
"""
docx-generator.py
Generates .docx files from markdown content with legal document formatting.

Usage:
    python3 docx-generator.py <input.md> <output.docx> [--lang ko|en]
                              [--jurisdiction korea|us|uk|intl]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.shared import Inches, Mm, Pt
except ImportError as exc:
    print(f"Error: python-docx is required: {exc}", file=sys.stderr)
    sys.exit(1)


PAGE_CONFIGS = {
    "ko-korea": {
        "page_width": Mm(210),
        "page_height": Mm(297),
        "margins": {"top": Mm(20), "bottom": Mm(15), "left": Mm(20), "right": Mm(20)},
        "body_font_ascii": "바탕체",
        "body_font_east_asia": "바탕체",
        "heading_font_ascii": "맑은 고딕",
        "heading_font_east_asia": "맑은 고딕",
        "body_size": 12,
        "line_spacing": 1.6,
    },
    "ko-korea-opinion": {
        "page_width": Mm(210),
        "page_height": Mm(297),
        "margins": {"top": Mm(25.4), "bottom": Mm(25.4), "left": Mm(25.4), "right": Mm(25.4)},
        "body_font_ascii": "Times New Roman",
        "body_font_east_asia": "맑은 고딕",
        "heading_font_ascii": "Times New Roman",
        "heading_font_east_asia": "맑은 고딕",
        "body_size": 11,
        "line_spacing": 1.15,
    },
    "en-us": {
        "page_width": Inches(8.5),
        "page_height": Inches(11),
        "margins": {"top": Inches(1), "bottom": Inches(1), "left": Inches(1), "right": Inches(1)},
        "body_font_ascii": "Times New Roman",
        "body_font_east_asia": "Times New Roman",
        "heading_font_ascii": "Times New Roman",
        "heading_font_east_asia": "Times New Roman",
        "body_size": 12,
        "line_spacing": 1.5,
    },
    "en-uk": {
        "page_width": Mm(210),
        "page_height": Mm(297),
        "margins": {"top": Mm(25.4), "bottom": Mm(25.4), "left": Mm(25.4), "right": Mm(25.4)},
        "body_font_ascii": "Times New Roman",
        "body_font_east_asia": "Times New Roman",
        "heading_font_ascii": "Arial",
        "heading_font_east_asia": "Arial",
        "body_size": 12,
        "line_spacing": 1.5,
    },
    "en-intl": {
        "page_width": Mm(210),
        "page_height": Mm(297),
        "margins": {"top": Mm(25), "bottom": Mm(25), "left": Mm(25), "right": Mm(25)},
        "body_font_ascii": "Times New Roman",
        "body_font_east_asia": "Times New Roman",
        "heading_font_ascii": "Arial",
        "heading_font_east_asia": "Arial",
        "body_size": 12,
        "line_spacing": 1.5,
    },
}


def get_config_key(lang: str, jurisdiction: str, document_type: str | None = None) -> str:
    if lang == "ko":
        opinion_types = {
            "advisory",
            "legal-opinion",
            "legal-review-opinion",
            "client-memorandum",
        }
        if document_type in opinion_types:
            return "ko-korea-opinion"
        return "ko-korea"
    if jurisdiction == "us":
        return "en-us"
    if jurisdiction == "uk":
        return "en-uk"
    return "en-intl"


def apply_run_font(
    run,
    ascii_font: str,
    east_asia_font: str,
    size_pt: int,
    *,
    bold: bool = False,
) -> None:
    run.font.name = ascii_font
    run.font.size = Pt(size_pt)
    run.bold = bold
    if run._element.rPr is not None and run._element.rPr.rFonts is not None:
        run._element.rPr.rFonts.set(qn("w:eastAsia"), east_asia_font)
        run._element.rPr.rFonts.set(qn("w:ascii"), ascii_font)
        run._element.rPr.rFonts.set(qn("w:hAnsi"), ascii_font)


def apply_style_font(style, ascii_font: str, east_asia_font: str, size_pt: int) -> None:
    style.font.name = ascii_font
    style.font.size = Pt(size_pt)
    if style._element.rPr is not None and style._element.rPr.rFonts is not None:
        style._element.rPr.rFonts.set(qn("w:eastAsia"), east_asia_font)
        style._element.rPr.rFonts.set(qn("w:ascii"), ascii_font)
        style._element.rPr.rFonts.set(qn("w:hAnsi"), ascii_font)


def configure_document(document: Document, config: dict) -> None:
    section = document.sections[0]
    section.page_width = config["page_width"]
    section.page_height = config["page_height"]
    section.top_margin = config["margins"]["top"]
    section.bottom_margin = config["margins"]["bottom"]
    section.left_margin = config["margins"]["left"]
    section.right_margin = config["margins"]["right"]

    apply_style_font(
        document.styles["Normal"],
        config["body_font_ascii"],
        config["body_font_east_asia"],
        config["body_size"],
    )
    apply_style_font(
        document.styles["Heading 1"],
        config["heading_font_ascii"],
        config["heading_font_east_asia"],
        16,
    )
    apply_style_font(
        document.styles["Heading 2"],
        config["heading_font_ascii"],
        config["heading_font_east_asia"],
        14,
    )
    apply_style_font(
        document.styles["Heading 3"],
        config["heading_font_ascii"],
        config["heading_font_east_asia"],
        12,
    )


def add_paragraph(document: Document, text: str, config: dict, *, heading_level: int | None = None) -> None:
    if heading_level == 1:
        paragraph = document.add_paragraph(style="Heading 1")
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif heading_level == 2:
        paragraph = document.add_paragraph(style="Heading 2")
    elif heading_level == 3:
        paragraph = document.add_paragraph(style="Heading 3")
    else:
        paragraph = document.add_paragraph(style="Normal")
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    run = paragraph.add_run(text)
    if heading_level == 1:
        apply_run_font(
            run,
            config["heading_font_ascii"],
            config["heading_font_east_asia"],
            16,
            bold=True,
        )
    elif heading_level == 2:
        apply_run_font(
            run,
            config["heading_font_ascii"],
            config["heading_font_east_asia"],
            14,
            bold=True,
        )
    elif heading_level == 3:
        apply_run_font(
            run,
            config["heading_font_ascii"],
            config["heading_font_east_asia"],
            12,
            bold=True,
        )
    else:
        apply_run_font(
            run,
            config["body_font_ascii"],
            config["body_font_east_asia"],
            config["body_size"],
        )

    fmt = paragraph.paragraph_format
    fmt.line_spacing = config["line_spacing"]
    if heading_level == 1:
        fmt.space_after = Pt(10)
    elif heading_level == 2:
        fmt.space_before = Pt(10)
        fmt.space_after = Pt(6)
    elif heading_level == 3:
        fmt.space_before = Pt(8)
        fmt.space_after = Pt(4)
    else:
        fmt.space_after = Pt(6)


def generate_docx(
    input_path: str,
    output_path: str,
    lang: str,
    jurisdiction: str,
    document_type: str | None = None,
) -> None:
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    config = PAGE_CONFIGS[get_config_key(lang, jurisdiction, document_type)]
    content = input_file.read_text(encoding="utf-8")

    document = Document()
    configure_document(document, config)

    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
          document.add_paragraph("")
          continue
        if line.startswith("# "):
            add_paragraph(document, line[2:].strip(), config, heading_level=1)
        elif line.startswith("## "):
            add_paragraph(document, line[3:].strip(), config, heading_level=2)
        elif line.startswith("### "):
            add_paragraph(document, line[4:].strip(), config, heading_level=3)
        else:
            add_paragraph(document, line, config)

    document.save(str(output_file))
    print(f"Document generated: {output_file}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a DOCX file from markdown using legal-document defaults."
    )
    parser.add_argument("input", help="Path to the input markdown file")
    parser.add_argument("output", help="Path to the output DOCX file")
    parser.add_argument("--lang", choices=["ko", "en"], default="ko")
    parser.add_argument(
        "--jurisdiction",
        choices=["korea", "us", "uk", "intl"],
        default="korea",
    )
    parser.add_argument(
        "--document-type",
        default=None,
        help="Optional document type hint (e.g. advisory, litigation, corporate)",
    )
    args = parser.parse_args()

    try:
        generate_docx(
            args.input,
            args.output,
            args.lang,
            args.jurisdiction,
            args.document_type,
        )
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error generating document: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
