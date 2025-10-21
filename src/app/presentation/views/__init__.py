"""
Views package for the Code Testing Suite.

This package contains all the GUI windows and their components.
"""

# Specific view window exports
from src.app.presentation.windows.benchmarker import BenchmarkerWindow
from src.app.presentation.windows.editor import CodeEditorWindow
from src.app.presentation.windows.comparator import ComparatorWindow
from src.app.presentation.windows.help_center import HelpCenterWindow

# Main window exports
from src.app.presentation.windows.main import (
    MainWindow,
    MainWindowContent,
)

# Results components
from src.app.presentation.windows.results.widgets.results_widget import ResultsWidget
from src.app.presentation.windows.results import ResultsWindow
from src.app.presentation.windows.validator import ValidatorWindow
from src.app.presentation.window_controller.base_window import SidebarWindowBase

# Window management
from src.app.presentation.window_controller.window_management import (
    WindowFactory,
    WindowManager,
)

__all__ = [
    # Base classes
    "SidebarWindowBase",
    # Main windows
    "MainWindow",
    "MainWindowContent",
    # Window management
    "WindowFactory",
    "WindowManager",
    # Specific windows
    "BenchmarkerWindow",
    "CodeEditorWindow",
    "ComparatorWindow",
    "HelpCenterWindow",
    "ResultsWindow",
    "ValidatorWindow",
    # Components
    "TestResultsWidget",
]
