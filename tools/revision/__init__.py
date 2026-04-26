"""Revision artifact generation utilities."""
from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "LevelBArtifactPaths",
    "build_change_map",
    "write_level_b_artifacts",
]


def __getattr__(name: str) -> Any:
    if name in __all__:
        module = import_module("tools.revision.level_b")
        return getattr(module, name)
    raise AttributeError(name)
