#!/usr/bin/env python3
"""
Register (formality) compliance validator for Korean and English legal documents.

Checks that legal documents maintain appropriate formality levels by detecting
colloquial language, informal expressions, and stylistic issues that are
inappropriate for legal writing.

Usage:
    python register-validator.py <file.md>

Output:
    JSON report to stdout with validation results.
"""

import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Korean register patterns
# ---------------------------------------------------------------------------

# Critical: Colloquial sentence endings
KOREAN_COLLOQUIAL_ENDINGS = [
    (r"거든요", "~거든요 (colloquial ending)"),
    (r"잖아요", "~잖아요 (colloquial ending)"),
    (r"인데요", "~인데요 (colloquial ending)"),
    (r"같아요", "~같아요 (colloquial ending)"),
    (r"할\s*거예요", "~할 거예요 (colloquial ending)"),
    (r"할게요", "~할게요 (colloquial ending)"),
    (r"하죠", "~하죠 (colloquial ending)"),
    (r"네요", "~네요 (colloquial ending)"),
    (r"군요", "~군요 (colloquial ending)"),
    (r"데요", "~데요 (colloquial ending)"),
]

# Major: Informal adverbs
KOREAN_INFORMAL_ADVERBS = [
    (r"(?<!\S)좀(?!\S|합|족)", "좀 (informal adverb)"),
    (r"(?<!\S)되게(?!\S)", "되게 (informal adverb)"),
    (r"(?<!\S)진짜(?!\S)", "진짜 (informal adverb)"),
    (r"(?<!\S)약간(?!\S)", "약간 (informal adverb)"),
    (r"(?<!\S)엄청(?!\S)", "엄청 (informal adverb)"),
    (r"(?<!\S)완전(?!\S)", "완전 (informal adverb)"),
    (r"(?<!\S)별로(?!\S)", "별로 (informal adverb)"),
    (r"(?<!\S)그냥(?!\S)", "그냥 (informal adverb)"),
    (r"(?<!\S)막(?!\S|대|론|아|을|는|이|다|히)", "막 (informal adverb)"),
]

# Major: Informal connectors at sentence start
KOREAN_INFORMAL_CONNECTORS = [
    (r"(?:^|(?<=\.\s)|(?<=\.\n))근데", "근데 (informal connector; use 그러나/그런데)"),
    (r"(?:^|(?<=\.\s)|(?<=\.\n))그래서(?=\s)", "그래서 at sentence start (informal; use 따라서/이에)"),
    (r"(?:^|(?<=\.\s)|(?<=\.\n))그리고(?=\s)", "그리고 at sentence start (informal; use 또한/아울러)"),
    (r"(?:^|(?<=\.\s)|(?<=\.\n))그래도(?=\s)", "그래도 at sentence start (informal; use 그럼에도 불구하고)"),
]

# Major: Double passives (이중 피동)
KOREAN_DOUBLE_PASSIVES = [
    (r"되어지다|되어진|되어지는|되어지고|되어져", "되어지다 (double passive; use 되다)"),
    (r"만들어지다|만들어진|만들어지는|만들어지고|만들어져", "만들어지다 (double passive; use 만들다/제작되다)"),
    (r"쓰여지다|쓰여진|쓰여지는|쓰여지고|쓰여져", "쓰여지다 (double passive; use 쓰이다)"),
    (r"보여지다|보여진|보여지는|보여지고|보여져", "보여지다 (double passive; use 보이다)"),
    (r"읽혀지다|읽혀진|읽혀지는|읽혀지고|읽혀져", "읽혀지다 (double passive; use 읽히다)"),
]

# Minor: Translation-style expressions (번역투)
KOREAN_TRANSLATION_STYLE = [
    (r"하는\s*것이\s*가능하다|하는\s*것이\s*가능한", "~하는 것이 가능하다 (번역투; rephrase natively)"),
    (r"에\s*의해\s*되어지", "~에 의해 ~되어지다 (번역투 + double passive)"),
    (r"에\s*의해서?\s+\w*되", "~에 의해 ~되다 (번역투; consider active voice)"),
    (r"것이\s*필요하다|것이\s*필요한", "~것이 필요하다 (번역투; rephrase with ~해야 한다)"),
    (r"것으로\s*사료된다|것으로\s*판단된다", "~것으로 사료/판단된다 (bureaucratic 번역투)"),
]

