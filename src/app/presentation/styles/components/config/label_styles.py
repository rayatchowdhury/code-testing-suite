"""
Config Dialog Label Styles.

Includes standard labels, info labels, and warning labels.
"""

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS

CONFIG_LABEL_STYLES = f"""
QLabel {{
    color: {MATERIAL_COLORS['on_surface']};
    font-size: 14px;
    font-family: 'Segoe UI', system-ui;
    font-weight: 500;
}}

QLabel#info_label {{
    color: {MATERIAL_COLORS['on_surface_variant']};
    font-size: 13px;
    font-style: italic;
    padding: 8px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 6px;
}}

QLabel#warning_label {{
    color: {MATERIAL_COLORS['error']};
    font-size: 12px;
    font-weight: 500;
    padding: 6px;
    background: rgba(244, 67, 54, 0.1);
    border: 1px solid rgba(244, 67, 54, 0.3);
    border-radius: 6px;
}}
"""

__all__ = [
    "CONFIG_LABEL_STYLES",
]
