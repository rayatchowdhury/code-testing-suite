"""
Language Configuration Manager - Per-language compilation settings.
"""

from typing import Dict, List
from ...config.config_models import LanguageConfig


class LanguageConfigManager:
    """Manages language-specific configuration settings."""
    
    def __init__(self, configs: Dict[str, LanguageConfig]):
        """Initialize with language configurations."""
        self.configs = configs
    
    def get_config(self, language: str) -> LanguageConfig:
        """Get configuration for specific language."""
        pass
    
    def validate_config(self, language: str, config: LanguageConfig) -> List[str]:
        """Validate language configuration."""
        pass
    
    def get_compiler_executable(self, language: str) -> str:
        """Get compiler executable for language."""
        pass
    
    def get_execution_command(self, language: str, executable_path: str) -> List[str]:
        """Get execution command for language."""
        pass