"""
Code Testing Suite - PySide6 Desktop Application

A comprehensive code editor with AI integration, comparison testing,
and time-limit testing capabilities.
"""

__version__ = "1.0.0"
__author__ = "Code Testing Suite Team"


# Lazy imports - only import when accessed
def get_main_window():
    """Lazy import of MainWindow"""
    from src.app.presentation.windows.main import MainWindow

    return MainWindow


def get_window_manager():
    """Lazy import of WindowManager"""
    from src.app.presentation.window_controller.window_management import WindowManager

    return WindowManager
