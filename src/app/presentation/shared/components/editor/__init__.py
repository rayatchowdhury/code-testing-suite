"""Editor components.

Note: Uses lazy imports for fast startup. Heavy components like syntax
highlighters and AI panel are only loaded when accessed.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .editor_widget import CodeEditor, EditorWidget
    from .editor_tab_widget import EditorTabWidget
    from .test_tab_widget import TestTabWidget
    from .testing_content_widget import TestingContentWidget
    from .ai_panel import AIPanel
    from .syntax_highlighter import (
        CPPSyntaxHighlighter, 
        PythonSyntaxHighlighter, 
        JavaSyntaxHighlighter
    )
    from .component_loader import ComponentLoader, get_component_loader

__all__ = [
    "CodeEditor", 
    "EditorWidget", 
    "EditorTabWidget", 
    "TestTabWidget",
    "TestingContentWidget",
    "AIPanel", 
    "CPPSyntaxHighlighter", 
    "PythonSyntaxHighlighter", 
    "JavaSyntaxHighlighter",
    "ComponentLoader",
    "get_component_loader"
]

def __getattr__(name: str):
    """Lazy import editor components on first access."""
    if name in ("CodeEditor", "EditorWidget"):
        from .editor_widget import CodeEditor, EditorWidget
        return locals()[name]
    elif name == "EditorTabWidget":
        from .editor_tab_widget import EditorTabWidget
        return EditorTabWidget
    elif name == "TestTabWidget":
        from .test_tab_widget import TestTabWidget
        return TestTabWidget
    elif name == "TestingContentWidget":
        from .testing_content_widget import TestingContentWidget
        return TestingContentWidget
    elif name == "AIPanel":
        from .ai_panel import AIPanel
        return AIPanel
    elif name in ("CPPSyntaxHighlighter", "PythonSyntaxHighlighter", "JavaSyntaxHighlighter"):
        from .syntax_highlighter import (
            CPPSyntaxHighlighter, 
            PythonSyntaxHighlighter, 
            JavaSyntaxHighlighter
        )
        return locals()[name]
    elif name in ("ComponentLoader", "get_component_loader"):
        from .component_loader import ComponentLoader, get_component_loader
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
