# -*- coding: utf-8 -*-
"""
Test View Control and Status Component Styles.

Includes styling for status dialogs, compilation dialogs, and status utility functions.
"""

from src.app.presentation.styles.constants.status_colors import ERROR_COLOR_HEX
from src.app.presentation.styles.style import MATERIAL_COLORS

# Status Window Styles
TEST_VIEW_STATUS_DIALOG_STYLE = f"""
QDialog {{
    background: {MATERIAL_COLORS['surface']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 8px;
}}
QLabel {{
    color: {MATERIAL_COLORS['on_surface']};
    font-weight: bold;
}}
QProgressBar {{
    border: none;
    background: {MATERIAL_COLORS['surface_variant']};
    height: 6px;
    border-radius: 3px;
}}
QProgressBar::chunk {{
    background: {MATERIAL_COLORS['primary']};
    border-radius: 3px;
}}
QScrollArea {{
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 4px;
    background: {MATERIAL_COLORS['surface']};
}}
QTextEdit {{
    background-color: {MATERIAL_COLORS['surface_variant']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 4px;
    color: {MATERIAL_COLORS['on_surface']};
    padding: 8px;
}}
QPushButton {{
    background: {MATERIAL_COLORS['primary']};
    border: none;
    border-radius: 4px;
    color: {MATERIAL_COLORS['on_primary']};
    padding: 8px 16px;
}}
QPushButton:hover {{
    background: {MATERIAL_COLORS['primary_container']};
}}
"""

# History Item Styles
TEST_VIEW_HISTORY_ITEM_STYLE = f"""
QFrame {{
    background: {MATERIAL_COLORS['surface_variant']};
    border-radius: 4px;
    padding: 4px 8px;
}}
"""

# Compilation Status Styles
TEST_VIEW_COMPILATION_STATUS_DIALOG_STYLE = f"""
QDialog {{
    background: {MATERIAL_COLORS['surface']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 8px;
}}
"""

TEST_VIEW_COMPILATION_STATUS_LABEL_STYLE = f"""
color: {MATERIAL_COLORS['on_surface']};
font-size: 14px;
font-weight: bold;
"""

TEST_VIEW_COMPILATION_PROGRESS_BAR_STYLE = f"""
QProgressBar {{
    border: none;
    background: {MATERIAL_COLORS['surface_variant']};
    height: 6px;
    border-radius: 3px;
}}
QProgressBar::chunk {{
    background: {MATERIAL_COLORS['primary']};
    border-radius: 3px;
}}
"""

TEST_VIEW_COMPILATION_DETAIL_LABEL_STYLE = (
    f"color: {MATERIAL_COLORS['text_secondary']};"
)

TEST_VIEW_COMPILATION_CLOSE_BUTTON_STYLE = f"""
QPushButton {{
    background: {MATERIAL_COLORS['primary']};
    border: none;
    border-radius: 4px;
    color: {MATERIAL_COLORS['on_primary']};
    padding: 8px 16px;
    min-width: 80px;
}}
QPushButton:hover {{
    background: {MATERIAL_COLORS['primary_container']};
}}
"""

# Status Label Styles
TEST_VIEW_STATUS_LABEL_STYLE = (
    f"color: {MATERIAL_COLORS['on_surface']}; font-weight: bold;"
)
TEST_VIEW_TIME_LABEL_STYLE = f"color: {MATERIAL_COLORS['primary']}; font-weight: bold;"


# Utility Functions
def get_history_label_style(passed=True):
    """Get history label style based on pass/fail status"""
    color = MATERIAL_COLORS["primary"] if passed else ERROR_COLOR_HEX
    return f"color: {color}; font-weight: bold;"


def get_running_status_style():
    return f"color: {MATERIAL_COLORS['on_surface']}; font-weight: bold;"


def get_test_view_error_status_style():
    return f"color: {ERROR_COLOR_HEX}; font-weight: bold;"


def get_test_view_success_status_style():
    return f"color: {MATERIAL_COLORS['primary']}; font-weight: bold;"


def get_compilation_status_style(is_success=True):
    color = MATERIAL_COLORS["primary"] if is_success else ERROR_COLOR_HEX
    return f"color: {color};"


def get_status_label_style(passed=True):
    color = MATERIAL_COLORS["primary"] if passed else ERROR_COLOR_HEX
    return f"color: {color}; font-weight: bold;"


def get_passed_status_style():
    return f"color: {MATERIAL_COLORS['primary']}; font-weight: bold;"


def get_failed_status_style():
    return f"color: {ERROR_COLOR_HEX}; font-weight: bold;"


__all__ = [
    "TEST_VIEW_STATUS_DIALOG_STYLE",
    "TEST_VIEW_HISTORY_ITEM_STYLE",
    "TEST_VIEW_COMPILATION_STATUS_DIALOG_STYLE",
    "TEST_VIEW_COMPILATION_STATUS_LABEL_STYLE",
    "TEST_VIEW_COMPILATION_PROGRESS_BAR_STYLE",
    "TEST_VIEW_COMPILATION_DETAIL_LABEL_STYLE",
    "TEST_VIEW_COMPILATION_CLOSE_BUTTON_STYLE",
    "TEST_VIEW_STATUS_LABEL_STYLE",
    "TEST_VIEW_TIME_LABEL_STYLE",
    "get_history_label_style",
    "get_running_status_style",
    "get_test_view_error_status_style",
    "get_test_view_success_status_style",
    "get_compilation_status_style",
    "get_status_label_style",
    "get_passed_status_style",
    "get_failed_status_style",
]
