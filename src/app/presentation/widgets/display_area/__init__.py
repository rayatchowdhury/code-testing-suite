"""Display Area Widget Package

Phase 6: Styles and Tokens
Contains main display area and tab-based content widgets.
"""

from src.app.presentation.widgets.display_area.display_area import DisplayArea
from src.app.presentation.widgets.display_area.ai_panel import AIPanel
from src.app.presentation.widgets.display_area.console import ConsoleWidget
from src.app.presentation.widgets.display_area.editor import CodeEditor, EditorWidget
from src.app.presentation.widgets.display_area.editor_tab_widget import EditorTabWidget
from src.app.presentation.widgets.display_area.test_tab_widget import TestTabWidget

# Backward compatibility
ConsoleOutput = ConsoleWidget

__all__ = [
    "DisplayArea",
    "AIPanel",
    "ConsoleWidget",
    "ConsoleOutput",
    "CodeEditor",
    "EditorWidget",
    "EditorTabWidget",
    "TestTabWidget",
]
