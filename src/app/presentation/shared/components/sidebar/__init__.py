"""Sidebar components.

Note: Uses lazy imports to avoid loading TestCountSlider and LimitsInputWidget
at startup (they pull in heavy style modules). Only Sidebar itself is eager.
"""

from typing import TYPE_CHECKING

# Sidebar itself is lightweight - import eagerly
from .sidebar import Sidebar, SidebarSection

if TYPE_CHECKING:
    from .test_count_slider import TestCountSlider
    from .limits_input import LimitsInputWidget

__all__ = ["Sidebar", "SidebarSection", "TestCountSlider", "LimitsInputWidget"]

def __getattr__(name: str):
    """Lazy import heavy sidebar widgets on first access."""
    if name == "TestCountSlider":
        from .test_count_slider import TestCountSlider
        return TestCountSlider
    elif name == "LimitsInputWidget":
        from .limits_input import LimitsInputWidget
        return LimitsInputWidget
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
