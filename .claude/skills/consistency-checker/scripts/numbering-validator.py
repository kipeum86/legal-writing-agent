#!/usr/bin/env python3
"""
numbering-validator.py
Validates sequential numbering in legal documents (Korean and English conventions).

Supports:
  - Korean statutory hierarchy: 편→장→절→관→조→항→호→목
  - Korean non-statutory numbering: I→1→가→(1)→(가)
  - English Roman numerals (I-XX), Section X.Y.Z deep nesting
  - English (a)(b)(c) -> (i)(ii)(iii) -> (A)(B)(C) hierarchy
  - Orphan numbering detection
  - Line-number-aware error messages

Usage: python numbering-validator.py <file.md> [--verbose]
Output: JSON report of numbering issues to stdout.
"""

import re
import sys
import json
import argparse


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

ROMAN_MAP = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
    'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
    'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
    'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20,
}

ROMAN_LOWER_MAP = {k.lower(): v for k, v in ROMAN_MAP.items()}

CIRCLE_NUMS = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳'

# Korean 목 characters
MOK_CHARS = list('가나다라마바사아자차카타파하')
MOK_SET = set(MOK_CHARS)


def _line_of(text: str, pos: int) -> int:
    """Return 1-based line number for a character position."""
    return text[:pos].count('\n') + 1


def _make_issue(
    issue_type: str,
    convention: str,
    level: str,
    severity: str,
    line: int,
    **kwargs,
) -> dict:
    result = {
        "type": issue_type,
        "convention": convention,
        "level": level,
        "severity": severity,
        "line": line,
    }
    result.update(kwargs)
    return result


# ---------------------------------------------------------------------------
# Korean statutory numbering: 편→장→절→관→조→항→호→목
# ---------------------------------------------------------------------------

_KR_HIERARCHY_PATTERNS = [
    ("편", re.compile(r'제(\d+)편')),
    ("장", re.compile(r'제(\d+)장')),
    ("절", re.compile(r'제(\d+)절')),
    ("관", re.compile(r'제(\d+)관')),
    ("조", re.compile(r'제(\d+)조')),
]


def _check_sequential(
    text: str,
    pattern: re.Pattern,
    level: str,
    convention: str,
    issues: list[dict],
    verbose_info: list[dict],
):
    """Check that numbered items matching `pattern` are sequential."""
    matches = list(pattern.finditer(text))
    if not matches:
        return

    nums_with_lines: list[tuple[int, int]] = []
    for m in matches:
        num = int(m.group(1))
        line = _line_of(text, m.start())
        nums_with_lines.append((num, line))

    # Track groups: reset when we see 1 again
    groups: list[list[tuple[int, int]]] = []
    current_group: list[tuple[int, int]] = []
    for num, line in nums_with_lines:
        if num == 1 and current_group:
            groups.append(current_group)
            current_group = [(num, line)]
        else:
            current_group.append((num, line))
    if current_group:
        groups.append(current_group)

    for group in groups:
        for i in range(1, len(group)):
            prev_num, _ = group[i - 1]
            curr_num, curr_line = group[i]
            expected = prev_num + 1
            if curr_num != expected:
                if curr_num == prev_num:
                    issues.append(_make_issue(
                        "duplicate", convention, level, "critical",
                        line=curr_line,
                        number=curr_num,
                        message=f"Duplicate {level} {curr_num} at line {curr_line}",
                    ))
                elif curr_num > expected:
                    issues.append(_make_issue(
                        "gap", convention, level, "critical",
                        line=curr_line,
                        expected=expected,
                        found=curr_num,
                        message=f"{level} numbering gap at line {curr_line}: "
                                f"expected {expected}, found {curr_num}",
                    ))
                else:
                    issues.append(_make_issue(
                        "out_of_order", convention, level, "critical",
                        line=curr_line,
                        expected=expected,
                        found=curr_num,
                        message=f"{level} out of order at line {curr_line}: "
                                f"expected {expected}, found {curr_num}",
                    ))

    if verbose_info is not None:
        for num, line in nums_with_lines:
            verbose_info.append({
                "level": level,
                "number": num,
                "line": line,
            })


