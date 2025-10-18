"""
Status View Container and Control Panel Styles.

Redesigned with Material Design principles:
- Proper Material surface colors for consistency with sidebar
- Elevation and shadows for depth
- Modern hover states and interactions
- Consistent with app's overall design language
"""

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS

# ============================================================================
# STATUS VIEW CONTAINER
# ============================================================================

STATUS_VIEW_CONTAINER_STYLE = f"""
QWidget {{
    background: {MATERIAL_COLORS['background']};
    border: none;
}}
"""

# ============================================================================
# CONTROLS PANEL (File buttons area at top)
# ============================================================================

CONTROLS_PANEL_STYLE = f"""
QWidget {{
    background: {MATERIAL_COLORS['surface']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 12px;
    padding: 16px;
}}
"""

FILE_BUTTON_STYLE = f"""
QPushButton {{
    color: {MATERIAL_COLORS['on_surface']};
    background: {MATERIAL_COLORS['surface_variant']};
    border: 1px solid {MATERIAL_COLORS['outline_variant']};
    text-align: center;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
    border-radius: 8px;
    margin: 0 4px;
    font-family: 'Segoe UI', system-ui;
    letter-spacing: 0.3px;
}}

QPushButton:hover {{
    background: {MATERIAL_COLORS['surface_bright']};
    border: 1px solid {MATERIAL_COLORS['primary']};
    color: {MATERIAL_COLORS['on_surface']};
}}

QPushButton:pressed {{
    background: {MATERIAL_COLORS['surface_dim']};
    border: 1px solid {MATERIAL_COLORS['primary']};
    padding: 11px 19px 9px 21px;
}}

QPushButton:disabled {{
    color: {MATERIAL_COLORS['on_surface_disabled']};
    background: {MATERIAL_COLORS['surface_dim']};
    border: 1px solid {MATERIAL_COLORS['outline_variant']};
}}
"""

# ============================================================================
# SECTION HEADERS
# ============================================================================

SECTION_HEADER_STYLE = f"""
QLabel {{
    color: {MATERIAL_COLORS['primary']};
    background: transparent;
    padding: 4px 8px;
    margin: 8px 0 4px 0;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-family: 'Segoe UI', system-ui;
}}
"""

__all__ = [
    "STATUS_VIEW_CONTAINER_STYLE",
    "CONTROLS_PANEL_STYLE",
    "FILE_BUTTON_STYLE",
    "SECTION_HEADER_STYLE",
]
