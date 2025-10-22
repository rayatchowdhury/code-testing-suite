"""
Help Center Document - Terminal/Glitch Design Layout
Self-contained document widget with embedded theme and styling
"""

from typing import List

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QLabel,
    QFrame,
)

from src.app.presentation.shared.design_system.tokens.colors import MATERIAL_COLORS
from .content import HelpSection

# =============================================================================
# LOCAL CONSTANTS (using centralized MATERIAL_COLORS)
# =============================================================================

# Spacing constants
SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
}

# Font configuration
FONTS = {
    "family": "Consolas, 'Courier New', monospace",
    "fallback": "'Segoe UI', system-ui, sans-serif",
    "emoji": "Noto Color Emoji, Segoe UI Emoji, Apple Color Emoji, sans-serif",
    "sizes": {
        "title": 22,
        "section_title": 14,
        "prompt": 10,
        "description": 11,
        "icon": 18,
    },
}

# Animation settings
ANIMATION = {
    "fade_duration": 300,
    "fade_start_delay": 50,
}

# UI constants
UI = {
    "separator_height": 1,
    "bullet_symbol": ">>",
    "prompt_symbol": ">> ",
    "icon_fallback": "▸",
}

# Surface color (semi-transparent overlay)
SURFACE_COLOR = "rgba(255, 255, 255, 0.03)"

# =============================================================================
# BASE DOCUMENT WIDGET
# =============================================================================