def validate_korean_numbering(text: str, verbose: bool = False) -> tuple[list[dict], list[dict]]:
    """Validate Korean numbering. Returns (issues, verbose_info)."""
    issues: list[dict] = []
    verbose_info: list[dict] = [] if verbose else []

    # --- Statutory hierarchy: 편, 장, 절, 관, 조 ---
    for level, pattern in _KR_HIERARCHY_PATTERNS:
        _check_sequential(text, pattern, level, "korean", issues, verbose_info if verbose else None)

    # --- 항 (circled numbers) ---
    matches = [(m.group(0), m.start()) for m in re.finditer(f'[{CIRCLE_NUMS}]', text)]
    if matches:
        groups: list[list[tuple[int, int]]] = []
        current: list[tuple[int, int]] = []
        for char, pos in matches:
            num = CIRCLE_NUMS.index(char) + 1
            line = _line_of(text, pos)
            if num == 1 and current:
                groups.append(current)
                current = [(num, line)]
            else:
                current.append((num, line))
        if current:
            groups.append(current)

        for group in groups:
            seen: set[int] = set()
            for i, (num, line) in enumerate(group):
                if num in seen:
                    issues.append(_make_issue(
                        "duplicate", "korean", "항", "critical",
                        line=line, number=num,
                        message=f"항 ①~⑳ duplicate {num} at line {line}",
                    ))
                seen.add(num)
                if i > 0:
                    prev_num = group[i - 1][0]
                    if num != prev_num + 1 and num != 1:
                        issues.append(_make_issue(
                            "gap", "korean", "항", "critical",
                            line=line, expected=prev_num + 1, found=num,
                            message=f"항 gap at line {line}: expected {prev_num + 1}, found {num}",
                        ))

            if verbose:
                for num, line in group:
                    verbose_info.append({"level": "항", "number": num, "line": line})

    # --- 호 (indented numbered items: 1. 2. 3.) ---
    ho_pattern = re.compile(r'^(\s+)(\d+)\.\s', re.MULTILINE)
    ho_matches = list(ho_pattern.finditer(text))
    if ho_matches:
        # Group by indentation level
        by_indent: dict[int, list[tuple[int, int]]] = {}
        for m in ho_matches:
            indent = len(m.group(1))
            num = int(m.group(2))
            line = _line_of(text, m.start())
            if indent not in by_indent:
                by_indent[indent] = []
            by_indent[indent].append((num, line))

        for indent, items in by_indent.items():
            groups_h: list[list[tuple[int, int]]] = []
            cur: list[tuple[int, int]] = []
            for num, line in items:
                if num == 1 and cur:
                    groups_h.append(cur)
                    cur = [(num, line)]
                else:
                    cur.append((num, line))
            if cur:
                groups_h.append(cur)

            for group in groups_h:
                # Orphan detection
                if len(group) == 1:
                    issues.append(_make_issue(
                        "orphan", "korean", "호", "minor",
                        line=group[0][1], number=group[0][0],
                        message=f"Orphan 호 item (only one sub-item) at line {group[0][1]}",
                    ))
                for i in range(1, len(group)):
                    prev_num, _ = group[i - 1]
                    curr_num, curr_line = group[i]
                    if curr_num == prev_num:
                        issues.append(_make_issue(
                            "duplicate", "korean", "호", "major",
                            line=curr_line, number=curr_num,
                            message=f"Duplicate 호 {curr_num} at line {curr_line}",
                        ))
                    elif curr_num != prev_num + 1:
                        issues.append(_make_issue(
                            "gap", "korean", "호", "major",
                            line=curr_line, expected=prev_num + 1, found=curr_num,
                            message=f"호 numbering gap at line {curr_line}: "
                                    f"expected {prev_num + 1}, found {curr_num}",
                        ))

    # --- 목 (가, 나, 다, 라, ...) ---
    mok_pattern = re.compile(r'^\s+([가나다라마바사아자차카타파하])\.\s', re.MULTILINE)
    mok_matches = list(mok_pattern.finditer(text))
    if mok_matches:
        groups_m: list[list[tuple[str, int, int]]] = []
        cur_m: list[tuple[str, int, int]] = []
        for m in mok_matches:
            char = m.group(1)
            idx = MOK_CHARS.index(char) if char in MOK_SET else -1
            line = _line_of(text, m.start())
            if char == '가' and cur_m:
                groups_m.append(cur_m)
                cur_m = [(char, idx, line)]
            else:
                cur_m.append((char, idx, line))
        if cur_m:
            groups_m.append(cur_m)

        for group in groups_m:
            if len(group) == 1:
                issues.append(_make_issue(
                    "orphan", "korean", "목", "minor",
                    line=group[0][2], found=group[0][0],
                    message=f"Orphan 목 item (only one sub-item) at line {group[0][2]}",
                ))
            for i in range(1, len(group)):
                _, prev_idx, _ = group[i - 1]
                char, curr_idx, curr_line = group[i]
                if curr_idx != prev_idx + 1:
                    expected_char = MOK_CHARS[prev_idx + 1] if prev_idx + 1 < len(MOK_CHARS) else '?'
                    issues.append(_make_issue(
                        "gap", "korean", "목", "major",
                        line=curr_line,
                        expected=expected_char,
                        found=char,
                        message=f"목 gap at line {curr_line}: expected '{expected_char}', found '{char}'",
                    ))

            if verbose:
                for char, idx, line in group:
                    verbose_info.append({"level": "목", "char": char, "line": line})

    # --- Non-statutory mixed numbering: I→1→가→(1)→(가) ---
    # Detect Roman numeral headings (e.g., "I. ", "II. ")
    roman_heading = re.compile(r'^(I{1,3}|IV|VI{0,3}|IX|XI{0,3}|XIV|XV|XVI{0,3}|XIX|XX)\.\s', re.MULTILINE)
    rh_matches = list(roman_heading.finditer(text))
    if rh_matches:
        nums = []
        for m in rh_matches:
            val = ROMAN_MAP.get(m.group(1))
            line = _line_of(text, m.start())
            if val:
                nums.append((val, line))
        for i in range(1, len(nums)):
            prev_val, _ = nums[i - 1]
            curr_val, curr_line = nums[i]
            if curr_val != prev_val + 1:
                issues.append(_make_issue(
                    "gap", "korean", "로마숫자 제목", "major",
                    line=curr_line, expected=prev_val + 1, found=curr_val,
                    message=f"Roman numeral heading gap at line {curr_line}: "
                            f"expected {prev_val + 1}, found {curr_val}",
                ))

    # Detect (1), (2), (3) numbering
    paren_num = re.compile(r'\((\d+)\)')
    pn_matches = list(paren_num.finditer(text))
    if pn_matches:
        groups_pn: list[list[tuple[int, int]]] = []
        cur_pn: list[tuple[int, int]] = []
        for m in pn_matches:
            num = int(m.group(1))
            line = _line_of(text, m.start())
            if num == 1 and cur_pn:
                groups_pn.append(cur_pn)
                cur_pn = [(num, line)]
            else:
                cur_pn.append((num, line))
        if cur_pn:
            groups_pn.append(cur_pn)

        for group in groups_pn:
            if len(group) == 1:
                # Single (1) is common, skip orphan for this
                pass
            for i in range(1, len(group)):
                prev_num, _ = group[i - 1]
                curr_num, curr_line = group[i]
                if curr_num == prev_num:
                    issues.append(_make_issue(
                        "duplicate", "korean", "(N) 번호", "major",
                        line=curr_line, number=curr_num,
                        message=f"Duplicate (N) numbering ({curr_num}) at line {curr_line}",
                    ))
                elif curr_num != prev_num + 1 and curr_num != 1:
                    issues.append(_make_issue(
                        "gap", "korean", "(N) 번호", "major",
                        line=curr_line, expected=prev_num + 1, found=curr_num,
                        message=f"(N) numbering gap at line {curr_line}: "
                                f"expected ({prev_num + 1}), found ({curr_num})",
                    ))

    # Detect (가), (나), (다) numbering
    paren_mok = re.compile(r'\(([가나다라마바사아자차카타파하])\)')
    pm_matches = list(paren_mok.finditer(text))
    if pm_matches:
        groups_pm: list[list[tuple[str, int, int]]] = []
        cur_pm: list[tuple[str, int, int]] = []
        for m in pm_matches:
            char = m.group(1)
            idx = MOK_CHARS.index(char) if char in MOK_SET else -1
            line = _line_of(text, m.start())
            if char == '가' and cur_pm:
                groups_pm.append(cur_pm)
                cur_pm = [(char, idx, line)]
            else:
                cur_pm.append((char, idx, line))
        if cur_pm:
            groups_pm.append(cur_pm)

        for group in groups_pm:
            for i in range(1, len(group)):
                _, prev_idx, _ = group[i - 1]
                char, curr_idx, curr_line = group[i]
                if curr_idx != prev_idx + 1:
                    expected_char = MOK_CHARS[prev_idx + 1] if prev_idx + 1 < len(MOK_CHARS) else '?'
                    issues.append(_make_issue(
                        "gap", "korean", "(가나다) 번호", "major",
                        line=curr_line, expected=f"({expected_char})", found=f"({char})",
                        message=f"(가나다) gap at line {curr_line}: "
                                f"expected '({expected_char})', found '({char})'",
                    ))

    return issues, verbose_info


