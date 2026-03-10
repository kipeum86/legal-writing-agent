#!/usr/bin/env python3
"""
citation-format-checker.py
Validates legal citation formats for Korean, US (Bluebook), and UK (OSCOLA) conventions.

Usage: python citation-format-checker.py <file.md> [--jurisdiction korea|us|uk|intl]
Output: JSON report of citation issues to stdout.
"""

import re
import sys
import json
import argparse
from typing import Optional


# ---------------------------------------------------------------------------
# Korean citation validation
# ---------------------------------------------------------------------------

# Korean statute: 「법률명」 제N조
_KR_STATUTE_CORRECT = re.compile(r'「([^」]+)」\s*제(\d+)조')
# Incorrect: bare name + 제N조 without 「」
_KR_STATUTE_BARE = re.compile(r'(?<!「)([가-힣]{2,}(?:법|령|규칙|조례))\s+제(\d+)조')

# Korean court case citation
# 대법원 2023. 5. 18. 선고 2022다12345 판결
_KR_COURT_NAMES = r'(?:대법원|고등법원|지방법원|헌법재판소|특허법원|가정법원|행정법원)'
_KR_CASE_FULL = re.compile(
    rf'({_KR_COURT_NAMES})\s+'
    r'(\d{{4}})\.\s*(\d{{1,2}})\.\s*(\d{{1,2}})\.\s*'
    r'선고\s+'
    r'(\d{{4}}[가-힣]{{1,2}}\d+)\s+'
    r'(판결|결정|명령)'
)
# Loose match to find malformed case citations
_KR_CASE_LOOSE = re.compile(
    rf'({_KR_COURT_NAMES})\s+(\d{{4}}[\.\s\d]*선고.+?(?:판결|결정|명령))'
)

# Constitutional Court specific pattern
_KR_CONST_COURT = re.compile(
    r'헌법재판소\s+'
    r'(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.\s*'
    r'선고\s+'
    r'(\d{4}헌[가나다라마바사아자차카타파하]{1,2}\d+)\s+'
    r'(결정)'
)

# Valid Constitutional Court case type prefixes
_KR_CONST_TYPES = {'헌가', '헌나', '헌바', '헌사', '헌아', '헌마', '헌라'}

# Disposition types appropriate for each court
_KR_DISPOSITION_MAP = {
    '대법원': {'판결', '결정', '명령'},
    '고등법원': {'판결', '결정', '명령'},
    '지방법원': {'판결', '결정', '명령'},
    '헌법재판소': {'결정'},
    '특허법원': {'판결', '결정'},
    '가정법원': {'판결', '결정', '명령'},
    '행정법원': {'판결', '결정'},
}


def _validate_korean_citations(text: str, lines: list[str]) -> tuple[list[dict], list[dict]]:
    """Return (citations_found, issues)."""
    citations: list[dict] = []
    issues: list[dict] = []

    # --- Statute citations ---
    for m in _KR_STATUTE_CORRECT.finditer(text):
        line_no = text[:m.start()].count('\n') + 1
        citations.append({
            "type": "statute",
            "text": m.group(0),
            "line": line_no,
            "valid": True,
        })

    for m in _KR_STATUTE_BARE.finditer(text):
        # Make sure this is not inside 「」 already
        before = text[max(0, m.start() - 5):m.start()]
        if '「' in before:
            continue
        line_no = text[:m.start()].count('\n') + 1
        name = m.group(1)
        article = m.group(2)
        citations.append({
            "type": "statute",
            "text": m.group(0),
            "line": line_no,
            "valid": False,
        })
        issues.append({
            "type": "format_error",
            "subtype": "missing_brackets",
            "line": line_no,
            "found": m.group(0),
            "suggestion": f"「{name}」 제{article}조",
            "message": f"법률명에 「」 괄호가 빠져 있습니다: '{m.group(0)}' -> '「{name}」 제{article}조'",
            "severity": "major",
        })

    # --- Case citations ---
    for m in _KR_CASE_FULL.finditer(text):
        line_no = text[:m.start()].count('\n') + 1
        court = m.group(1)
        disposition = m.group(6)
        citation_text = m.group(0)
        valid = True
        citations.append({
            "type": "case",
            "text": citation_text,
            "line": line_no,
            "court": court,
            "valid": True,
        })

        # Check disposition appropriateness
        allowed = _KR_DISPOSITION_MAP.get(court, {'판결', '결정', '명령'})
        if disposition not in allowed:
            valid = False
            issues.append({
                "type": "format_error",
                "subtype": "wrong_disposition",
                "line": line_no,
                "found": citation_text,
                "message": f"'{court}'에 '{disposition}'은(는) 부적절합니다. 허용: {', '.join(sorted(allowed))}",
                "severity": "major",
            })
            citations[-1]["valid"] = False

    # Check for Constitutional Court case type validity
    for m in _KR_CONST_COURT.finditer(text):
        line_no = text[:m.start()].count('\n') + 1
        case_num = m.group(4)
        case_type_match = re.search(r'헌[가-힣]{1,2}', case_num)
        if case_type_match:
            case_type = case_type_match.group(0)
            if case_type not in _KR_CONST_TYPES:
                issues.append({
                    "type": "format_error",
                    "subtype": "invalid_const_case_type",
                    "line": line_no,
                    "found": case_num,
                    "message": f"헌법재판소 사건 유형 '{case_type}'이(가) 올바르지 않습니다. "
                               f"유효한 유형: {', '.join(sorted(_KR_CONST_TYPES))}",
                    "severity": "critical",
                })

    # Detect loosely matched but not fully matched case citations
    full_starts = {m.start() for m in _KR_CASE_FULL.finditer(text)}
    for m in _KR_CASE_LOOSE.finditer(text):
        if m.start() not in full_starts:
            line_no = text[:m.start()].count('\n') + 1
            citations.append({
                "type": "case",
                "text": m.group(0).strip(),
                "line": line_no,
                "valid": False,
            })
            issues.append({
                "type": "format_error",
                "subtype": "malformed_case_citation",
                "line": line_no,
                "found": m.group(0).strip(),
                "message": "판례 인용 형식이 올바르지 않습니다. "
                           "올바른 형식: '법원명 YYYY. MM. DD. 선고 사건번호 판결/결정'",
                "severity": "critical",
            })

    return citations, issues


