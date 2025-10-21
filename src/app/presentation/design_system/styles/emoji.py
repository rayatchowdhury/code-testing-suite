"""
Emoji font utilities for consistent emoji rendering across platforms.

Provides functions to apply Noto Color Emoji font to QLabel widgets
to ensure emojis display properly on all operating systems.
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel


# Emoji font family with fallbacks for different platforms
EMOJI_FONT_FAMILY = "Noto Color Emoji, Segoe UI Emoji, Apple Color Emoji, sans-serif"


def set_emoji_font(label: QLabel, size: int = None) -> None:
    """
    Set emoji font for a QLabel containing emojis.
    
    Args:
        label: The QLabel widget to apply emoji font to
        size: Optional font size in pixels. If None, uses label's current size.
    """
    font = QFont(EMOJI_FONT_FAMILY)
    if size is not None:
        font.setPixelSize(size)
    label.setFont(font)
