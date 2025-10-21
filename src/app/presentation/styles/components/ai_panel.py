from src.app.presentation.design_system.tokens.colors import MATERIAL_COLORS

# Base gradient and color variables for reuse
PANEL_GRADIENT = f"""
    qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {MATERIAL_COLORS['surface_dim']},
        stop:0.5 {MATERIAL_COLORS['surface']},
        stop:1 {MATERIAL_COLORS['surface_dim']})
"""

BUTTON_GRADIENT = """
    qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #2A333B,
        stop:1 #1E2429)
"""

BUTTON_HOVER_GRADIENT = """
    qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #21272D,
        stop:1 #171A1E)
"""

# Base AI panel styles with consistent sizing
AI_PANEL_STYLE = f"""
QWidget#ai_panel {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(15, 18, 23, 0.4),
               stop:1 rgba(10, 12, 16, 0.4));
    border-top: 1px solid {MATERIAL_COLORS['outline']};
    min-height: 48px;  /* Increased height */
    max-height: 48px;  /* Increased height */
}}

QWidget#ai_left_container,
QWidget#ai_button_container,
QWidget#ai_button_sections {{
    background: transparent;
    margin: 0px;
    padding: 0px;
}}

QPushButton#ai_button {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(20, 24, 28, 0.5),
               stop:1 rgba(14, 17, 20, 0.5));
    color: {MATERIAL_COLORS['on_primary']};
    border: 1px solid #3C4A52;
    border-radius: 7px;
    padding: 4px 10px;
    margin: 0px;
    min-width: 50px;
    max-width: 80px;
    min-height: 24px;
    max-height: 24px;
    font: 500 11px 'Segoe UI';
    letter-spacing: 0.3px;
}}

QPushButton#ai_button:hover {{
    background: #171A1E; /* Even darker */
    border: 1px solid #525F67;
}}

QPushButton#ai_button:pressed {{
    background: #131619;
    border: 1px solid #68737B;
    padding: 3px 9px 1px 11px;
}}

QPushButton#ai_button:disabled {{
    background: #2A2A2D;
    color: {MATERIAL_COLORS['on_surface_disabled']};
    border-color: #3C4A52;
}}

QFrame#ai_separator {{
    background: {MATERIAL_COLORS['outline_variant']};
    width: 1px;
    margin: 4px 4px;
    opacity: 0.5;
}}
"""

# Custom command input styles
CUSTOM_COMMAND_STYLE = f"""
QFrame#custom_command_frame {{
    background: transparent;
    margin: 0px;
    padding: 0px;
    min-width: 200px;  /* Added minimum width */
}}

QLineEdit#custom_command_input {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(10, 12, 16, 0.5),
               stop:1 rgba(5, 7, 10, 0.5));
    border: 1px solid #5DC7FF;  /* Distinct glowing border */
    color: {MATERIAL_COLORS['on_surface']};
    border-radius: 14px;
    padding: 4px 12px;
    margin: 0px;
    font: 400 11px 'Segoe UI';
    letter-spacing: 0.2px;
    min-height: 24px;
    max-height: 24px;
}}

QLineEdit#custom_command_input:focus {{
    background: #171A1E; /* Keep it slightly darker */
    border: 1px solid #68737B;
}}

QLineEdit#custom_command_input:hover {{
    border: 1px solid #525F67; /* Maintain subtle dark border, no glow */
}}

QLineEdit#custom_command_input:disabled {{
    background: #2A2A2D;
    color: {MATERIAL_COLORS['on_surface_disabled']};
    border-color: #3C4A52;
}}

QLineEdit#custom_command_input::placeholder {{
    color: {MATERIAL_COLORS['on_surface_variant']};
    opacity: 0.6;
}}
"""

# AI Dialog styles with consistent theme
AI_DIALOG_STYLE = f"""
QDialog {{
    background: {MATERIAL_COLORS['surface']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 8px;
}}

QScrollArea {{
    border: none;
    background: transparent;
}}

QLabel {{
    color: {MATERIAL_COLORS['on_surface']};
    background: transparent;
    font: 400 13px 'Segoe UI';
}}

QPushButton {{
    background: {MATERIAL_COLORS['primary']};
    color: {MATERIAL_COLORS['on_primary']};
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font: 500 12px 'Segoe UI';
    letter-spacing: 0.3px;
}}

QPushButton:hover {{
    background: {MATERIAL_COLORS['primary_container']};
}}

QPushButton:pressed {{
    background: {MATERIAL_COLORS['primary_dark']};
    padding: 9px 15px 7px 17px;
}}
"""

__all__ = ["AI_PANEL_STYLE", "CUSTOM_COMMAND_STYLE", "AI_DIALOG_STYLE"]
