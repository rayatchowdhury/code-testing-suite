"""
Status View Container and Control Panel Styles.

Designed to match the app's gradient-based design language with:
- Subtle gradients matching sidebar and console
- Consistent borders and shadows
- Material Design color palette
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

__all__ = [
    "STATUS_VIEW_CONTAINER_STYLE",
    "CONTROLS_PANEL_STYLE",
    "FILE_BUTTON_STYLE",
    "SECTION_HEADER_STYLE",
]
