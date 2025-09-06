"""
Core module for the Code Testing Suite.

This module contains the core business logic and domain models,
including AI functionality, configuration management, and tools.
"""

# AI Module exports
from src.app.core.ai import (
    EditorAI,
    get_gemini_client,
    is_gemini_available,
    initialize_gemini,
    should_show_ai_panel,
    is_ai_ready,
    PromptTemplates,
)

# Configuration Module exports
from src.app.core.config import (
    ConfigManager,
    ConfigPersistence,
    ConfigError,
    ConfigLoadError,
    ConfigSaveError,
    ConfigView,
    ErrorDialog,
    DatabaseOperations,
    GeminiConfig,
    GeminiConfigUI,
    GeminiModelDiscoveryThread,
)

# Tools Module exports
from src.app.core.tools.compiler_runner import CompilerRunner
from src.app.core.tools.validation_compiler_runner import ValidationCompilerRunner
from src.app.core.tools.stress_compiler_runner import StressCompilerRunner
from src.app.core.tools.tle_compiler_runner import TLECompilerRunner
from src.app.core.tools.validator import Validator
from src.app.core.tools.stresser import Stresser
from src.app.core.tools.tle_runner import TLERunner
