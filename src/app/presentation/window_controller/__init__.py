"""
Window Controller Package

This package contains the core window management and base window classes
for the Code Testing Suite application.

Components:
- base_window: SidebarWindowBase - Base class for all sidebar-based windows
- window_management: WindowFactory, WindowManager - Window creation and navigation
- qt_doc_engine: Document rendering components for help and welcome screens
"""

from src.app.presentation.window_controller.base_window import SidebarWindowBase
from src.app.presentation.window_controller.qt_doc_engine import (
    AppTheme,
    CallToActionSection,
    DocumentWidget,
    FeatureCard,
    FontUtils,
    GradientText,
    HelpDocument,
    HelpSectionData,
    StyleSheet,
)
from src.app.presentation.window_controller.window_management import (
    WindowFactory,
    WindowManager,
)

__all__ = [
    "SidebarWindowBase",
    "WindowFactory",
    "WindowManager",
    "HelpDocument",
    "HelpSectionData",
    "DocumentWidget",
    "AppTheme",
    "StyleSheet",
    "FontUtils",
    "GradientText",
    "FeatureCard",
    "CallToActionSection",
]
