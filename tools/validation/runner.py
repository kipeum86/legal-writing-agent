"""Release-gate validation runner for generated legal drafts.

This module wraps the existing deterministic validators and emits a single
versioned validation report. It deliberately treats validator failures as data:
all failures are normalized into findings, then the severity x review intensity
rule decides whether rendering or delivery should be blocked.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.artifacts import schemas
from tools.artifacts.store import ArtifactStore


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_DIR = ROOT / ".claude" / "skills" / "consistency-checker" / "scripts"

DEFAULT_VALIDATORS = ("numbering", "cross_reference", "register", "term", "citation")
SEVERITY_ORDER = {"critical": 0, "major": 1, "minor": 2}
BLOCKING_BY_INTENSITY = {
    "light": {"critical"},
    "standard": {"critical", "major"},
    "thorough": {"critical", "major", "minor"},
}

CANONICAL_PLACEHOLDER_RE = re.compile(
    r"^\[(?:"
    r"Citation needed: .+|"
    r"Authority needed: .+|"
    r"Argument: .+|"
    r"Factual basis needed|"
    r"Counsel conclusion needed: .+|"
    r"Counsel certainty needed: .+|"
    r"Counsel risk assessment needed: .+|"
    r"Convention Note: .+|"
    r"Drafting Gap: .+|"
    r"Insert [^\]]+|"
    r"[^\]]+ needed"
    r")\]$"
)
BRACKET_PLACEHOLDER_RE = re.compile(r"\[[^\]\n]{2,200}\]")


@dataclass(frozen=True)
class ValidatorSpec:
    name: str
    script: Path

    def command(self, document: Path, *, jurisdiction: str) -> list[str]:
        command = [sys.executable, str(self.script), str(document)]
        if self.name == "citation":
            command.extend(["--jurisdiction", jurisdiction])
        return command


VALIDATOR_SPECS = {
    "numbering": ValidatorSpec("numbering", VALIDATOR_DIR / "numbering-validator.py"),
    "cross_reference": ValidatorSpec("cross_reference", VALIDATOR_DIR / "cross-reference-checker.py"),
    "register": ValidatorSpec("register", VALIDATOR_DIR / "register-validator.py"),
    "term": ValidatorSpec("term", VALIDATOR_DIR / "term-consistency-checker.py"),
    "citation": ValidatorSpec("citation", VALIDATOR_DIR / "citation-format-checker.py"),
}


def is_blocking(severity: str, review_intensity: str) -> bool:
    return severity.lower() in BLOCKING_BY_INTENSITY[review_intensity]


def run_validation(
    document: Path,
    *,
    manifest_path: Path | None = None,
    placeholder_registry_path: Path | None = None,
    false_positive_labels_path: Path | None = None,
    review_intensity: str | None = None,
    validators: tuple[str, ...] = DEFAULT_VALIDATORS,
) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path)
    document_id = manifest.get("documentId") or schemas.new_document_id()
    resolved_intensity = review_intensity or manifest.get("reviewIntensity") or "standard"
    if resolved_intensity not in BLOCKING_BY_INTENSITY:
        raise ValueError(f"review intensity must be one of {sorted(BLOCKING_BY_INTENSITY)}")

    jurisdiction = _jurisdiction_for_citation(manifest.get("jurisdiction"))
    labels = _load_false_positive_labels(false_positive_labels_path)

    checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for validator_name in validators:
        check = _run_validator(validator_name, document, jurisdiction=jurisdiction)
        checks.append(check)
        for issue in check["issues"]:
            findings.append(_normalize_issue(validator_name, issue, resolved_intensity, labels))

    registry_path = placeholder_registry_path or _infer_placeholder_registry_path(manifest_path, document_id)
    placeholder_check = _check_placeholder_registry(document, registry_path, resolved_intensity, labels)
    checks.append(placeholder_check)
    for issue in placeholder_check["issues"]:
        findings.append(_normalize_issue("placeholder_registry", issue, resolved_intensity, labels))

    return build_report(
        document_id=document_id,
        document_path=document,
        manifest_path=manifest_path,
        review_intensity=resolved_intensity,
        checks=checks,
        findings=findings,
    )


def build_report(
    *,
    document_id: str,
    document_path: Path,
    manifest_path: Path | None,
    review_intensity: str,
    checks: list[dict[str, Any]],
    findings: list[dict[str, Any]],
) -> dict[str, Any]:
    findings.sort(
        key=lambda item: (
            item.get("suppressed", False),
            SEVERITY_ORDER.get(item.get("severity", "major"), 9),
            item.get("line") or 0,
            item.get("validator", ""),
        )
    )
    blocking = any(item["blocking"] for item in findings)
    severity_counts = {severity: 0 for severity in SEVERITY_ORDER}
    suppressed_count = 0
    for finding in findings:
        if finding.get("suppressed"):
            suppressed_count += 1
        severity = finding.get("severity", "major")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    report = schemas.ValidationReport(
        documentId=document_id,
        status="failed" if blocking else "passed",
        findings=tuple(findings),
        blocking=blocking,
        renderAllowed=not blocking,
        documentPath=str(document_path),
        manifestPath=str(manifest_path) if manifest_path else None,
        reviewIntensity=review_intensity,
        checks=tuple(checks),
        summary={
            "issueCount": len(findings),
            "blockingIssueCount": sum(1 for finding in findings if finding["blocking"]),
            "suppressedIssueCount": suppressed_count,
            "severityCounts": severity_counts,
        },
    )
    return schemas.validate_artifact(report, expected_type="validation_report")


def _run_validator(name: str, document: Path, *, jurisdiction: str) -> dict[str, Any]:
    spec = VALIDATOR_SPECS[name]
    command = spec.command(document, jurisdiction=jurisdiction)
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    parsed = _parse_validator_stdout(completed.stdout)

    issues = parsed.get("issues", [])
    if not isinstance(issues, list):
        issues = []

    if parsed.get("status") == "error" or completed.returncode == 2:
        issues.append(
            {
                "type": "validator_error",
                "severity": "critical",
                "message": parsed.get("error") or completed.stderr or f"{name} validator failed",
            }
        )
    elif completed.returncode not in (0, 1):
        issues.append(
            {
                "type": "validator_error",
                "severity": "critical",
                "message": completed.stderr or f"{name} validator exited with {completed.returncode}",
            }
        )

    return {
        "validator": name,
        "command": command,
        "exitCode": completed.returncode,
        "status": "pass" if not issues else "fail",
        "issueCount": len(issues),
        "issues": issues,
        "rawStatus": parsed.get("status", "unknown"),
    }


def _parse_validator_stdout(stdout: str) -> dict[str, Any]:
    try:
        parsed = json.loads(stdout)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    return {
        "status": "error",
        "error": "validator did not emit valid JSON",
        "issues": [],
    }


def _normalize_issue(
    validator: str,
    issue: dict[str, Any],
    review_intensity: str,
    labels: list[dict[str, Any]],
) -> dict[str, Any]:
    severity = str(issue.get("severity") or "major").lower()
    if severity not in SEVERITY_ORDER:
        severity = "major"

    line = issue.get("line")
    if line is None and isinstance(issue.get("position"), dict):
        line = issue["position"].get("line")

    finding = {
        "validator": validator,
        "type": issue.get("type", "validation_issue"),
        "severity": severity,
        "line": line,
        "message": issue.get("message") or issue.get("suggestion") or issue.get("error") or str(issue),
        "raw": issue,
    }
    suppressed = _matches_false_positive(finding, labels)
    finding["suppressed"] = suppressed
    finding["blocking"] = False if suppressed else is_blocking(severity, review_intensity)
    return finding


def _check_placeholder_registry(
    document: Path,
    registry_path: Path | None,
    review_intensity: str,
    labels: list[dict[str, Any]],
) -> dict[str, Any]:
    text = document.read_text(encoding="utf-8")
    found = _extract_placeholders(text)
    issues: list[dict[str, Any]] = []

    for item in found:
        if not CANONICAL_PLACEHOLDER_RE.match(item["text"]):
            issues.append(
                {
                    "type": "placeholder_format",
                    "severity": "major",
                    "line": item["line"],
                    "placeholder": item["text"],
                    "message": f"Non-canonical placeholder format: {item['text']}",
                }
            )

    if not found:
        return _placeholder_check_result(registry_path, issues)

    if registry_path is None or not registry_path.exists():
        issues.append(
            {
                "type": "placeholder_registry_missing",
                "severity": "critical",
                "line": found[0]["line"],
                "message": "Document contains placeholders but no placeholder registry was provided or found.",
            }
        )
        return _placeholder_check_result(registry_path, issues)

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    tracked = _placeholder_texts_from_registry(registry)
    found_texts = {item["text"] for item in found}

    for item in found:
        if item["text"] not in tracked:
            issues.append(
                {
                    "type": "placeholder_untracked",
                    "severity": "critical",
                    "line": item["line"],
                    "placeholder": item["text"],
                    "message": f"Placeholder is not tracked in registry: {item['text']}",
                }
            )

    for text in sorted(tracked - found_texts):
        issues.append(
            {
                "type": "placeholder_stale_registry_entry",
                "severity": "major",
                "line": None,
                "placeholder": text,
                "message": f"Registry placeholder is not present in document: {text}",
            }
        )

    normalized = [
        _normalize_issue("placeholder_registry", issue, review_intensity, labels)
        for issue in issues
    ]
    return {
        "validator": "placeholder_registry",
        "registryPath": str(registry_path),
        "status": "pass" if not any(not item["suppressed"] for item in normalized) else "fail",
        "issueCount": len(issues),
        "issues": issues,
    }


def _placeholder_check_result(registry_path: Path | None, issues: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "validator": "placeholder_registry",
        "registryPath": str(registry_path) if registry_path else None,
        "status": "pass" if not issues else "fail",
        "issueCount": len(issues),
        "issues": issues,
    }


def _extract_placeholders(text: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for match in BRACKET_PLACEHOLDER_RE.finditer(text):
        if _is_likely_markdown_link(text, match):
            continue
        if _is_markdown_footnote_token(match.group(0)):
            continue
        found.append(
            {
                "text": match.group(0),
                "line": text.count("\n", 0, match.start()) + 1,
            }
        )
    return found


def _is_likely_markdown_link(text: str, match: re.Match[str]) -> bool:
    return match.end() < len(text) and text[match.end()] == "("


def _is_markdown_footnote_token(value: str) -> bool:
    return bool(re.match(r"^\[\^[^\]]+\]$", value))


def _placeholder_texts_from_registry(registry: dict[str, Any]) -> set[str]:
    placeholders = registry.get("placeholders", [])
    if not isinstance(placeholders, list):
        return set()
    tracked: set[str] = set()
    for item in placeholders:
        if isinstance(item, dict) and isinstance(item.get("text"), str):
            tracked.add(item["text"])
    return tracked


def _load_manifest(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return schemas.validate_artifact(payload, expected_type="manifest")


def _infer_placeholder_registry_path(manifest_path: Path | None, document_id: str) -> Path | None:
    if manifest_path is None:
        return None
    if manifest_path.parent.name == "manifests":
        candidate = manifest_path.parent.parent / "placeholders" / f"{document_id}.json"
        if candidate.exists():
            return candidate
    return None


def _jurisdiction_for_citation(jurisdiction: Any) -> str:
    if jurisdiction in {"korea", "us", "uk"}:
        return str(jurisdiction)
    return "intl"


def _load_false_positive_labels(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    labels = payload.get("falsePositives", [])
    return labels if isinstance(labels, list) else []


def _matches_false_positive(finding: dict[str, Any], labels: list[dict[str, Any]]) -> bool:
    for label in labels:
        if label.get("validator") and label["validator"] != finding["validator"]:
            continue
        if label.get("type") and label["type"] != finding["type"]:
            continue
        if label.get("line") is not None and label["line"] != finding.get("line"):
            continue
        contains = label.get("messageContains")
        if contains:
            raw = finding.get("raw", {})
            haystack = " ".join(
                str(part)
                for part in (
                    finding.get("message", ""),
                    raw.get("text", "") if isinstance(raw, dict) else "",
                    raw.get("found", "") if isinstance(raw, dict) else "",
                    raw.get("placeholder", "") if isinstance(raw, dict) else "",
                )
            )
            if contains not in haystack:
                continue
        return True
    return False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tools.validation.runner",
        description="Run all deterministic validators and emit one release-gate JSON report.",
    )
    parser.add_argument("document", type=Path, help="draft file to validate")
    parser.add_argument("--manifest", type=Path, help="MatterManifest JSON path")
    parser.add_argument("--placeholder-registry", type=Path, help="PlaceholderRegistry JSON path")
    parser.add_argument("--false-positive-labels", type=Path, help="manual false-positive label JSON")
    parser.add_argument(
        "--review-intensity",
        choices=sorted(BLOCKING_BY_INTENSITY),
        help="override manifest reviewIntensity",
    )
    parser.add_argument("--out", type=Path, help="write report JSON to a specific path")
    parser.add_argument(
        "--store",
        action="store_true",
        help="also store report under the resolved artifact output directory",
    )
    parser.add_argument(
        "--fail-on-blocking",
        action="store_true",
        help="exit 1 when the report blocks rendering",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = run_validation(
        args.document,
        manifest_path=args.manifest,
        placeholder_registry_path=args.placeholder_registry,
        false_positive_labels_path=args.false_positive_labels,
        review_intensity=args.review_intensity,
    )

    body = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(body, encoding="utf-8")
    if args.store:
        ArtifactStore().write_artifact(report)

    print(body, end="")
    if args.fail_on_blocking and report["blocking"]:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
