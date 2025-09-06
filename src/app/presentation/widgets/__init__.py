"""
Widgets package for the Code Testing Suite.

This package contains all the UI widgets and components.
"""

# Main widget exports
from src.app.presentation.widgets.sidebar import Sidebar
from src.app.presentation.widgets.display_area import DisplayArea

# Display area widgets
from src.app.presentation.widgets.display_area_widgets.editor import EditorWidget, CodeEditor
from src.app.presentation.widgets.display_area_widgets.console import ConsoleOutput
from src.app.presentation.widgets.display_area_widgets.ai_panel import AIPanel

__all__ = [
    "Sidebar",
    "DisplayArea",
    "EditorWidget", 
    "CodeEditor",
    "ConsoleOutput",
    "AIPanel"
]