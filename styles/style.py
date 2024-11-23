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
}

QLabel#section_title {
    color: """ + COLORS['text_secondary'] + """;
    padding: 16px 20px 8px 20px;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    font-family: 'Segoe UI', system-ui;
}

QLabel#sidebar_title {
    color: """ + COLORS['text_light'] + """;
    background-color: """ + COLORS['primary'] + """;
    padding: 24px 20px;
    font-size: 20px;
    font-weight: bold;
    letter-spacing: 0.5px;
    font-family: 'Segoe UI', system-ui;
}

QPushButton#sidebar_button {
    color: """ + COLORS['text_light'] + """;
    background-color: transparent;
    border: none;
    text-align: left;
    padding: 12px 20px;
    font-size: 14px;
    font-weight: 500;
    border-radius: 6px;
    margin: 2px 8px;
    font-family: 'Segoe UI', system-ui;
}

QPushButton#sidebar_button:hover {
    background-color: """ + COLORS['hover'] + """;
}

QPushButton#sidebar_button:pressed {
    background-color: """ + COLORS['pressed'] + """;
}

QPushButton#back_button {
    color: """ + COLORS['text_light'] + """;
    background-color: """ + COLORS['primary'] + """;
    border: none;
    text-align: center;
    padding: 12px 20px;
    font-size: 14px;
    font-weight: 600;
    margin: 12px 16px;
    border-radius: 8px;
    font-family: 'Segoe UI', system-ui;
}

QPushButton#back_button:hover {
    background-color: """ + COLORS['primary_dark'] + """;
}

QFrame#sidebar_section {
    background-color: transparent;
    border-bottom: 1px solid """ + COLORS['border'] + """;
    margin-bottom: 8px;
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
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: """ + COLORS['border'] + """;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
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
