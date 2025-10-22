"""
CodeEditor Window Package

Phase 5: Per-Window Packaging
Code Editor Window with syntax highlighting and file management

Note: Uses lazy imports for fast startup. Classes are imported when accessed.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.presentation.windows.editor.view import CodeEditorWindow

__all__ = ["CodeEditorWindow"]

def __getattr__(name: str):
    """Lazy import window classes on first access."""
    if name == "CodeEditorWindow":
        from src.app.presentation.windows.editor.view import CodeEditorWindow
        return CodeEditorWindow
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
