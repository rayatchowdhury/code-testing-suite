"""
UI state model.

Represents global UI state.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class UIState:
    """
    Global UI state.
    
    Attributes:
        current_window: Name of current window
        is_testing: Whether tests are running
        unsaved_changes: Whether there are unsaved changes
    """
    current_window: Optional[str] = None
    is_testing: bool = False
    unsaved_changes: bool = False
