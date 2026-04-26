"""Deterministic source retrieval utilities."""
from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "apply_retrieval_to_manifest",
    "retrieve_authority_chunks",
    "validate_source_registry",
]


def __getattr__(name: str) -> Any:
    if name in __all__:
        module = import_module("tools.retrieval.deterministic")
        return getattr(module, name)
    raise AttributeError(name)

