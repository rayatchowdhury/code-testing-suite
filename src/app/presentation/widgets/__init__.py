"""
Widgets package for the Code Testing Suite.

This package contains all the UI widgets and components.
"""

from src.app.presentation.widgets.display_area import DisplayArea
from src.app.presentation.widgets.display_area_widgets.ai_panel import AIPanel
from src.app.presentation.widgets.display_area_widgets.console import ConsoleOutput

# Display area widgets
from src.app.presentation.widgets.display_area_widgets.editor import (
    CodeEditor,
    EditorWidget,
)

# Main widget exports
from src.app.presentation.widgets.sidebar import Sidebar

__all__ = [
    "Sidebar",
    "DisplayArea",
    "EditorWidget",
    "CodeEditor",
    "ConsoleOutput",
    "AIPanel",
]
