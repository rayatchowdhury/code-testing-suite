"""
Window configuration models.

Defines configuration structures for windows.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class WindowConfig:
    """
    Configuration for a window.
    
    Attributes:
        title: Window title
        sidebar_config: Sidebar configuration
        content_config: Content area configuration
        metadata: Additional metadata
    """
    title: str
    sidebar_config: Dict[str, Any]
    content_config: Dict[str, Any]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize defaults."""
        if self.metadata is None:
            self.metadata = {}
