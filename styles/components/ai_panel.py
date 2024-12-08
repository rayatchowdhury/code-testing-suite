from ..constants.colors import MATERIAL_COLORS

AI_PANEL_STYLE = f"""
QWidget#ai_panel_container {{
    background-color: {MATERIAL_COLORS['surface_dim']} !important;
    border-top: 1px solid {MATERIAL_COLORS['outline_variant']};
}}

QPushButton#ai_button {{
    background-color: rgba(20, 20, 22, 0.8);
    color: {MATERIAL_COLORS['text_secondary']};
    border: 1px solid {MATERIAL_COLORS['outline_variant']};
    border-radius: 4px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 500;
}}

QPushButton#ai_button:hover {{
    background: {MATERIAL_COLORS['primary']};
    color: {MATERIAL_COLORS['on_primary']};
    border-color: {MATERIAL_COLORS['primary']};
}}

QPushButton#ai_button:pressed {{
    background: {MATERIAL_COLORS['primary_dark']};
    color: {MATERIAL_COLORS['on_primary']};
    border-color: {MATERIAL_COLORS['primary_dark']};
}}"""