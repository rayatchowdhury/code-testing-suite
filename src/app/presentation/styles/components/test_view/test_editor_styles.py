# -*- coding: utf-8 -*-
"""
Test View Editor and UI Component Styles.

Includes styling for file buttons, content panels, and editor controls.
"""

from src.app.presentation.styles.style import MATERIAL_COLORS

TEST_VIEW_BUTTON_PANEL_STYLE = f"""
QWidget {{
    background-color: {MATERIAL_COLORS['surface_dim']};
    border-bottom: 1px solid {MATERIAL_COLORS['outline']};
}}
"""

TEST_VIEW_FILE_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {MATERIAL_COLORS['surface_variant']};
    border: 1px solid {MATERIAL_COLORS['outline_variant']};
    border-radius: 8px;
    color: {MATERIAL_COLORS['on_surface']};
    padding: 8px 16px;
    font-weight: 500;
    font-size: 13px;
}}

QPushButton:hover {{
    background-color: {MATERIAL_COLORS['surface_bright']};
    border-color: {MATERIAL_COLORS['outline']};
}}

QPushButton[isActive="true"] {{
    background-color: {MATERIAL_COLORS['primary_container']};
    border: 1px solid {MATERIAL_COLORS['primary']};
    color: {MATERIAL_COLORS['on_primary_container']};
    font-weight: 600;
}}

QPushButton[isActive="true"]:hover {{
    background-color: {MATERIAL_COLORS['primary']};
    color: {MATERIAL_COLORS['on_primary']};
}}

QPushButton[isActive="true"][hasUnsavedChanges="true"] {{
    background-color: {MATERIAL_COLORS['primary_container']};
    border: 2px solid {MATERIAL_COLORS['error']};
    border-radius: 8px;
    color: {MATERIAL_COLORS['on_primary']};
    font-weight: 600;
    padding: 7px 15px;  /* Adjust padding to account for thicker border */
}}

QPushButton[isActive="true"][hasUnsavedChanges="true"]:hover {{
    background-color: {MATERIAL_COLORS['primary']};
    border-color: {MATERIAL_COLORS['error']};
    color: {MATERIAL_COLORS['on_primary']};
}}
"""

TEST_VIEW_CONTENT_PANEL_STYLE = f"""
QWidget {{
    background-color: {MATERIAL_COLORS['surface']};
}}
"""

TEST_VIEW_SLIDER_STYLE = f"""
QSlider::groove:horizontal {{
    border: none;
    height: 4px;
    background: {MATERIAL_COLORS['surface_variant']};
    margin: 0px;
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {MATERIAL_COLORS['primary']};
    border: none;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}
QSlider::handle:horizontal:hover {{
    background: {MATERIAL_COLORS['primary_container']};
}}
QSlider::sub-page:horizontal {{
    background: {MATERIAL_COLORS['primary']};
    border-radius: 2px;
}}
"""

TEST_VIEW_SLIDER_VALUE_LABEL_STYLE = f"""
color: {MATERIAL_COLORS['on_surface']};
font-size: 13px;
padding: 0 8px;
min-width: 28px;
"""

__all__ = [
    "TEST_VIEW_BUTTON_PANEL_STYLE",
    "TEST_VIEW_FILE_BUTTON_STYLE",
    "TEST_VIEW_CONTENT_PANEL_STYLE",
    "TEST_VIEW_SLIDER_STYLE",
    "TEST_VIEW_SLIDER_VALUE_LABEL_STYLE",
]
