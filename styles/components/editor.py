from ..constants.colors import MATERIAL_COLORS

EDITOR_WIDGET_STYLE = f"""
QWidget#editor_widget {{
    background: {MATERIAL_COLORS['surface_dim']};
    border: none;
}}

QPlainTextEdit#code_editor {{
    background: {MATERIAL_COLORS['surface']};
    color: {MATERIAL_COLORS['text_primary']};
    border: none;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 14px;
    selection-background-color: {MATERIAL_COLORS['primary']}44;
}}

QLineNumber {{
    background: {MATERIAL_COLORS['surface_dim']};
    color: {MATERIAL_COLORS['text_secondary']};
    border: none;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 14px;
    padding: 0 8px;
}}
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