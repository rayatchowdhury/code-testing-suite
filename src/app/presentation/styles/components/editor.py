from src.app.presentation.styles.constants.colors import MATERIAL_COLORS
from src.app.presentation.styles.constants.editor_colors import EDITOR_COLORS

AI_DIALOG_STYLE = f"""
    QDialog {{
        background-color: {MATERIAL_COLORS['surface']};
        border: 1px solid {MATERIAL_COLORS['outline']};
        border-radius: 16px;
        min-width: 900px;
        min-height: 650px;
    }}

    QScrollArea {{
        border: none;
        background-color: transparent;
        margin: 0;
        padding: 0;
    }}

    QLabel {{
        color: {MATERIAL_COLORS['on_surface']};
        background-color: transparent;
        padding: 30px;
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px;
        line-height: 1.7;
    }}

    /* Headers with emoji */
    QLabel h1, QLabel h2, QLabel h3 {{
        color: {MATERIAL_COLORS['primary']};
        margin: 20px 0;
        font-weight: 500;
        opacity: 0.9;
    }}

    QLabel h1 {{
        font-size: 32px;
        padding-bottom: 15px;
        border-bottom: 2px solid {MATERIAL_COLORS['primary']};
    }}

    QLabel h2 {{
        font-size: 24px;
    }}

    QLabel h3 {{
        font-size: 18px;
    }}

    /* Enhanced Sections */
    QLabel .section {{
        margin: 25px 0;
        padding: 20px;
        background: {MATERIAL_COLORS['surface_bright']};
        border-radius: 12px;
        border: 1px solid {MATERIAL_COLORS['outline']};
    }}

    QLabel .section.bordered {{
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}

    /* Code Sections */
    QLabel pre, QLabel code {{
        background: {MATERIAL_COLORS['surface_variant']};
        padding: 20px;
        border-radius: 12px;
        border: 1px solid {MATERIAL_COLORS['outline_variant']};
        font-family: 'Consolas', monospace;
        font-size: 14px;
        line-height: 1.5;
    }}

    QLabel code {{
        padding: 3px 6px;
        font-size: 13px;
    }}

    /* Lists */
    QLabel ul, QLabel ol {{
        margin: 15px 0;
        padding-left: 28px;
    }}

    QLabel li {{
        margin: 10px 0;
        line-height: 1.6;
        color: {MATERIAL_COLORS['on_surface']};
    }}

    /* Info Boxes */
    QLabel .info-box {{
        margin: 20px 0;
        padding: 20px;
        background: {MATERIAL_COLORS['surface_variant']};
        border-left: 4px solid {MATERIAL_COLORS['primary']};
        border-radius: 8px;
    }}

    /* Algorithm Steps */
    QLabel .algorithm-steps {{
        margin: 20px 0;
        padding: 20px;
        background: {MATERIAL_COLORS['surface_bright']};
        border-radius: 12px;
        border: 1px solid {MATERIAL_COLORS['outline']};
    }}

    /* Issue Sections */
    QLabel .issue-section {{
        margin: 15px 0;
        padding: 20px;
        border-radius: 10px;
    }}

    QLabel .issue-section.critical {{
        background: linear-gradient(90deg, 
            rgba(255, 70, 70, 0.1) 0%,
            rgba(255, 70, 70, 0.05) 100%);
        border-left: 4px solid #ff4646;
    }}

    QLabel .issue-section.warning {{
        background: linear-gradient(90deg, 
            rgba(255, 184, 0, 0.1) 0%,
            rgba(255, 184, 0, 0.05) 100%);
        border-left: 4px solid #ffb800;
    }}

    QLabel .issue-section.info {{
        background: linear-gradient(90deg, 
            rgba(0, 150, 199, 0.1) 0%,
            rgba(0, 150, 199, 0.05) 100%);
        border-left: 4px solid #0096c7;
    }}

    QLabel .issue-summary {{
        margin: 20px 0;
        padding: 15px 20px;
        background: {MATERIAL_COLORS['surface_variant']};
        border-radius: 8px;
        font-size: 13px;
    }}

    /* Dialog Buttons */
    QWidget#button_container {{
        background: {MATERIAL_COLORS['surface']};
        border-top: 1px solid {MATERIAL_COLORS['outline_variant']};
        padding: 15px 25px;
    }}

    QPushButton {{
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        min-width: 120px;
        font-size: 14px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }}

    QPushButton:pressed {{
        padding: 13px 23px 11px 25px;
    }}

    /* Close Button - Dark Red */
    QPushButton#cancel_button {{
        background-color: #2B1919;
        color: #FF6B6B;
        border: 1px solid #4D2C2C;
    }}

    QPushButton#cancel_button:hover {{
        background-color: #3A2222;
        border-color: #FF6B6B;
    }}

    QPushButton#cancel_button:pressed {{
        background-color: #241515;
    }}

    /* Apply Button - Deep Dark Primary */
    QPushButton#apply_button {{
        background-color: #012E52;
        color: {MATERIAL_COLORS['on_primary']};
        margin-left: 15px;
    }}

    QPushButton#apply_button:hover {{
        background-color: #023E8A;
    }}

    QPushButton#apply_button:pressed {{
        background-color: #011E36;
    }}
"""

EDITOR_WIDGET_STYLE = f"""
QWidget#editor_widget {{
    background-color: {MATERIAL_COLORS['surface']};
    border: none;
}}
"""


def get_editor_style():
    return f"""
    QPlainTextEdit {{
        background-color: {EDITOR_COLORS['background']};
        color: {EDITOR_COLORS['text']};
        border: none;
        selection-background-color: {EDITOR_COLORS['selection']};
        selection-color: {EDITOR_COLORS['text']};
    }}
    """


def get_tab_style():
    return f"""
    QTabWidget {{
        background-color: {MATERIAL_COLORS['surface']};
    }}
    QTabWidget::pane {{
        border: none;
    }}
    QTabBar::tab {{
        background: {MATERIAL_COLORS['surface_variant']};
        color: {MATERIAL_COLORS['text_secondary']};
        padding: 8px 16px;
        border: none;
        min-width: 100px;
        max-width: 200px;
    }}
    QTabBar::tab:selected {{
        background: {MATERIAL_COLORS['primary_container']};
        color: {MATERIAL_COLORS['on_primary_container']};
    }}
    QTabBar::tab:hover:!selected {{
        background: {MATERIAL_COLORS['surface_bright']};
    }}
    QPushButton#new_tab_button {{
        background: transparent;
        color: {MATERIAL_COLORS['text_secondary']};
        border: none;
        padding: 4px 8px;
        font-size: 20px;
    }}
    QPushButton#new_tab_button:hover {{
        color: {MATERIAL_COLORS['text_primary']};
    }}
    """


# Export all styles
__all__ = [
    "EDITOR_WIDGET_STYLE",
    "get_editor_style",
    "get_tab_style",
    "AI_DIALOG_STYLE",
]
