"""
Common reusable style helpers.

These functions provide simple, reusable style snippets that can be composed
together to build consistent styling across the application.
"""

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS


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


def success_text(font_size: int = 14, bold: bool = False) -> str:
    """
    Create success text style.
    
    Args:
        font_size: Font size in pixels (default: 14)
        bold: Whether to make text bold (default: False)
    
    Returns:
        CSS style string for success text
    """
    weight = "bold" if bold else "normal"
    return f"color: {MATERIAL_COLORS['success']}; font-size: {font_size}px; font-weight: {weight};"


def warning_text(font_size: int = 14, bold: bool = False) -> str:
    """
    Create warning text style.
    
    Args:
        font_size: Font size in pixels (default: 14)
        bold: Whether to make text bold (default: False)
    
    Returns:
        CSS style string for warning text
    """
    weight = "bold" if bold else "normal"
    return f"color: {MATERIAL_COLORS['warning']}; font-size: {font_size}px; font-weight: {weight};"


def info_text(font_size: int = 14, bold: bool = False) -> str:
    """
    Create info text style.
    
    Args:
        font_size: Font size in pixels (default: 14)
        bold: Whether to make text bold (default: False)
    
    Returns:
        CSS style string for info text
    """
    weight = "bold" if bold else "normal"
    return f"color: {MATERIAL_COLORS['primary']}; font-size: {font_size}px; font-weight: {weight};"


def background_surface() -> str:
    """
    Standard surface background color.
    
    Returns:
        CSS background-color property
    """
    return f"background-color: {MATERIAL_COLORS['surface']};"


def background_variant() -> str:
    """
    Variant surface background color.
    
    Returns:
        CSS background-color property
    """
    return f"background-color: {MATERIAL_COLORS['surface_variant']};"


def border_standard(width: int = 1, radius: int = 4) -> str:
    """
    Standard border style.
    
    Args:
        width: Border width in pixels (default: 1)
        radius: Border radius in pixels (default: 4)
    
    Returns:
        CSS border properties
    """
    return f"border: {width}px solid {MATERIAL_COLORS['outline']}; border-radius: {radius}px;"


def border_primary(width: int = 1, radius: int = 4) -> str:
    """
    Primary colored border style.
    
    Args:
        width: Border width in pixels (default: 1)
        radius: Border radius in pixels (default: 4)
    
    Returns:
        CSS border properties
    """
    return f"border: {width}px solid {MATERIAL_COLORS['primary']}; border-radius: {radius}px;"


def border_error(width: int = 1, radius: int = 4) -> str:
    """
    Error colored border style.
    
    Args:
        width: Border width in pixels (default: 1)
        radius: Border radius in pixels (default: 4)
    
    Returns:
        CSS border properties
    """
    return f"border: {width}px solid {MATERIAL_COLORS['error']}; border-radius: {radius}px;"


def rounded_corners(radius: int = 4) -> str:
    """
    Rounded corner style.
    
    Args:
        radius: Border radius in pixels (default: 4)
    
    Returns:
        CSS border-radius property
    """
    return f"border-radius: {radius}px;"


def padding_standard(size: int = 8) -> str:
    """
    Standard padding.
    
    Args:
        size: Padding size in pixels (default: 8)
    
    Returns:
        CSS padding property
    """
    return f"padding: {size}px;"


def padding_custom(top: int, right: int, bottom: int, left: int) -> str:
    """
    Custom padding for each side.
    
    Args:
        top: Top padding in pixels
        right: Right padding in pixels
        bottom: Bottom padding in pixels
        left: Left padding in pixels
    
    Returns:
        CSS padding property
    """
    return f"padding: {top}px {right}px {bottom}px {left}px;"


def margin_standard(size: int = 8) -> str:
    """
    Standard margin.
    
    Args:
        size: Margin size in pixels (default: 8)
    
    Returns:
        CSS margin property
    """
    return f"margin: {size}px;"


def text_secondary() -> str:
    """
    Secondary text color style.
    
    Returns:
        CSS color property
    """
    return f"color: {MATERIAL_COLORS['text_secondary']};"


def text_disabled() -> str:
    """
    Disabled text color style.
    
    Returns:
        CSS color property
    """
    return f"color: {MATERIAL_COLORS['text_disabled']};"


def no_border() -> str:
    """
    Remove border styling.
    
    Returns:
        CSS border property
    """
    return "border: none;"


def transparent_background() -> str:
    """
    Transparent background.
    
    Returns:
        CSS background property
    """
    return "background: transparent;"


__all__ = [
    'bold_label',
    'error_text',
    'success_text',
    'warning_text',
    'info_text',
    'background_surface',
    'background_variant',
    'border_standard',
    'border_primary',
    'border_error',
    'rounded_corners',
    'padding_standard',
    'padding_custom',
    'margin_standard',
    'text_secondary',
    'text_disabled',
    'no_border',
    'transparent_background',
]
