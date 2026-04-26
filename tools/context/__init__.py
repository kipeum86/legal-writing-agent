"""Context planning utilities for prompt and reference loading."""
from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = ["build_context_plan", "estimate_plan_chars", "select_style_profile"]


def __getattr__(name: str) -> Any:
    if name in __all__:
        module = import_module("tools.context.budget")
        return getattr(module, name)
    raise AttributeError(name)
