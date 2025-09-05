"""
TLE Tester component styles
"""

from ..style import MATERIAL_COLORS
from ..constants.status_colors import ERROR_COLOR_HEX

# TLE Test Status Window Styles
TLE_TEST_STATUS_WINDOW_STYLE = f"""
QDialog {{
    background: {MATERIAL_COLORS['surface']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 8px;
}}

QLabel {{
    color: {MATERIAL_COLORS['on_surface']};
    font-weight: bold;
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

# Status Label Styles
TLE_STATUS_LABEL_STYLE = f"color: {MATERIAL_COLORS['on_surface']}; font-weight: bold;"
TLE_TIME_LABEL_STYLE = f"color: {MATERIAL_COLORS['primary']}; font-weight: bold;"

# Dynamic styles for status colors
def get_status_label_style(color):
    """Get status label style with specific color"""
    return f"color: {color}; font-weight: bold;"

def get_passed_status_style():
    """Get style for passed test status"""
    return get_status_label_style(MATERIAL_COLORS['primary'])

def get_failed_status_style():
    """Get style for failed test status"""
    return get_status_label_style(ERROR_COLOR_HEX)

# History Frame Style
TLE_HISTORY_FRAME_STYLE = f"""
QFrame {{
    background: {MATERIAL_COLORS['surface_variant']};
    border-radius: 4px;
    padding: 4px 8px;
}}
"""

# TLE Display Area Button Panel Style
TLE_BUTTON_PANEL_STYLE = f"""
QWidget {{
    background-color: {MATERIAL_COLORS['surface_dim']};
    border-bottom: 1px solid {MATERIAL_COLORS['outline']};
}}
"""

# Content Panel Style
TLE_CONTENT_PANEL_STYLE = f"background-color: {MATERIAL_COLORS['surface']};"

# File Button Style
TLE_FILE_BUTTON_STYLE = f"""
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

# Time Limit Slider Styles
TLE_SLIDER_STYLE = f"""
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

TLE_SLIDER_VALUE_LABEL_STYLE = f"""
color: {MATERIAL_COLORS['on_surface']};
font-size: 13px;
padding: 0 8px;
min-width: 36px;
"""

__all__ = [
    'TLE_TEST_STATUS_WINDOW_STYLE',
    'TLE_STATUS_LABEL_STYLE', 
    'TLE_TIME_LABEL_STYLE',
    'TLE_HISTORY_FRAME_STYLE',
    'TLE_BUTTON_PANEL_STYLE',
    'TLE_CONTENT_PANEL_STYLE',
    'TLE_FILE_BUTTON_STYLE',
    'TLE_SLIDER_STYLE',
    'TLE_SLIDER_VALUE_LABEL_STYLE',
    'get_status_label_style',
    'get_passed_status_style',
    'get_failed_status_style'
]
