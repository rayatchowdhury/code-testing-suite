from ..constants.colors import MATERIAL_COLORS
from ..constants.editor_colors import EDITOR_COLORS

# Add a new style constant for AI response dialog
AI_DIALOG_STYLE = f"""
    QDialog {{
        background-color: {MATERIAL_COLORS['surface']};
        min-width: 600px;
        min-height: 400px;
    }}
    QScrollArea {{
        border: none;
        background-color: {MATERIAL_COLORS['surface']};
    }}
    QLabel {{
        color: {MATERIAL_COLORS['on_surface']};
        background-color: {MATERIAL_COLORS['surface']};
        padding: 15px;
        selection-background-color: {MATERIAL_COLORS['primary_container']};
        selection-color: {MATERIAL_COLORS['on_primary_container']};
    }}
    QPushButton {{
        background-color: {MATERIAL_COLORS['primary']};
        color: {MATERIAL_COLORS['on_primary']};
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        min-width: 80px;
        font-size: 12px;
    }}
    QPushButton:hover {{
        background-color: {MATERIAL_COLORS['primary_dark']};
    }}
    QPushButton:pressed {{
        background-color: {MATERIAL_COLORS['primary_darker']};
    }}
"""

def get_editor_style():
    return f"""
        QPlainTextEdit {{
            background-color: {EDITOR_COLORS['background']};
            color: {EDITOR_COLORS['text']};
            selection-background-color: {EDITOR_COLORS['selection']};
            border: none;
            font-family: 'Cascadia Code', 'Consolas', monospace;
            font-size: 14px;
        }}
    """

EDITOR_WIDGET_STYLE = f"""
QWidget#editor_widget {{
    background: {EDITOR_COLORS['background_darker']};
    border: none;
}}

{get_editor_style()}

QLineNumber {{
    background: {EDITOR_COLORS['background_darker']};
    color: {EDITOR_COLORS['line_number']};
    border: none;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 14px;
    padding: 0 8px;
}}
"""

AI_PANEL_STYLE = """
    QWidget#ai_panel_container {
        background-color: #1E1E1E;
        border-bottom: 1px solid #333333;
    }
    
    QPushButton#ai_button {
        background-color: #2D2D2D;
        color: #CCCCCC;
        border: 1px solid #404040;
        border-radius: 3px;
        padding: 5px 10px;
        min-width: 80px;
    }
    
    QPushButton#ai_button:hover {
        background-color: #3D3D3D;
        border-color: #505050;
    }
    
    QPushButton#ai_button:pressed {
        background-color: #505050;
    }
    
    QLineEdit#ai_command_input {
        background-color: #1A1A1A;
        color: #CCCCCC;
        border: 1px solid #404040;
        border-radius: 10px;
        padding: 5px 15px;
        font-family: 'Segoe UI';
        font-size: 12px;
    }
    
    QLineEdit#ai_command_input:focus {
        border-color: #505050;
        background-color: #252525;
    }
"""

def get_tab_style():
    return f"""
        QTabWidget::pane {{
            border: none;
            background: {MATERIAL_COLORS['surface']};
        }}
        QTabBar {{
            background: {MATERIAL_COLORS['surface_variant']};
        }}
        QTabBar::tab {{
            background: {MATERIAL_COLORS['surface']};
            color: {MATERIAL_COLORS['text_secondary']};
            padding: 8px 16px;
            border: none;
            border-right: 1px solid {MATERIAL_COLORS['outline_variant']};
            min-width: 100px;
            max-width: 200px;
            font-family: 'Segoe UI';
            font-size: 12px;
        }}
        QTabBar::tab:selected {{
            background: {MATERIAL_COLORS['surface_variant']};
            color: {MATERIAL_COLORS['text_primary']};
            border-bottom: 2px solid {MATERIAL_COLORS['primary']};
        }}
        QTabBar::tab:hover {{
            background: {MATERIAL_COLORS['surface_bright']};
            color: {MATERIAL_COLORS['text_primary']};
        }}
        QTabBar::close-button {{
            image: url(resources/icons/close.png);
            subcontrol-position: right;
        }}
        QTabBar::close-button:hover {{
            background: {MATERIAL_COLORS['error_container']};
            border-radius: 2px;
        }}
        QPushButton#new_tab_button {{
            background: {MATERIAL_COLORS['primary_container']};
            color: {MATERIAL_COLORS['on_primary_container']};
            border: none;
            padding: 8px;
            font-size: 20px;
            font-weight: bold;
            min-width: 36px;
            max-width: 36px;
        }}
        QPushButton#new_tab_button:hover {{
            background: {MATERIAL_COLORS['primary']};
            color: {MATERIAL_COLORS['on_primary']};
        }}
        QPushButton#new_tab_button:pressed {{
            background: {MATERIAL_COLORS['primary_dark']};
            color: {MATERIAL_COLORS['on_primary']};
        }}
    """