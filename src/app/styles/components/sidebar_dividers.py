"""
Sidebar specific styles including dividers and gradients
"""
from ...styles.constants.colors import MATERIAL_COLORS

# Sidebar divider container styles
SIDEBAR_DIVIDER_CONTAINER_STYLE = "background-color: #1b1b1e;"

SIDEBAR_DIVIDER_SPACE_STYLE = "background-color: #1b1b1e;"

# Main sidebar divider gradient style
SIDEBAR_MAIN_DIVIDER_STYLE = """
    background: qlineargradient(
        spread: pad,
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 rgba(247, 37, 133, 0.6),
        stop: 0.5 rgba(144, 12, 63, 0.8),
        stop: 1 rgba(88, 24, 69, 0.6)
    );
    border-radius: 1px;
    margin-left: 10px;
    margin-right: 10px;
"""

# Footer divider styles
SIDEBAR_FOOTER_CONTAINER_STYLE = "background-color: #1e1e1e;"

SIDEBAR_FOOTER_SPACE_STYLE = "background-color: #1e1e1e;"

SIDEBAR_FOOTER_DIVIDER_STYLE = """
    background: qlineargradient(
        spread: pad,
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 rgba(96, 125, 139, 0.6),
        stop: 0.5 rgba(69, 90, 100, 0.8),
        stop: 1 rgba(38, 50, 56, 0.6)
    );
    border-radius: 1px;
    margin-left: 10px;
    margin-right: 10px;
"""

# Vertical footer divider style
SIDEBAR_VERTICAL_FOOTER_DIVIDER_STYLE = """
    background: qlineargradient(
        spread: pad,
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(96, 125, 139, 0.6),
        stop: 0.5 rgba(69, 90, 100, 0.8),
        stop: 1 rgba(38, 50, 56, 0.6)
    );
"""
