"""
Base classes for the Code Testing Suite tools.

This package contains the base classes that consolidate common functionality
across different tool implementations, eliminating code duplication and
providing consistent behavior.

Base Classes:
- BaseCompiler: Consolidates compilation logic and caching
- BaseTestWorker: Unifies parallel testing patterns and error handling
- BaseRunner: Standardizes runner initialization, threading, and database integration
- ProcessExecutor: Provides common subprocess execution utilities
- LanguageDetector: Multi-language detection and compiler configuration
- Language Compilers: Language-specific compilation implementations
"""

from src.app.core.tools.base.base_compiler import BaseCompiler
from src.app.core.tools.base.base_runner import BaseRunner
from src.app.core.tools.specialized.base_test_worker import BaseTestWorker
from src.app.core.tools.base.language_compilers import (
    BaseLanguageCompiler,
    CppCompiler,
    JavaCompiler,
    LanguageCompilerFactory,
    PythonCompiler,
)
from src.app.core.tools.base.language_detector import Language, LanguageDetector
from src.app.core.tools.base.process_executor import ProcessExecutor

__all__ = [
    "BaseCompiler",
    "BaseTestWorker",
    "BaseRunner",
    "ProcessExecutor",
    "LanguageDetector",
    "Language",
    "BaseLanguageCompiler",
    "CppCompiler",
    "PythonCompiler",
    "JavaCompiler",
    "LanguageCompilerFactory",
]
