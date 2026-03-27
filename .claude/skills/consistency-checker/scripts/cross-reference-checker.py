#!/usr/bin/env python3
"""
cross-reference-checker.py
Validates internal cross-references in legal documents.

Usage: python cross-reference-checker.py <file.md>
Output: JSON report of cross-reference issues to stdout.
"""

import json
import re
import sys
from pathlib import Path


CIRCLED_NUMS = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳'
MOK_CHARS = '가나다라마바사아자차카타파하'


def _line_of(text: str, pos: int) -> int:
    """Return a 1-based line number for a character offset."""
    return text[:pos].count('\n') + 1


def _normalize_space(value: str) -> str:
    return re.sub(r'\s+', ' ', value).strip()


def _normalize_korean_reference(value: str) -> str:
    """Normalize Korean cross-reference text to a stable token sequence."""
    parts = re.findall(
        r'제\d+조(?:의\d+)?|제\d+항|제\d+호|[가나다라마바사아자차카타파하]목',
        value,
    )
    if parts:
        return ' '.join(parts)
    return _normalize_space(value)


def _error_report(filepath: str, message: str) -> dict:
    return {
        "file": filepath,
        "language": "unknown",
        "sectionsFound": 0,
        "referencesFound": 0,
        "issueCount": 0,
        "issues": [],
        "status": "error",
        "error": message,
    }


def _load_text_file(filepath: str) -> tuple[str, str]:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    return path.read_text(encoding='utf-8'), str(path)


def extract_sections_korean(text: str) -> set[str]:
    """Extract defined section identifiers from Korean document text."""
    sections: set[str] = set()
    current_article: str | None = None
    current_paragraph: str | None = None
    current_item: str | None = None

    article_re = re.compile(r'제\d+조(?:의\d+)?')
    explicit_paragraph_re = re.compile(r'제(\d+)항')
    explicit_item_re = re.compile(r'제(\d+)호')
    numbered_item_re = re.compile(r'^(\d+)\.\s')
    mok_re = re.compile(r'^([가나다라마바사아자차카타파하])\.\s')

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        article_match = article_re.match(line)
        if article_match:
            current_article = _normalize_korean_reference(article_match.group(0))
            current_paragraph = None
            current_item = None
            sections.add(current_article)

        paragraph_match = explicit_paragraph_re.search(line)
        if paragraph_match:
            current_paragraph = f"제{paragraph_match.group(1)}항"
            sections.add(current_paragraph)
            if current_article:
                sections.add(f"{current_article} {current_paragraph}")
        else:
            for char in line:
                if char in CIRCLED_NUMS:
                    current_paragraph = f"제{CIRCLED_NUMS.index(char) + 1}항"
                    sections.add(current_paragraph)
                    if current_article:
                        sections.add(f"{current_article} {current_paragraph}")
                    break

        explicit_item_match = explicit_item_re.search(line)
        numbered_item_match = numbered_item_re.match(line)
        if explicit_item_match:
            current_item = f"제{explicit_item_match.group(1)}호"
        elif numbered_item_match and (current_article or current_paragraph):
            current_item = f"제{numbered_item_match.group(1)}호"
        else:
            current_item = current_item if line.startswith(tuple(MOK_CHARS)) else None

        if current_item:
            sections.add(current_item)
            if current_article and current_paragraph:
                sections.add(f"{current_article} {current_paragraph} {current_item}")
            elif current_article:
                sections.add(f"{current_article} {current_item}")

        mok_match = mok_re.match(line)
        if mok_match:
            mok = f"{mok_match.group(1)}목"
            sections.add(mok)
            if current_article and current_paragraph and current_item:
                sections.add(f"{current_article} {current_paragraph} {current_item} {mok}")

    return sections


def extract_sections_english(text: str) -> set[str]:
    """Extract defined section identifiers from English document."""
    sections = set()

    for m in re.finditer(r'ARTICLE\s+([IVXLC]+)', text, re.IGNORECASE):
        sections.add(f"ARTICLE {m.group(1).upper()}")

    for m in re.finditer(r'Section\s+(\d+(?:\.\d+)*)', text, re.IGNORECASE):
        sections.add(f"Section {m.group(1)}")

    for m in re.finditer(r'Clause\s+(\d+(?:\.\d+)*)', text, re.IGNORECASE):
        sections.add(f"Clause {m.group(1)}")

    return sections


