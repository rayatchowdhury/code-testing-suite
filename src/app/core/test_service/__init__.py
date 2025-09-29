"""
Test Service - Next-generation testing system for Code Testing Suite.

This module replaces core/tools with a modern, multi-language,
configuration-driven architecture.
"""

# Main service exports
from .service_factory import TestServiceFactory
from .handlers.test_handler import TestHandler

# Configuration exports  
from .config.config_service import ConfigService
from .config.config_models import TestServiceConfig, LanguageConfig

# Result exports
from .results.result_models import TestResult, CompilationResult

__version__ = "1.0.0"
__all__ = [
    'TestServiceFactory',
    'TestHandler', 
    'ConfigService',
    'TestServiceConfig',
    'LanguageConfig',
    'TestResult',
    'CompilationResult'
]