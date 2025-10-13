"""Configuration views and dialogs.

This module contains UI components for configuration management:
- Configuration dialog with all settings sections
- UI event handlers and validation
- Error dialogs and user feedback
"""

from src.app.core.config.views.config_dialog import ConfigView, ErrorDialog

__all__ = ["ConfigView", "ErrorDialog"]