# Minor: Informal hedging expressions
KOREAN_INFORMAL_EXPRESSIONS = [
    (r"한\s*것\s*같다|한\s*것\s*같습니다", "~한 것 같다 (informal hedging; state directly)"),
    (r"라고\s*생각하다|라고\s*생각합니다|라고\s*생각한다", "~라고 생각하다 (informal; use ~로 판단된다/~로 사료된다)"),
    (r"하면\s*좋겠다|하면\s*좋겠습니다", "~하면 좋겠다 (informal wish; use ~할 필요가 있다/~하여야 한다)"),
]


# ---------------------------------------------------------------------------
# English register patterns
# ---------------------------------------------------------------------------

# Critical: Contractions
ENGLISH_CONTRACTIONS = [
    (r"\bcan'?t\b", "can't (contraction; use 'cannot')"),
    (r"\bwon'?t\b", "won't (contraction; use 'will not')"),
    (r"\bdoesn'?t\b", "doesn't (contraction; use 'does not')"),
    (r"\bisn'?t\b", "isn't (contraction; use 'is not')"),
    (r"\baren'?t\b", "aren't (contraction; use 'are not')"),
    (r"\bwasn'?t\b", "wasn't (contraction; use 'was not')"),
    (r"\bweren'?t\b", "weren't (contraction; use 'were not')"),
    (r"\bdon'?t\b", "don't (contraction; use 'do not')"),
    (r"\bdidn'?t\b", "didn't (contraction; use 'did not')"),
    (r"\bcouldn'?t\b", "couldn't (contraction; use 'could not')"),
    (r"\bshouldn'?t\b", "shouldn't (contraction; use 'should not')"),
    (r"\bwouldn'?t\b", "wouldn't (contraction; use 'would not')"),
    (r"\bhaven'?t\b", "haven't (contraction; use 'have not')"),
    (r"\bhasn'?t\b", "hasn't (contraction; use 'has not')"),
    (r"\bhadn'?t\b", "hadn't (contraction; use 'had not')"),
    (r"\bit'?s\b", "it's (contraction; use 'it is' or 'it has')"),
    (r"\bthat'?s\b", "that's (contraction; use 'that is')"),
    (r"\bthere'?s\b", "there's (contraction; use 'there is')"),
    (r"\bwho'?s\b", "who's (contraction; use 'who is' or 'who has')"),
    (r"\blet'?s\b", "let's (contraction; use 'let us')"),
    (r"\bI'?m\b", "I'm (contraction; use 'I am')"),
    (r"\bI'?ve\b", "I've (contraction; use 'I have')"),
    (r"\bI'?ll\b", "I'll (contraction; use 'I will')"),
    (r"\bI'?d\b", "I'd (contraction; use 'I would' or 'I had')"),
    (r"\bwe'?re\b", "we're (contraction; use 'we are')"),
    (r"\bwe'?ve\b", "we've (contraction; use 'we have')"),
    (r"\bwe'?ll\b", "we'll (contraction; use 'we will')"),
    (r"\bthey'?re\b", "they're (contraction; use 'they are')"),
    (r"\bthey'?ve\b", "they've (contraction; use 'they have')"),
    (r"\bthey'?ll\b", "they'll (contraction; use 'they will')"),
    (r"\byou'?re\b", "you're (contraction; use 'you are')"),
    (r"\byou'?ve\b", "you've (contraction; use 'you have')"),
    (r"\byou'?ll\b", "you'll (contraction; use 'you will')"),
]

