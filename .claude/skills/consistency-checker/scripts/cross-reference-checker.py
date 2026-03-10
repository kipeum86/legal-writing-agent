#!/usr/bin/env python3
"""
cross-reference-checker.py
Validates internal cross-references in legal documents.

Usage: python cross-reference-checker.py <file.md>
Output: JSON report of cross-reference issues to stdout.
"""

import re
import sys
import json


def extract_sections_korean(text: str) -> set[str]:
    """Extract all defined section identifiers from Korean document."""
    sections = set()
    # 제N조
    for m in re.finditer(r'제(\d+)조', text):
        sections.add(f"제{m.group(1)}조")
    # 제N항
    for m in re.finditer(r'제(\d+)항', text):
        sections.add(f"제{m.group(1)}항")
    # 제N호
    for m in re.finditer(r'제(\d+)호', text):
        sections.add(f"제{m.group(1)}호")
    return sections


def extract_sections_english(text: str) -> set[str]:
    """Extract all defined section identifiers from English document."""
    sections = set()
    # ARTICLE I, II, etc.
    for m in re.finditer(r'ARTICLE\s+([IVXLC]+)', text, re.IGNORECASE):
        sections.add(f"ARTICLE {m.group(1).upper()}")
    # Section N.N
    for m in re.finditer(r'Section\s+(\d+\.\d+)', text):
        sections.add(f"Section {m.group(1)}")
    # Section N
    for m in re.finditer(r'Section\s+(\d+)(?!\.\d)', text):
        sections.add(f"Section {m.group(1)}")
    return sections


def find_references_korean(text: str) -> list[dict]:
    """Find all cross-references in Korean document."""
    refs = []
    # Patterns: 제N조, 위 제N조, 같은 법 제N조, 본 조 제N항
    patterns = [
        (r'(?:위|상기|전술한|같은\s*법)\s*(제\d+조(?:\s*제\d+항)?)', 'cross-ref'),
        (r'(?:본\s*조|이\s*조)\s*(제\d+항)', 'internal-ref'),
    ]
    for pattern, ref_type in patterns:
        for m in re.finditer(pattern, text):
            refs.append({
                "reference": m.group(1),
                "type": ref_type,
                "position": m.start()
            })
    return refs


def find_references_english(text: str) -> list[dict]:
    """Find all cross-references in English document."""
    refs = []
    patterns = [
        (r'(?:see|See|pursuant to|under|per)\s+(Section\s+\d+(?:\.\d+)?)', 'cross-ref'),
        (r'(?:see|See)\s+(ARTICLE\s+[IVXLC]+)', 'cross-ref'),
        (r'(?:above|supra|herein)\s+(?:in\s+)?(Section\s+\d+(?:\.\d+)?)', 'cross-ref'),
    ]
    for pattern, ref_type in patterns:
        for m in re.finditer(pattern, text):
            refs.append({
                "reference": m.group(1),
                "type": ref_type,
                "position": m.start()
            })
    return refs


def detect_language(text: str) -> str:
    """Detect whether document is primarily Korean or English."""
    korean_chars = len(re.findall(r'[가-힣]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    return "korean" if korean_chars > english_chars else "english"


def main():
    if len(sys.argv) < 2:
        print("Usage: python cross-reference-checker.py <file.md>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    language = detect_language(text)

    if language == "korean":
        sections = extract_sections_korean(text)
        references = find_references_korean(text)
    else:
        sections = extract_sections_english(text)
        references = find_references_english(text)

    issues = []
    for ref in references:
        # Check if the referenced section exists
        ref_target = ref["reference"]
        if ref_target not in sections:
            # Try partial match
            found = any(ref_target in s for s in sections)
            if not found:
                issues.append({
                    "type": "broken_reference",
                    "reference": ref_target,
                    "position": ref["position"],
                    "severity": "major",
                    "message": f"Reference to '{ref_target}' but no matching section found"
                })

    report = {
        "file": filepath,
        "language": language,
        "sectionsFound": len(sections),
        "referencesFound": len(references),
        "issueCount": len(issues),
        "issues": issues,
        "status": "pass" if len(issues) == 0 else "fail"
    }

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
