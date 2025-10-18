"""
Status View Progress Bar and Statistics Styles.

Includes:
- Visual progress bar with segments
- Segment styles for different test states
- Statistics panel and labels
"""

from src.app.presentation.styles.constants.colors import COLORS, MATERIAL_COLORS

# ============================================================================
# PROGRESS SECTION
# ============================================================================

PROGRESS_SECTION_CONTAINER_STYLE = """
QWidget {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                             stop:0 rgba(36, 36, 38, 0.98),
                             stop:0.5 rgba(40, 40, 43, 0.95),
                             stop:1 rgba(36, 36, 38, 0.98));
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 16px;
}}
"""

VISUAL_PROGRESS_BAR_STYLE = """
QWidget {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                             stop:0 rgba(27, 27, 30, 0.98),
                             stop:1 rgba(31, 31, 33, 0.98));
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 10px;
}}
"""

# Segment styles for different states
SEGMENT_DEFAULT_STYLE = """
QFrame {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                             stop:0 rgba(31, 31, 33, 0.98),
                             stop:1 rgba(35, 35, 37, 0.98));
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 3px;
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
                                         stop:0 {COLORS['primary']},
                                         stop:1 {COLORS['primary_dark']});
                border: 1px solid {COLORS['primary']};
                border-radius: 3px;
            }}
        """,
        "failed": f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 {MATERIAL_COLORS['error']},
                                         stop:1 rgba(200, 40, 40, 1));
                border: 1px solid {MATERIAL_COLORS['error']};
                border-radius: 3px;
            }}
        """,
        "mixed_pass": f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 rgba(64, 169, 212, 1),
                                         stop:1 {COLORS['primary']});
                border: 1px solid rgba(64, 169, 212, 0.8);
                border-radius: 3px;
            }}
        """,
        "mixed_fail": """
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 rgba(255, 140, 66, 1),
                                         stop:1 rgba(255, 100, 40, 1));
                border: 1px solid rgba(255, 140, 66, 0.8);
                border-radius: 3px;
            }}
        """,
        "default": SEGMENT_DEFAULT_STYLE,
    }
    return gradients.get(state, SEGMENT_DEFAULT_STYLE)


STATS_PANEL_STYLE = f"""
QWidget {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                             stop:0 rgba(36, 36, 38, 0.98),
                             stop:0.5 rgba(40, 40, 43, 0.95),
                             stop:1 rgba(36, 36, 38, 0.98));
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 12px;
}}

QLabel {{
    color: {MATERIAL_COLORS['text_primary']};
    background: transparent;
    font-weight: 600;
    font-size: 14px;
    font-family: 'Segoe UI', system-ui;
    letter-spacing: 0.3px;
}}
"""

STATS_LABEL_PASSED_STYLE = f"""
color: {COLORS['primary']};
font-weight: 700;
font-size: 14px;
background: transparent;
"""

STATS_LABEL_FAILED_STYLE = f"""
color: {MATERIAL_COLORS['error']};
font-weight: 700;
font-size: 14px;
background: transparent;
"""

STATS_PERCENTAGE_STYLE = f"""
color: {MATERIAL_COLORS['text_primary']};
font-weight: 700;
font-size: 18px;
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
