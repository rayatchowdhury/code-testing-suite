"""
Views package for the Code Testing Suite.

This package contains all the GUI windows and their components.
"""

# Specific view window exports
from src.app.presentation.views.benchmarker.benchmarker_window import BenchmarkerWindow
from src.app.presentation.views.code_editor.code_editor_window import CodeEditorWindow
from src.app.presentation.views.comparator.comparator_window import ComparatorWindow
from src.app.presentation.views.help_center.help_center_window import HelpCenterWindow

# Main window exports
from src.app.presentation.views.main_window.main_window import (
    MainWindow,
    MainWindowContent,
)

# Results components
from src.app.presentation.views.results.results_widget import TestResultsWidget
from src.app.presentation.views.results.results_window import ResultsWindow
from src.app.presentation.views.validator.validator_window import ValidatorWindow
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
