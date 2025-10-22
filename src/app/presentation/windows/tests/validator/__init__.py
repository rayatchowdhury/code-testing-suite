"""
Validator Window Package

Phase 5: Per-Window Packaging
Validator window for code validation testing

Note: Uses lazy imports for fast startup. Classes are imported when accessed.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.presentation.windows.tests.validator.view import ValidatorWindow

__all__ = ["ValidatorWindow"]

def __getattr__(name: str):
    """Lazy import window classes on first access."""
    if name == "ValidatorWindow":
        from src.app.presentation.windows.tests.validator.view import ValidatorWindow
        return ValidatorWindow
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
