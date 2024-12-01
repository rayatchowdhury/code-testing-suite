from PySide6.QtGui import QColor

# Modern Pantone-inspired color palette
COLORS = {
    'primary': '#0096C7',           # Pantone Process Blue
    'primary_dark': '#023E8A',      # Pantone Classic Blue
    'secondary': '#FFB703',         # Pantone Warm Yellow
    'accent': '#F72585',            # Pantone Pink
    'background': '#1B1B1E',        # Dark background
    'surface': '#242426',           # Slightly lighter surface
    'sidebar': '#171717',           # Dark sidebar
    'text_primary': '#FFFFFF',
    'text_secondary': '#B3B3B3',
    'text_light': '#FFFFFF',
    'border': '#333333',
    'hover': '#2A2A2D',
    'pressed': '#323235'
}

# Update Material colors
MATERIAL_COLORS = {
    'background': '#1B1B1E',
    'surface': '#242426',
    'surface_dim': '#1F1F21',
    'surface_variant': '#2A2A2D',
    'primary': '#0096C7',
    'secondary': '#FFB703',
    'accent': '#F72585',
    'error': '#FF6B6B',
    'text_primary': '#FFFFFF',
    'text_secondary': '#B3B3B3',
    'button_hover': '#2A2A2D',
    'border': '#333333',
    'outline': '#3F3F3F'
}

# Styles
SIDEBAR_STYLE = """
QWidget#sidebar {
    background-color: """ + COLORS['sidebar'] + """;
    border: none;
    border-right: 1px solid """ + COLORS['border'] + """;
}

QLabel#section_title {
    color: """ + COLORS['accent'] + "CC" + """;
    padding: 2px 15px 2px 15px;
    margin: 0;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-family: 'Segoe UI', system-ui;
    background: transparent;
    border: none;
    position: relative;
}

QLabel#section_title::after {
    content: '';
    position: absolute;
    left: 20px;
    bottom: 0;
    width: 24px;
    height: 2px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                             stop:0 """ + COLORS['accent'] + "CC" + """,
                             stop:1 transparent);
}

QLabel#sidebar_title {
    color: """ + COLORS['text_light'] + """;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                             stop:0 """ + COLORS['primary_dark'] + "CC" + """,
                             stop:0.3 """ + COLORS['accent'] + "99" + """,
                             stop:0.6 """ + COLORS['primary'] + "BB" + """,
                             stop:1 """ + COLORS['primary_dark'] + "CC" + """);
    padding: 25px 16px;
    font-size: 21px;
    font-weight: 600;
    font-family: 'Segoe UI', system-ui;
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2),
                inset 0 0 30px rgba(255, 255, 255, 0.05);
    clip-path: polygon(0 0, 100% 0, 100% 85%, 95% 100%, 0 100%);
}

QPushButton#sidebar_button {
    color: """ + COLORS['text_light'] + """;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    text-align: left;
    padding: 14px 24px;
    font-size: 14px;
    font-weight: 500;
    border-radius: 12px;
    margin: 4px 12px;
    font-family: 'Segoe UI', system-ui;
    backdrop-filter: blur(10px);
}

QPushButton#sidebar_button:hover {
    background: linear-gradient(135deg,
                rgba(0, 150, 199, 0.1),
                rgba(255, 255, 255, 0.05));
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding-left: 28px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

QPushButton#sidebar_button:pressed {
    background: linear-gradient(135deg,
                rgba(0, 150, 199, 0.15),
                rgba(255, 255, 255, 0.07));
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding-left: 28px;
}

QPushButton#back_button {
    color: """ + COLORS['text_light'] + """;
    background: linear-gradient(135deg,
                rgba(0, 150, 199, 0.8),
                rgba(2, 62, 138, 0.9));
    border: 1px solid rgba(255, 255, 255, 0.1);
    text-align: center;
    padding: 14px 24px;
    font-size: 14px;
    font-weight: 600;
    margin: 16px;
    border-radius: 12px;
    font-family: 'Segoe UI', system-ui;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

QPushButton#back_button:hover {
    background: linear-gradient(135deg,
                rgba(2, 62, 138, 0.9),
                rgba(0, 150, 199, 0.8));
    border: 1px solid """ + COLORS['primary'] + """;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3),
                inset 0 0 20px rgba(255, 255, 255, 0.1);
}

QPushButton#back_button:pressed {
    background: linear-gradient(135deg,
                rgba(2, 62, 138, 1),
                rgba(0, 150, 199, 0.9));
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2),
                inset 0 0 15px rgba(0, 0, 0, 0.2);
}

QFrame#sidebar_section {
    background-color: transparent;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    margin: 2px 0 4px 0;
    padding-bottom: 4px;
}

QComboBox, QSpinBox, QSlider {
    color: """ + COLORS['text_light'] + """;
    background-color: """ + COLORS['surface'] + """;
    border: 1px solid """ + COLORS['border'] + """;
    padding: 8px;
    margin: 5px 15px;
    border-radius: 6px;
    font-family: 'Segoe UI', system-ui;
}

QScrollBar:vertical {
    border: none;
    background-color: """ + COLORS['sidebar'] + """;
    width: 6px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 3px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: rgba(255, 255, 255, 0.3);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
"""

SIDEBAR_BUTTON_STYLE = """
QPushButton {
    color: """ + COLORS['text_light'] + """;
    background-color: transparent;
    border: none;
    text-align: left;
    padding: 12px 15px;
    font-size: 14px;
}

QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.1);
}

QPushButton:pressed {
    background-color: rgba(255, 255, 255, 0.2);
}
"""

DISPLAY_AREA_STYLE = """
QWidget#display_area {
    background-color: """ + COLORS['background'] + """;
    border: none;
}
"""
