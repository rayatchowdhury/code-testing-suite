"""
Common inline style helpers for frequently used style combinations
"""

from src.app.presentation.shared.design_system.tokens.colors import MATERIAL_COLORS
from src.app.presentation.shared.design_system.tokens.status_colors import ERROR_COLOR_HEX

# Common error label styles (used in detailed_results_widget.py)
ERROR_LABEL_STYLE = f"color: {MATERIAL_COLORS['error']};"
ERROR_LABEL_BOLD_STYLE = f"color: {MATERIAL_COLORS['error']}; font-weight: bold;"

# Error title style (used in detailed_results_widget.py)
ERROR_TITLE_STYLE = (
    f"color: {MATERIAL_COLORS['error']}; font-weight: bold; font-size: 16px;"
)

# Status label style builder (used in detailed_results_widget.py and test_detail_view.py)
def get_status_label_style(color, weight="bold", size="14px"):
    """Get a status label style with customizable color, weight, and size"""
    return f"color: {color}; font-weight: {weight}; font-size: {size};"

# Status style builder (used in detailed_results_widget.py)
def build_status_style(passed, weight="bold", size=None):
    """Build a status style based on pass/fail state"""
    color = MATERIAL_COLORS["primary"] if passed else ERROR_COLOR_HEX
    style = f"color: {color};"
    if weight:
        style += f" font-weight: {weight};"
    if size:
        style += f" font-size: {size};"
    return style
