"""Config module for managing application configuration.

Structured configuration management with organized subdirectories (Phase 3).

## Usage

### Standard Pattern (Recommended - Singleton):
```python
from src.app.core.config import ConfigManager

# Get singleton instance
config_manager = ConfigManager.instance()
config = config_manager.load_config()
editor_settings = config.get("editor_settings", {})
```

### Direct Instantiation (Testing/Special Cases):
```python
from src.app.core.config import ConfigManager

# Create new instance (not recommended for production)
config_manager = ConfigManager("custom_config.json")
```

### Best Practices:
1. **Always use ConfigManager.instance()** for application code
2. Direct instantiation should only be used in tests with ConfigManager.reset_instance()
3. Config changes should go through ConfigPersistence for UI consistency
4. Use proper exception handling for ConfigError types
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

__all__ = [
    # Core configuration management
    "ConfigManager",
    "ConfigPersistence",
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
