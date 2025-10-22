"""
Status View Test Card Styles.

Redesigned with Glassmorphism V2 design:
- Modern glassmorphism effects with rgba transparency
- Uses MATERIAL_COLORS palette for consistency
- Left-border accent for pass/fail status
- Subtle gradients for depth
- Consistent with app's overall design

Includes:
- Card section scroll area
- Card section titles
- Individual test card styles
- Card label styles
"""

from src.app.presentation.shared.design_system.tokens.colors import MATERIAL_COLORS

# ============================================================================
# TEST CARDS SECTION
# ============================================================================

CARDS_SECTION_SCROLL_STYLE = f"""
QScrollArea {{
    border: 2px solid {MATERIAL_COLORS['outline']};
    border-radius: 10px;
    background: {MATERIAL_COLORS['surface_dim']};
}}

QScrollBar:vertical {{
    background: {MATERIAL_COLORS['surface_variant']};
    width: 12px;
    border-radius: 6px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {MATERIAL_COLORS['primary']};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {MATERIAL_COLORS['primary_container']};
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
    background: {MATERIAL_COLORS['primary_container']};
    color: {MATERIAL_COLORS['on_primary_container']};
    padding: 12px 16px;
    border-radius: 8px;
    border: 2px solid {MATERIAL_COLORS['primary']};
    font-weight: 700;
    font-size: 15px;
    letter-spacing: 0.5px;
    font-family: 'Segoe UI', system-ui;
}}
"""

CARDS_SECTION_TITLE_FAILED_STYLE = f"""
QLabel {{
    background: {MATERIAL_COLORS['error_container']};
    color: {MATERIAL_COLORS['on_error_container']};
    padding: 12px 16px;
    border-radius: 8px;
    border: 2px solid {MATERIAL_COLORS['error']};
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
    Get test card style based on pass/fail state with glassmorphism V2 design.
    
    Uses rgba gradients and left-border accent.

    Args:
        passed: Whether test passed
        is_hover: Whether in hover state
    """
    border_color = MATERIAL_COLORS['success'] if passed else MATERIAL_COLORS['error']

    if is_hover:
        return f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(48, 48, 51, 0.90),
                    stop:1 rgba(42, 42, 45, 0.95));
                border-left: 4px solid {border_color};
                border-top: 1px solid {MATERIAL_COLORS['outline']};
                border-right: 1px solid {MATERIAL_COLORS['outline']};
                border-bottom: 1px solid {MATERIAL_COLORS['outline']};
                border-radius: 8px;
                border-top-left-radius: 0;
                border-bottom-left-radius: 0;
            }}
        """

    return f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(42, 42, 45, 0.85),
                    stop:1 rgba(36, 36, 38, 0.90));
                border-left: 4px solid {border_color};
                border-top: 1px solid {MATERIAL_COLORS['outline']};
                border-right: 1px solid {MATERIAL_COLORS['outline']};
                border-bottom: 1px solid {MATERIAL_COLORS['outline']};
                border-radius: 8px;
                border-top-left-radius: 0;
                border-bottom-left-radius: 0;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(48, 48, 51, 0.90),
                    stop:1 rgba(42, 42, 45, 0.95));
            }}
        """


# ============================================================================
# CARD LABEL STYLES (V2 Glassmorphism)
# ============================================================================

TEST_CARD_LABEL_HEADER_STYLE = f"""
font-weight: 700;
font-size: 14px;
color: {MATERIAL_COLORS['text_primary']};
background: transparent;
letter-spacing: 0.3px;
"""

TEST_CARD_LABEL_STATUS_PASSED_STYLE = f"""
color: {MATERIAL_COLORS['success']};
font-weight: 700;
font-size: 13px;
background: transparent;
"""

TEST_CARD_LABEL_STATUS_FAILED_STYLE = f"""
color: {MATERIAL_COLORS['error']};
font-weight: 700;
font-size: 13px;
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
