"""
Main Window Package

Note: This module has been moved to src.app.presentation.windows.main
This file remains for backwards compatibility.
"""

from src.app.presentation.windows.main import (
    MainWindow,
    MainWindowConfig,
    MainWindowContent,
    UnsavedChangesHandler,
)

__all__ = [
    "MainWindow",
    "MainWindowContent",
    "MainWindowConfig",
    "UnsavedChangesHandler",
]
