from ..constants.colors import MATERIAL_COLORS

CONSOLE_STYLE = f"""
* {{
    background-color: transparent;
}}

QWidget#console_title {{
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
        stop:0 #2C3333,
        stop:1 #2C3333
    );
    color: {MATERIAL_COLORS['text_primary']};
    font-weight: bold;
    font-family: 'Segoe UI';
    font-size: 16px;
    border-bottom: 1px solid #1A1A1A;
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