def find_references_korean(text: str) -> list[dict]:
    """Find Korean internal cross-references, including compound article/paragraph/item forms."""
    refs = []
    article = r'제\d+조(?:의\d+)?'
    paragraph = r'제\d+항'
    item = r'제\d+호'
    mok = r'[가나다라마바사아자차카타파하]목'
    compound = rf'{article}(?:\s*{paragraph})?(?:\s*{item})?(?:\s*{mok})?'

    patterns = [
        (rf'(?:위|상기|전술한|같은\s*법|같은\s*조|동조)\s*({compound})', 'cross-ref'),
        (rf'(?:본\s*조|이\s*조)\s*({paragraph}(?:\s*{item})?(?:\s*{mok})?)', 'internal-ref'),
        (rf'(?:본\s*항|이\s*항)\s*({item}(?:\s*{mok})?)', 'internal-ref'),
        (rf'(?:본\s*호|이\s*호)\s*({mok})', 'internal-ref'),
    ]

    for pattern, ref_type in patterns:
        for match in re.finditer(pattern, text):
            refs.append({
                "reference": _normalize_korean_reference(match.group(1)),
                "type": ref_type,
                "position": match.start(),
                "line": _line_of(text, match.start()),
            })

    return refs


def find_references_english(text: str) -> list[dict]:
    """Find internal references in English documents."""
    refs = []
    patterns = [
        (r'(?:see|See|pursuant to|under|per)\s+(Section\s+\d+(?:\.\d+)?)', 'cross-ref'),
        (r'(?:see|See)\s+(ARTICLE\s+[IVXLC]+)', 'cross-ref'),
        (r'(?:above|supra|herein)\s+(?:in\s+)?(Section\s+\d+(?:\.\d+)?)', 'cross-ref'),
        (r'(?:above|supra|herein)\s+(?:in\s+)?(Clause\s+\d+(?:\.\d+)?)', 'cross-ref'),
    ]
    for pattern, ref_type in patterns:
        for match in re.finditer(pattern, text):
            refs.append({
                "reference": _normalize_space(match.group(1)),
                "type": ref_type,
                "position": match.start(),
                "line": _line_of(text, match.start()),
            })
    return refs


def detect_language(text: str) -> str:
    """Detect whether document is primarily Korean or English."""
    korean_chars = len(re.findall(r'[가-힣]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    return "korean" if korean_chars > english_chars else "english"


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "error": "Usage: python cross-reference-checker.py <file.md>",
        }, indent=2, ensure_ascii=False))
        sys.exit(2)

    filepath = sys.argv[1]

    try:
        text, normalized_path = _load_text_file(filepath)
    except FileNotFoundError as exc:
        print(json.dumps(_error_report(filepath, str(exc)), indent=2, ensure_ascii=False))
        sys.exit(2)
    except UnicodeDecodeError:
        print(json.dumps(
            _error_report(filepath, f"Unable to decode file as UTF-8: {filepath}"),
            indent=2,
            ensure_ascii=False,
        ))
        sys.exit(2)
    except OSError as exc:
        print(json.dumps(_error_report(filepath, f"Unable to read file: {exc}"), indent=2, ensure_ascii=False))
        sys.exit(2)
    except Exception as exc:
        print(json.dumps(_error_report(filepath, f"Unexpected error: {exc}"), indent=2, ensure_ascii=False))
        sys.exit(2)

    language = detect_language(text)

    if language == "korean":
        sections = extract_sections_korean(text)
        references = find_references_korean(text)
    else:
        sections = extract_sections_english(text)
        references = find_references_english(text)

    issues = []
    for ref in references:
        ref_target = ref["reference"]
        if ref_target not in sections:
            issues.append({
                "type": "broken_reference",
                "reference": ref_target,
                "position": ref["position"],
                "line": ref["line"],
                "severity": "major",
                "message": f"Reference to '{ref_target}' but no matching section found",
            })

    report = {
        "file": normalized_path,
        "language": language,
        "sectionsFound": len(sections),
        "referencesFound": len(references),
        "issueCount": len(issues),
        "issues": issues,
        "status": "pass" if len(issues) == 0 else "fail",
    }

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