# Major: Informal words and phrases
ENGLISH_INFORMAL_WORDS = [
    (r"\bkind\s+of\b", "'kind of' (informal; use 'somewhat' or remove)"),
    (r"\bsort\s+of\b", "'sort of' (informal; use 'somewhat' or remove)"),
    (r"\ba\s+lot\s+of\b", "'a lot of' (informal; use 'numerous', 'many', or 'significant')"),
    (r"\bbasically\b", "'basically' (informal filler; remove or rephrase)"),
    (r"\bessentially\b", "'essentially' (informal filler; remove or rephrase)"),
    (r"\bactually\b", "'actually' (informal filler; remove or rephrase)"),
    (r"\breally\b", "'really' (informal intensifier; remove or use precise language)"),
    (r"\bpretty\s+much\b", "'pretty much' (informal; use 'substantially' or 'largely')"),
    (r"\bstuff\b", "'stuff' (informal; use specific terminology)"),
    (r"(?<!\breal\s)\bthings\b(?!\s+that|\s+which)", "'things' (vague; use specific terminology)"),
    (r"\bgonna\b", "'gonna' (informal; use 'going to')"),
    (r"\bwanna\b", "'wanna' (informal; use 'want to')"),
    (r"\bgotta\b", "'gotta' (informal; use 'have to' or 'must')"),
    (r"\b(?:get|got|gotten)\b(?!\s+(?:up|down|in|out|off|on|into|onto|through|over|under|around|away|back|along|ahead|behind|beyond|across|between|within|without))",
     "'get/got' (informal in legal context; use precise verb)"),
    (r"\bokay\b|\bok\b", "'okay/ok' (informal; use 'acceptable' or 'satisfactory')"),
    (r"\banyway\b", "'anyway' (informal; remove or rephrase)"),
    (r"\bplus\b(?!\s*[-\d])", "'plus' as conjunction (informal; use 'additionally' or 'moreover')"),
]

# Minor: Legalese that should be simplified
ENGLISH_LEGALESE = [
    (r"\bprior\s+to\b", "'prior to' (legalese; consider 'before')"),
    (r"\bsubsequent\s+to\b", "'subsequent to' (legalese; consider 'after')"),
    (r"\bin\s+the\s+event\s+that\b", "'in the event that' (legalese; consider 'if')"),
    (r"\bat\s+this\s+point\s+in\s+time\b", "'at this point in time' (legalese; consider 'now' or 'currently')"),
    (r"\bit\s+is\s+important\s+to\s+note\s+that\b", "'it is important to note that' (legalese; state the point directly)"),
    (r"\bhereinabove\b", "'hereinabove' (archaic legalese; use 'above' or specific reference)"),
    (r"\bhereinafter\b", "'hereinafter' (archaic legalese; use 'below' or specific reference)"),
    (r"\bhereinbefore\b", "'hereinbefore' (archaic legalese; use 'above' or specific reference)"),
    (r"\bwhereas\b", "'whereas' (archaic legalese; consider rephrasing)"),
    (r"\bwherein\b", "'wherein' (archaic legalese; consider 'in which' or 'where')"),
    (r"\bnotwithstanding\s+the\s+foregoing\b", "'notwithstanding the foregoing' (legalese; simplify)"),
    (r"\bin\s+accordance\s+with\b", "'in accordance with' (legalese; consider 'under' or 'following')"),
    (r"\bfor\s+the\s+purpose\s+of\b", "'for the purpose of' (legalese; consider 'to')"),
    (r"\bwith\s+respect\s+to\b", "'with respect to' (legalese; consider 'about' or 'regarding')"),
    (r"\bin\s+connection\s+with\b", "'in connection with' (legalese; consider 'about' or 'regarding')"),
]

# Minor: "shall" usage
ENGLISH_SHALL = [
    (r"\bshall\b", "'shall' (consider 'must' for obligations per modern drafting style)"),
]


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

def detect_language(text: str) -> str:
    """Detect whether the document is primarily Korean or English."""
    korean_chars = len(re.findall(r"[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f\ua960-\ua97f\ud7b0-\ud7ff]", text))
    latin_chars = len(re.findall(r"[a-zA-Z]", text))
    total = korean_chars + latin_chars
    if total == 0:
        return "unknown"
    if korean_chars / total > 0.3:
        return "ko"
    return "en"


