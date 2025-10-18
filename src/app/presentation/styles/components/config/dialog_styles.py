"""
Config Dialog Container and Layout Styles.

Dialog-level styling including container, scroll areas, and section frames.
"""

from src.app.presentation.styles.components.scrollbar import SCROLLBAR_STYLE
from src.app.presentation.styles.constants.colors import MATERIAL_COLORS

CONFIG_DIALOG_CONTAINER_STYLE = f"""
QDialog {{
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(18, 18, 20, 0.98),
        stop:0.3 rgba(22, 22, 24, 0.95),
        stop:0.7 rgba(18, 18, 20, 0.98),
        stop:1 rgba(22, 22, 24, 0.95));
    color: {MATERIAL_COLORS['on_surface']};
    font-family: 'Segoe UI', system-ui;
    font-size: 14px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}}

QScrollArea {{
    background: transparent;
    border: none;
    outline: none;
}}

QScrollArea > QWidget {{
    background: transparent;
}}

QScrollArea > QWidget > QWidget {{
    background: transparent;
}}

QWidget#button_container {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(255, 255, 255, 0.02),
               stop:1 rgba(255, 255, 255, 0.01));
    border-top: 1px solid rgba(255, 255, 255, 0.06);
}}

QWidget#section_frame {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(255, 255, 255, 0.06),
               stop:1 rgba(255, 255, 255, 0.03));
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    margin: 2px 0px;
    padding: 6px;
}}

QWidget#section_frame:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(100, 181, 246, 0.1),
               stop:1 rgba(255, 255, 255, 0.08));
    border: 1px solid rgba(100, 181, 246, 0.2);
}}

QLabel#section_title {{
    color: rgba(100, 181, 246, 0.87);
    font-size: 12px;
    font-weight: 600;
    padding: 8px 12px;
    background: transparent;
    border: none;
    margin: 2px 0px;
}}

QWidget#section_content {{
    padding: 12px;
    background: transparent;
    border: none;
}}
""" + SCROLLBAR_STYLE

__all__ = [
    "CONFIG_DIALOG_CONTAINER_STYLE",
]
