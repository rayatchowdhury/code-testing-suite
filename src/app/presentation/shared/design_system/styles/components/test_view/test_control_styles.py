# -*- coding: utf-8 -*-
"""
Test View Control and Status Component Styles.

Includes styling for status dialogs, compilation dialogs, and status utility functions.
"""

from src.app.presentation.shared.design_system.tokens.status_colors import ERROR_COLOR_HEX
from src.app.presentation.shared.design_system.tokens import MATERIAL_COLORS
from src.app.presentation.shared.design_system.styles.common_styles import bold_label

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
TEST_VIEW_STATUS_LABEL_STYLE = bold_label(color=MATERIAL_COLORS['on_surface'])
TEST_VIEW_TIME_LABEL_STYLE = bold_label(color=MATERIAL_COLORS['primary'])


# Utility Functions (actively used)
def get_status_label_style(passed=True):
    color = MATERIAL_COLORS["primary"] if passed else ERROR_COLOR_HEX
    return bold_label(color=color)


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
    "get_status_label_style",
]

