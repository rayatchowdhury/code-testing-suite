from src.app.presentation.styles.constants import COLORS, MATERIAL_COLORS
from src.app.presentation.styles.components import (
    SCROLLBAR_STYLE,
    SIDEBAR_STYLE,
    SIDEBAR_BUTTON_STYLE,
    SPLITTER_STYLE,
    CONSOLE_STYLE,
    EDITOR_WIDGET_STYLE,
    get_tab_style,
    AI_PANEL_STYLE,
    CUSTOM_COMMAND_STYLE
)

# Simplified DISPLAY_AREA_STYLE
DISPLAY_AREA_STYLE = f"""
QWidget#display_area {{
    background-color: {COLORS['background']};
    border: none;
}}
"""

# Simplified WEBVIEW_STYLE
WEBVIEW_STYLE = f"""
QWebEngineView {{
    background-color: {COLORS['background']};
    border: none;
}}
""" + SCROLLBAR_STYLE

# Export all styles
__all__ = [
    'COLORS',
    'MATERIAL_COLORS',
    'SCROLLBAR_STYLE',
    'SIDEBAR_STYLE',
    'SIDEBAR_BUTTON_STYLE',
    'SPLITTER_STYLE',
    'DISPLAY_AREA_STYLE',
    'WEBVIEW_STYLE',
    'CONSOLE_STYLE',
    'EDITOR_WIDGET_STYLE',
    'get_tab_style',
    'AI_PANEL_STYLE',
    'CUSTOM_COMMAND_STYLE'
]
