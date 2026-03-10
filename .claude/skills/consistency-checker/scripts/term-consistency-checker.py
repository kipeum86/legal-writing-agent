#!/usr/bin/env python3
"""
term-consistency-checker.py
Validates defined term consistency in legal documents (Korean and English).

Usage:
    python term-consistency-checker.py <file.md>
    python term-consistency-checker.py <file.md> --generate-registry

Output: JSON report of term consistency issues to stdout.
With --generate-registry: outputs a term registry JSON suitable for
saving to output/term-registries/.
"""

import re
import sys
import json
from collections import defaultdict


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

def detect_language(text: str) -> str:
    """Detect whether document is primarily Korean or English."""
    korean_chars = len(re.findall(r'[가-힣]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    return "korean" if korean_chars > english_chars else "english"


# ---------------------------------------------------------------------------
# Line index helpers
# ---------------------------------------------------------------------------

def build_line_index(text: str) -> list[int]:
    """Return list of character offsets marking the start of each line."""
    offsets = [0]
    for i, ch in enumerate(text):
        if ch == '\n':
            offsets.append(i + 1)
    return offsets


def offset_to_line(offsets: list[int], pos: int) -> int:
    """Convert a character offset to a 1-based line number."""
    lo, hi = 0, len(offsets) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if offsets[mid] <= pos:
            lo = mid
        else:
            hi = mid - 1
    return lo + 1


# ---------------------------------------------------------------------------
# Korean term detection
# ---------------------------------------------------------------------------

# Common party designations
KOREAN_PARTY_TERMS = {
    "갑": "party-designation",
    "을": "party-designation",
    "병": "party-designation",
    "정": "party-designation",
    "원고": "party-designation",
    "피고": "party-designation",
    "신청인": "party-designation",
    "피신청인": "party-designation",
}


def extract_korean_definitions(text: str, line_offsets: list[int]) -> list[dict]:
    """Extract defined terms from Korean legal text.

    Patterns:
      - Full Name(이하 "Term"이라 한다)
      - Full Name(이하 "Term")
      - 「Full Law Name」(이하 "Abbreviation")
    """
    definitions = []

    # Pattern 1: General defined terms
    # e.g., 주식회사 테스트(이하 "회사"라 한다) or (이하 "회사"이라 한다)
    pattern_general = (
        r'([^(（\n]{2,}?)'           # full form (capture group 1)
        r'[(（]이하\s*'              # opening: (이하 or （이하
        r'["\u201C\u201D]'           # opening quote
        r'([^"\u201C\u201D]+?)'      # defined term (capture group 2)
        r'["\u201C\u201D]'           # closing quote
        r'(?:이?라\s*한다)?'         # optional 이라 한다 / 라 한다
        r'[)）]'                     # closing paren
    )
    for m in re.finditer(pattern_general, text):
        full_form = m.group(1).strip()
        term = m.group(2).strip()
        definitions.append({
            "term": term,
            "fullForm": full_form,
            "type": "general",
            "position": m.start(),
            "line": offset_to_line(line_offsets, m.start()),
        })

    # Pattern 2: Law abbreviations with guillemets
    # e.g., 「민사소송법」(이하 "민소법")
    pattern_law = (
        r'[「]([^」]+)[」]'          # full law name in guillemets
        r'\s*[(（]이하\s*'
        r'["\u201C\u201D]'
        r'([^"\u201C\u201D]+?)'
        r'["\u201C\u201D]'
        r'(?:이?라\s*한다)?'
        r'[)）]'
    )
    for m in re.finditer(pattern_law, text):
        full_form = m.group(1).strip()
        term = m.group(2).strip()
        definitions.append({
            "term": term,
            "fullForm": full_form,
            "type": "law-abbreviation",
            "position": m.start(),
            "line": offset_to_line(line_offsets, m.start()),
        })

    return definitions


def detect_korean_party_terms(text: str, line_offsets: list[int]) -> list[dict]:
    """Detect party designation terms used in Korean documents."""
    found = []
    for term, term_type in KOREAN_PARTY_TERMS.items():
        # Look for party designation patterns like "갑"은, "을"에게, (이하 "갑")
        pattern = rf'["\u201C]{re.escape(term)}["\u201D]'
        for m in re.finditer(pattern, text):
            found.append({
                "term": term,
                "fullForm": None,
                "type": term_type,
                "position": m.start(),
                "line": offset_to_line(line_offsets, m.start()),
            })
    return found


# ---------------------------------------------------------------------------
# English term detection
# ---------------------------------------------------------------------------

def extract_english_definitions(text: str, line_offsets: list[int]) -> list[dict]:
    """Extract defined terms from English legal text.

    Patterns:
      - Full Name (the "Term")
      - Full Name ("Term")
    """
    definitions = []

    # Pattern 1: Full Name (the "Term")
    pattern_the = (
        r'([A-Z][A-Za-z\s,&]+?)'       # full form starting with capital
        r'\s*\(the\s+'
        r'["\u201C]'
        r'([^"\u201D]+?)'
        r'["\u201D]'
        r'\)'
    )
    for m in re.finditer(pattern_the, text):
        full_form = m.group(1).strip()
        term = m.group(2).strip()
        definitions.append({
            "term": term,
            "fullForm": full_form,
            "type": "general",
            "position": m.start(),
            "line": offset_to_line(line_offsets, m.start()),
        })

    # Pattern 2: Full Name ("Term")
    pattern_direct = (
        r'([A-Z][A-Za-z\s,&]+?)'
        r'\s*\('
        r'["\u201C]'
        r'([^"\u201D]+?)'
        r'["\u201D]'
        r'\)'
    )
    for m in re.finditer(pattern_direct, text):
        full_form = m.group(1).strip()
        term = m.group(2).strip()
        # Avoid duplicates from pattern 1 (which also matches pattern 2)
        already = any(
            d["term"] == term and d["position"] == m.start()
            for d in definitions
        )
        if not already:
            definitions.append({
                "term": term,
                "fullForm": full_form,
                "type": "general",
                "position": m.start(),
                "line": offset_to_line(line_offsets, m.start()),
            })

    return definitions


# ---------------------------------------------------------------------------
# Consistency checks
# ---------------------------------------------------------------------------

def check_full_form_after_definition(
    text: str,
    definitions: list[dict],
    line_offsets: list[int],
) -> list[dict]:
    """Check if full form is used after the defined term has been introduced."""
    issues = []
    for defn in definitions:
        full_form = defn["fullForm"]
        if not full_form or len(full_form) < 3:
            continue
        # Search for full form occurrences AFTER the definition
        after_text = text[defn["position"]:]
        # Skip the definition site itself by advancing past it
        defn_match_end = text.find(")", defn["position"])
        if defn_match_end == -1:
            defn_match_end = defn["position"] + len(full_form)
        search_start = defn_match_end + 1
        if search_start >= len(text):
            continue

        escaped_full = re.escape(full_form)
        for m in re.finditer(escaped_full, text[search_start:]):
            abs_pos = search_start + m.start()
            # Skip occurrences inside another definition
            context_before = text[max(0, abs_pos - 10):abs_pos]
            if "이하" in context_before or "(the " in context_before:
                continue
            issues.append({
                "type": "full_form_after_definition",
                "severity": "major",
                "term": defn["term"],
                "fullForm": full_form,
                "location": {
                    "line": offset_to_line(line_offsets, abs_pos),
                    "offset": abs_pos,
                },
                "message": (
                    f'Full form "{full_form}" used after it was defined as '
                    f'"{defn["term"]}" (defined at line {defn["line"]}). '
                    f'Use the defined term instead.'
                ),
            })
    return issues


def check_term_used_before_definition(
    text: str,
    definitions: list[dict],
    line_offsets: list[int],
) -> list[dict]:
    """Check if a defined term is used before its definition site."""
    issues = []
    for defn in definitions:
        term = defn["term"]
        if len(term) < 2:
            continue
        before_text = text[:defn["position"]]
        escaped_term = re.escape(term)
        for m in re.finditer(escaped_term, before_text):
            issues.append({
                "type": "term_before_definition",
                "severity": "major",
                "term": term,
                "location": {
                    "line": offset_to_line(line_offsets, m.start()),
                    "offset": m.start(),
                },
                "message": (
                    f'Term "{term}" used at line '
                    f'{offset_to_line(line_offsets, m.start())} '
                    f'before its definition at line {defn["line"]}.'
                ),
            })
    return issues


def check_unused_terms(
    text: str,
    definitions: list[dict],
    line_offsets: list[int],
) -> list[dict]:
    """Flag defined terms that are never used after their definition."""
    issues = []
    for defn in definitions:
        term = defn["term"]
        # Find end of the definition site
        defn_match_end = text.find(")", defn["position"])
        if defn_match_end == -1:
            defn_match_end = defn["position"] + len(term)
        search_start = defn_match_end + 1
        if search_start >= len(text):
            after_text = ""
        else:
            after_text = text[search_start:]

        escaped_term = re.escape(term)
        if not re.search(escaped_term, after_text):
            issues.append({
                "type": "unused_term",
                "severity": "minor",
                "term": term,
                "location": {
                    "line": defn["line"],
                    "offset": defn["position"],
                },
                "message": (
                    f'Defined term "{term}" (line {defn["line"]}) '
                    f'is never used after its definition.'
                ),
            })
    return issues


def check_duplicate_definitions(
    definitions: list[dict],
) -> list[dict]:
    """Check for conflicting definitions:
    - Same full form mapped to multiple defined terms
    - Same defined term mapped to multiple full forms
    """
    issues = []

    # full form -> list of terms
    full_to_terms: dict[str, list[dict]] = defaultdict(list)
    # term -> list of full forms
    term_to_fulls: dict[str, list[dict]] = defaultdict(list)

    for defn in definitions:
        if defn["fullForm"]:
            full_to_terms[defn["fullForm"]].append(defn)
        term_to_fulls[defn["term"]].append(defn)

    for full_form, defns in full_to_terms.items():
        unique_terms = set(d["term"] for d in defns)
        if len(unique_terms) > 1:
            lines = [d["line"] for d in defns]
            issues.append({
                "type": "multiple_terms_same_concept",
                "severity": "critical",
                "term": list(unique_terms),
                "fullForm": full_form,
                "location": {"lines": lines},
                "message": (
                    f'Concept "{full_form}" has multiple defined terms: '
                    f'{", ".join(sorted(unique_terms))} '
                    f'(lines {", ".join(str(l) for l in lines)}).'
                ),
            })

    for term, defns in term_to_fulls.items():
        unique_fulls = set(d["fullForm"] for d in defns if d["fullForm"])
        if len(unique_fulls) > 1:
            lines = [d["line"] for d in defns]
            issues.append({
                "type": "same_term_multiple_concepts",
                "severity": "critical",
                "term": term,
                "fullForm": list(unique_fulls),
                "location": {"lines": lines},
                "message": (
                    f'Defined term "{term}" refers to multiple concepts: '
                    f'{", ".join(sorted(unique_fulls))} '
                    f'(lines {", ".join(str(l) for l in lines)}).'
                ),
            })

    return issues


def check_english_capitalization(
    text: str,
    definitions: list[dict],
    line_offsets: list[int],
) -> list[dict]:
    """Check that English defined terms are used with consistent capitalization."""
    issues = []
    for defn in definitions:
        term = defn["term"]
        if not term or not term[0].isupper():
            continue
        # Look for lowercase variant after definition
        defn_match_end = text.find(")", defn["position"])
        if defn_match_end == -1:
            continue
        search_start = defn_match_end + 1
        if search_start >= len(text):
            continue

        lowercase_term = term[0].lower() + term[1:]
        for m in re.finditer(re.escape(lowercase_term), text[search_start:]):
            abs_pos = search_start + m.start()
            # Skip if at start of sentence (preceded by ". ")
            before = text[max(0, abs_pos - 3):abs_pos]
            if re.search(r'[.!?]\s+$', before):
                continue
            issues.append({
                "type": "capitalization_inconsistency",
                "severity": "minor",
                "term": term,
                "location": {
                    "line": offset_to_line(line_offsets, abs_pos),
                    "offset": abs_pos,
                },
                "message": (
                    f'Defined term "{term}" used with inconsistent '
                    f'capitalization ("{lowercase_term}") at line '
                    f'{offset_to_line(line_offsets, abs_pos)}.'
                ),
            })
    return issues


def check_undefined_abbreviations_korean(
    text: str,
    definitions: list[dict],
    line_offsets: list[int],
) -> list[dict]:
    """Detect Korean abbreviation patterns that lack a preceding definition."""
    issues = []
    defined_terms = set(d["term"] for d in definitions)

    # Look for quoted terms that appear to be used as abbreviations
    # Pattern: "SomeTerm" used in context but not defined
    for m in re.finditer(r'["\u201C]([^"\u201D]{2,20})["\u201D]', text):
        candidate = m.group(1).strip()
        if candidate in defined_terms:
            continue
        # Skip if this IS a definition site
        context_before = text[max(0, m.start() - 15):m.start()]
        if "이하" in context_before or "(the " in context_before.lower():
            continue
        # Only flag if used multiple times (suggests it should be defined)
        count = len(re.findall(re.escape(candidate), text))
        if count >= 2 and len(candidate) >= 2:
            issues.append({
                "type": "undefined_abbreviation",
                "severity": "minor",
                "term": candidate,
                "location": {
                    "line": offset_to_line(line_offsets, m.start()),
                    "offset": m.start(),
                },
                "message": (
                    f'Term "{candidate}" is used {count} times but '
                    f'has no formal definition.'
                ),
            })
    # Deduplicate by term
    seen = set()
    deduped = []
    for issue in issues:
        if issue["term"] not in seen:
            seen.add(issue["term"])
            deduped.append(issue)
    return deduped


def check_undefined_abbreviations_english(
    text: str,
    definitions: list[dict],
    line_offsets: list[int],
) -> list[dict]:
    """Detect English abbreviation patterns that lack a preceding definition."""
    issues = []
    defined_terms = set(d["term"] for d in definitions)

    # Look for quoted terms: "SomeTerm" or capitalized abbreviations (e.g., "NDA")
    for m in re.finditer(r'["\u201C]([^"\u201D]{2,30})["\u201D]', text):
        candidate = m.group(1).strip()
        if candidate in defined_terms:
            continue
        context_before = text[max(0, m.start() - 15):m.start()]
        if "(the " in context_before.lower() or '("' in context_before:
            continue
        count = len(re.findall(re.escape(candidate), text))
        if count >= 2 and len(candidate) >= 2:
            issues.append({
                "type": "undefined_abbreviation",
                "severity": "minor",
                "term": candidate,
                "location": {
                    "line": offset_to_line(line_offsets, m.start()),
                    "offset": m.start(),
                },
                "message": (
                    f'Term "{candidate}" is used {count} times but '
                    f'has no formal definition.'
                ),
            })
    seen = set()
    deduped = []
    for issue in issues:
        if issue["term"] not in seen:
            seen.add(issue["term"])
            deduped.append(issue)
    return deduped


# ---------------------------------------------------------------------------
# Term registry generator
# ---------------------------------------------------------------------------

def generate_registry(
    filepath: str,
    language: str,
    definitions: list[dict],
) -> dict:
    """Generate a term registry JSON from extracted definitions."""
    entries = []
    for defn in definitions:
        entries.append({
            "term": defn["term"],
            "fullForm": defn["fullForm"],
            "type": defn["type"],
            "definedAtLine": defn["line"],
        })

    return {
        "file": filepath,
        "language": language,
        "generatedBy": "term-consistency-checker.py",
        "termCount": len(entries),
        "terms": entries,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python term-consistency-checker.py <file.md> "
            "[--generate-registry]",
            file=sys.stderr,
        )
        sys.exit(1)

    filepath = sys.argv[1]
    generate_reg = "--generate-registry" in sys.argv

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    language = detect_language(text)
    line_offsets = build_line_index(text)

    # ---- Extract definitions ------------------------------------------------
    if language == "korean":
        definitions = extract_korean_definitions(text, line_offsets)
        party_terms = detect_korean_party_terms(text, line_offsets)
        all_definitions = definitions + party_terms
    else:
        definitions = extract_english_definitions(text, line_offsets)
        all_definitions = definitions

    # ---- Registry mode ------------------------------------------------------
    if generate_reg:
        registry = generate_registry(filepath, language, all_definitions)
        print(json.dumps(registry, indent=2, ensure_ascii=False))
        return

    # ---- Consistency checks -------------------------------------------------
    issues: list[dict] = []

    # Full form used after definition
    issues.extend(
        check_full_form_after_definition(text, definitions, line_offsets)
    )

    # Term used before definition
    issues.extend(
        check_term_used_before_definition(text, definitions, line_offsets)
    )

    # Unused terms
    issues.extend(check_unused_terms(text, definitions, line_offsets))

    # Duplicate / conflicting definitions
    issues.extend(check_duplicate_definitions(definitions))

    # Language-specific checks
    if language == "english":
        issues.extend(
            check_english_capitalization(text, definitions, line_offsets)
        )
        issues.extend(
            check_undefined_abbreviations_english(
                text, definitions, line_offsets
            )
        )
    else:
        issues.extend(
            check_undefined_abbreviations_korean(
                text, definitions, line_offsets
            )
        )

    # ---- Build defined-terms summary ----------------------------------------
    defined_terms_summary = []
    for defn in all_definitions:
        defined_terms_summary.append({
            "term": defn["term"],
            "fullForm": defn["fullForm"],
            "type": defn["type"],
            "line": defn["line"],
        })

    # ---- Output report ------------------------------------------------------
    report = {
        "file": filepath,
        "language": language,
        "definedTerms": defined_terms_summary,
        "issues": issues,
        "issueCount": len(issues),
        "status": "pass" if len(issues) == 0 else "fail",
    }

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
