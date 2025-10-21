"""
Display Area Widgets package for the Code Testing Suite.

This package contains specialized widgets for display areas.
"""

from src.app.presentation.widgets.display_area_widgets.ai_panel import AIPanel
from src.app.presentation.widgets.display_area_widgets.console import ConsoleWidget
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

# Alias for backward compatibility
ConsoleOutput = ConsoleWidget

__all__ = [
    "EditorWidget",
    "CodeEditor",
    "ConsoleWidget",
    "ConsoleOutput",  # Keep for backward compatibility
    "AIPanel",
    "TestTabWidget",
    "EditorTabWidget",
]
