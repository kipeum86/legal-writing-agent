from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from tests.rendering.normalize import (
    docx_paragraph_texts,
    docx_paragraph_styles,
    docx_run_flags,
    docx_table_count,
    docx_table_texts,
    normalized_docx_part,
    read_docx_part,
)


REPO = Path(__file__).resolve().parents[2]
DOCX_GENERATOR = REPO / ".claude/skills/output-formatter/scripts/docx-generator.py"
TABLE_FIXTURE = REPO / "tests/fixtures/public/table_heavy_document"


def _load_docx_generator():
    spec = importlib.util.spec_from_file_location("docx_generator", DOCX_GENERATOR)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_renderer_preserves_markdown_structures_as_docx_objects(tmp_path: Path) -> None:
    generator = _load_docx_generator()
    output_path = tmp_path / "table-heavy.docx"

    generator.generate_docx(
        str(TABLE_FIXTURE / "input.md"),
        str(output_path),
        lang="ko",
        jurisdiction="korea",
        document_type="general",
    )

    paragraphs = docx_paragraph_texts(output_path)
    assert "표 렌더링 기준선" in paragraphs
    assert "1. 구조 보존 확인" in paragraphs
    assert "이 문장은 향후 blockquote 스타일로 렌더링되어야 한다." in paragraphs
    assert "첫 번째 항목" in paragraphs
    assert "번호 항목" in paragraphs
    assert "굵게 및 기울임 표시는 현재 plain text로 남는다." in paragraphs

    assert docx_table_count(output_path) == 1
    assert docx_table_texts(output_path)[0] == [
        ["항목", "현재 값", "목표 값"],
        ["표", "plain paragraph", "DOCX table"],
        ["인용", "plain paragraph", "indented blockquote"],
        ["목록", "plain paragraph", "numbered/bulleted list"],
    ]

    styles = docx_paragraph_styles(output_path)
    assert ("이 문장은 향후 blockquote 스타일로 렌더링되어야 한다.", "LegalBlockQuote") in styles
    assert ("첫 번째 항목", "ListBullet") in styles
    assert ("번호 항목", "ListNumber") in styles

    runs = docx_run_flags(output_path)
    assert ("굵게", True, False) in runs
    assert ("기울임", False, True) in runs

    normalized_xml = normalized_docx_part(output_path)
    assert "rsid" not in normalized_xml


def test_renderer_outputs_footnote_candidates_header_and_page_footer(tmp_path: Path) -> None:
    generator = _load_docx_generator()
    input_path = tmp_path / "footnote.md"
    output_path = tmp_path / "footnote.docx"
    input_path.write_text(
        "# Memorandum\n\n"
        "The supplied sentence includes a footnote candidate.[^1]\n\n"
        "[^1]: This is preserved as a footnote candidate.\n",
        encoding="utf-8",
    )

    generator.generate_docx(
        str(input_path),
        str(output_path),
        lang="en",
        jurisdiction="us",
        document_type="advisory",
        classification="Confidential - AI-Generated Draft",
    )

    paragraphs = docx_paragraph_texts(output_path)
    assert "The supplied sentence includes a footnote candidate.[^1]" in paragraphs
    assert "1. This is preserved as a footnote candidate." in paragraphs
    assert ("1. This is preserved as a footnote candidate.", "LegalFootnoteCandidate") in docx_paragraph_styles(output_path)

    header_xml = read_docx_part(output_path, "word/header1.xml")
    footer_xml = read_docx_part(output_path, "word/footer1.xml")
    assert "Confidential - AI-Generated Draft" in header_xml
    assert "PAGE" in footer_xml
