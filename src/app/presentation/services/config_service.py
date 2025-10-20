"""
Configuration service for centralized config access.

Wraps core.config to provide consistent configuration access
without lazy imports.
"""

from typing import Any, Optional
from PySide6.QtCore import QObject, Signal


class ConfigService(QObject):
    """
    Singleton service for configuration management.
    
    Centralizes access to application configuration, eliminating
    lazy imports and providing change notifications.
    
    Usage:
        from src.app.presentation.services.config_service import ConfigService
        
        config = ConfigService.instance()
        theme = config.get("theme", "dark")
        config.set("theme", "light")
    """
    
    # Singleton instance
    _instance: Optional['ConfigService'] = None
    
    # Signals
    configChanged = Signal(str, object)  # key, value
    
    @classmethod
    def instance(cls) -> 'ConfigService':
        """
        Get singleton instance.
        
        Returns:
            ConfigService singleton
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """
        Initialize ConfigService.
        
        Raises:
            RuntimeError: If called directly (use instance() instead)
        """
        if ConfigService._instance is not None:
            raise RuntimeError("Use ConfigService.instance()")
        super().__init__()
        # TODO: Implementation in Phase 1C
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        # TODO: Implementation in Phase 1C
        pass
    
    def set(self, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: New value
        """
        # TODO: Implementation in Phase 1C
        pass
