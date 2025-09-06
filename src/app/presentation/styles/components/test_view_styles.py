# -*- coding: utf-8 -*-

# Shared styles for test views (comparator, benchmarker, validator)
from src.app.presentation.styles.style import MATERIAL_COLORS
from src.app.presentation.styles.constants.status_colors import ERROR_COLOR_HEX

TEST_VIEW_BUTTON_PANEL_STYLE = f"""
QWidget {{
    background-color: {MATERIAL_COLORS['surface_dim']};
    border-bottom: 1px solid {MATERIAL_COLORS['outline']};
}}
"""

TEST_VIEW_FILE_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {MATERIAL_COLORS['surface_variant']};
    border: 1px solid {MATERIAL_COLORS['outline_variant']};
    border-radius: 8px;
    color: {MATERIAL_COLORS['on_surface']};
    padding: 8px 16px;
    font-weight: 500;
    font-size: 13px;
}}

QPushButton:hover {{
    background-color: {MATERIAL_COLORS['surface_bright']};
    border-color: {MATERIAL_COLORS['outline']};
}}

QPushButton[isActive="true"] {{
    background-color: {MATERIAL_COLORS['primary_container']};
    border: 1px solid {MATERIAL_COLORS['primary']};
    color: {MATERIAL_COLORS['on_primary_container']};
    font-weight: 600;
}}

QPushButton[isActive="true"]:hover {{
    background-color: {MATERIAL_COLORS['primary']};
    color: {MATERIAL_COLORS['on_primary']};
}}

QPushButton[isActive="true"][hasUnsavedChanges="true"] {{
    background-color: {MATERIAL_COLORS['primary_container']};
    border: 2px solid {MATERIAL_COLORS['error']};
    border-radius: 8px;
    color: {MATERIAL_COLORS['on_primary']};
    font-weight: 600;
    padding: 7px 15px;  /* Adjust padding to account for thicker border */
}}

QPushButton[isActive="true"][hasUnsavedChanges="true"]:hover {{
    background-color: {MATERIAL_COLORS['primary']};
    border-color: {MATERIAL_COLORS['error']};
    color: {MATERIAL_COLORS['on_primary']};
}}
"""

TEST_VIEW_CONTENT_PANEL_STYLE = f"""
QWidget {{
    background-color: {MATERIAL_COLORS['surface']};
}}
"""

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

TEST_VIEW_COMPILATION_DETAIL_LABEL_STYLE = f"color: {MATERIAL_COLORS['text_secondary']};"

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

# Slider Styles
TEST_VIEW_SLIDER_STYLE = f"""
QSlider::groove:horizontal {{
    border: none;
    height: 4px;
    background: {MATERIAL_COLORS['surface_variant']};
    margin: 0px;
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {MATERIAL_COLORS['primary']};
    border: none;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}
QSlider::handle:horizontal:hover {{
    background: {MATERIAL_COLORS['primary_container']};
}}
QSlider::sub-page:horizontal {{
    background: {MATERIAL_COLORS['primary']};
    border-radius: 2px;
}}
"""

TEST_VIEW_SLIDER_VALUE_LABEL_STYLE = f"""
color: {MATERIAL_COLORS['on_surface']};
font-size: 13px;
padding: 0 8px;
min-width: 28px;
"""

# Status Label Styles
TEST_VIEW_STATUS_LABEL_STYLE = f"color: {MATERIAL_COLORS['on_surface']}; font-weight: bold;"
TEST_VIEW_TIME_LABEL_STYLE = f"color: {MATERIAL_COLORS['primary']}; font-weight: bold;"

# Utility Functions
def get_history_label_style(passed=True):
    """Get history label style based on pass/fail status"""
    color = MATERIAL_COLORS['primary'] if passed else ERROR_COLOR_HEX
    return f"color: {color}; font-weight: bold;"

def get_running_status_style():
    return f"color: {MATERIAL_COLORS['on_surface']}; font-weight: bold;"

def get_test_view_error_status_style():
    return f"color: {ERROR_COLOR_HEX}; font-weight: bold;"

def get_test_view_success_status_style():
    return f"color: {MATERIAL_COLORS['primary']}; font-weight: bold;"

def get_compilation_status_style(is_success=True):
    color = MATERIAL_COLORS['primary'] if is_success else ERROR_COLOR_HEX
    return f"color: {color};"

def get_status_label_style(passed=True):
    color = MATERIAL_COLORS['primary'] if passed else ERROR_COLOR_HEX
    return f"color: {color}; font-weight: bold;"

def get_passed_status_style():
    return f"color: {MATERIAL_COLORS['primary']}; font-weight: bold;"

def get_failed_status_style():
    return f"color: {ERROR_COLOR_HEX}; font-weight: bold;"