# ---------------------------------------------------------------------------
# Sentence utilities
# ---------------------------------------------------------------------------

def split_sentences_korean(text: str) -> list[str]:
    """Split Korean text into sentences."""
    sentences = re.split(r"(?<=[.!?。])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def split_sentences_english(text: str) -> list[str]:
    """Split English text into sentences."""
    # Remove markdown headings, list markers, etc.
    clean = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    clean = re.sub(r"^[-*]\s+", "", clean, flags=re.MULTILINE)
    clean = re.sub(r"^\d+\.\s+", "", clean, flags=re.MULTILINE)
    sentences = re.split(r"(?<=[.!?])\s+", clean)
    return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]


def is_passive_english(sentence: str) -> bool:
    """Heuristic check for passive voice in an English sentence."""
    passive_pattern = (
        r"\b(?:is|are|was|were|be|been|being|am)\s+"
        r"(?:\w+\s+)*?"
        r"(?:\w+ed|(?:taken|given|made|done|seen|known|found|told|shown|written|"
        r"held|brought|kept|set|run|put|paid|sent|built|left|understood|read|"
        r"born|cut|grown|drawn|chosen|fallen|spoken|broken|driven|forgotten|"
        r"hidden|ridden|risen|shaken|stolen|sworn|torn|worn|woven|frozen|"
        r"struck|begun|drunk|rung|sung|sunk|swum|thrown|withdrawn))\b"
    )
    return bool(re.search(passive_pattern, sentence, re.IGNORECASE))


def word_count(sentence: str) -> int:
    """Count words in a sentence."""
    return len(re.findall(r"\b\w+\b", sentence))


# ---------------------------------------------------------------------------
# Pattern scanning
# ---------------------------------------------------------------------------

def find_pattern_issues(text: str, patterns: list[tuple], issue_type: str,
                        severity: str, lang: str) -> list[dict]:
    """Scan text for regex pattern matches and return issue dicts."""
    issues = []
    lines = text.split("\n")
    for line_num, line in enumerate(lines, start=1):
        for pattern, description in patterns:
            flags = re.IGNORECASE if lang == "en" else 0
            for match in re.finditer(pattern, line, flags):
                matched_text = match.group(0)
                col = match.start() + 1
                suggestion = ""
                # Extract suggestion from description if present
                if ";" in description:
                    suggestion = description.split(";", 1)[1].strip()
                elif "consider" in description.lower():
                    suggestion = description
                issues.append({
                    "type": issue_type,
                    "severity": severity,
                    "text": matched_text,
                    "position": {"line": line_num, "column": col},
                    "suggestion": suggestion if suggestion else f"Review and revise: {description}",
                })
    return issues


# ---------------------------------------------------------------------------
# Korean validation
# ---------------------------------------------------------------------------

def validate_korean(text: str) -> list[dict]:
    """Run all Korean register checks."""
    issues = []

    # Critical: colloquial endings
    issues.extend(find_pattern_issues(
        text, KOREAN_COLLOQUIAL_ENDINGS,
        "colloquial_ending", "critical", "ko"
    ))

    # Major: informal adverbs
    issues.extend(find_pattern_issues(
        text, KOREAN_INFORMAL_ADVERBS,
        "informal_adverb", "major", "ko"
    ))

    # Major: informal connectors
    issues.extend(find_pattern_issues(
        text, KOREAN_INFORMAL_CONNECTORS,
        "informal_connector", "major", "ko"
    ))

    # Major: double passives
    issues.extend(find_pattern_issues(
        text, KOREAN_DOUBLE_PASSIVES,
        "double_passive", "major", "ko"
    ))

    # Minor: translation-style expressions
    issues.extend(find_pattern_issues(
        text, KOREAN_TRANSLATION_STYLE,
        "translation_style", "minor", "ko"
    ))

    # Minor: informal hedging
    issues.extend(find_pattern_issues(
        text, KOREAN_INFORMAL_EXPRESSIONS,
        "informal_expression", "minor", "ko"
    ))

    return issues


