"""
Status View Container Styles.

Container styling for the unified status view widget.
Uses Material Design principles for consistency with the app's overall design.
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

__all__ = [
    "STATUS_VIEW_CONTAINER_STYLE",
]
