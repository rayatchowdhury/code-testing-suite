"""Core configuration management components.

This module contains the fundamental configuration handling logic:
- Configuration loading, saving, and validation
- Configuration exceptions and error handling
- Core configuration management classes
"""

from src.app.core.config.core.config_handler import ConfigManager, ConfigPersistence
from src.app.core.config.core.exceptions import (
    ConfigError,
    ConfigFormatError,
    ConfigLoadError,
    ConfigMissingError,
    ConfigPermissionError,
    ConfigSaveError,
    ConfigValidationError,
)

__all__ = [
    # Configuration management
    "ConfigManager",
    "ConfigPersistence",
    # Exceptions
    "ConfigError",
    "ConfigPermissionError",
    "ConfigFormatError",
    "ConfigValidationError",
    "ConfigLoadError",
    "ConfigSaveError",
    "ConfigMissingError",
]
