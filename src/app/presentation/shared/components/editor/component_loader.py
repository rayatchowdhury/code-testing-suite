"""
Component Loader for Editor Widget

Replaces global variable pattern with encapsulated lazy loading.
Makes components injectable, testable, and thread-safe.

Issue #5: Global Variable Abuse - FIXED
"""

from typing import Any, Callable, Optional


class ComponentLoader:
    """
    Lazy loader for heavy editor components.
    
    Provides lazy loading without global state pollution.
    All dependencies are instance attributes, making the class:
    - Testable (can be mocked)
    - Injectable (can pass different instances)
    - Resettable (for test isolation)
    - Thread-safe per instance (no shared global state)
    """
    
    def __init__(self):
        """Initialize with all lazy-loaded components set to None."""
        self._markdown: Optional[Callable] = None
        self._pygments_highlight: Optional[Callable] = None
        self._pygments_formatter: Optional[type] = None
        self._pygments_lexer: Optional[Callable] = None
        self._syntax_highlighters: Optional[dict[str, type]] = None
        self._editor_ai: Optional[type] = None
        self._ai_panel: Optional[type] = None
    
    @property
    def markdown(self) -> Callable:
        """
        Lazy-load markdown renderer.
        
        Returns:
            Callable markdown function or fallback for plain text
        """
        if self._markdown is None:
            try:
                from markdown import markdown
                self._markdown = markdown
            except ImportError:
                # Fallback: return plain text function if markdown not available
                def plain_text_fallback(text: str, **kwargs: Any) -> str:
                    return f"<pre>{text}</pre>"
                self._markdown = plain_text_fallback
        return self._markdown
    
    @property
    def pygments(self) -> tuple[Callable, type, Callable]:
        """
        Lazy-load Pygments components (highlight, formatter, lexer).
        
        Returns:
            Tuple of (highlight function, HtmlFormatter class, get_lexer_by_name function)
        """
        if self._pygments_highlight is None:
            from pygments import highlight
            from pygments.formatters import HtmlFormatter
            from pygments.lexers import get_lexer_by_name
            
            self._pygments_highlight = highlight
            self._pygments_formatter = HtmlFormatter
            self._pygments_lexer = get_lexer_by_name
        
        return self._pygments_highlight, self._pygments_formatter, self._pygments_lexer
    
    @property
    def syntax_highlighters(self) -> dict[str, type]:
        """
        Lazy-load syntax highlighter classes.
        
        Returns:
            Dict mapping language names to highlighter classes
        """
        if self._syntax_highlighters is None:
            from src.app.presentation.shared.components.editor.syntax_highlighter import (
                CPPSyntaxHighlighter,
                JavaSyntaxHighlighter,
                PythonSyntaxHighlighter,
            )
            
            self._syntax_highlighters = {
                "cpp": CPPSyntaxHighlighter,
                "python": PythonSyntaxHighlighter,
                "java": JavaSyntaxHighlighter,
            }
        return self._syntax_highlighters
    
    @property
    def editor_ai(self) -> type:
        """
        Lazy-load EditorAI class.
        
        Returns:
            EditorAI class (not instantiated)
        """
        if self._editor_ai is None:
            from src.app.core.ai.core.editor_ai import EditorAI
            self._editor_ai = EditorAI
        return self._editor_ai
    
    @property
    def ai_panel(self) -> type:
        """
        Lazy-load AIPanel class.
        
        Returns:
            AIPanel class (not instantiated)
        """
        if self._ai_panel is None:
            from src.app.presentation.shared.components.editor.ai_panel import AIPanel
            self._ai_panel = AIPanel
        return self._ai_panel
    
    def reset(self) -> None:
        """
        Reset all lazy-loaded components.
        
        Useful for testing to ensure clean state between tests.
        """
        self._markdown = None
        self._pygments_highlight = None
        self._pygments_formatter = None
        self._pygments_lexer = None
        self._syntax_highlighters = None
        self._editor_ai = None
        self._ai_panel = None


# Module-level singleton for convenient access
# Can still be replaced/mocked in tests via dependency injection
_default_loader = ComponentLoader()


def get_component_loader() -> ComponentLoader:
    """
    Get the default component loader instance.
    
    This provides a convenient way to access the loader while still
    allowing tests to inject their own instance.
    
    Returns:
        Default ComponentLoader instance
    """
    return _default_loader
