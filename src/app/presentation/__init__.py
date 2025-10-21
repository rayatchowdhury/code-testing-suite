"""
Presentation module for the Code Testing Suite.

This module contains the user interface components and view logic.
"""

# Lazy imports to avoid circular dependencies
def get_main_window():
    """Lazy import of MainWindow"""
    from src.app.presentation.windows.main import MainWindow

    return MainWindow


# Import design_system and widgets modules
from src.app.presentation import design_system, widgets

__all__ = ["get_main_window", "design_system", "widgets"]
