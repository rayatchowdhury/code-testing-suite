"""
Status View Styles - Comprehensive styling for unified status views.

Designed to match the app's gradient-based design language with:
- Subtle gradients matching sidebar and console
- Consistent borders and shadows
- Material Design color palette
- Smooth transitions and hover effects
"""

from src.app.presentation.styles.constants.colors import COLORS, MATERIAL_COLORS

# ============================================================================
# STATUS VIEW CONTAINER
# ============================================================================

STATUS_VIEW_CONTAINER_STYLE = """
QWidget {{
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(27, 27, 30, 0.98),
        stop:0.3 rgba(30, 30, 33, 0.95),
        stop:0.7 rgba(27, 27, 30, 0.98),
        stop:1 rgba(30, 30, 33, 0.95));
    border: none;
}}
"""

# ============================================================================
# CONTROLS PANEL (File buttons area at top)
# ============================================================================

CONTROLS_PANEL_STYLE = """
QWidget {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                             stop:0 rgba(36, 36, 38, 0.98),
                             stop:0.5 rgba(40, 40, 43, 0.95),
                             stop:1 rgba(36, 36, 38, 0.98));
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 12px 16px;
}}
"""

FILE_BUTTON_STYLE = f"""
QPushButton {{
    color: {COLORS['text_light']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                             stop:0 rgba(255, 255, 255, 0.06),
                             stop:1 rgba(255, 255, 255, 0.03));
    border: 1px solid rgba(255, 255, 255, 0.08);
    text-align: center;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
    border-radius: 8px;
    margin: 0 4px;
    font-family: 'Segoe UI', system-ui;
    letter-spacing: 0.3px;
}}

QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {COLORS['primary']}33,
                stop:1 rgba(255, 255, 255, 0.08));
    border: 1px solid {COLORS['primary']}66;
}}

QPushButton:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {COLORS['primary']}22,
                stop:1 rgba(255, 255, 255, 0.05));
    border: 1px solid {COLORS['primary']}44;
    padding: 11px 19px 9px 21px;
}}

QPushButton:disabled {{
    color: {MATERIAL_COLORS['text_disabled']};
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.03);
}}
"""

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

# ============================================================================
# TEST CARDS SECTION
# ============================================================================

CARDS_SECTION_SCROLL_STYLE = f"""
QScrollArea {{
    border: 2px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                             stop:0 rgba(27, 27, 30, 0.98),
                             stop:1 rgba(31, 31, 33, 0.98));
}}

QScrollBar:vertical {{
    background: rgba(255, 255, 255, 0.03);
    width: 12px;
    border-radius: 6px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                             stop:0 {COLORS['primary']}80,
                             stop:1 {COLORS['primary']}60);
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                             stop:0 {COLORS['primary']},
                             stop:1 {COLORS['primary']}80);
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}
"""

CARDS_SECTION_TITLE_PASSED_STYLE = f"""
QLabel {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                             stop:0 rgba(0, 150, 199, 0.18),
                             stop:0.5 rgba(0, 120, 160, 0.15),
                             stop:1 rgba(0, 150, 199, 0.18));
    color: {MATERIAL_COLORS['text_primary']};
    padding: 10px 16px;
    border-radius: 8px;
    border: 1px solid {COLORS['primary']}40;
    font-weight: 700;
    font-size: 15px;
    letter-spacing: 0.5px;
    font-family: 'Segoe UI', system-ui;
}}
"""

CARDS_SECTION_TITLE_FAILED_STYLE = f"""
QLabel {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                             stop:0 rgba(255, 107, 107, 0.18),
                             stop:0.5 rgba(220, 80, 80, 0.15),
                             stop:1 rgba(255, 107, 107, 0.18));
    color: {MATERIAL_COLORS['text_primary']};
    padding: 10px 16px;
    border-radius: 8px;
    border: 1px solid {MATERIAL_COLORS['error']}40;
    font-weight: 700;
    font-size: 15px;
    letter-spacing: 0.5px;
    font-family: 'Segoe UI', system-ui;
}}
"""

# ============================================================================
# TEST CARD STYLES
# ============================================================================


