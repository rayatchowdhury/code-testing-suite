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

# Unified scrollbar styling for all components
SCROLLBAR_STYLE = """
QScrollBar:vertical, QScrollBar:horizontal {
    border: none;
    background: transparent;
    margin: 0;
}

QScrollBar:vertical {
    width: 8px;
}

QScrollBar:horizontal {
    height: 8px;
}

QScrollBar::handle {
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    min-height: 40px;
    min-width: 40px;
}

QScrollBar::handle:hover {
    background-color: rgba(255, 255, 255, 0.15);
}

QScrollBar::handle:pressed {
    background-color: rgba(255, 255, 255, 0.2);
}

QScrollBar::add-line, QScrollBar::sub-line {
    height: 0;
    width: 0;
    background: none;
}

QScrollBar::add-page, QScrollBar::sub-page {
    background: none;
}
"""

# Modified SIDEBAR_STYLE to use the unified scrollbar style
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
}

QPushButton#sidebar_button:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(0, 150, 199, 0.1),
                stop:1 rgba(255, 255, 255, 0.05));
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding-left: 28px;
}

QPushButton#sidebar_button:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(0, 150, 199, 0.15),
                stop:1 rgba(255, 255, 255, 0.07));
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding-left: 28px;
}

QPushButton#back_button {
    color: """ + COLORS['text_secondary'] + """;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(30, 30, 32, 0.95),
                stop:1 rgba(40, 40, 42, 0.95));
    border: 1px solid rgba(255, 255, 255, 0.08);
    text-align: center;
    padding: 12px 20px;
    font-size: 13px;
    font-weight: 500;
    margin: 16px;
    border-radius: 8px;
    font-family: 'Segoe UI', system-ui;
}

QPushButton#back_button:hover {
    color: """ + COLORS['text_light'] + """;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(40, 40, 42, 0.98),
                stop:1 rgba(50, 50, 52, 0.98));
    border: 1px solid rgba(255, 255, 255, 0.12);
}

QPushButton#back_button:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(25, 25, 27, 1),
                stop:1 rgba(35, 35, 37, 1));
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 12px 20px;
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
""" + SCROLLBAR_STYLE

# Simplified DISPLAY_AREA_STYLE
DISPLAY_AREA_STYLE = """
QWidget#display_area {
    background-color: """ + COLORS['background'] + """;
    border: none;
}
"""

# Simplified WEBVIEW_STYLE
WEBVIEW_STYLE = """
QWebEngineView {
    background-color: """ + COLORS['background'] + """;
    border: none;
}
""" + SCROLLBAR_STYLE

# Simplified SIDEBAR_BUTTON_STYLE - remove redundant properties
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
