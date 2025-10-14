"""Config module for managing application configuration.

Structured configuration management with organized subdirectories (Phase 3).
"""

# Phase 3: Imports from organized subdirectories
from src.app.core.config.core import (
    ConfigError,
    ConfigFormatError,
    ConfigLoadError,
    ConfigManager,
    ConfigMissingError,
    ConfigPermissionError,
    ConfigPersistence,
    ConfigSaveError,
    ConfigValidationError,
)
from src.app.core.config.database import DatabaseOperations
from src.app.core.config.gemini import GeminiConfig, GeminiConfigUI
from src.app.core.config.views import ConfigView, ErrorDialog

__all__ = [
    # Core configuration management
    "ConfigManager",
    "ConfigPersistence",
    # Views and dialogs
    "ConfigView",
    "ErrorDialog",
    # Database operations
    "DatabaseOperations",
    # Gemini AI configuration
    "GeminiConfig",
    "GeminiConfigUI",
    # Exceptions
    "ConfigError",
    "ConfigPermissionError",
    "ConfigFormatError",
    "ConfigValidationError",
    "ConfigLoadError",
    "ConfigSaveError",
    "ConfigMissingError",
]