# ---------------------------------------------------------------------------
# English numbering
# ---------------------------------------------------------------------------

def validate_english_numbering(text: str, verbose: bool = False) -> tuple[list[dict], list[dict]]:
    """Validate English numbering. Returns (issues, verbose_info)."""
    issues: list[dict] = []
    verbose_info: list[dict] = [] if verbose else []

    # --- ARTICLE Roman numerals (I-XX) ---
    article_pattern = re.compile(r'ARTICLE\s+([IVXLC]+)', re.IGNORECASE)
    art_matches = list(article_pattern.finditer(text))
    if art_matches:
        nums: list[tuple[int, str, int]] = []
        for m in art_matches:
            numeral = m.group(1).upper()
            val = ROMAN_MAP.get(numeral)
            line = _line_of(text, m.start())
            if val is not None:
                nums.append((val, numeral, line))
            else:
                issues.append(_make_issue(
                    "invalid_numeral", "english", "article", "major",
                    line=line, found=numeral,
                    message=f"Unrecognized Roman numeral '{numeral}' at line {line}",
                ))

        for i in range(1, len(nums)):
            prev_val, _, _ = nums[i - 1]
            curr_val, curr_numeral, curr_line = nums[i]
            expected = prev_val + 1
            if curr_val != expected:
                issues.append(_make_issue(
                    "gap", "english", "article", "critical",
                    line=curr_line, expected=expected, found=curr_val,
                    message=f"Article numbering gap at line {curr_line}: "
                            f"expected {expected}, found {curr_val} ('{curr_numeral}')",
                ))

        if verbose:
            for val, numeral, line in nums:
                verbose_info.append({"level": "article", "numeral": numeral, "value": val, "line": line})

    # --- Section X.Y.Z deep nesting ---
    section_pattern = re.compile(r'Section\s+([\d]+(?:\.[\d]+)*)', re.IGNORECASE)
    sec_matches = list(section_pattern.finditer(text))
    if sec_matches:
        # Group by parent prefix
        by_parent: dict[str, list[tuple[int, int, str]]] = {}
        for m in sec_matches:
            full = m.group(1)
            parts = full.split('.')
            line = _line_of(text, m.start())

            if verbose:
                verbose_info.append({"level": "section", "number": full, "line": line})

            if len(parts) == 1:
                parent = ""
                num = int(parts[0])
            else:
                parent = '.'.join(parts[:-1])
                num = int(parts[-1])

            if parent not in by_parent:
                by_parent[parent] = []
            by_parent[parent].append((num, line, full))

        for parent, items in by_parent.items():
            for i in range(1, len(items)):
                prev_num, _, _ = items[i - 1]
                curr_num, curr_line, curr_full = items[i]
                expected = prev_num + 1
                if curr_num != expected:
                    issues.append(_make_issue(
                        "gap", "english", "section", "critical",
                        line=curr_line, expected=expected, found=curr_num,
                        message=f"Section numbering gap at line {curr_line}: "
                                f"expected Section {parent + '.' if parent else ''}{expected}, "
                                f"found Section {curr_full}",
                    ))

            # Orphan detection
            if len(items) == 1 and parent:
                num, line, full = items[0]
                issues.append(_make_issue(
                    "orphan", "english", "section", "minor",
                    line=line, found=full,
                    message=f"Orphan section (only one sub-section under "
                            f"Section {parent}) at line {line}: Section {full}",
                ))

    # --- (a)(b)(c) lowercase letter sub-sections ---
    lower_letter = re.compile(r'\(([a-z])\)')
    ll_matches = list(lower_letter.finditer(text))
    if ll_matches:
        groups: list[list[tuple[str, int]]] = []
        current: list[tuple[str, int]] = []
        for m in ll_matches:
            letter = m.group(1)
            line = _line_of(text, m.start())
            if letter == 'a' and current:
                groups.append(current)
                current = [(letter, line)]
            else:
                current.append((letter, line))
        if current:
            groups.append(current)

        for group in groups:
            if len(group) == 1:
                issues.append(_make_issue(
                    "orphan", "english", "sub-section (a)", "minor",
                    line=group[0][1], found=f"({group[0][0]})",
                    message=f"Orphan sub-section: only ({group[0][0]}) with no siblings at line {group[0][1]}",
                ))
            for i in range(1, len(group)):
                prev_letter, _ = group[i - 1]
                curr_letter, curr_line = group[i]
                expected = chr(ord(prev_letter) + 1)
                if curr_letter != expected:
                    if curr_letter == prev_letter:
                        issues.append(_make_issue(
                            "duplicate", "english", "sub-section (a)", "major",
                            line=curr_line, found=f"({curr_letter})",
                            message=f"Duplicate sub-section ({curr_letter}) at line {curr_line}",
                        ))
                    else:
                        issues.append(_make_issue(
                            "gap", "english", "sub-section (a)", "major",
                            line=curr_line,
                            expected=f"({expected})",
                            found=f"({curr_letter})",
                            message=f"Sub-section gap at line {curr_line}: "
                                    f"expected ({expected}), found ({curr_letter})",
                        ))

    # --- (i)(ii)(iii) lowercase Roman sub-sub-sections ---
    lower_roman = re.compile(r'\((i{1,3}|iv|vi{0,3}|ix|xi{0,3}|xiv|xv|xvi{0,3}|xix|xx)\)')
    lr_matches = list(lower_roman.finditer(text))
    # Filter out matches that overlap with (a)-(z) single letters already captured
    lr_filtered = []
    for m in lr_matches:
        numeral = m.group(1)
        if numeral in ROMAN_LOWER_MAP:
            lr_filtered.append(m)

    if lr_filtered:
        groups_lr: list[list[tuple[int, str, int]]] = []
        current_lr: list[tuple[int, str, int]] = []
        for m in lr_filtered:
            numeral = m.group(1)
            val = ROMAN_LOWER_MAP[numeral]
            line = _line_of(text, m.start())
            if val == 1 and current_lr:
                groups_lr.append(current_lr)
                current_lr = [(val, numeral, line)]
            else:
                current_lr.append((val, numeral, line))
        if current_lr:
            groups_lr.append(current_lr)

        for group in groups_lr:
            if len(group) == 1:
                issues.append(_make_issue(
                    "orphan", "english", "sub-sub-section (i)", "minor",
                    line=group[0][2], found=f"({group[0][1]})",
                    message=f"Orphan sub-sub-section: only ({group[0][1]}) with no siblings at line {group[0][2]}",
                ))
            for i in range(1, len(group)):
                prev_val, _, _ = group[i - 1]
                curr_val, curr_numeral, curr_line = group[i]
                expected = prev_val + 1
                if curr_val != expected:
                    issues.append(_make_issue(
                        "gap", "english", "sub-sub-section (i)", "major",
                        line=curr_line,
                        expected=expected,
                        found=curr_val,
                        message=f"Sub-sub-section gap at line {curr_line}: "
                                f"expected ({list(ROMAN_LOWER_MAP.keys())[expected - 1] if expected <= 20 else '?'}), "
                                f"found ({curr_numeral})",
                    ))

    # --- (A)(B)(C) uppercase letter sub-sections ---
    upper_letter = re.compile(r'\(([A-Z])\)')
    ul_matches = list(upper_letter.finditer(text))
    if ul_matches:
        groups_ul: list[list[tuple[str, int]]] = []
        current_ul: list[tuple[str, int]] = []
        for m in ul_matches:
            letter = m.group(1)
            line = _line_of(text, m.start())
            if letter == 'A' and current_ul:
                groups_ul.append(current_ul)
                current_ul = [(letter, line)]
            else:
                current_ul.append((letter, line))
        if current_ul:
            groups_ul.append(current_ul)

        for group in groups_ul:
            if len(group) == 1:
                issues.append(_make_issue(
                    "orphan", "english", "sub-section (A)", "minor",
                    line=group[0][1], found=f"({group[0][0]})",
                    message=f"Orphan sub-section: only ({group[0][0]}) with no siblings at line {group[0][1]}",
                ))
            for i in range(1, len(group)):
                prev_letter, _ = group[i - 1]
                curr_letter, curr_line = group[i]
                expected = chr(ord(prev_letter) + 1)
                if curr_letter != expected:
                    if curr_letter == prev_letter:
                        issues.append(_make_issue(
                            "duplicate", "english", "sub-section (A)", "major",
                            line=curr_line, found=f"({curr_letter})",
                            message=f"Duplicate sub-section ({curr_letter}) at line {curr_line}",
                        ))
                    else:
                        issues.append(_make_issue(
                            "gap", "english", "sub-section (A)", "major",
                            line=curr_line,
                            expected=f"({expected})",
                            found=f"({curr_letter})",
                            message=f"Sub-section gap at line {curr_line}: "
                                    f"expected ({expected}), found ({curr_letter})",
                        ))

    return issues, verbose_info


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

def detect_language(text: str) -> str:
    """Detect whether document is primarily Korean or English."""
    korean_chars = len(re.findall(r'[가-힣]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    return "korean" if korean_chars > english_chars else "english"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Validate sequential numbering in legal documents."
    )
    parser.add_argument("file", help="Path to the document file (.md, .txt, etc.)")
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Include detailed item-by-item listing in output",
    )
    args = parser.parse_args()

    with open(args.file, 'r', encoding='utf-8') as f:
        text = f.read()

    language = detect_language(text)

    if language == "korean":
        issues, verbose_info = validate_korean_numbering(text, verbose=args.verbose)
    else:
        issues, verbose_info = validate_english_numbering(text, verbose=args.verbose)

    report: dict = {
        "file": args.file,
        "language": language,
        "issueCount": len(issues),
        "issues": issues,
        "status": "pass" if len(issues) == 0 else "fail",
    }

    if args.verbose and verbose_info:
        report["details"] = verbose_info

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
