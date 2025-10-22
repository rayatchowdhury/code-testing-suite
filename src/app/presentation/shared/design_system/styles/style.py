"""
Central style module.

WARNING: This module should ONLY contain lightweight, frequently-used styles.
Do NOT import heavy component styles here - they should be imported directly
where needed.

For component-specific styles, import from:
  src.app.presentation.shared.design_system.styles.components.{component_name}
"""

from src.app.presentation.shared.design_system.tokens import COLORS

# Simplified DISPLAY_AREA_STYLE - only what's needed for DisplayArea
DISPLAY_AREA_STYLE = f"""
QWidget#display_area {{
    background-color: {COLORS['background']};
    border: none;
}}
"""

# Export only the lightweight styles that are used everywhere
__all__ = [
    "DISPLAY_AREA_STYLE",
    "COLORS",
]
