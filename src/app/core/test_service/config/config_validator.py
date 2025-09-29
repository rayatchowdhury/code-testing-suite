"""
Configuration Validator - Validates configuration integrity.
"""

from typing import List, Dict
from .config_models import TestServiceConfig, LanguageConfig


class ConfigValidator:
    """Validates configuration settings and dependencies."""
    
    def validate_config(self, config: TestServiceConfig) -> List[str]:
        """Validate complete configuration."""
        pass
    
    def validate_language_config(self, language: str, config: LanguageConfig) -> List[str]:
        """Validate language-specific configuration."""
        pass
    
    def _check_compiler_availability(self, compiler: str) -> bool:
        """Check if compiler is available on system."""
        pass
    
    def _validate_flags(self, flags: List[str], compiler: str) -> List[str]:
        """Validate compiler flags."""
        pass
    
    def _check_paths(self, config: TestServiceConfig) -> List[str]:
        """Validate file paths in configuration."""
        pass