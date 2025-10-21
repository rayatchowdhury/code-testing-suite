"""
Test Detail Dialog Styles

Centralized styles for test detail view dialogs (Comparator, Validator, Benchmarker).
These dialogs show detailed information when a test card is clicked.
"""

from src.app.presentation.design_system.tokens.colors import MATERIAL_COLORS

# Dialog Background
TEST_DETAIL_DIALOG_STYLE = f"""
QDialog {{
    background: {MATERIAL_COLORS['background']};
}}
"""

# Header Styles
def get_test_label_style() -> str:
    """Style for test number label in header"""
    return """
        font-weight: bold;
        font-size: 18px;
    """


def get_status_label_style(passed: bool) -> str:
    """
    Style for status label (✓ Passed / ✗ Failed) in header
    
    Args:
        passed: Whether test passed
    
    Returns:
        QSS style string
    """
    status_color = (
        MATERIAL_COLORS["primary"] if passed else MATERIAL_COLORS["error"]
    )
    return f"""
        color: {status_color};
        font-weight: bold;
        font-size: 18px;
    """

def get_header_frame_style(passed: bool) -> str:
    """
    Style for header frame container
    
    Args:
        passed: Whether test passed
    
    Returns:
        QSS style string
    """
    bg_color = (
        MATERIAL_COLORS.get("primary_container", MATERIAL_COLORS["surface_variant"])
        if passed
        else MATERIAL_COLORS["error_container"]
    )
    return f"""
        QFrame {{
            background: {bg_color};
            border-radius: 8px;
        }}
    """

# Metrics Panel Styles
TEST_DETAIL_METRICS_LABEL_STYLE = """
    font-size: 14px;
    font-weight: 500;
"""


TEST_DETAIL_METRICS_FRAME_STYLE = f"""
QFrame {{
    background: {MATERIAL_COLORS['surface_variant']};
    border-radius: 6px;
}}
"""

# Button Styles
TEST_DETAIL_CLOSE_BUTTON_STYLE = f"""
QPushButton {{
    background: {MATERIAL_COLORS['primary']};
    color: {MATERIAL_COLORS['on_primary']};
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 14px;
}}
QPushButton:hover {{
    background: {MATERIAL_COLORS['primary_dark']};
}}
"""

# Content Section Styles
TEST_DETAIL_SECTION_LABEL_STYLE = """
    font-weight: bold;
    font-size: 14px;
"""

# Text Edit Styles (for input/output display)
TEST_DETAIL_TEXT_EDIT_MONOSPACE_STYLE = f"""
QTextEdit {{
    background: {MATERIAL_COLORS['surface']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 6px;
    padding: 8px;
    color: {MATERIAL_COLORS['text_primary']};
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}}
"""

def get_validator_log_style(passed: bool) -> str:
    """
    Style for validator log text edit (special styling for pass/fail)
    
    Args:
        passed: Whether test passed
    
    Returns:
        QSS style string
    """
    bg_color = MATERIAL_COLORS["surface"] if passed else "#2d1f1f"
    return f"""
        QTextEdit {{
            background: {bg_color};
            border: 1px solid {MATERIAL_COLORS['outline']};
            border-radius: 6px;
            padding: 12px;
            color: {MATERIAL_COLORS['text_primary']};
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-size: 13px;
            line-height: 1.5;
        }}
    """

def get_performance_summary_style(passed: bool) -> str:
    """
    Style for benchmarker performance summary section
    
    Args:
        passed: Whether test passed (within performance limits)
    
    Returns:
        QSS style string
    """
    bg_color = MATERIAL_COLORS["surface"] if passed else "#2d1f1f"
    return f"""
        QTextEdit {{
            background: {bg_color};
            border: 1px solid {MATERIAL_COLORS['outline']};
            border-radius: 6px;
            padding: 12px;
            color: {MATERIAL_COLORS['text_primary']};
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-size: 13px;
            line-height: 1.5;
        }}
    """
