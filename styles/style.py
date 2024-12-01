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
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 """ + COLORS['primary'] + "44" + """,
                stop:1 """ + COLORS['primary_dark'] + "44" + """);
    border-radius: 4px;
    min-height: 40px;
    min-width: 40px;
}

QScrollBar::handle:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 """ + COLORS['primary'] + "66" + """,
                stop:1 """ + COLORS['primary_dark'] + "66" + """);
}

QScrollBar::handle:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 """ + COLORS['primary'] + "88" + """,
                stop:1 """ + COLORS['primary_dark'] + "88" + """);
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
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}

QLabel#section_title {
    color: """ + COLORS['accent'] + "CC" + """;
    background: transparent;
    padding: 2px 15px;
    margin: 4px 0;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-family: 'Segoe UI', system-ui;
}

QLabel#sidebar_title {
    color: """ + COLORS['text_light'] + """;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                             stop:0 """ + COLORS['primary_dark'] + "99" + """,
                             stop:0.4 """ + COLORS['primary'] + "77" + """,
                             stop:0.6 """ + COLORS['secondary'] + "33" + """,
                             stop:1 """ + COLORS['primary_dark'] + "99" + """);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    margin: 8px 12px;
    padding: 20px 16px;
    font-size: 21px;
    font-weight: 600;
    font-family: 'Segoe UI', system-ui;
}

QPushButton#sidebar_button {
    color: """ + COLORS['text_light'] + """;
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
}

QPushButton#sidebar_button:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 """ + COLORS['primary'] + "33" + """,
                stop:1 rgba(255, 255, 255, 0.07));
    border: 1px solid """ + COLORS['primary'] + "66" + """;
}

QPushButton#sidebar_button:pressed {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 """ + COLORS['primary'] + "22" + """,
                stop:1 rgba(255, 255, 255, 0.05));
    border: 1px solid """ + COLORS['primary'] + "44" + """;
    padding-left: 28px;
}

QPushButton#back_button {
    color: """ + COLORS['text_secondary'] + """;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(247, 37, 133, 0.15),
                stop:0.5 rgba(247, 37, 133, 0.08),
                stop:1 rgba(247, 37, 133, 0.15));
    border: 1px solid rgba(247, 37, 133, 0.2);
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
                stop:0 rgba(247, 37, 133, 0.25),
                stop:0.5 rgba(247, 37, 133, 0.15),
                stop:1 rgba(247, 37, 133, 0.25));
    border: 1px solid rgba(247, 37, 133, 0.3);
}

QPushButton#back_button:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(247, 37, 133, 0.35),
                stop:0.5 rgba(247, 37, 133, 0.25),
                stop:1 rgba(247, 37, 133, 0.35));
    border: 1px solid rgba(247, 37, 133, 0.4);
}

QFrame#sidebar_section {
    background: transparent;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    margin: 2px 0 4px 0;
    padding-bottom: 4px;
}

QComboBox, QSpinBox, QSlider {
    color: """ + COLORS['text_light'] + """;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(255, 255, 255, 0.05),
                stop:1 rgba(255, 255, 255, 0.02));
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 8px;
    margin: 5px 15px;
    border-radius: 6px;
    font-family: 'Segoe UI', system-ui;
}

QComboBox:hover, QSpinBox:hover, QSlider:hover {
    border: 1px solid """ + COLORS['primary'] + "44" + """;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 """ + COLORS['primary'] + "22" + """,
                stop:1 rgba(255, 255, 255, 0.05));
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
