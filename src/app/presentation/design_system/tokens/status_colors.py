"""
Centralized error and status color definitions
"""

# Standard error color (used across multiple files)
ERROR_COLOR_HEX = "#ff4444"

# Status colors for various UI states
STATUS_COLORS = {
    "error": ERROR_COLOR_HEX,
    "warning": "#FFC107",
    "success": "#4CAF50",
    "info": "#2196F3",
    "pending": "#FF9800",
    "disabled": "#9E9E9E",
}

# Test result colors
TEST_STATUS_COLORS = {
    "passed": STATUS_COLORS["success"],
    "failed": STATUS_COLORS["error"],
    "timeout": "#FF6F00",  # Deep Orange
    "compilation_error": STATUS_COLORS["error"],
    "runtime_error": "#E91E63",  # Pink
}

# Font weight constants
FONT_WEIGHTS = {
    "normal": "normal",
    "bold": "bold",
    "light": "300",
    "medium": "500",
    "semibold": "600",
}

# Font size constants
FONT_SIZES = {
    "small": "12px",
    "medium": "13px",
    "default": "14px",
    "large": "16px",
    "title": "18px",
}
