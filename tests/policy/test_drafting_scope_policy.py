from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

SCOPE_POLICY = "docs/policies/drafting-scope.md"
COUNSEL_PLACEHOLDERS = [
    "[Counsel conclusion needed: {issue}]",
    "[Counsel certainty needed: {issue}]",
    "[Counsel risk assessment needed: {issue}]",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_scope_policy_defines_counsel_placeholders() -> None:
    policy = read(SCOPE_POLICY)

    for placeholder in COUNSEL_PLACEHOLDERS:
        assert placeholder in policy

    assert "must not assign its own certainty level" in policy
    assert "Unsafe inference must become a placeholder or a clarification question" in policy


def test_core_prompts_reference_scope_policy_and_placeholders() -> None:
    paths = [
        "CLAUDE.md",
        ".claude/skills/request-interpreter/SKILL.md",
        ".claude/skills/request-interpreter/references/parameter-schema.md",
        ".claude/skills/legal-drafter/SKILL.md",
        ".claude/skills/legal-drafter/references/placeholder-format.md",
        ".claude/skills/structure-planner/references/template-advisory-en.md",
        ".claude/skills/structure-planner/references/template-advisory-kr.md",
    ]

    for path in paths:
        text = read(path)
        assert SCOPE_POLICY in text, path
        assert "[Counsel conclusion needed:" in text, path
        assert "[Counsel certainty needed:" in text, path
        assert "[Counsel risk assessment needed:" in text, path


def test_request_manifest_records_safe_and_unsafe_inference() -> None:
    interpreter = read(".claude/skills/request-interpreter/SKILL.md")
    schema = read(".claude/skills/request-interpreter/references/parameter-schema.md")

    for text in (interpreter, schema):
        assert '"safeInference"' in text
        assert '"unsafeInference"' in text
        assert "placeholder | clarification_required" in text or "placeholder|clarification_required" in text


def test_corporate_registry_is_subtype_specific() -> None:
    registry = read(".claude/skills/request-interpreter/references/document-type-registry.md")

    assert "**Support Level**: Mixed" in registry
    assert "Simple board resolution" in registry
    assert "Simple shareholders meeting minutes" in registry
    assert "| 정관 | Articles of incorporation / bylaws | Conditional | Yes |" in registry
    assert "Internal regulations / company policies" in registry
    assert "Organizational regulations" in registry


def test_style_guides_do_not_override_drafting_scope() -> None:
    public_style = read("legal-writing-formatting-guide.md")

    assert SCOPE_POLICY in public_style
    assert "formatting convention only" in public_style

    private_style_path = ROOT / "docs/_private/ko-legal-opinion-style-guide.md"
    if private_style_path.exists():
        private_style = private_style_path.read_text(encoding="utf-8")
        assert "Drafting-scope override" in private_style
        assert "`counselProvidedCertainty`" in private_style
        assert "[Counsel certainty needed: {issue}]" in private_style


def test_skeleton_only_examples_are_available() -> None:
    examples = read("docs/examples/skeleton-only-examples.md")

    assert "Example 1: Advisory Memo Without Authority Packet" in examples
    assert "Example 2: Conditional Corporate Bylaws Draft" in examples
    assert "[Counsel conclusion needed:" in examples
    assert "[Counsel certainty needed:" in examples
    assert "[Counsel risk assessment needed:" in examples
    assert "[Authority needed:" in examples