# ---------------------------------------------------------------------------
# US English citation validation (Bluebook)
# ---------------------------------------------------------------------------

# Case: Party v. Party, Vol Reporter Page (Court Year)
_US_CASE = re.compile(
    r'([A-Z][A-Za-z\'\.\s]+?)\s+v\.\s+([A-Z][A-Za-z\'\.\s]+?),\s+'
    r'(\d+)\s+([A-Z][A-Za-z\.\s]{1,20}?)\s+(\d+)'
    r'(?:\s*\(([^)]+)\s+(\d{4})\))?'
)

# Case name italic/underline markers (markdown)
_US_CASE_ITALIC = re.compile(
    r'(?:\*|_)([A-Z][A-Za-z\'\.\s]+?\s+v\.\s+[A-Z][A-Za-z\'\.\s]+?)(?:\*|_)'
)

# Statute: Title U.S.C. ss Section
_US_STATUTE = re.compile(
    r'(\d+)\s+U\.S\.C\.\s*(?:§|ss?\.?)\s*(\d+(?:\([a-z]\))*)'
    r'(?:\s*\((\d{4})\))?'
)

# Id. usage
_US_ID = re.compile(r'\bId\.\s')
_US_ID_AT = re.compile(r'\bId\.\s+at\s+\d+')

# Supra / infra
_US_SUPRA = re.compile(r'\b(\w+),?\s+supra\b', re.IGNORECASE)
_US_INFRA = re.compile(r'\b(\w+),?\s+infra\b', re.IGNORECASE)

# Non-Bluebook detector: e.g., [Year] UKSC or ECHR-style
_NON_BB_UK_STYLE = re.compile(r'\[\d{4}\]\s+(?:UKSC|UKHL|EWCA|EWHC|AC|QB|Ch)')


