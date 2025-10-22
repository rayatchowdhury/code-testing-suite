"""
Benchmarker Window Package

Phase 5: Per-Window Packaging
Benchmarker window for code performance testing

Note: Uses lazy imports for fast startup. Classes are imported when accessed.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.presentation.windows.tests.benchmarker.view import BenchmarkerWindow

__all__ = ["BenchmarkerWindow"]

def __getattr__(name: str):
    """Lazy import window classes on first access."""
    if name == "BenchmarkerWindow":
        from src.app.presentation.windows.tests.benchmarker.view import BenchmarkerWindow
        return BenchmarkerWindow
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
