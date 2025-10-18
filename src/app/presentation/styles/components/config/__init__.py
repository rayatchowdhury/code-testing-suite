"""
Config Dialog Styles - Modular organization.

This package contains all styling for the configuration dialog,
split into logical modules for better maintainability.
"""

from .dialog_styles import CONFIG_DIALOG_CONTAINER_STYLE
from .input_styles import CONFIG_INPUT_STYLES
from .button_styles import CONFIG_BUTTON_STYLES
from .label_styles import CONFIG_LABEL_STYLES

# Combine all styles into the single CONFIG_DIALOG_STYLE for backward compatibility
CONFIG_DIALOG_STYLE = (
    CONFIG_DIALOG_CONTAINER_STYLE +
    CONFIG_INPUT_STYLES +
    CONFIG_BUTTON_STYLES +
    CONFIG_LABEL_STYLES
)

__all__ = [
    "CONFIG_DIALOG_STYLE",
    "CONFIG_DIALOG_CONTAINER_STYLE",
    "CONFIG_INPUT_STYLES",
    "CONFIG_BUTTON_STYLES",
    "CONFIG_LABEL_STYLES",
]
