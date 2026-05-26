from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[2]
LINK_RE = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
FENCED_BLOCK_RE = re.compile(r"(?ms)^```.*?^```")
EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel"}
CHECKED_PATHS = {
    "CLAUDE.md",
    "README.md",
    "input/README.md",
    "output/README.md",
    "tests/fixtures/public/README.md",
}


def test_tracked_markdown_internal_links_resolve() -> None:
    broken_links: list[str] = []

    for path in _tracked_markdown_docs():
        text = FENCED_BLOCK_RE.sub("", path.read_text(encoding="utf-8"))
        for raw_target in LINK_RE.findall(text):
            target = _extract_link_target(raw_target)
            if not target or _is_external(target):
                continue

            target_path = _resolve_target(path, target)
            if not target_path.exists():
                rel_path = path.relative_to(ROOT)
                broken_links.append(f"{rel_path}: {raw_target} -> {target_path.relative_to(ROOT)}")

    assert broken_links == []


def _tracked_markdown_docs() -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "*.md"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    paths = []
    for relative in completed.stdout.splitlines():
        path = ROOT / relative
        if path.exists() and (relative in CHECKED_PATHS or relative.startswith("docs/")):
            paths.append(path)
    return paths


def _extract_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1:target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]
    return unquote(target.split("#", 1)[0])


def _is_external(target: str) -> bool:
    parsed = urlparse(target)
    return bool(parsed.scheme in EXTERNAL_SCHEMES or target.startswith("//"))


def _resolve_target(source: Path, target: str) -> Path:
    if target.startswith("/"):
        return (ROOT / target.lstrip("/")).resolve()
    return (source.parent / target).resolve()
