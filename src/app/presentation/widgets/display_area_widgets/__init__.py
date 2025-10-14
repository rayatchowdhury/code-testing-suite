"""
Display Area Widgets package for the Code Testing Suite.

This package contains specialized widgets for display areas.
"""

from src.app.presentation.widgets.display_area_widgets.ai_panel import AIPanel
from src.app.presentation.widgets.display_area_widgets.console import ConsoleOutput
from src.app.presentation.widgets.display_area_widgets.editor import (
    CodeEditor,
    EditorWidget,
)
from src.app.presentation.widgets.display_area_widgets.editor_tab_widget import (
    EditorTabWidget,
)
from src.app.presentation.widgets.display_area_widgets.test_tab_widget import (
    TestTabWidget,
)

__all__ = [
    "EditorWidget",
    "CodeEditor",
    "ConsoleOutput",
    "AIPanel",
    "TestTabWidget",
    "EditorTabWidget",
]
