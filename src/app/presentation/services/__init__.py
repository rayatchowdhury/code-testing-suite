"""
Application services for presentation layer.

Services provide centralized functionality that windows and widgets
can consume without tight coupling.
"""

from .error_handler_service import ErrorHandlerService, ErrorSeverity
from .results_export_service import export_test_cases_to_zip, create_export_summary

__all__ = [
    "ErrorHandlerService",
    "ErrorSeverity",
    "export_test_cases_to_zip",
    "create_export_summary",
]