def get_test_card_style(passed: bool, is_hover: bool = False) -> str:
    """
    Get test card style based on pass/fail state and hover.

    Args:
        passed: Whether test passed
        is_hover: Whether in hover state
    """
    if passed:
        base_bg = """
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                     stop:0 rgba(0, 75, 99, 0.25),
                                     stop:0.5 rgba(0, 90, 120, 0.20),
                                     stop:1 rgba(0, 75, 99, 0.25));
        """
        border = f"border: 2px solid {COLORS['primary']}60;"
        hover_bg = """
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                     stop:0 rgba(0, 100, 135, 0.35),
                                     stop:0.5 rgba(0, 120, 160, 0.28),
                                     stop:1 rgba(0, 100, 135, 0.35));
        """
        hover_border = f"border: 3px solid {COLORS['primary']}90;"
    else:
        base_bg = """
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                     stop:0 rgba(66, 1, 1, 0.35),
                                     stop:0.5 rgba(80, 10, 10, 0.28),
                                     stop:1 rgba(66, 1, 1, 0.35));
        """
        border = f"border: 2px solid {MATERIAL_COLORS['error']}60;"
        hover_bg = """
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                     stop:0 rgba(90, 15, 15, 0.45),
                                     stop:0.5 rgba(110, 20, 20, 0.38),
                                     stop:1 rgba(90, 15, 15, 0.45));
        """
        hover_border = f"border: 3px solid {MATERIAL_COLORS['error']}90;"

    if is_hover:
        return f"""
            QFrame {{
                {hover_bg}
                {hover_border}
                border-radius: 10px;
                padding: 2px;
            }}
        """

    return f"""
            QFrame {{
                {base_bg}
                {border}
                border-radius: 10px;
            }}
            QFrame:hover {{
                {hover_bg}
                {hover_border}
                padding: 2px;
            }}
        """


TEST_CARD_LABEL_HEADER_STYLE = f"""
font-weight: 700;
font-size: 14px;
color: {MATERIAL_COLORS['text_primary']};
background: transparent;
letter-spacing: 0.3px;
"""

TEST_CARD_LABEL_STATUS_PASSED_STYLE = f"""
color: {COLORS['primary']};
font-weight: 700;
font-size: 14px;
background: transparent;
"""

TEST_CARD_LABEL_STATUS_FAILED_STYLE = f"""
color: {MATERIAL_COLORS['error']};
font-weight: 700;
font-size: 14px;
background: transparent;
"""

TEST_CARD_LABEL_METRIC_STYLE = f"""
color: {MATERIAL_COLORS['text_secondary']};
font-size: 12px;
background: transparent;
"""

# ============================================================================
# SECTION HEADERS
# ============================================================================

SECTION_HEADER_STYLE = f"""
QLabel {{
    color: {COLORS['accent']}CC;
    background: transparent;
    padding: 4px 8px;
    margin: 8px 0 4px 0;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-family: 'Segoe UI', system-ui;
}}
"""

# ============================================================================
# EXPORT ALL STYLES
# ============================================================================

__all__ = [
    "STATUS_VIEW_CONTAINER_STYLE",
    "CONTROLS_PANEL_STYLE",
    "FILE_BUTTON_STYLE",
    "PROGRESS_SECTION_CONTAINER_STYLE",
    "VISUAL_PROGRESS_BAR_STYLE",
    "SEGMENT_DEFAULT_STYLE",
    "get_segment_style",
    "STATS_PANEL_STYLE",
    "STATS_LABEL_PASSED_STYLE",
    "STATS_LABEL_FAILED_STYLE",
    "STATS_PERCENTAGE_STYLE",
    "CARDS_SECTION_SCROLL_STYLE",
    "CARDS_SECTION_TITLE_PASSED_STYLE",
    "CARDS_SECTION_TITLE_FAILED_STYLE",
    "get_test_card_style",
    "TEST_CARD_LABEL_HEADER_STYLE",
    "TEST_CARD_LABEL_STATUS_PASSED_STYLE",
    "TEST_CARD_LABEL_STATUS_FAILED_STYLE",
    "TEST_CARD_LABEL_METRIC_STYLE",
    "SECTION_HEADER_STYLE",
]
