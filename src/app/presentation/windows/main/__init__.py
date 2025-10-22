"""Main Window Package

Phase 5: Per-Window Packaging
Main application window with sidebar navigation and display area.

Note: Uses lazy imports for fast startup. Classes are imported when accessed.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.presentation.windows.main.view import (
        MainWindow,
        MainWindowContent,
        MainWindowConfig,
        UnsavedChangesHandler,
    )

__all__ = [
    "MainWindow",
    "MainWindowContent",
    "MainWindowConfig",
    "UnsavedChangesHandler",
]

def __getattr__(name: str):
    """Lazy import window classes on first access."""
    if name in __all__:
        from src.app.presentation.windows.main.view import (
            MainWindow,
            MainWindowContent,
            MainWindowConfig,
            UnsavedChangesHandler,
        )
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
