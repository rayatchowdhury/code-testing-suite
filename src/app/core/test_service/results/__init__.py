"""
Results module - Results processing and formatting.
"""

from .result_models import TestResult, CompilationResult
from .result_processor import ResultProcessor
from .result_formatter import ResultFormatter

__all__ = ['TestResult', 'CompilationResult', 'ResultProcessor', 'ResultFormatter']