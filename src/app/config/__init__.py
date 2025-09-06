"""Config module for managing application configuration.

Structured configuration management with organized subdirectories (Phase 3).
"""

# Phase 3: Imports from organized subdirectories
from src.app.config.core import (
    ConfigManager, ConfigPersistence,
    ConfigError, ConfigPermissionError, ConfigFormatError,
    ConfigValidationError, ConfigLoadError, ConfigSaveError, ConfigMissingError
)
from src.app.config.views import ConfigView, ErrorDialog
from src.app.config.database import DatabaseOperations
from src.app.config.gemini import GeminiConfig, GeminiConfigUI, GeminiModelDiscoveryThread

__all__ = [
    # Core configuration management
    'ConfigManager', 'ConfigPersistence',
    # Views and dialogs
    'ConfigView', 'ErrorDialog',
    # Database operations
    'DatabaseOperations',
    # Gemini AI configuration
    'GeminiConfig', 'GeminiConfigUI', 'GeminiModelDiscoveryThread',
    # Exceptions
    'ConfigError', 'ConfigPermissionError', 'ConfigFormatError',
    'ConfigValidationError', 'ConfigLoadError', 'ConfigSaveError', 'ConfigMissingError'
]
