#!/usr/bin/env python3
"""Document the fixture policy.

Fixtures in this repository are intentionally static and synthetic. This script
is a placeholder for future fixture generation when a test case benefits from
programmatic construction.
"""

from __future__ import annotations

from pathlib import Path


PUBLIC_FIXTURE_DIR = Path(__file__).resolve().parent / "public"


def main() -> None:
    print(f"Public fixtures live in: {PUBLIC_FIXTURE_DIR}")
    print("Only synthetic or public-source fixtures may be committed.")


if __name__ == "__main__":
    main()