class HelpDocument(QWidget):
    """
    Base document widget with scroll container and fade-in animation
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._init_ui()
        self._apply_styles()
        self._setup_fade_in()

    def _init_ui(self):
        """Initialize UI with scroll container"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setObjectName("help_scroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Hide scrollbar
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(self.build_content())
        
        layout.addWidget(scroll)

    def build_content(self) -> QWidget:
        """Override in subclasses to provide content"""
        raise NotImplementedError("Subclasses must implement build_content()")

    def _apply_styles(self):
        """Apply base stylesheet"""
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a1c,
                    stop:1 #1e1e20
                );
                color: {MATERIAL_COLORS['text']};
                font-family: {FONTS['fallback']};
            }}
            
            QScrollArea#help_scroll {{
                border: none;
                background: transparent;
            }}
            
            QScrollArea QWidget {{
                background-color: transparent;
            }}
        """)

    def _setup_fade_in(self):
        """Setup fade-in entrance animation"""
        self.setWindowOpacity(0)
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(ANIMATION["fade_duration"])
        anim.setStartValue(0)
        anim.setEndValue(1)
        QTimer.singleShot(ANIMATION["fade_start_delay"], anim.start)
        self._fade_anim = anim  # Keep reference

# =============================================================================
# TERMINAL DOCS IMPLEMENTATION
# =============================================================================

class TerminalDocsWidget(HelpDocument):
    """Terminal-style help documentation with monospace fonts"""
    
    def __init__(self, title: str, sections: List[HelpSection], parent: QWidget = None):
        self.title = title
        self.sections_data = sections
        super().__init__(parent)

    def build_content(self) -> QWidget:
        """Build terminal-style content"""
        content = QWidget()
        content.setObjectName("terminal_content")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(
            SPACING["lg"], 
            SPACING["lg"], 
            SPACING["lg"], 
            SPACING["lg"]
        )
        layout.setSpacing(0)

        self._add_header(layout)
        self._add_sections(layout)

        # Apply content-specific styling (using ACCENT color from MATERIAL_COLORS for consistency with main window)
        content.setStyleSheet(f"""
            QWidget#terminal_content {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a1c,
                    stop:1 #1e1e20
                );
                border: 2px solid {MATERIAL_COLORS['accent']};
                border-radius: 8px;
            }}
        """)

        return content

    def _add_header(self, layout: QVBoxLayout):
        """Add terminal-style header"""
        header = QWidget()
        h_layout = QVBoxLayout(header)
        h_layout.setSpacing(SPACING["sm"])
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        # Terminal prompt
        prompt = QLabel(UI["prompt_symbol"] + "HELP DOCUMENTATION")
        prompt.setFont(self._create_font("prompt", QFont.Weight.Bold, mono=True))
        prompt.setStyleSheet(f"""
            color: {MATERIAL_COLORS['accent']};
            background: transparent;
            letter-spacing: 2px;
        """)
        h_layout.addWidget(prompt)
        
        # Title
        title_label = QLabel(self.title.upper())
        title_label.setFont(self._create_font("title", QFont.Weight.ExtraBold, mono=True))
        title_label.setWordWrap(True)
        title_label.setStyleSheet(f"""
            color: {MATERIAL_COLORS['text']};
            background: transparent;
            letter-spacing: 1px;
        """)
        h_layout.addWidget(title_label)
        
        # Separator
        sep = QFrame()
        sep.setFixedHeight(UI["separator_height"])
        sep.setStyleSheet(f"background: {MATERIAL_COLORS['separator']}; border: none;")
        h_layout.addWidget(sep)
        
        layout.addWidget(header)
        layout.addSpacing(SPACING["md"] + SPACING["xs"])

    def _add_sections(self, layout: QVBoxLayout):
        """Add all sections"""
        for i, section_data in enumerate(self.sections_data):
            if i > 0:
                layout.addSpacing(SPACING["lg"])
            
            section = self._create_section(
                section_data.icon,
                section_data.title,
                section_data.content,
                section_data.items or []
            )
            layout.addWidget(section)

    def _create_section(self, icon: str, title: str, content: str, items: List[str]) -> QFrame:
        """Create a terminal-style section"""
        section = QFrame()
        section.setObjectName("terminal_section")
        section.setStyleSheet(f"""
            QFrame#terminal_section {{
                background: {SURFACE_COLOR};
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-left: 3px solid {MATERIAL_COLORS['accent']};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        
        s_layout = QVBoxLayout(section)
        s_layout.setSpacing(12)
        s_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header: icon + title
        header = QWidget()
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(10)
        
        # Icon
        icon_label = QLabel(icon if len(icon) <= 2 else UI["icon_fallback"])
        icon_label.setFont(self._create_font("icon", mono=False, emoji=True))
        icon_label.setStyleSheet(f"color: {MATERIAL_COLORS['accent']}; background: transparent;")
        h_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title.upper())
        title_label.setFont(self._create_font("section_title", QFont.Weight.Bold, mono=True))
        title_label.setStyleSheet(f"""
            color: {MATERIAL_COLORS['text']};
            background: transparent;
            letter-spacing: 1px;
        """)
        h_layout.addWidget(title_label)
        h_layout.addStretch()
        
        s_layout.addWidget(header)
        
        # Content text
        if content:
            content_label = QLabel(content)
            content_label.setWordWrap(True)
            content_label.setFont(self._create_font("description", mono=False))
            content_label.setStyleSheet(f"""
                color: {MATERIAL_COLORS['text_dim']};
                background: transparent;
                line-height: 1.6;
            """)
            s_layout.addWidget(content_label)
        
        # List items
        if items:
            for item in items:
                item_widget = QWidget()
                item_layout = QHBoxLayout(item_widget)
                item_layout.setContentsMargins(0, 0, 0, 0)
                item_layout.setSpacing(SPACING["sm"])
                
                # Bullet
                bullet = QLabel(UI["bullet_symbol"])
                bullet.setFont(self._create_font("prompt", QFont.Weight.Bold, mono=True))
                bullet.setStyleSheet(f"color: {MATERIAL_COLORS['accent']}; background: transparent;")
                item_layout.addWidget(bullet)
                
                # Text
                text = QLabel(item)
                text.setWordWrap(True)
                text.setFont(self._create_font("description", mono=False))
                text.setStyleSheet(f"color: {MATERIAL_COLORS['text_bright']}; background: transparent;")
                item_layout.addWidget(text, 1)
                
                s_layout.addWidget(item_widget)
        
        return section

    def _create_font(self, size_key: str, weight: QFont.Weight = QFont.Weight.Normal, mono: bool = True, emoji: bool = False) -> QFont:
        """Create font with specified parameters"""
        if emoji:
            family = FONTS["emoji"]
        else:
            family = FONTS["family"] if mono else FONTS["fallback"]
        font = QFont(family, -1, weight)
        font.setPixelSize(FONTS["sizes"][size_key])
        return font

# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_help_document(title: str, sections: List[HelpSection]) -> TerminalDocsWidget:
    """
    Create a help center document with terminal/glitch aesthetic
    
    Args:
        title: Document title
        sections: List of HelpSection objects
        
    Returns:
        Styled document widget
    """
    return TerminalDocsWidget(title, sections)
