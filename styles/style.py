from PySide6.QtGui import QColor

# Color scheme
COLORS = {
    'primary': '#2196F3',
    'primary_dark': '#1976D2',
    'secondary': '#FFC107',
    'background': '#FFFFFF',
    'surface': '#F5F5F5',
    'sidebar': '#263238',
    'text_primary': '#212121',
    'text_secondary': '#757575',
    'text_light': '#FFFFFF'
}
MATERIAL_COLORS = {
    'background': '#121212',
    'surface': '#1e1e1e',
    'surface_dim': '#171717',
    'surface_variant': '#252525',
    'primary': '#bb86fc',
    'secondary': '#03dac6',
    'error': '#cf6679',
    'text_primary': '#ffffff',
    'text_secondary': '#b3ffffff',  # 70% white
    'button_hover': '#bb86fc20',    # primary with 12% opacity
    'border': '#333333',
    'outline': '#3f3f3f'
}

# Styles
SIDEBAR_STYLE = """
QWidget#sidebar {
    background-color: """ + COLORS['sidebar'] + """;
    border: none;
}

QLabel#section_title {
    color: """ + COLORS['text_secondary'] + """;
    padding: 8px 15px;
    font-size: 12px;
    font-weight: bold;
    text-transform: uppercase;
}

QLabel#sidebar_title {
    color: """ + COLORS['text_light'] + """;
    background-color: """ + COLORS['primary_dark'] + """;
    padding: 20px 15px;
    font-size: 18px;
    font-weight: bold;
}

QPushButton#sidebar_button {
    color: """ + COLORS['text_light'] + """;
    background-color: transparent;
    border: none;
    text-align: left;
    padding: 12px 15px;
    font-size: 14px;
}

QPushButton#sidebar_button:hover {
    background-color: rgba(255, 255, 255, 0.1);
}

QPushButton#sidebar_button:pressed {
    background-color: rgba(255, 255, 255, 0.2);
}

QPushButton#back_button {
    color: """ + COLORS['text_light'] + """;
    background-color: """ + COLORS['primary_dark'] + """;
    border: none;
    text-align: center;
    padding: 12px 15px;
    font-size: 14px;
    margin: 10px;
    border-radius: 4px;
}

QPushButton#back_button:hover {
    background-color: """ + COLORS['primary'] + """;
}

QFrame#sidebar_section {
    background-color: transparent;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

QComboBox, QSpinBox, QSlider {
    color: """ + COLORS['text_light'] + """;
    background-color: """ + COLORS['primary_dark'] + """;
    border: none;
    padding: 5px;
    margin: 5px 15px;
    border-radius: 4px;
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
