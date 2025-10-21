"""
Input Widget Styles

Centralized styles for input widgets including QLineEdit, QSpinBox, QDoubleSpinBox,
and QComboBox. Used across sidebar widgets and configuration dialogs.
"""

from src.app.presentation.design_system.tokens.colors import MATERIAL_COLORS


# QGroupBox style for titled input sections (Time/Memory limits)
INPUT_GROUP_STYLE = f"""
QGroupBox {{
    font-size: 11px;
    font-weight: 600;
    color: {MATERIAL_COLORS['primary']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 8px;
    margin: 4px 0px;
    padding-top: 6px;
    background: transparent;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 8px;
    padding: 0px 6px 0px 6px;
    color: {MATERIAL_COLORS['primary']};
    font-weight: 600;
}}
"""


# Standard QLineEdit style with gradient background (used in limits widget)
INPUT_LINEEDIT_STYLE = f"""
QLineEdit {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(20, 24, 28, 0.8),
               stop:1 rgba(14, 17, 20, 0.8));
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 12px;
    color: {MATERIAL_COLORS['text_primary']};
    padding: 8px 12px;
    font-size: 13px;
    font-weight: 500;
    selection-background-color: {MATERIAL_COLORS['primary']}40;
    selection-color: {MATERIAL_COLORS['on_primary']};
}}

QLineEdit:hover {{
    border: 1px solid {MATERIAL_COLORS['primary']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 {MATERIAL_COLORS['primary']}10,
               stop:1 rgba(255, 255, 255, 0.08));
}}

QLineEdit:focus {{
    border: 2px solid {MATERIAL_COLORS['primary']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 {MATERIAL_COLORS['primary']}15,
               stop:1 rgba(255, 255, 255, 0.08));
    outline: none;
}}
"""


# Compact QLineEdit style (used in slider value input)
INPUT_LINEEDIT_COMPACT_STYLE = f"""
QLineEdit {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(20, 24, 28, 0.8),
               stop:1 rgba(14, 17, 20, 0.8));
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 8px;
    color: {MATERIAL_COLORS['text_primary']};
    padding: 6px 8px;
    font-size: 12px;
    font-weight: 500;
    selection-background-color: {MATERIAL_COLORS['primary']}40;
    selection-color: {MATERIAL_COLORS['on_primary']};
}}

QLineEdit:hover {{
    border: 1px solid {MATERIAL_COLORS['primary']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 {MATERIAL_COLORS['primary']}10,
               stop:1 rgba(255, 255, 255, 0.08));
}}

QLineEdit:focus {{
    border: 2px solid {MATERIAL_COLORS['primary']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 {MATERIAL_COLORS['primary']}15,
               stop:1 rgba(255, 255, 255, 0.08));
    outline: none;
}}
"""


# QSpinBox style (integer input with up/down buttons)
INPUT_SPINBOX_STYLE = f"""
QSpinBox {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(20, 24, 28, 0.8),
               stop:1 rgba(14, 17, 20, 0.8));
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 8px;
    color: {MATERIAL_COLORS['text_primary']};
    padding: 6px 8px;
    font-size: 12px;
    font-weight: 500;
    selection-background-color: {MATERIAL_COLORS['primary']}40;
}}

QSpinBox:hover {{
    border: 1px solid {MATERIAL_COLORS['primary']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 {MATERIAL_COLORS['primary']}10,
               stop:1 rgba(255, 255, 255, 0.08));
}}

QSpinBox:focus {{
    border: 2px solid {MATERIAL_COLORS['primary']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 {MATERIAL_COLORS['primary']}15,
               stop:1 rgba(255, 255, 255, 0.08));
}}

QSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid {MATERIAL_COLORS['outline']};
    background: transparent;
    border-top-right-radius: 8px;
}}

QSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 20px;
    border-left: 1px solid {MATERIAL_COLORS['outline']};
    background: transparent;
    border-bottom-right-radius: 8px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background: {MATERIAL_COLORS['primary']}20;
}}

QSpinBox::up-arrow {{
    image: none;
    width: 0px;
    height: 0px;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 6px solid {MATERIAL_COLORS['text_primary']};
}}

QSpinBox::down-arrow {{
    image: none;
    width: 0px;
    height: 0px;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid {MATERIAL_COLORS['text_primary']};
}}
"""


# QDoubleSpinBox style (decimal input with up/down buttons)
INPUT_DOUBLE_SPINBOX_STYLE = f"""
QDoubleSpinBox {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(20, 24, 28, 0.8),
               stop:1 rgba(14, 17, 20, 0.8));
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 8px;
    color: {MATERIAL_COLORS['text_primary']};
    padding: 6px 8px;
    font-size: 12px;
    font-weight: 500;
    selection-background-color: {MATERIAL_COLORS['primary']}40;
}}

QDoubleSpinBox:hover {{
    border: 1px solid {MATERIAL_COLORS['primary']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 {MATERIAL_COLORS['primary']}10,
               stop:1 rgba(255, 255, 255, 0.08));
}}

QDoubleSpinBox:focus {{
    border: 2px solid {MATERIAL_COLORS['primary']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 {MATERIAL_COLORS['primary']}15,
               stop:1 rgba(255, 255, 255, 0.08));
}}

QDoubleSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid {MATERIAL_COLORS['outline']};
    background: transparent;
    border-top-right-radius: 8px;
}}

QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 20px;
    border-left: 1px solid {MATERIAL_COLORS['outline']};
    background: transparent;
    border-bottom-right-radius: 8px;
}}

QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
    background: {MATERIAL_COLORS['primary']}20;
}}

QDoubleSpinBox::up-arrow {{
    image: none;
    width: 0px;
    height: 0px;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 6px solid {MATERIAL_COLORS['text_primary']};
}}

QDoubleSpinBox::down-arrow {{
    image: none;
    width: 0px;
    height: 0px;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid {MATERIAL_COLORS['text_primary']};
}}
"""


# QComboBox style (dropdown selector)
INPUT_COMBOBOX_STYLE = f"""
QComboBox {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 rgba(20, 24, 28, 0.8),
               stop:1 rgba(14, 17, 20, 0.8));
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 8px;
    color: {MATERIAL_COLORS['text_primary']};
    padding: 6px 8px;
    font-size: 12px;
    font-weight: 500;
    selection-background-color: {MATERIAL_COLORS['primary']};
}}

QComboBox:hover {{
    border: 1px solid {MATERIAL_COLORS['primary']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
               stop:0 {MATERIAL_COLORS['primary']}10,
               stop:1 rgba(255, 255, 255, 0.08));
}}

QComboBox:focus {{
    border: 2px solid {MATERIAL_COLORS['primary']};
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid {MATERIAL_COLORS['outline']};
    background: transparent;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
}}

QComboBox::down-arrow {{
    image: none;
    width: 0px;
    height: 0px;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid {MATERIAL_COLORS['text_primary']};
}}

QComboBox QAbstractItemView {{
    background: {MATERIAL_COLORS['surface']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 8px;
    color: {MATERIAL_COLORS['text_primary']};
    selection-background-color: {MATERIAL_COLORS['primary']};
    selection-color: {MATERIAL_COLORS['on_primary']};
    padding: 4px;
}}

QComboBox QAbstractItemView::item {{
    padding: 6px 8px;
    border-radius: 4px;
}}

QComboBox QAbstractItemView::item:hover {{
    background: {MATERIAL_COLORS['primary']}20;
}}
"""


# Divider style (used between input sections)
INPUT_DIVIDER_STYLE = f"""
QWidget {{
    background-color: {MATERIAL_COLORS['outline_variant']};
}}
"""
