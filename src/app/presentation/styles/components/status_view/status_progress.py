"""
Status View Progress Bar and Statistics Styles.

Redesigned with Material Design:
- Clean surface colors with proper elevation
- Vibrant segment colors for visual feedback
- Modern shadows and hover effects
- Consistent with app design language

Includes:
- Visual progress bar with segments
- Segment styles for different test states
- Statistics panel and labels
"""

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS
from src.app.presentation.styles.constants.spacing import SPACING, FONTS, BORDER_RADIUS, BORDER_WIDTH, SIZES

# ============================================================================
# PROGRESS SECTION
# ============================================================================

PROGRESS_SECTION_CONTAINER_STYLE = f"""
QWidget {{
    background: {MATERIAL_COLORS['surface']};
    border: {BORDER_WIDTH['THIN']}px solid {MATERIAL_COLORS['outline']};
    border-radius: {BORDER_RADIUS['XL']}px;
    padding: {SPACING['XL']}px;
}}
"""

VISUAL_PROGRESS_BAR_STYLE = f"""
QWidget {{
    background: {MATERIAL_COLORS['surface_dim']};
    border: {BORDER_WIDTH['MEDIUM']}px solid {MATERIAL_COLORS['outline_variant']};
    border-radius: {BORDER_RADIUS['LG']}px;
    padding: {SPACING['PADDING_SM']}px;
    min-height: {SIZES['PROGRESS_LG'] + SPACING['XL']}px;
}}
"""

# Segment styles for different states
SEGMENT_DEFAULT_STYLE = f"""
QFrame {{
    background: {MATERIAL_COLORS['surface_variant']};
    border: {BORDER_WIDTH['THIN']}px solid {MATERIAL_COLORS['outline_variant']};
    border-radius: {BORDER_RADIUS['SM']}px;
    min-height: {SIZES['PROGRESS_MD']}px;
}}
"""


def get_segment_style(state: str) -> str:
    """
    Get segment style based on test state.

    Args:
        state: 'passed', 'failed', 'mixed_pass', 'mixed_fail', or 'default'
    """
    gradients = {
        "passed": f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 {MATERIAL_COLORS['primary']},
                                         stop:1 {MATERIAL_COLORS['primary_container']});
                border: {BORDER_WIDTH['THIN']}px solid {MATERIAL_COLORS['primary']};
                border-radius: {BORDER_RADIUS['SM']}px;
                min-height: {SIZES['PROGRESS_MD']}px;
            }}
        """,
        "failed": f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 {MATERIAL_COLORS['error']},
                                         stop:1 #C62828);
                border: {BORDER_WIDTH['THIN']}px solid {MATERIAL_COLORS['error']};
                border-radius: {BORDER_RADIUS['SM']}px;
                min-height: {SIZES['PROGRESS_MD']}px;
            }}
        """,
        "mixed_pass": f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 {MATERIAL_COLORS['primary']},
                                         stop:1 {MATERIAL_COLORS['primary_container']});
                border: {BORDER_WIDTH['THIN']}px solid {MATERIAL_COLORS['primary']};
                border-radius: {BORDER_RADIUS['SM']}px;
                min-height: {SIZES['PROGRESS_MD']}px;
                opacity: 0.7;
            }}
        """,
        "mixed_fail": f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #FF8A65,
                                         stop:1 {MATERIAL_COLORS['error']});
                border: {BORDER_WIDTH['THIN']}px solid #FF8A65;
                border-radius: {BORDER_RADIUS['SM']}px;
                min-height: {SIZES['PROGRESS_MD']}px;
            }}
        """,
        "default": SEGMENT_DEFAULT_STYLE,
    }
    return gradients.get(state, SEGMENT_DEFAULT_STYLE)


STATS_PANEL_STYLE = f"""
QWidget {{
    background: {MATERIAL_COLORS['surface']};
    border: {BORDER_WIDTH['THIN']}px solid {MATERIAL_COLORS['outline_variant']};
    border-radius: {BORDER_RADIUS['MD']}px;
    padding: {SPACING['MD']}px {SPACING['PADDING_MD']}px;
}}

QLabel {{
    color: {MATERIAL_COLORS['on_surface']};
    background: transparent;
    font-weight: {FONTS['WEIGHT_SEMIBOLD']};
    font-size: {FONTS['BODY_LG']}px;
    font-family: 'Segoe UI', system-ui;
    letter-spacing: 0.3px;
}}
"""

STATS_LABEL_PASSED_STYLE = f"""
color: {MATERIAL_COLORS['primary']};
font-weight: {FONTS['WEIGHT_BOLD']};
font-size: {FONTS['TITLE_SM']}px;
background: transparent;
"""

STATS_LABEL_FAILED_STYLE = f"""
color: {MATERIAL_COLORS['error']};
font-weight: {FONTS['WEIGHT_BOLD']};
font-size: {FONTS['TITLE_SM']}px;
background: transparent;
"""

STATS_PERCENTAGE_STYLE = f"""
color: {MATERIAL_COLORS['on_surface']};
font-weight: {FONTS['WEIGHT_BOLD']};
font-size: {FONTS['TITLE_LG']}px;
background: transparent;
"""

__all__ = [
    "PROGRESS_SECTION_CONTAINER_STYLE",
    "VISUAL_PROGRESS_BAR_STYLE",
    "SEGMENT_DEFAULT_STYLE",
    "get_segment_style",
    "STATS_PANEL_STYLE",
    "STATS_LABEL_PASSED_STYLE",
    "STATS_LABEL_FAILED_STYLE",
    "STATS_PERCENTAGE_STYLE",
]
