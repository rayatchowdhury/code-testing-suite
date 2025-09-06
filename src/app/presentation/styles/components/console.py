from src.app.presentation.styles.constants.colors import MATERIAL_COLORS, COLORS

CONSOLE_CONTAINER_STYLE = """
QWidget#console_container {
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(22, 22, 24, 0.98),
        stop:0.3 rgba(26, 26, 28, 0.95),
        stop:0.7 rgba(22, 22, 24, 0.98),
        stop:1 rgba(26, 26, 28, 0.95)
    );
    border: none;
}
"""

# Update existing CONSOLE_STYLE to include the container style
CONSOLE_STYLE = CONSOLE_CONTAINER_STYLE + f"""
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
    margin: 8px 10px;
    padding: 8px 24px;
    font-size: 18px;
    font-weight: 600;
    font-family: 'Segoe UI', system-ui;
    letter-spacing: 1px;
    text-transform: uppercase;
    text-align: center;
    width: 100%;
}}

QLabel#output_title, QLabel#input_title {{
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

QPushButton#compile_run_btn {{
    color: #D0D0D0;  /* Dimmer white */
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(46, 125, 50, 0.25),   /* Darker green */
                stop:0.3 rgba(37, 110, 41, 0.2),  /* Darker green */
                stop:0.7 rgba(26, 92, 30, 0.23),  /* Darker green */
                stop:1 rgba(16, 75, 20, 0.25));   /* Darker green */

    text-align: center;
    padding: 4px 12px;  /* Reduced padding */
    font-size: 13px;    /* Slightly smaller font */
    font-weight: 600;
    margin: 4px 10px;    /* Reduced margin */
    border-radius: 9px;
    font-family: 'Segoe UI', system-ui;
    letter-spacing: 0.5px;
}}

QPushButton#compile_run_btn:hover {{
    color: #C8E6C9;  /* Dimmer green tint */
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(46, 125, 50, 0.35),
                stop:0.3 rgba(37, 110, 41, 0.3),
                stop:0.7 rgba(26, 92, 30, 0.33),
                stop:1 rgba(16, 75, 20, 0.35));
    border: 1.5px solid rgba(46, 125, 50, 0.5);
    padding: 4px 12px;  /* Keep consistent padding */
}}

QPushButton#compile_run_btn:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(46, 125, 50, 0.4),
                stop:0.3 rgba(37, 110, 41, 0.35),
                stop:0.7 rgba(26, 92, 30, 0.38),
                stop:1 rgba(16, 75, 20, 0.4));
    border: 1.2px solid rgba(46, 125, 50, 0.6);
    padding: 5px 11px 3px 13px;  /* Adjust pressed state padding */
}}

QPushButton#compile_run_btn:disabled {{
    color: #707070;  /* Dimmer grey text */
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(40, 40, 40, 0.08),
                stop:1 rgba(30, 30, 30, 0.08));
    border: 1.2px solid rgba(60, 60, 60, 0.15);
}}
"""
