"""
Core module for the Code Testing Suite.

This module contains the core business logic and domain models,
including AI functionality, configuration management, and tools.
"""

# AI Module exports
from src.app.core.ai import (
    EditorAI,
    PromptTemplates,
    get_gemini_client,
    initialize_gemini,
    is_ai_ready,
    is_gemini_available,
    should_show_ai_panel,
)

# Configuration Module exports
from src.app.core.config import (
    ConfigError,
    ConfigLoadError,
    ConfigManager,
    ConfigPersistence,
    ConfigSaveError,
    ConfigView,
    DatabaseOperations,
    ErrorDialog,
    GeminiConfig,
    GeminiConfigUI,
)
from src.app.core.tools.benchmarker import BenchmarkCompilerRunner, Benchmarker
from src.app.core.tools.comparator import Comparator

# Tools Module exports
from src.app.core.tools.compiler_runner import CompilerRunner
