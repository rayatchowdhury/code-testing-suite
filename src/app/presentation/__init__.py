"""
Presentation module for the Code Testing Suite.

This module contains the user interface components and view logic.
"""

# Lazy imports to avoid circular dependencies
def get_main_window():
    """Lazy import of MainWindow"""
    from src.app.presentation.windows.main import MainWindow

    return MainWindow

def get_sidebar_window_base():
    """Lazy import of SidebarWindowBase"""
    from src.app.presentation._deprecated.base_window import SidebarWindowBase

    return SidebarWindowBase

# Widgets module - this is safe to import directly
# Styles module - this is safe to import directly
from src.app.presentation import styles, widgets

__all__ = ["get_main_window", "get_sidebar_window_base", "styles", "widgets"]
