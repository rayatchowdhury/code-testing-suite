"""Main Window Package

Phase 5: Per-Window Packaging
Main application window with sidebar navigation and display area.
"""

from src.app.presentation.windows.main.widgets.view import (
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
