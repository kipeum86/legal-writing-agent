from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.context.budget import ROOT, build_context_plan, estimate_plan_chars, select_style_profile


def test_simple_korean_corporate_plan_excludes_unrelated_guides() -> None:
    plan = build_context_plan(
        step="D2",
        document_type="corporate",
        target_language="ko",
        jurisdiction="korea",
    )
    references = "\n".join(plan["references"] + plan["optionalReferences"])
    loaded_text = _plan_text(plan)
    baseline = len((ROOT / "CLAUDE.md").read_text(encoding="utf-8")) + len(
        (ROOT / "legal-writing-formatting-guide.md").read_text(encoding="utf-8")
    )

    assert ".claude/skills/convention-selector/style-profiles/ko-korea-corporate.md" in references
    assert ".claude/skills/structure-planner/references/template-corporate-kr.md" in references
    assert "style-guide-en-us" not in references
    assert "style-guide-en-uk" not in references
    assert "legal-writing-formatting-guide.md" not in references
    assert "Mode B" not in loaded_text
    assert estimate_plan_chars(plan) <= int(baseline * 0.6)
    assert plan["withinBudget"] is True


def test_korean_advisory_plan_loads_opinion_specific_supplement_only_as_optional() -> None:
    plan = build_context_plan(
        step="D2",
        document_type="advisory",
        target_language="ko",
        jurisdiction="korea",
    )
    references = "\n".join(plan["references"])
    optional = "\n".join(plan["optionalReferences"])

    assert ".claude/skills/convention-selector/style-profiles/ko-korea-advisory.md" in references
    assert ".claude/skills/structure-planner/references/template-advisory-kr.md" in references
    assert "docs/_private/ko-legal-opinion-style-guide.md" in optional
    assert "style-guide-en-uk" not in references
    assert "formatting-modes-reference.md" not in references
    assert plan["withinBudget"] is True


def test_d1_plan_uses_registry_and_scope_without_style_payloads() -> None:
    plan = build_context_plan(
        step="D1",
        document_type="corporate",
        target_language="ko",
        jurisdiction="korea",
    )
    references = "\n".join(plan["references"])

    assert "document-type-registry.md" in references
    assert "drafting-scope.md" in references
    assert "style-guide" not in references
    assert "style-profiles" not in references
    assert plan["withinBudget"] is True


def test_style_profile_falls_back_to_smallest_base_guide_when_exact_missing() -> None:
    profile = select_style_profile(
        target_language="en",
        jurisdiction="us",
        document_type="corporate",
    )

    assert profile == Path(".claude/skills/convention-selector/references/style-guide-en-us.md")


def test_context_budget_cli_emits_json_plan() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.context.budget",
            "--step",
            "D2",
            "--document-type",
            "corporate",
            "--target-language",
            "ko",
            "--jurisdiction",
            "korea",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["step"] == "D2"
    assert payload["withinBudget"] is True


def test_default_prompt_docs_do_not_embed_mode_or_unselected_style_payloads() -> None:
    formatting_guide = (ROOT / "legal-writing-formatting-guide.md").read_text(encoding="utf-8")
    selector = (ROOT / ".claude/skills/convention-selector/SKILL.md").read_text(encoding="utf-8")

    assert "### 20. Mode B" not in formatting_guide
    assert "### 21. Mode C" not in formatting_guide
    assert "### 22. Mode D" not in formatting_guide
    assert "style-guide-en-uk)" not in selector
    assert "Bluebook. Statutes" not in selector


def _plan_text(plan: dict[str, object]) -> str:
    text = []
    for reference in plan["references"]:  # type: ignore[index]
        path = ROOT / str(reference)
        if path.exists():
            text.append(path.read_text(encoding="utf-8"))
    return "\n".join(text)
