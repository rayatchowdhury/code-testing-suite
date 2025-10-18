"""
Status View Test Card Styles.

Includes:
- Card section scroll area
- Card section titles
- Individual test card styles
- Card label styles
"""

from src.app.presentation.styles.constants.colors import COLORS, MATERIAL_COLORS

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

__all__ = [
    "CARDS_SECTION_SCROLL_STYLE",
    "CARDS_SECTION_TITLE_PASSED_STYLE",
    "CARDS_SECTION_TITLE_FAILED_STYLE",
    "get_test_card_style",
    "TEST_CARD_LABEL_HEADER_STYLE",
    "TEST_CARD_LABEL_STATUS_PASSED_STYLE",
    "TEST_CARD_LABEL_STATUS_FAILED_STYLE",
    "TEST_CARD_LABEL_METRIC_STYLE",
]
