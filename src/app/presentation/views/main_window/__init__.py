"""
Main Window Package

This package contains the main application window and its content.

Components:
- main_window: MainWindow (QMainWindow container), MainWindowContent (content widget)
- main_window_content: Qt document widget for welcome screen
"""

from src.app.presentation.views.main_window.main_window import (
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
