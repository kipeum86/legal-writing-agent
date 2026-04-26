"""Deterministic context budget and lazy-load planning."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STYLE_PROFILE_DIR = Path(".claude/skills/convention-selector/style-profiles")
CONVENTION_REFERENCES = Path(".claude/skills/convention-selector/references")
TEMPLATE_REFERENCES = Path(".claude/skills/structure-planner/references")

STEP_BUDGETS = {
    "D1": 16_000,
    "D2": 24_000,
    "D3": 24_000,
    "D4": 14_000,
    "R1": 16_000,
    "R6": 12_000,
    "library_authority_packet": 15_000,
}

BASE_STYLE_GUIDES = {
    ("ko", "korea"): CONVENTION_REFERENCES / "style-guide-kr.md",
    ("ko", "international"): CONVENTION_REFERENCES / "style-guide-kr.md",
    ("en", "us"): CONVENTION_REFERENCES / "style-guide-en-us.md",
    ("en", "uk"): CONVENTION_REFERENCES / "style-guide-en-uk.md",
    ("en", "international"): CONVENTION_REFERENCES / "style-guide-en-intl.md",
}


def build_context_plan(
    *,
    step: str,
    document_type: str,
    target_language: str,
    jurisdiction: str,
    mode: str | None = None,
) -> dict[str, Any]:
    """Return the minimal reference set for one pipeline step."""
    resolved_step = step.strip()
    language = _normalize_language(target_language)
    normalized_jurisdiction = _normalize_jurisdiction(jurisdiction)
    normalized_type = _normalize_document_type(document_type)

    references: list[str] = []
    optional_references: list[str] = []
    notes: list[str] = []

    if resolved_step == "D1":
        references.extend(
            [
                "docs/policies/context-budget.md",
                "docs/policies/drafting-scope.md",
                ".claude/skills/request-interpreter/references/document-type-registry.md",
                ".claude/skills/request-interpreter/references/parameter-schema.md",
            ]
        )
    elif resolved_step == "D2":
        style_profile = select_style_profile(
            target_language=language,
            jurisdiction=normalized_jurisdiction,
            document_type=normalized_type,
        )
        references.extend(
            [
                "docs/policies/context-budget.md",
                str(style_profile),
                str(_template_path(normalized_type, language)),
            ]
        )
        if language == "ko" and normalized_jurisdiction == "korea" and normalized_type == "advisory":
            optional_references.append("docs/_private/ko-legal-opinion-style-guide.md")
            notes.append("Korean advisory work loads the private opinion supplement when present.")
    elif resolved_step == "D3":
        references.extend(
            [
                "docs/policies/context-budget.md",
                ".claude/skills/legal-drafter/references/defined-term-rules.md",
                ".claude/skills/legal-drafter/references/placeholder-format.md",
                str(select_style_profile(
                    target_language=language,
                    jurisdiction=normalized_jurisdiction,
                    document_type=normalized_type,
                )),
            ]
        )
        references.append(
            ".claude/skills/legal-drafter/references/register-guide-kr.md"
            if language == "ko"
            else ".claude/skills/legal-drafter/references/register-guide-en.md"
        )
    elif resolved_step == "D4":
        references.extend(
            [
                "docs/policies/context-budget.md",
                ".claude/skills/consistency-checker/references/consistency-checklist.md",
            ]
        )
    elif resolved_step == "R1":
        references.extend(
            [
                "docs/policies/context-budget.md",
                ".claude/skills/request-interpreter/references/parameter-schema.md",
                "tools/parsing/docx_parser.py",
            ]
        )
    elif resolved_step == "R6":
        references.extend(
            [
                "docs/policies/context-budget.md",
                "tools/revision/level_b.py",
                ".claude/skills/output-formatter/SKILL.md",
            ]
        )
    elif resolved_step == "library_authority_packet":
        references.append("docs/policies/context-budget.md")
        notes.append("Select top 5 chunks, about 500 tokens each, from retrieval metadata.")
    else:
        raise ValueError(f"unknown context step: {step}")

    if mode:
        references.append("docs/references/formatting-modes-reference.md")

    plan = {
        "schemaVersion": "1.0",
        "step": resolved_step,
        "documentType": normalized_type,
        "targetLanguage": language,
        "jurisdiction": normalized_jurisdiction,
        "mode": mode,
        "maxInjectedChars": STEP_BUDGETS[resolved_step],
        "references": _dedupe(references),
        "optionalReferences": _dedupe(optional_references),
        "forbiddenByDefault": [
            "legal-writing-formatting-guide.md",
            "unselected style-guide-* files",
            "docs/references/formatting-modes-reference.md unless mode is requested",
            "full source documents when parser artifacts or chunks suffice",
        ],
        "notes": notes,
    }
    plan["estimatedChars"] = estimate_plan_chars(plan)
    plan["withinBudget"] = plan["estimatedChars"] <= plan["maxInjectedChars"]
    return plan


def select_style_profile(*, target_language: str, jurisdiction: str, document_type: str) -> Path:
    language = _normalize_language(target_language)
    normalized_jurisdiction = _normalize_jurisdiction(jurisdiction)
    normalized_type = _normalize_document_type(document_type)
    candidates = [
        STYLE_PROFILE_DIR / f"{language}-{normalized_jurisdiction}-{normalized_type}.md",
        STYLE_PROFILE_DIR / f"{language}-{normalized_jurisdiction}-general.md",
    ]
    for candidate in candidates:
        if (ROOT / candidate).exists():
            return candidate
    return BASE_STYLE_GUIDES.get(
        (language, normalized_jurisdiction),
        BASE_STYLE_GUIDES.get((language, "international"), CONVENTION_REFERENCES / "style-guide-en-intl.md"),
    )


def estimate_plan_chars(plan: dict[str, Any]) -> int:
    total = 0
    for key in ("references", "optionalReferences"):
        for reference in plan.get(key, []):
            path = ROOT / reference
            if path.exists() and path.is_file():
                total += len(path.read_text(encoding="utf-8"))
    return total


def _template_path(document_type: str, language: str) -> Path:
    suffix = "kr" if language == "ko" else "en"
    return TEMPLATE_REFERENCES / f"template-{document_type}-{suffix}.md"


def _normalize_language(value: str) -> str:
    lowered = value.strip().lower()
    if lowered in {"korean", "kr", "ko", "한국어"}:
        return "ko"
    if lowered in {"english", "en"}:
        return "en"
    return lowered


def _normalize_jurisdiction(value: str) -> str:
    lowered = value.strip().lower()
    aliases = {
        "kr": "korea",
        "korean": "korea",
        "한국": "korea",
        "한국법": "korea",
        "usa": "us",
        "u.s.": "us",
        "united states": "us",
        "england": "uk",
        "international english": "international",
        "intl": "international",
    }
    return aliases.get(lowered, lowered or "international")


def _normalize_document_type(value: str) -> str:
    lowered = value.strip().lower()
    aliases = {
        "memo": "advisory",
        "legal opinion": "advisory",
        "opinion": "advisory",
        "corporation": "corporate",
        "lit": "litigation",
        "reg": "regulatory",
    }
    return aliases.get(lowered, lowered or "general")


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tools.context.budget",
        description="Build a minimal context-loading plan for one pipeline step.",
    )
    parser.add_argument("--step", required=True, choices=sorted(STEP_BUDGETS))
    parser.add_argument("--document-type", default="general")
    parser.add_argument("--target-language", default="ko")
    parser.add_argument("--jurisdiction", default="korea")
    parser.add_argument("--mode", help="optional Mode A-D reference trigger")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    plan = build_context_plan(
        step=args.step,
        document_type=args.document_type,
        target_language=args.target_language,
        jurisdiction=args.jurisdiction,
        mode=args.mode,
    )
    print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
