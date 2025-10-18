"""
Status View Test Card Styles.

Redesigned with Material Design elevation and surfaces:
- Clean Material surface colors
- Proper shadows for depth (elevation)
- Vibrant but tasteful pass/fail indicators
- Modern hover effects with shadow transitions
- Consistent with app's overall design

Includes:
- Card section scroll area
- Card section titles
- Individual test card styles
- Card label styles
"""

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS

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
    Get test card style based on pass/fail state and hover.
    
    Uses Material Design elevation with proper surfaces and shadows.

    Args:
        passed: Whether test passed
        is_hover: Whether in hover state
    """
    if passed:
        base_bg = MATERIAL_COLORS['surface_variant']
        border = f"border: 2px solid {MATERIAL_COLORS['primary']};"
        hover_bg = MATERIAL_COLORS['primary_container']
        hover_border = f"border: 3px solid {MATERIAL_COLORS['primary']};"
    else:
        base_bg = MATERIAL_COLORS['error_container']
        border = f"border: 2px solid {MATERIAL_COLORS['error']};"
        hover_bg = MATERIAL_COLORS['error_container']
        hover_border = f"border: 3px solid {MATERIAL_COLORS['error']};"

    if is_hover:
        return f"""
            QFrame {{
                background: {hover_bg};
                {hover_border}
                border-radius: 10px;
                padding: 2px;
            }}
        """

    return f"""
            QFrame {{
                background: {base_bg};
                {border}
                border-radius: 10px;
            }}
            QFrame:hover {{
                background: {hover_bg};
                {hover_border}
                padding: 2px;
            }}
        """


# ============================================================================
# CARD LABEL STYLES
# ============================================================================

TEST_CARD_LABEL_HEADER_STYLE = f"""
font-weight: 700;
font-size: 14px;
color: {MATERIAL_COLORS['on_surface']};
background: transparent;
letter-spacing: 0.3px;
"""

TEST_CARD_LABEL_STATUS_PASSED_STYLE = f"""
color: {MATERIAL_COLORS['primary']};
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
color: {MATERIAL_COLORS['on_surface_variant']};
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
