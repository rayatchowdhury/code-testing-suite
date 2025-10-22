"""
Comparator Window Package

Phase 5: Per-Window Packaging
Comparator window for code comparison testing

Note: Uses lazy imports for fast startup. Classes are imported when accessed.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.presentation.windows.tests.comparator.view import ComparatorWindow

__all__ = ["ComparatorWindow"]

def __getattr__(name: str):
    """Lazy import window classes on first access."""
    if name == "ComparatorWindow":
        from src.app.presentation.windows.tests.comparator.view import ComparatorWindow
        return ComparatorWindow
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