# ---------------------------------------------------------------------------
# English validation
# ---------------------------------------------------------------------------

def validate_english(text: str) -> list[dict]:
    """Run all English register checks."""
    issues = []

    # Critical: contractions
    issues.extend(find_pattern_issues(
        text, ENGLISH_CONTRACTIONS,
        "contraction", "critical", "en"
    ))

    # Major: informal words
    issues.extend(find_pattern_issues(
        text, ENGLISH_INFORMAL_WORDS,
        "informal_word", "major", "en"
    ))

    # Minor: legalese
    issues.extend(find_pattern_issues(
        text, ENGLISH_LEGALESE,
        "legalese", "minor", "en"
    ))

    # Minor: shall usage
    issues.extend(find_pattern_issues(
        text, ENGLISH_SHALL,
        "shall_usage", "minor", "en"
    ))

    # Passive voice overuse analysis
    sentences = split_sentences_english(text)
    if sentences:
        passive_count = sum(1 for s in sentences if is_passive_english(s))
        passive_ratio = passive_count / len(sentences)
        if passive_ratio > 0.4:
            issues.append({
                "type": "passive_voice_overuse",
                "severity": "minor",
                "text": f"{passive_count}/{len(sentences)} sentences ({passive_ratio:.0%}) use passive voice",
                "position": {"line": 0, "column": 0},
                "suggestion": (
                    f"Passive voice detected in {passive_ratio:.0%} of sentences "
                    f"(threshold: 40%). Consider converting some passive constructions "
                    f"to active voice for clarity."
                ),
            })

    # Sentence length analysis
    if sentences:
        total_words = sum(word_count(s) for s in sentences)
        avg_length = total_words / len(sentences)
        if avg_length > 30:
            # Also find the longest sentences
            long_sentences = []
            lines = text.split("\n")
            for line_num, line in enumerate(lines, start=1):
                line_sentences = split_sentences_english(line)
                for s in line_sentences:
                    wc = word_count(s)
                    if wc > 40:
                        long_sentences.append((line_num, wc, s[:80]))

            issues.append({
                "type": "sentence_length",
                "severity": "minor",
                "text": f"Average sentence length: {avg_length:.1f} words (threshold: 30)",
                "position": {"line": 0, "column": 0},
                "suggestion": (
                    f"Average sentence length is {avg_length:.1f} words. "
                    f"Consider breaking long sentences for readability. "
                    f"Found {len(long_sentences)} sentence(s) exceeding 40 words."
                ),
            })

    return issues


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def validate_file(filepath: str) -> dict:
    """Validate a file and return the JSON report dict."""
    path = Path(filepath)
    if not path.exists():
        return {
            "file": filepath,
            "language": "unknown",
            "issueCount": 0,
            "issues": [],
            "status": "error",
            "error": f"File not found: {filepath}",
        }

    text = path.read_text(encoding="utf-8")
    language = detect_language(text)

    if language == "ko":
        issues = validate_korean(text)
    elif language == "en":
        issues = validate_english(text)
    else:
        # Try both
        issues = validate_korean(text) + validate_english(text)

    # Determine pass/fail: fail if any critical or major issues exist
    has_critical = any(i["severity"] == "critical" for i in issues)
    has_major = any(i["severity"] == "major" for i in issues)
    status = "fail" if (has_critical or has_major) else "pass"

    # Sort issues by severity priority then line number
    severity_order = {"critical": 0, "major": 1, "minor": 2}
    issues.sort(key=lambda i: (severity_order.get(i["severity"], 9), i["position"]["line"]))

    return {
        "file": str(path),
        "language": language,
        "issueCount": len(issues),
        "issues": issues,
        "status": status,
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python register-validator.py <file.md>",
            "status": "error",
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

    filepath = sys.argv[1]
    report = validate_file(filepath)
    print(json.dumps(report, indent=2, ensure_ascii=False))

    # Exit with non-zero if validation failed
    if report["status"] == "fail":
        sys.exit(1)
    elif report["status"] == "error":
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
