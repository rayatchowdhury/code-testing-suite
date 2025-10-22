"""
Help Center Window Package

Phase 5: Per-Window Packaging
Help Center window with documentation and guides

Note: Uses lazy imports for fast startup. Classes are imported when accessed.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.presentation.windows.help_center.view import HelpCenterWindow

__all__ = ["HelpCenterWindow"]

def __getattr__(name: str):
    """Lazy import window classes on first access."""
    if name == "HelpCenterWindow":
        from src.app.presentation.windows.help_center.view import HelpCenterWindow
        return HelpCenterWindow
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
