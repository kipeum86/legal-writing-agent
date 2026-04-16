"""Prompt-injection pattern catalog.

The catalog is intentionally conservative. False positives are acceptable;
false negatives are not. Every match is wrapped as <escape>MATCH</escape>
in the sanitized output — it is NOT removed. Reviewers keep context.

Patterns are grouped so the audit JSON can explain why each match triggered.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Pattern


@dataclass(frozen=True)
class InjectionPattern:
    name: str
    language: str
    category: str
    regex: Pattern[str]
    description: str


def _compile(pattern: str, flags: int = 0) -> Pattern[str]:
    return re.compile(pattern, flags | re.MULTILINE)


ROLE_MARKERS: tuple[InjectionPattern, ...] = (
    InjectionPattern(
        name="role_marker_square_system",
        language="multi",
        category="role-marker",
        regex=_compile(r"\[\s*(SYSTEM|SYS|USER|ASSISTANT|AI|HUMAN|TOOL)\s*\]", re.IGNORECASE),
        description="Forged role marker in square brackets.",
    ),
    InjectionPattern(
        name="role_marker_chatml",
        language="multi",
        category="role-marker",
        regex=_compile(
            r"<\|(?:im_start|im_end|system|user|assistant|endoftext)\|>(?:\s*(?:system|user|assistant|tool))?",
            re.IGNORECASE,
        ),
        description="ChatML / OpenAI-style turn marker.",
    ),
    InjectionPattern(
        name="role_marker_markdown_heading",
        language="multi",
        category="role-marker",
        regex=_compile(r"^#{1,3}\s*(System|User|Assistant|Human|AI)\s*:", re.IGNORECASE),
        description="Forged role heading at start of line.",
    ),
    InjectionPattern(
        name="role_marker_prefix",
        language="multi",
        category="role-marker",
        regex=_compile(r"^(System|User|Assistant|Human|AI)\s*:\s", re.IGNORECASE),
        description="Line-leading role prefix.",
    ),
    InjectionPattern(
        name="role_marker_ko",
        language="ko",
        category="role-marker",
        regex=_compile(r"\[\s*(시스템|사용자|유저|어시스턴트|AI)\s*\]"),
        description="Forged Korean role marker.",
    ),
)


JAILBREAK: tuple[InjectionPattern, ...] = (
    InjectionPattern(
        name="jailbreak_ignore_previous_en",
        language="en",
        category="jailbreak",
        regex=_compile(
            r"\bignore\s+(all\s+)?(previous|prior|above|preceding)\s+(instructions?|prompts?|messages?|rules?)\b",
            re.IGNORECASE,
        ),
        description="Classic 'ignore previous instructions' variant.",
    ),
    InjectionPattern(
        name="jailbreak_disregard_en",
        language="en",
        category="jailbreak",
        regex=_compile(r"\bdisregard\s+(the\s+)?(above|prior|previous|system)\b", re.IGNORECASE),
        description="'Disregard the above…' variant.",
    ),
    InjectionPattern(
        name="jailbreak_new_instructions_en",
        language="en",
        category="jailbreak",
        regex=_compile(r"\b(new|updated|revised)\s+instructions?\s*:", re.IGNORECASE),
        description="Forged 'New instructions:' header.",
    ),
    InjectionPattern(
        name="jailbreak_reveal_prompt_en",
        language="en",
        category="jailbreak",
        regex=_compile(
            r"\b(reveal|print|show|output|repeat|echo)\s+(the\s+)?(system\s+prompt|initial\s+prompt|hidden\s+prompt|your\s+instructions)\b",
            re.IGNORECASE,
        ),
        description="Attempt to exfiltrate the system prompt.",
    ),
    InjectionPattern(
        name="jailbreak_roleplay_en",
        language="en",
        category="jailbreak",
        regex=_compile(r"\byou\s+are\s+now\s+(a|an|the)\s+", re.IGNORECASE),
        description="Persona-replacement attempt.",
    ),
    InjectionPattern(
        name="jailbreak_developer_mode_en",
        language="en",
        category="jailbreak",
        regex=_compile(r"\b(developer|debug|dev|sudo|god|admin|jailbreak)\s+mode\b", re.IGNORECASE),
        description="'Developer mode' / 'sudo mode' trope.",
    ),
    InjectionPattern(
        name="jailbreak_ignore_previous_ko",
        language="ko",
        category="jailbreak",
        regex=_compile(r"(이전|앞의|위의)\s*(지시|명령|규칙|프롬프트)(사항|을|를)?\s*(무시|잊)"),
        description="Korean 'ignore previous instructions' variant.",
    ),
    InjectionPattern(
        name="jailbreak_new_instructions_ko",
        language="ko",
        category="jailbreak",
        regex=_compile(r"(새로운|업데이트된|변경된)\s*(지시|명령|규칙)"),
        description="Korean 'new instructions' header.",
    ),
    InjectionPattern(
        name="jailbreak_reveal_prompt_ko",
        language="ko",
        category="jailbreak",
        regex=_compile(r"(시스템\s*프롬프트|원래\s*지시사항|초기\s*프롬프트)\s*(보여|출력|공개|알려)"),
        description="Korean prompt-exfiltration attempt.",
    ),
    InjectionPattern(
        name="jailbreak_roleplay_ko",
        language="ko",
        category="jailbreak",
        regex=_compile(r"(당신은|너는)\s*(이제|지금부터)\s*"),
        description="Korean persona-replacement prefix.",
    ),
)


AUDIENCE_FIREWALL: tuple[InjectionPattern, ...] = (
    InjectionPattern(
        name="audience_firewall_end_system",
        language="multi",
        category="audience-firewall",
        regex=_compile(r"(end of\s+(system\s+prompt|instructions|rules))|(-{3,}\s*END OF SYSTEM\s*-{3,})", re.IGNORECASE),
        description="Forged 'end of system prompt' banner.",
    ),
    InjectionPattern(
        name="audience_firewall_begin_user",
        language="multi",
        category="audience-firewall",
        regex=_compile(r"(begin\s+(user|new)\s+input)|(-{3,}\s*BEGIN USER\s*-{3,})", re.IGNORECASE),
        description="Forged 'begin user input' banner.",
    ),
    InjectionPattern(
        name="audience_firewall_jinju_specific",
        language="multi",
        category="audience-firewall",
        regex=_compile(r"(end\s+of\s+CLAUDE\.md|end\s+of\s+SKILL\.md|END\s+OF\s+CONSTRAINTS)", re.IGNORECASE),
        description="Attempts to fake the end of this repo's rule docs.",
    ),
)


ROLE_TAGS: tuple[InjectionPattern, ...] = (
    InjectionPattern(
        name="role_tag_xml_pair",
        language="multi",
        category="role-tag",
        regex=_compile(
            r"<(system|user|assistant|tool|function|persona|role|admin)[^>]*>.*?</\1>",
            re.IGNORECASE,
        ),
        description="Paired XML-ish role/tool tag.",
    ),
    InjectionPattern(
        name="role_tag_xml",
        language="multi",
        category="role-tag",
        regex=_compile(r"</?(system|user|assistant|tool|function|persona|role|admin)[^>]*>", re.IGNORECASE),
        description="XML-ish role/tool tag.",
    ),
    InjectionPattern(
        name="role_tag_claude_antml",
        language="multi",
        category="role-tag",
        regex=_compile(r"</?antml[:a-zA-Z0-9_]*[^>]*>", re.IGNORECASE),
        description="Forged Anthropic-style tag (antml:*).",
    ),
)


ALL_PATTERNS: tuple[InjectionPattern, ...] = (
    *ROLE_MARKERS,
    *JAILBREAK,
    *AUDIENCE_FIREWALL,
    *ROLE_TAGS,
)
