"""
Common reusable style helpers.

These functions provide simple, reusable style snippets that can be composed
together to build consistent styling across the application.
"""

from src.app.presentation.shared.design_system.tokens.colors import MATERIAL_COLORS


def bold_label(font_size: int = 14, color: str = None) -> str:
    """
    Create a bold label style.
    
    Args:
        font_size: Font size in pixels (default: 14)
        color: Text color (default: on_surface)
    
    Returns:
        CSS style string for bold text
    
    Example:
        >>> label.setStyleSheet(bold_label(16, MATERIAL_COLORS['primary']))
    """
    text_color = color if color else MATERIAL_COLORS['on_surface']
    return f"font-weight: bold; font-size: {font_size}px; color: {text_color};"


def error_text(font_size: int = 14, bold: bool = False) -> str:
    """
    Create error text style.
    
    Args:
        font_size: Font size in pixels (default: 14)
        bold: Whether to make text bold (default: False)
    
    Returns:
        CSS style string for error text
    """
    weight = "bold" if bold else "normal"
    return f"color: {MATERIAL_COLORS['error']}; font-size: {font_size}px; font-weight: {weight};"


__all__ = [
    'bold_label',
    'error_text',
]

