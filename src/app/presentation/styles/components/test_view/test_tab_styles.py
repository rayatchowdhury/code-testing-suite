# -*- coding: utf-8 -*-
"""
Test Tab Widget Styles.

Comprehensive styling for TestTabWidget component including tab containers,
file buttons, language selectors, and context menus.
"""

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS


# ============================================================================
# TAB CONTAINER STYLES
# ============================================================================

TAB_CONTAINER_STYLE = f"""
QWidget {{
    border: 1px solid {MATERIAL_COLORS['outline_variant']};
    border-radius: 8px;
    background: {MATERIAL_COLORS['surface_variant']};
    margin: 1px 0 1px 1px;
}}
QWidget:hover {{
    border-color: {MATERIAL_COLORS['outline']};
    background: {MATERIAL_COLORS['surface_bright']};
}}
QWidget[hasUnsavedChanges="true"] {{
    border: 2px solid {MATERIAL_COLORS['error']} !important;
    margin: 0px 0 0px 0px;
}}
"""


# ============================================================================
# FILE TAB BUTTON STYLES (Multi-language mode)
# ============================================================================

TAB_FILE_BUTTON_STYLE = f"""
QPushButton {{
    border: none;
    border-radius: 6px;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
    background: transparent;
    color: {MATERIAL_COLORS['on_surface']};
    font-size: 13px;
    font-weight: 500;
    text-align: center;
}}
QPushButton:hover {{
    background: rgba(255, 255, 255, 0.08);
}}
QPushButton:pressed {{
    background: rgba(255, 255, 255, 0.12);
}}
QPushButton[isActive="true"] {{
    background: {MATERIAL_COLORS['primary_container']};
    color: {MATERIAL_COLORS['on_primary_container']};
    font-weight: 600;
}}
QPushButton[isActive="true"]:hover {{
    background: {MATERIAL_COLORS['primary']};
    color: {MATERIAL_COLORS['on_primary']};
}}
QPushButton[hasUnsavedChanges="true"] {{
    border: 2px solid {MATERIAL_COLORS['error']} !important;
    border-radius: 6px;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
    padding: 6px 6px;
    padding-right: 0px;
}}
"""


# ============================================================================
# FILE TAB BUTTON STYLES (Single-language mode)
# ============================================================================

TAB_FILE_BUTTON_SINGLE_STYLE = f"""
QPushButton {{
    background-color: {MATERIAL_COLORS['surface_variant']};
    border: 1px solid {MATERIAL_COLORS['outline_variant']};
    border-radius: 8px;
    color: {MATERIAL_COLORS['on_surface']};
    padding: 8px 12px;
    font-weight: 500;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: {MATERIAL_COLORS['surface_bright']};
    border-color: {MATERIAL_COLORS['outline']};
}}
QPushButton[isActive="true"] {{
    background-color: {MATERIAL_COLORS['primary_container']};
    border: 2px solid {MATERIAL_COLORS['primary']};
    color: {MATERIAL_COLORS['on_primary_container']};
    font-weight: 600;
    padding: 7px 11px;
}}
QPushButton[isActive="true"]:hover {{
    background-color: {MATERIAL_COLORS['primary']};
    color: {MATERIAL_COLORS['on_primary']};
}}
QPushButton[hasUnsavedChanges="true"] {{
    border: 2px solid {MATERIAL_COLORS['error']} !important;
    padding: 7px 11px;
}}
"""


# ============================================================================
# LANGUAGE SELECTOR STYLES
# ============================================================================

LANGUAGE_CONTAINER_STYLE = f"""
QWidget {{
    border: none;
    border-left: 1px solid {MATERIAL_COLORS['outline_variant']};
    border-radius: 0;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
    background: {MATERIAL_COLORS['surface_dim']};
    min-width: 45px;
    max-width: 45px;
}}
QWidget:hover {{
    background: {MATERIAL_COLORS['surface_bright']};
    border-left-color: {MATERIAL_COLORS['outline']};
}}
"""


LANGUAGE_LABEL_STYLE = f"""
QLabel {{
    color: {MATERIAL_COLORS['text_secondary']};
    font-size: 9px;
    font-weight: 600;
    padding: 4px 1px;
    background: transparent;
    border: none;
    border-radius: 3px;
}}
QLabel:hover {{
    color: {MATERIAL_COLORS['primary']};
    background: rgba(0, 150, 199, 0.1);
}}
"""


# ============================================================================
# CONTEXT MENU STYLES
# ============================================================================

LANGUAGE_CONTEXT_MENU_STYLE = f"""
QMenu {{
    background-color: {MATERIAL_COLORS['surface']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 8px;
    padding: 8px 0px;
    min-width: 100px;
}}
QMenu::item {{
    background-color: transparent;
    padding: 10px 16px;
    margin: 2px 6px;
    border-radius: 6px;
    color: {MATERIAL_COLORS['on_surface']};
    font-size: 12px;
    font-weight: 500;
    min-height: 20px;
}}
QMenu::item:selected {{
    background-color: {MATERIAL_COLORS['primary_container']};
    color: {MATERIAL_COLORS['on_primary_container']};
}}
QMenu::item:checked {{
    background-color: {MATERIAL_COLORS['primary']};
    color: {MATERIAL_COLORS['on_primary']};
    font-weight: 600;
}}
QMenu::separator {{
    height: 1px;
    background-color: {MATERIAL_COLORS['outline_variant']};
    margin: 6px 12px;
}}
"""


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Container styles
    'TAB_CONTAINER_STYLE',
    
    # Button styles
    'TAB_FILE_BUTTON_STYLE',
    'TAB_FILE_BUTTON_SINGLE_STYLE',
    
    # Language selector styles
    'LANGUAGE_CONTAINER_STYLE',
    'LANGUAGE_LABEL_STYLE',
    
    # Menu styles
    'LANGUAGE_CONTEXT_MENU_STYLE',
]
