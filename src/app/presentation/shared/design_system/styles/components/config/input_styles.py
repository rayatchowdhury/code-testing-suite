"""
Config Dialog Input Field Styles.

Includes styling for QComboBox, QLineEdit, QSpinBox, and QCheckBox.
"""

from src.app.presentation.shared.design_system.tokens.colors import MATERIAL_COLORS

CONFIG_INPUT_STYLES = f"""
QComboBox, QLineEdit, QSpinBox {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(20, 24, 28, 0.8),
               stop:1 rgba(14, 17, 20, 0.8));
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 8px;
    color: {MATERIAL_COLORS['on_surface']};
    padding: 6px 12px;
    min-height: 20px;
    font-size: 14px;
    font-family: 'Segoe UI', system-ui;
    font-weight: 500;
    selection-background-color: {MATERIAL_COLORS['primary']}40;
    selection-color: {MATERIAL_COLORS['on_primary']};
}}

QComboBox:hover, QLineEdit:hover, QSpinBox:hover {{
    border: 1px solid {MATERIAL_COLORS['primary']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 {MATERIAL_COLORS['primary']}10,
               stop:1 rgba(255, 255, 255, 0.08));
}}

QComboBox:focus, QLineEdit:focus, QSpinBox:focus {{
    border: 2px solid {MATERIAL_COLORS['primary']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 {MATERIAL_COLORS['primary']}15,
               stop:1 rgba(255, 255, 255, 0.08));
    outline: none;
}}

QComboBox:disabled, QLineEdit:disabled, QSpinBox:disabled {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(20, 24, 28, 0.3),
               stop:1 rgba(14, 17, 20, 0.3));
    border: 1px solid rgba(255, 255, 255, 0.02);
    color: {MATERIAL_COLORS['on_surface_disabled']};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 16px;
    background: transparent;
    width: 20px;
}}

QComboBox::down-arrow {{
    image: url(resources/icons/dropdown.png);
    width: 12px;
    height: 12px;
}}

QComboBox QAbstractItemView {{
    background: {MATERIAL_COLORS['surface']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 8px;
    color: {MATERIAL_COLORS['on_surface']};
    selection-background-color: {MATERIAL_COLORS['primary']};
    selection-color: {MATERIAL_COLORS['on_primary']};
    outline: none;
}}

QSpinBox::up-button, QSpinBox::down-button {{
    border-radius: 4px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(255, 255, 255, 0.05),
               stop:1 rgba(255, 255, 255, 0.02));
    min-width: 20px;
    border: 1px solid {MATERIAL_COLORS['outline']};
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 {MATERIAL_COLORS['primary']}30,
               stop:1 rgba(255, 255, 255, 0.1));
    border: 1px solid {MATERIAL_COLORS['primary']};
}}

QCheckBox {{
    color: {MATERIAL_COLORS['on_surface']};
    spacing: 8px;
    min-height: 24px;
    font-size: 14px;
    font-family: 'Segoe UI', system-ui;
    font-weight: 500;
    padding: 2px;
}}

QCheckBox:disabled {{
    color: {MATERIAL_COLORS['on_surface_disabled']};
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid {MATERIAL_COLORS['outline']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(20, 24, 28, 0.8),
               stop:1 rgba(14, 17, 20, 0.8));
}}

QCheckBox::indicator:hover {{
    border: 1px solid {MATERIAL_COLORS['primary']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 {MATERIAL_COLORS['primary']}10,
               stop:1 rgba(255, 255, 255, 0.08));
}}

QCheckBox::indicator:checked {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
               stop:0 {MATERIAL_COLORS['primary']},
               stop:1 {MATERIAL_COLORS['primary_dark']});
    border: 1px solid {MATERIAL_COLORS['primary']};
    image: url(resources/icons/check.png);
}}

QCheckBox::indicator:checked:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
               stop:0 {MATERIAL_COLORS['primary']}E6,
               stop:1 {MATERIAL_COLORS['primary_dark']}E6);
}}

QCheckBox::indicator:disabled {{
    border: 1px solid rgba(255, 255, 255, 0.02);
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(20, 24, 28, 0.3),
               stop:1 rgba(14, 17, 20, 0.3));
}}
"""

__all__ = [
    "CONFIG_INPUT_STYLES",
]
