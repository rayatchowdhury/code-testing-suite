"""
Compilation Configuration module - Language-specific compilation settings.
"""

from .language_config import LanguageConfigManager
from .compiler_flags import CompilerFlagsManager

__all__ = ['LanguageConfigManager', 'CompilerFlagsManager']