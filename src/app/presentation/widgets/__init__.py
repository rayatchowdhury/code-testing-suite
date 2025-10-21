"""
Widgets package for the Code Testing Suite.

This package contains all the UI widgets and components.
"""

from src.app.presentation.widgets.display_area import DisplayArea
from src.app.presentation.widgets.display_area.ai_panel import AIPanel
from src.app.presentation.widgets.display_area.console import ConsoleWidget

# Display area widgets
from src.app.presentation.widgets.display_area.editor import (
    CodeEditor,
    EditorWidget,
)

# Main widget exports
from src.app.presentation.widgets.sidebar import Sidebar

# Backward compatibility alias
ConsoleOutput = ConsoleWidget

__all__ = [
    "Sidebar",
    "DisplayArea",
    "EditorWidget",
    "CodeEditor",
    "ConsoleWidget",
    "ConsoleOutput",  # Backward compatibility
    "AIPanel",
]
