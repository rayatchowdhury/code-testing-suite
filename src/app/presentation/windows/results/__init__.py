"""
Results Window Package

Phase 5: Per-Window Packaging
Results Window for test history and detailed views

Note: Uses lazy imports for fast startup. Classes are imported when accessed.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.presentation.windows.results.view import ResultsWindow

__all__ = ["ResultsWindow"]

def __getattr__(name: str):
    """Lazy import window classes on first access."""
    if name == "ResultsWindow":
        from src.app.presentation.windows.results.view import ResultsWindow
        return ResultsWindow
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
