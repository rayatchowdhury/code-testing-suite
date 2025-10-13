"""
Sidebar widgets package for the Code Testing Suite application.

This package contains reusable sidebar widgets used across different views:
- TestCountSlider: Widget for selecting number of test cases to generate
- LimitsInputWidget: Widget for configuring time and memory limits
- Other specialized sidebar components

All widgets in this package are designed to be reusable across validator,
comparator, and benchmarker views.
"""

from .test_count_slider import TestCountSlider
from .limits_input_widget import LimitsInputWidget

__all__ = ["TestCountSlider", "LimitsInputWidget"]