def _validate_us_citations(text: str, lines: list[str]) -> tuple[list[dict], list[dict]]:
    """Return (citations_found, issues) for Bluebook format."""
    citations: list[dict] = []
    issues: list[dict] = []

    # --- Case citations ---
    italic_ranges: set[tuple[int, int]] = set()
    for m in _US_CASE_ITALIC.finditer(text):
        italic_ranges.add((m.start(), m.end()))

    for m in _US_CASE.finditer(text):
        line_no = text[:m.start()].count('\n') + 1
        case_text = m.group(0)
        citations.append({
            "type": "case",
            "text": case_text,
            "line": line_no,
            "valid": True,
        })

        # Check italics/underline
        case_name = f"{m.group(1).strip()} v. {m.group(2).strip()}"
        is_italicized = any(
            s <= m.start() and e >= m.start() + len(case_name)
            for s, e in italic_ranges
        )
        # Also check if preceded by * or _
        pre_char_pos = m.start() - 1
        if pre_char_pos >= 0:
            pre_char = text[pre_char_pos]
        else:
            pre_char = ''
        if not is_italicized and pre_char not in ('*', '_'):
            issues.append({
                "type": "format_warning",
                "subtype": "case_name_not_italicized",
                "line": line_no,
                "found": case_name,
                "message": f"Bluebook requires case names to be italicized or underlined: '{case_name}'",
                "severity": "minor",
            })

        # Check court/year parenthetical
        if not m.group(6) and not m.group(7):
            # Check if it's a well-known reporter that doesn't need parenthetical
            reporter = m.group(4).strip()
            supreme_reporters = {'U.S.', 'S. Ct.', 'L. Ed.'}
            if reporter not in supreme_reporters:
                issues.append({
                    "type": "format_error",
                    "subtype": "missing_parenthetical",
                    "line": line_no,
                    "found": case_text,
                    "message": "Bluebook citation missing court and year parenthetical: "
                               f"'{case_text}' -- expected (Court Year) at the end",
                    "severity": "major",
                })
                citations[-1]["valid"] = False

    # --- Statute citations ---
    for m in _US_STATUTE.finditer(text):
        line_no = text[:m.start()].count('\n') + 1
        citations.append({
            "type": "statute",
            "text": m.group(0),
            "line": line_no,
            "valid": True,
        })

    # --- Id. usage ---
    # Id. must follow immediately after a full citation (within ~2 lines)
    id_positions = [m.start() for m in _US_ID.finditer(text)]
    all_cite_ends: list[int] = []
    for m in _US_CASE.finditer(text):
        all_cite_ends.append(m.end())
    for m in _US_STATUTE.finditer(text):
        all_cite_ends.append(m.end())
    all_cite_ends.sort()

    prev_was_cite_or_id = False
    for pos in id_positions:
        line_no = text[:pos].count('\n') + 1
        citations.append({
            "type": "short_form",
            "text": "Id.",
            "line": line_no,
            "valid": True,
        })
        # Check if there is a citation or previous Id. close before this Id.
        # "close" means within the previous 500 characters (rough heuristic)
        nearby_cite = any(
            (pos - ce) < 500 and (pos - ce) > 0
            for ce in all_cite_ends
        )
        nearby_prev_id = any(
            (pos - prev_pos) < 500 and (pos - prev_pos) > 0
            for prev_pos in id_positions if prev_pos < pos
        )
        if not nearby_cite and not nearby_prev_id:
            issues.append({
                "type": "format_error",
                "subtype": "orphan_id",
                "line": line_no,
                "found": "Id.",
                "message": "'Id.' must follow immediately after a full citation or another 'Id.' reference",
                "severity": "major",
            })
            citations[-1]["valid"] = False

    # --- Supra / infra ---
    for m in _US_SUPRA.finditer(text):
        line_no = text[:m.start()].count('\n') + 1
        citations.append({
            "type": "short_form",
            "text": m.group(0),
            "line": line_no,
            "valid": True,
        })

    for m in _US_INFRA.finditer(text):
        line_no = text[:m.start()].count('\n') + 1
        citations.append({
            "type": "short_form",
            "text": m.group(0),
            "line": line_no,
            "valid": True,
        })

    # --- Non-Bluebook detection ---
    for m in _NON_BB_UK_STYLE.finditer(text):
        line_no = text[:m.start()].count('\n') + 1
        issues.append({
            "type": "format_error",
            "subtype": "non_bluebook_citation",
            "line": line_no,
            "found": m.group(0),
            "message": f"UK/OSCOLA-style citation detected in Bluebook document: '{m.group(0)}'",
            "severity": "major",
        })

    return citations, issues


# ---------------------------------------------------------------------------
# UK English citation validation (OSCOLA)
# ---------------------------------------------------------------------------

# Case: Party v Party [Year] Court Reference
_UK_CASE = re.compile(
    r'([A-Z][A-Za-z\'\s]+?)\s+v\s+([A-Z][A-Za-z\'\s]+?)\s+'
    r'\[(\d{4})\]\s+([A-Z]{2,})\s+(\d+)'
)

# Statute: Act Name Year, s Section
_UK_STATUTE = re.compile(
    r'([A-Z][A-Za-z\s]+?Act)\s+(\d{4}),?\s+s\s+(\d+(?:\(\d+\))*)'
)

