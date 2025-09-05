"""
Styles for the Stress Tester View Components
"""

from styles.style import MATERIAL_COLORS
from styles.constants.status_colors import ERROR_COLOR_HEX

# Stress Test Status Window Styles
STRESS_TEST_STATUS_DIALOG_STYLE = f"""
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

# Status label styles for different states
def get_status_label_style(color=None):
    """Get status label style with optional color override"""
    color = color or MATERIAL_COLORS['on_surface']
    return f"color: {color}; font-weight: bold;"

def get_running_status_style():
    """Style for running test status"""
    return get_status_label_style(MATERIAL_COLORS['on_surface'])

def get_error_status_style():
    """Style for error test status"""
    return get_status_label_style(ERROR_COLOR_HEX)

def get_success_status_style():
    """Style for success test status"""
    return get_status_label_style(MATERIAL_COLORS['primary'])

# Test history item style
HISTORY_ITEM_STYLE = f"""
    QFrame {{
        background: {MATERIAL_COLORS['surface_variant']};
        border-radius: 4px;
        padding: 4px 8px;
    }}
"""

def get_history_label_style(passed=True):
    """Get history label style based on pass/fail status"""
    color = MATERIAL_COLORS['primary'] if passed else ERROR_COLOR_HEX
    return f"color: {color}; font-weight: bold;"

# Compilation Status Window Styles
COMPILATION_STATUS_DIALOG_STYLE = f"""
    QDialog {{
        background: {MATERIAL_COLORS['surface']};
        border: 1px solid {MATERIAL_COLORS['outline']};
        border-radius: 8px;
    }}
"""

COMPILATION_STATUS_LABEL_STYLE = f"""
    color: {MATERIAL_COLORS['on_surface']};
    font-size: 14px;
    font-weight: bold;
"""

COMPILATION_PROGRESS_BAR_STYLE = f"""
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

COMPILATION_DETAIL_LABEL_STYLE = f"color: {MATERIAL_COLORS['text_secondary']};"

COMPILATION_CLOSE_BUTTON_STYLE = f"""
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

def get_compilation_status_style(is_success=True):
    """Get compilation status label style based on success/failure"""
    color = MATERIAL_COLORS['primary'] if is_success else ERROR_COLOR_HEX
    return f"color: {color};"

# Stress Tester Display Area Styles
STRESS_TESTER_BUTTON_PANEL_STYLE = f"""
    QWidget {{
        background-color: {MATERIAL_COLORS['surface_dim']};
        border-bottom: 1px solid {MATERIAL_COLORS['outline']};
    }}
"""

FILE_BUTTON_STYLE = f"""
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

STRESS_CONTENT_PANEL_STYLE = f"background-color: {MATERIAL_COLORS['surface']};"

# Test Count Slider Styles
TEST_COUNT_SLIDER_STYLE = f"""
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

TEST_COUNT_VALUE_LABEL_STYLE = f"""
    color: {MATERIAL_COLORS['on_surface']};
    font-size: 13px;
    padding: 0 8px;
    min-width: 28px;
"""
