"""Validation runner package.

Imports are lazy so `python -m tools.validation.runner` can execute without
preloading the runner module through the package initializer.
"""
from __future__ import annotations

__all__ = [
    "DEFAULT_VALIDATORS",
    "build_report",
    "is_blocking",
    "run_validation",
]


def __getattr__(name: str):
    if name in __all__:
        from tools.validation import runner

        return getattr(runner, name)
    raise AttributeError(name)
