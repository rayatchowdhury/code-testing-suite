"""
Gradient Helper Functions for Qt Style Sheets

This module provides reusable gradient functions to eliminate duplicate
gradient patterns across the application. All gradients use Material Design
colors from the centralized MATERIAL_COLORS dictionary.

Usage:
    from src.app.presentation.styles.helpers.gradients import surface_gradient
    
    widget.setStyleSheet(f"background: {surface_gradient()};")
"""

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS


def surface_gradient(opacity: float = 0.03) -> str:
    """
    Creates a subtle glass-like surface gradient.
    
    Used for: Cards, panels, dialog backgrounds
    
    Args:
        opacity: Background opacity (default 0.03)
    
    Returns:
        QSS gradient string
    """
    return f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, {opacity}), stop:1 rgba(255, 255, 255, {opacity * 0.5}))"


def input_gradient() -> str:
    """
    Creates a dark gradient for input fields.
    
    Used for: Text inputs, spinboxes, comboboxes
    
    Returns:
        QSS gradient string
    """
    return "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 0, 0, 0.2), stop:1 rgba(0, 0, 0, 0.3))"


def button_gradient() -> str:
    """
    Creates a subtle gradient for standard buttons.
    
    Used for: Secondary buttons, cancel buttons
    
    Returns:
        QSS gradient string
    """
    return "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 0.05), stop:1 rgba(255, 255, 255, 0.02))"


def primary_button_gradient() -> str:
    """
    Creates a vibrant gradient for primary action buttons.
    
    Uses the primary cyan color (#0096C7).
    
    Returns:
        QSS gradient string
    """
    primary = MATERIAL_COLORS['primary']  # #0096C7
    return f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {primary}, stop:1 rgba(0, 123, 163, 1))"


def hover_gradient() -> str:
    """
    Creates a bright gradient for hover states.
    
    Used for: Button hover effects, card hover states
    
    Returns:
        QSS gradient string
    """
    return "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 0.1), stop:1 rgba(255, 255, 255, 0.05))"


def pressed_gradient() -> str:
    """
    Creates a darker gradient for pressed/active states.
    
    Used for: Button pressed effects
    
    Returns:
        QSS gradient string
    """
    return "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 0, 0, 0.1), stop:1 rgba(0, 0, 0, 0.2))"


def progress_gradient() -> str:
    """
    Creates a gradient for progress bars.
    
    Uses primary cyan color with subtle variation.
    
    Returns:
        QSS gradient string
    """
    primary = MATERIAL_COLORS['primary']  # #0096C7
    return f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {primary}, stop:1 rgba(0, 180, 216, 1))"


def success_gradient() -> str:
    """
    Creates a green gradient for success states.
    
    Returns:
        QSS gradient string
    """
    success = MATERIAL_COLORS['success']  # #2ECC71
    return f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {success}, stop:1 rgba(39, 174, 96, 1))"


def error_gradient() -> str:
    """
    Creates a red gradient for error states.
    
    Returns:
        QSS gradient string
    """
    error = MATERIAL_COLORS['error']  # #E74C3C
    return f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {error}, stop:1 rgba(192, 57, 43, 1))"


def warning_gradient() -> str:
    """
    Creates an orange gradient for warning states.
    
    Returns:
        QSS gradient string
    """
    warning = MATERIAL_COLORS['warning']  # #F39C12
    return f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {warning}, stop:1 rgba(211, 84, 0, 1))"


def header_gradient() -> str:
    """
    Creates a gradient for header sections.
    
    Uses primary color with transparency.
    
    Returns:
        QSS gradient string
    """
    primary = MATERIAL_COLORS['primary']  # #0096C7
    return f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 150, 199, 0.1), stop:1 rgba(0, 150, 199, 0.05))"


def dialog_gradient() -> str:
    """
    Creates a gradient for dialog backgrounds.
    
    Darker than surface_gradient for better contrast.
    
    Returns:
        QSS gradient string
    """
    return "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(30, 30, 30, 0.95), stop:1 rgba(20, 20, 20, 0.98))"
