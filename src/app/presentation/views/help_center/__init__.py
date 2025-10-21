# Backwards compatibility - import from new location
from src.app.presentation.windows.help_center.widgets.content import HelpSection, get_available_topics, get_document_data
from src.app.presentation.windows.help_center import HelpCenterWindow

__all__ = [
    "HelpCenterWindow",
    "HelpSection",
    "get_document_data",
    "get_available_topics",
]
