"""
Config Dialog Button Styles.

Includes all button variants: primary, secondary, save, cancel, reset, danger.
"""

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS

CONFIG_BUTTON_STYLES = f"""
QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(255, 255, 255, 0.06),
               stop:1 rgba(255, 255, 255, 0.03));
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    color: {MATERIAL_COLORS['on_surface']};
    padding: 8px 16px;
    min-height: 18px;
    font-weight: 500;
    font-size: 14px;
    font-family: 'Segoe UI', system-ui;
}}

QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(100, 181, 246, 0.25),
               stop:1 rgba(255, 255, 255, 0.08));
    border: 1px solid rgba(100, 181, 246, 0.60);
    color: {MATERIAL_COLORS['on_surface']};
}}

QPushButton:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(100, 181, 246, 0.20),
               stop:1 rgba(255, 255, 255, 0.05));
    border: 1px solid rgba(100, 181, 246, 0.80);
}}

QPushButton#small_button {{
    padding: 4px;
    border-radius: 6px;
    font-size: 14px;
    min-width: 28px;
    min-height: 28px;
}}

QPushButton#small_button:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(100, 181, 246, 0.2),
               stop:1 rgba(255, 255, 255, 0.1));
    border: 1px solid rgba(100, 181, 246, 0.4);
}}

QPushButton#save_button {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
               stop:0 {MATERIAL_COLORS['primary']},
               stop:1 {MATERIAL_COLORS['primary_dark']});
    border: 1px solid {MATERIAL_COLORS['primary']};
    color: {MATERIAL_COLORS['on_primary']};
    font-weight: 600;
}}

QPushButton#save_button:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
               stop:0 {MATERIAL_COLORS['primary']}E6,
               stop:1 {MATERIAL_COLORS['primary_dark']}E6);
    border: 1px solid {MATERIAL_COLORS['primary']}E6;
}}

QPushButton#save_button:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
               stop:0 {MATERIAL_COLORS['primary']}CC,
               stop:1 {MATERIAL_COLORS['primary_dark']}CC);
}}

QPushButton#cancel_button {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(220, 38, 38, 0.15),
               stop:1 rgba(185, 28, 28, 0.15));
    border: 1px solid rgba(220, 38, 38, 0.3);
    color: #FECACA;
}}

QPushButton#cancel_button:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(220, 38, 38, 0.25),
               stop:1 rgba(185, 28, 28, 0.25));
    border: 1px solid rgba(220, 38, 38, 0.5);
    color: #FEF2F2;
}}

QPushButton#reset_button {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(251, 146, 60, 0.15),
               stop:1 rgba(245, 101, 101, 0.15));
    border: 1px solid rgba(251, 146, 60, 0.3);
    color: #FED7AA;
}}

QPushButton#reset_button:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(251, 146, 60, 0.25),
               stop:1 rgba(245, 101, 101, 0.25));
    border: 1px solid rgba(251, 146, 60, 0.5);
    color: #FFF7ED;
}}

QPushButton#secondary_button {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(255, 255, 255, 0.08),
               stop:1 rgba(255, 255, 255, 0.04));
    color: {MATERIAL_COLORS['on_surface']};
    border: 1px solid rgba(255, 255, 255, 0.12);
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: 500;
    font-size: 13px;
}}

QPushButton#secondary_button:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 {MATERIAL_COLORS['primary']}40,
               stop:1 {MATERIAL_COLORS['primary']}20);
    border: 1px solid {MATERIAL_COLORS['primary']};
}}

QPushButton#danger_button {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 {MATERIAL_COLORS['error']}80,
               stop:1 {MATERIAL_COLORS['error']}60);
    color: white;
    border: 1px solid {MATERIAL_COLORS['error']};
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 13px;
}}

QPushButton#danger_button:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 {MATERIAL_COLORS['error']},
               stop:1 {MATERIAL_COLORS['error']}90);
    border: 1px solid {MATERIAL_COLORS['error']};
}}
"""

__all__ = [
    "CONFIG_BUTTON_STYLES",
]
