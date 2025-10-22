"""
Emoji font utilities for consistent emoji rendering across platforms.

Provides functions to apply Noto Color Emoji font to QLabel widgets
to ensure emojis display properly on all operating systems.
"""

from pathlib import Path
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QLabel


# Emoji font family with fallbacks for different platforms
EMOJI_FONT_FAMILY = "Noto Color Emoji, Segoe UI Emoji, Apple Color Emoji, sans-serif"

# Track if font has been loaded
_font_loaded = False


def load_emoji_font() -> bool:
    """
    Load Noto Color Emoji font file into the application.
    
    Returns:
        bool: True if font was loaded successfully, False otherwise
    """
    global _font_loaded
    
    if _font_loaded:
        return True
    
    # Get the directory where this file is located
    fonts_dir = Path(__file__).parent
    
    # Try to find the font file
    font_files = [
        fonts_dir / "NotoColorEmoji-subset.ttf",
        fonts_dir / "NotoColorEmoji.ttf",
    ]
    
    for font_path in font_files:
        if font_path.exists():
            font_id = QFontDatabase.addApplicationFont(str(font_path))
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                print(f"✅ Loaded emoji font: {families}")
                _font_loaded = True
                return True
            else:
                print(f"⚠️ Failed to load font from: {font_path}")
    
    print("⚠️ Emoji font not found, emojis may display as blocks on some systems")
    return False


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
