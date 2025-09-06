"""
Common inline style helpers for frequently used style combinations
"""
from src.app.styles.constants.colors import MATERIAL_COLORS
from src.app.styles.constants.status_colors import ERROR_COLOR_HEX, FONT_WEIGHTS, FONT_SIZES

# Common error label styles
ERROR_LABEL_STYLE = f"color: {MATERIAL_COLORS['error']};"
ERROR_LABEL_BOLD_STYLE = f"color: {MATERIAL_COLORS['error']}; font-weight: bold;"

# Status label styles with different weights and sizes
def get_status_label_style(color, weight='bold', size='14px'):
    """Get a status label style with customizable color, weight, and size"""
    return f"color: {color}; font-weight: {weight}; font-size: {size};"

# Error title styles
ERROR_TITLE_STYLE = f"color: {MATERIAL_COLORS['error']}; font-weight: bold; font-size: 16px;"

# Status-specific styles
PRIMARY_BOLD_STYLE = f"color: {MATERIAL_COLORS['primary']}; font-weight: bold;"
ON_SURFACE_BOLD_STYLE = f"color: {MATERIAL_COLORS['on_surface']}; font-weight: bold;"

# Info label styles
INFO_LABEL_STYLE = f"color: {MATERIAL_COLORS['on_surface_variant']}; font-size: 12px;"

# Icon styles
LARGE_ICON_STYLE = "font-size: 48px; margin: 10px;"

# Progress label style
PROGRESS_LABEL_STYLE = f"color: {MATERIAL_COLORS['on_surface']}; font-weight: 500; margin-top: 8px;"

# Common style builders
def build_color_font_style(color, weight=None, size=None):
    """Build a style string with color and optional font properties"""
    style = f"color: {color};"
    if weight:
        style += f" font-weight: {weight};"
    if size:
        style += f" font-size: {size};"
    return style

def build_error_style(weight=None, size=None):
    """Build an error style with optional font properties"""
    return build_color_font_style(MATERIAL_COLORS['error'], weight, size)

def build_status_style(passed, weight='bold', size=None):
    """Build a status style based on pass/fail state"""
    color = MATERIAL_COLORS['primary'] if passed else ERROR_COLOR_HEX
    return build_color_font_style(color, weight, size)
