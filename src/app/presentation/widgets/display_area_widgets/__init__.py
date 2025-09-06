"""
Display Area Widgets package for the Code Testing Suite.

This package contains specialized widgets for display areas.
"""

from src.app.presentation.widgets.display_area_widgets.editor import EditorWidget, CodeEditor
from src.app.presentation.widgets.display_area_widgets.console import ConsoleOutput
from src.app.presentation.widgets.display_area_widgets.ai_panel import AIPanel

__all__ = [
    "EditorWidget",
    "CodeEditor", 
    "ConsoleOutput",
    "AIPanel"
]