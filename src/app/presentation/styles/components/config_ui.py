"""
Config UI component styles
"""

from src.app.presentation.design_system.tokens import MATERIAL_COLORS

# Error Dialog Styles
ERROR_DIALOG_STYLE = f"""
QDialog {{
    background: {MATERIAL_COLORS['surface']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 8px;
}}

QLabel#error_title {{
    color: {MATERIAL_COLORS['error']};
    margin-bottom: 8px;
}}

QLabel#error_message {{
    color: {MATERIAL_COLORS['on_surface']};
    line-height: 1.4;
}}

QLabel#error_details_label {{
    color: {MATERIAL_COLORS['on_surface']};
    margin-top: 8px;
    margin-bottom: 4px;
}}

QFrame#error_separator {{
    color: {MATERIAL_COLORS['outline']};
    margin: 8px 0;
}}

QTextEdit#error_details {{
    background: {MATERIAL_COLORS['surface_variant']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 4px;
    color: {MATERIAL_COLORS['on_surface']};
    padding: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
}}

QPushButton#error_ok_button {{
    background: {MATERIAL_COLORS['primary']};
    border: none;
    border-radius: 4px;
    color: {MATERIAL_COLORS['on_primary']};
    padding: 8px 24px;
    font-weight: 600;
    min-width: 80px;
}}

QPushButton#error_ok_button:hover {{
    background: {MATERIAL_COLORS['primary_container']};
    color: {MATERIAL_COLORS['on_primary_container']};
}}
"""

# Config Dialog Title Style
CONFIG_DIALOG_TITLE_STYLE = f"""
font-size: 18px; 
color: {MATERIAL_COLORS['primary']}; 
font-weight: 600;
font-family: 'Segoe UI', system-ui;
margin: 8px 0;
text-align: center;
"""

# Success Message Dialog Styles
SUCCESS_MESSAGE_STYLE = """
QMessageBox {
    background-color: #2E7D32;
    color: white;
}
QMessageBox QPushButton {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}
"""

# Info Message Dialog Styles
INFO_MESSAGE_STYLE = """
QMessageBox {
    background-color: #1976D2;
    color: white;
}
QMessageBox QPushButton {
    background-color: #2196F3;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}
"""

# Section Builder Info Label Style
SECTION_INFO_LABEL_STYLE = (
    f"color: {MATERIAL_COLORS['on_surface_variant']}; font-size: 12px;"
)


# Dynamic style for success status (used in config_handler.py)
def get_success_status_style():
    """Get style for success status"""
    return f"color: {MATERIAL_COLORS['primary']}"


__all__ = [
    "ERROR_DIALOG_STYLE",
    "CONFIG_DIALOG_TITLE_STYLE",
    "SUCCESS_MESSAGE_STYLE",
    "INFO_MESSAGE_STYLE",
    "SECTION_INFO_LABEL_STYLE",
    "get_success_status_style",
]

