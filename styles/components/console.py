from ..constants.colors import MATERIAL_COLORS, COLORS  # Add COLORS import

CONSOLE_STYLE = f"""
* {{
    background-color: transparent;
}}

QWidget#console_title {{
    background: qlineargradient(x1: 1, y1: 0, x2: 0, y2: 1,
                             stop: 0 rgba(25, 25, 27, 0.98),
                             stop: 0.03 rgba(25, 25, 27, 0.98),
                             stop: 0.5 rgba(45, 55, 65, 0.8),
                             stop: 0.6 rgba(30, 30, 30, 0.6),
                             stop: 0.8 rgba(24, 24, 26, 0.98),
                             stop: 1 rgba(24, 24, 26, 0.98));
    color: {COLORS['text_light']};
    border-radius: 12px;
    margin: 8px auto;
    padding: 8px 24px;
    font-size: 18px;
    font-weight: 600;
    font-family: 'Segoe UI', system-ui;
    letter-spacing: 1px;
    text-transform: uppercase;
    max-width: 250px;
}}

QLabel#output_title, QLabel#input_title {{
    background: #2A2A2A;
    color: #E0E0E0;
    font-family: 'Segoe UI';
    font-size: 13px;
    font-weight: 600;
    padding: 4px 8px;
    margin: 4px 8px 0 8px;
    letter-spacing: 0.5px;
}}

QPlainTextEdit {{
    color: #FFFFFF;
    border: 2px solid;
    border-radius: 4px;
    padding: 8px;
    margin: 4px 8px 8px 8px;
}}

QPlainTextEdit#console_output {{
    background-color: #1A1A1A;
    border-color: #151515;
}}

QPlainTextEdit#console_input {{
    background-color: #242424;
    border-color: #1F1F1F;
}}

# ...existing button styles...
"""
