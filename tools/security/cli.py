"""Standalone CLI for spot-checking a file for prompt-injection patterns."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.security.sanitizer import sanitize, wrap_untrusted, write_audit


def _read(source: str) -> str:
    if source == "-":
        return sys.stdin.read()
    return Path(source).read_text(encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tools.security.cli",
        description="Scan text for prompt-injection patterns (stdlib only).",
    )
    parser.add_argument("source", help="path to file, or '-' for stdin")
    parser.add_argument("--out", type=Path, help="write the <escape>-wrapped text to this path")
    parser.add_argument("--audit", type=Path, help="write the audit JSON to this path")
    parser.add_argument(
        "--wrap-untrusted",
        action="store_true",
        help="additionally wrap the whole output in <untrusted_content>",
    )
    parser.add_argument(
        "--source-label",
        default="cli-check",
        help="value for the source attribute when --wrap-untrusted is set",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress per-match summary (exit code still signals the result)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        text = _read(args.source)
    except FileNotFoundError:
        print(f"error: file not found: {args.source}", file=sys.stderr)
        return 2

    result = sanitize(text)
    body = result.wrapped_text
    if args.wrap_untrusted:
        body = wrap_untrusted(body, source=args.source_label, path=args.source)

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(body, encoding="utf-8")

    if args.audit is not None:
        write_audit(result, source_path=args.source, audit_path=args.audit)

    if not args.quiet:
        print(f"source: {args.source}")
        print(f"sha256: {result.input_sha256}")
        print(f"matches: {result.match_count} ({'clean' if result.is_clean else 'DIRTY'})")
        for match in result.matches[:20]:
            print(
                f"  - [{match.category}/{match.language}] "
                f"{match.pattern_name} @ line {match.line}: {match.snippet!r}"
            )
        if result.match_count > 20:
            print(f"  ...and {result.match_count - 20} more")

    return 0 if result.is_clean else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
