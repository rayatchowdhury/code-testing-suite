from ..constants.colors import COLORS
from .scrollbar import SCROLLBAR_STYLE

SIDEBAR_STYLE = f"""
QWidget {{
    background:  '#1B1B1E';
}}

QWidget#sidebar, QWidget#sidebar_scroll, QWidget#sidebar_content {{
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(22, 22, 24, 0.98),
        stop:0.3 rgba(26, 26, 28, 0.95),
        stop:0.7 rgba(22, 22, 24, 0.98),
        stop:1 rgba(26, 26, 28, 0.95));
}}

QWidget#sidebar {{
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}}

QLabel#section_title {{
    color: {COLORS['accent']}CC;
    background: transparent;
    padding: 2px 15px;
    margin: 4px 0;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-family: 'Segoe UI', system-ui;
}}

QLabel#sidebar_title {{
    color: {COLORS['text_light']};
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                             stop: 0 rgba(30, 30, 30, 0.98),
                             stop: 0.03 rgba(30, 30, 30, 0.98),
                             stop: 0.5 rgba(135, 20, 65, 0.8),
                             stop: 0.6 rgba(30, 30, 30, 0.6),
                             stop: 1 rgba(30, 30, 30, 0.98));
    border: 2px solid {COLORS['primary']}44;
    border-radius: 12px;
    margin: 8px 12px;
    padding: 20px 16px;
    font-size: 21px;
    font-weight: 600;
    font-family: 'Segoe UI', system-ui;
}}

QPushButton#sidebar_button {{
    color: {COLORS['text_light']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                             stop:0 rgba(255, 255, 255, 0.05),
                             stop:1 rgba(255, 255, 255, 0.02));
    border: 1px solid rgba(255, 255, 255, 0.05);
    text-align: left;
    padding: 14px 24px;
    font-size: 14px;
    font-weight: 500;
    border-radius: 12px;
    margin: 4px 12px;
    font-family: 'Segoe UI', system-ui;
}}

QPushButton#sidebar_button:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {COLORS['primary']}33,
                stop:1 rgba(255, 255, 255, 0.07));
    border: 1px solid {COLORS['primary']}66;
}}

QPushButton#sidebar_button:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {COLORS['primary']}22,
                stop:1 rgba(255, 255, 255, 0.05));
    border: 1px solid {COLORS['primary']}44;
    padding-left: 28px;
}}

QPushButton#back_button {{ 
    color: {COLORS['text_light']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(247, 37, 133, 0.18),
                stop:0.3 rgba(247, 37, 133, 0.12),
                stop:0.7 rgba(144, 12, 63, 0.15),
                stop:1 rgba(88, 24, 69, 0.18));
    border: 1.2px solid rgba(247, 37, 133, 0.25);
    text-align: center;
    padding: 12px 20px;
    font-size: 14px;
    font-weight: 600;
    margin: 8px 16px; 
    border-radius: 10px;
    font-family: 'Segoe UI', system-ui;
    letter-spacing: 0.3px;
}}

QPushButton#back_button:hover {{
    color: white;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(247, 37, 133, 0.32),
                stop:0.3 rgba(247, 37, 133, 0.26),
                stop:0.7 rgba(144, 12, 63, 0.29),
                stop:1 rgba(88, 24, 69, 0.32));
    border: 1.5px solid rgba(247, 37, 133, 0.5);
}}

QPushButton#back_button:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(247, 37, 133, 0.38),
                stop:0.3 rgba(247, 37, 133, 0.32),
                stop:0.7 rgba(144, 12, 63, 0.35),
                stop:1 rgba(88, 24, 69, 0.38));
    border: 1.2px solid rgba(247, 37, 133, 0.5);
    padding: 13px 19px 11px 21px;
}}

QPushButton#footer_button {{ 
    color: {COLORS['text_secondary']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(38, 50, 56, 0.7),
                stop:0.5 rgba(55, 71, 79, 0.5),
                stop:1 rgba(69, 90, 100, 0.7));
    border: 1px solid rgba(96, 125, 139, 0.4);
    text-align: center;
    padding: 10px 18px;
    font-size: 14px;
    font-weight: 500;
    margin: 8px 16px; 
    border-radius: 8px;
    font-family: 'Segoe UI', system-ui;
}}

QPushButton#footer_button:hover {{
    color: {COLORS['text_light']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(55, 71, 79, 0.8),
                stop:0.5 rgba(69, 90, 100, 0.6),
                stop:1 rgba(96, 125, 139, 0.8));
    border: 1px solid rgba(120, 144, 156, 0.5);
}}

QPushButton#footer_button:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(69, 90, 100, 0.9),
                stop:0.5 rgba(84, 110, 122, 0.7),
                stop:1 rgba(120, 144, 156, 0.9));
    border: 1px solid rgba(144, 164, 174, 0.6);
    padding: 11px 17px 9px 19px;
}}

QFrame#sidebar_section {{
    background: 1b1b1e;
    border-bottom: 1px solid {COLORS['primary']}44;
    margin: 2px 0 4px 0;
    padding-bottom: 4px;
}}

QComboBox, QSpinBox, QSlider {{
    color: {COLORS['text_light']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(255, 255, 255, 0.05),
                stop:1 rgba(255, 255, 255, 0.02));
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 8px;
    margin: 5px 15px;
    border-radius: 6px;
    font-family: 'Segoe UI', system-ui;
}}

QComboBox:hover, QSpinBox:hover, QSlider:hover {{
    border: 1px solid {COLORS['primary']}44;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {COLORS['primary']}22,
                stop:1 rgba(255, 255, 255, 0.05));
}}
""" + SCROLLBAR_STYLE + """
QScrollArea#sidebar_scroll {{
    border: none;
}}

QWidget#sidebar_content {{
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(22, 22, 24, 0.98),
        stop:0.3 rgba(26, 26, 28, 0.95),
        stop:0.7 rgba(22, 22, 24, 0.98),
        stop:1 rgba(26, 26, 28, 0.95));
}}

QWidget#sidebar > QWidget {{
    background: 1b1b1e;
}}
"""

SIDEBAR_BUTTON_STYLE = f"""
QPushButton {{
    color: {COLORS['text_light']};
    background-color: transparent;
    border: none;
    text-align: left;
    padding: 12px 15px;
    font-size: 14px;
}}

QPushButton:hover {{
    background-color: rgba(255, 255, 255, 0.1);
}}

QPushButton:pressed {{
    background-color: rgba(255, 255, 255, 0.2);
}}
"""