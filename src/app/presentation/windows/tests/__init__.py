"""
Test Windows Package

Contains all test-related windows: benchmarker, comparator, and validator.

Note: Uses lazy imports for fast startup. Classes are imported when accessed.
WindowFactory already handles lazy creation, but this prevents eager loading
when this module is imported.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.presentation.windows.tests.benchmarker import BenchmarkerWindow
    from src.app.presentation.windows.tests.comparator import ComparatorWindow
    from src.app.presentation.windows.tests.validator import ValidatorWindow

__all__ = ["BenchmarkerWindow", "ComparatorWindow", "ValidatorWindow"]

def __getattr__(name: str):
    """Lazy import window classes on first access."""
    if name == "BenchmarkerWindow":
        from src.app.presentation.windows.tests.benchmarker import BenchmarkerWindow
        return BenchmarkerWindow
    elif name == "ComparatorWindow":
        from src.app.presentation.windows.tests.comparator import ComparatorWindow
        return ComparatorWindow
    elif name == "ValidatorWindow":
        from src.app.presentation.windows.tests.validator import ValidatorWindow
        return ValidatorWindow
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