# Detect Bluebook-style in UK docs
_BB_IN_UK = re.compile(
    r'\d+\s+(?:U\.S\.|S\.\s*Ct\.|F\.\s*\d+[a-z]*|N\.(?:E|W|S)\.\s*\d+[a-z]*)\s+\d+'
)

# "v." (with period) is Bluebook; OSCOLA uses "v" (no period)
_UK_V_DOT = re.compile(r'\bv\.\s')


def _validate_uk_citations(text: str, lines: list[str]) -> tuple[list[dict], list[dict]]:
    """Return (citations_found, issues) for OSCOLA format."""
    citations: list[dict] = []
    issues: list[dict] = []

    # --- Case citations ---
    for m in _UK_CASE.finditer(text):
        line_no = text[:m.start()].count('\n') + 1
        citations.append({
            "type": "case",
            "text": m.group(0),
            "line": line_no,
            "valid": True,
        })

    # --- Statute citations ---
    for m in _UK_STATUTE.finditer(text):
        line_no = text[:m.start()].count('\n') + 1
        citations.append({
            "type": "statute",
            "text": m.group(0),
            "line": line_no,
            "valid": True,
        })

    # --- Detect Bluebook-style citations ---
    for m in _BB_IN_UK.finditer(text):
        line_no = text[:m.start()].count('\n') + 1
        issues.append({
            "type": "format_error",
            "subtype": "bluebook_in_oscola",
            "line": line_no,
            "found": m.group(0),
            "message": f"Bluebook-style citation detected in OSCOLA document: '{m.group(0)}'",
            "severity": "major",
        })

    # --- Detect "v." instead of "v" ---
    for m in _UK_V_DOT.finditer(text):
        line_no = text[:m.start()].count('\n') + 1
        issues.append({
            "type": "format_warning",
            "subtype": "v_dot_in_oscola",
            "line": line_no,
            "found": m.group(0).strip(),
            "message": "OSCOLA uses 'v' (no period) between parties, not 'v.' (Bluebook style)",
            "severity": "minor",
        })

    return citations, issues


# ---------------------------------------------------------------------------
# International / auto-detect
# ---------------------------------------------------------------------------

def _detect_jurisdiction(text: str) -> str:
    """Heuristic jurisdiction detection."""
    korean_chars = len(re.findall(r'[가-힣]', text))
    if korean_chars > 50:
        return "korea"

    uk_markers = len(re.findall(r'\[\d{4}\]\s+[A-Z]{2,}', text))
    us_markers = len(re.findall(r'\d+\s+(?:U\.S\.|F\.\d|S\.\s*Ct)', text))
    bluebook_v = len(re.findall(r'\bv\.', text))
    oscola_v = len(re.findall(r'\bv\b(?!\.)', text))

    if uk_markers > us_markers and oscola_v >= bluebook_v:
        return "uk"
    return "us"


def _detect_language(text: str) -> str:
    korean_chars = len(re.findall(r'[가-힣]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    return "korean" if korean_chars > english_chars else "english"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def validate_citations(text: str, jurisdiction: Optional[str] = None) -> dict:
    """Run citation validation and return a report dict."""
    lines = text.splitlines()
    language = _detect_language(text)

    if jurisdiction is None or jurisdiction == "intl":
        jurisdiction = _detect_jurisdiction(text)

    all_citations: list[dict] = []
    all_issues: list[dict] = []

    if jurisdiction == "korea":
        c, i = _validate_korean_citations(text, lines)
        all_citations.extend(c)
        all_issues.extend(i)
    elif jurisdiction == "us":
        c, i = _validate_us_citations(text, lines)
        all_citations.extend(c)
        all_issues.extend(i)
    elif jurisdiction == "uk":
        c, i = _validate_uk_citations(text, lines)
        all_citations.extend(c)
        all_issues.extend(i)

    return {
        "language": language,
        "jurisdiction": jurisdiction,
        "citationsFound": len(all_citations),
        "citations": all_citations,
        "issueCount": len(all_issues),
        "issues": all_issues,
        "status": "pass" if len(all_issues) == 0 else "fail",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate legal citation formats (Korean / US Bluebook / UK OSCOLA)."
    )
    parser.add_argument("file", help="Path to the document file (.md, .txt, etc.)")
    parser.add_argument(
        "--jurisdiction",
        choices=["korea", "us", "uk", "intl"],
        default="intl",
        help="Jurisdiction for citation rules (default: intl = auto-detect)",
    )
    args = parser.parse_args()

    with open(args.file, 'r', encoding='utf-8') as f:
        text = f.read()

    report = validate_citations(text, args.jurisdiction)
    report["file"] = args.file

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
