from src.app.presentation.shared.design_system.styles.components import (
    AI_PANEL_STYLE,
    CONSOLE_STYLE,
    CUSTOM_COMMAND_STYLE,
    EDITOR_WIDGET_STYLE,
    SCROLLBAR_STYLE,
    SIDEBAR_BUTTON_STYLE,
    SIDEBAR_STYLE,
    SPLITTER_STYLE,
    get_tab_style,
)
from src.app.presentation.shared.design_system.tokens import COLORS, SPACING, STATUS_COLORS

# Simplified DISPLAY_AREA_STYLE
DISPLAY_AREA_STYLE = f"""
QWidget#display_area {{
    background-color: {COLORS['background']};
    border: none;
}}
"""

# Export all styles
__all__ = [
    "COLORS",
    "MATERIAL_COLORS",
    "SCROLLBAR_STYLE",
    "SIDEBAR_STYLE",
    "SIDEBAR_BUTTON_STYLE",
    "SPLITTER_STYLE",
    "DISPLAY_AREA_STYLE",
    "CONSOLE_STYLE",
    "EDITOR_WIDGET_STYLE",
    "get_tab_style",
    "AI_PANEL_STYLE",
    "CUSTOM_COMMAND_STYLE",
]
