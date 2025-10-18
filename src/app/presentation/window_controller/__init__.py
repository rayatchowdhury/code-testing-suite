"""
Window Controller Package

This package contains the core window management and base window classes
for the Code Testing Suite application.

Components:
- base_window: SidebarWindowBase - Base class for all sidebar-based windows
- window_management: WindowFactory, WindowManager - Window creation and navigation
"""

from src.app.presentation.window_controller.base_window import SidebarWindowBase
from src.app.presentation.window_controller.window_management import (
    WindowFactory,
    WindowManager,
)

__all__ = [
    "SidebarWindowBase",
    "WindowFactory",
    "WindowManager",
    "DocumentWidget",
    "AppTheme",
    "StyleSheet",
    "FontUtils",
    "GradientText",
    "HelpSectionData",
]
