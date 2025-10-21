"""
Main Window Document - Glassmorphism Terminal/Glitch Design Layout
Self-contained document widget with embedded theme and styling
"""

import logging
from typing import List, Tuple

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS
from .content import FEATURE_DATA, WELCOME_TITLE, WELCOME_SUBTITLE, CTA_TITLE, CTA_SUBTITLE

logger = logging.getLogger(__name__)

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
        "hero": 26,
        "glitch": 11,
        "card_title": 15,
        "feature": 11,
        "cta": 14,
        "cta_sub": 11,
    },
}

# Animation settings
ANIMATION = {
    "fade_duration": 300,
    "fade_start_delay": 50,
}

# UI dimensions
UI = {
    "separator_height": 1,
    "card_border_width": 2,
    "card_border_radius": 10,
    "card_padding": 14,
    "cta_border_radius": 12,
    "cta_padding": 18,
    "content_border_radius": 8,
}

# Surface colors (semi-transparent overlays)
SURFACE_COLORS = {
    "surface": "rgba(255, 255, 255, 0.03)",
    "surface_hover": "rgba(255, 255, 255, 0.08)",
    "border": "rgba(255, 255, 255, 0.15)",
    "border_hover": "rgba(255, 255, 255, 0.5)",
}

# =============================================================================
# BASE DOCUMENT WIDGET
# =============================================================================

class MainWindowDocument(QWidget):
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
        scroll.setObjectName("main_scroll")
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
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a1c,
                    stop:0.5 #1e1e20,
                    stop:1 #1a1a1c
                );
                color: {MATERIAL_COLORS['text']};
                font-family: {FONTS['fallback']};
            }}
            
            QScrollArea#main_scroll {{
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
# GLASSMORPHISM IMPLEMENTATION
# =============================================================================

class ClickableCard(QFrame):
    """Clickable card that emits signal on click"""
    
    def __init__(self, feature_name: str, parent=None):
        super().__init__(parent)
        self.feature_name = feature_name
        
    def mousePressEvent(self, event):
        """Handle mouse press to navigate to feature"""
        if event.button() == Qt.LeftButton:
            # Navigate up to find the main window
            widget = self
            main_window = None
            
            # Keep going up the parent chain
            while widget:
                widget = widget.parentWidget()
                if widget and hasattr(widget, 'window_manager'):
                    main_window = widget
                    break
            
            if main_window and hasattr(main_window, 'window_manager'):
                # Map feature names to window names
                feature_map = {
                    "Code Editor": "code_editor",
                    "Compare": "comparator",
                    "Benchmark": "benchmarker",
                    "Validate": "validator",
                    "Results & Analytics": "results",
                    "Configuration": "config",
                }
                
                window_name = feature_map.get(self.feature_name)
                if window_name == "config":
                    # Special case for configuration
                    try:
                        from src.app.core.config import ConfigView
                        config_dialog = ConfigView(main_window)
                        config_dialog.exec()
                    except Exception as e:
                        logger.error(f"Error opening config: {e}", exc_info=True)
                elif window_name:
                    try:
                        main_window.window_manager.show_window(window_name)
                    except Exception as e:
                        logger.error(f"Error navigating to {window_name}: {e}", exc_info=True)
        
        super().mousePressEvent(event)

class ClickableCTA(QFrame):
    """Clickable CTA that opens Help Center"""
    
    def mousePressEvent(self, event):
        """Handle mouse press to open Help Center"""
        if event.button() == Qt.LeftButton:
            # Navigate through parent chain to find main window
            current = self.parentWidget()
            while current:
                if hasattr(current, 'parent') and current.parent:
                    main_window = current.parent
                    if hasattr(main_window, 'window_manager'):
                        main_window.window_manager.show_window("help_center")
                        break
                current = current.parentWidget()
        
        super().mousePressEvent(event)

class GlassmorphismDocument(MainWindowDocument):
    """Glassmorphism terminal/glitch aesthetic for main window"""
    
    def build_content(self) -> QWidget:
        """Build glassmorphism content"""
        content = QWidget()
        content.setObjectName("glass_content")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(
            SPACING["lg"],
            SPACING["md"] + SPACING["xs"],
            SPACING["lg"],
            SPACING["lg"]
        )
        layout.setSpacing(0)

        self._add_hero(layout)
        self._add_features_grid(layout)
        self._add_cta(layout)

        # Apply content-specific styling
        content.setStyleSheet(f"""
            QWidget#glass_content {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a1c,
                    stop:0.5 #1e1e20,
                    stop:1 #1a1a1c
                );
                border: {UI['card_border_width']}px solid {MATERIAL_COLORS['accent']};
                border-radius: {UI['content_border_radius']}px;
            }}
        """)

        return content

    def _add_hero(self, layout: QVBoxLayout):
        """Add hero section with title"""
        hero = QWidget()
        hero.setObjectName("hero_section")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setSpacing(SPACING["sm"] - 2)
        hero_layout.setContentsMargins(0, SPACING["sm"] + 2, 0, SPACING["md"] + 2)
        
        # Main title
        title = QLabel(WELCOME_TITLE)
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        title.setFont(self._create_font("hero", QFont.Weight.ExtraBold, mono=True))
        title.setStyleSheet(f"""
            color: {MATERIAL_COLORS['accent']};
            background: transparent;
            letter-spacing: 3px;
        """)
        hero_layout.addWidget(title)
        
        # Glitch subtitle
        glitch = QLabel(WELCOME_SUBTITLE)
        glitch.setAlignment(Qt.AlignCenter)
        glitch.setFont(self._create_font("glitch", mono=True))
        glitch.setStyleSheet(f"""
            color: {MATERIAL_COLORS['success']};
            background: transparent;
            letter-spacing: 2px;
        """)
        hero_layout.addWidget(glitch)
        
        layout.addWidget(hero)

    def _add_features_grid(self, layout: QVBoxLayout):
        """Add features in 2-column grid"""
        grid = QGridLayout()
        grid.setSpacing(SPACING["md"] - 2)
        grid.setContentsMargins(0, 0, 0, 0)
        
        for i, (title, color, features) in enumerate(FEATURE_DATA):
            card = self._create_glass_card(title, color, features)
            row = i // 2
            col = i % 2
            grid.addWidget(card, row, col)
        
        layout.addLayout(grid)

    def _create_glass_card(self, title: str, accent_color: str, features: List[str]) -> QFrame:
        """Create a clickable glassmorphism feature card"""
        card = ClickableCard(title)
        card.setObjectName("glass_card")
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame#glass_card {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {SURFACE_COLORS['surface']},
                    stop:1 rgba(255, 255, 255, 0.01)
                );
                border: 1px solid {SURFACE_COLORS['border']};
                border-left: 3px solid {accent_color};
                border-radius: {UI['card_border_radius']}px;
                padding: {UI['card_padding']}px;
            }}
            QFrame#glass_card:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {SURFACE_COLORS['surface_hover']},
                    stop:1 rgba(255, 255, 255, 0.03)
                );
                border: 1px solid {accent_color}80;
                border-left: 3px solid {accent_color};
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(SPACING["sm"] + 2)
        
        # Title
        title_label = QLabel(title.upper())
        title_label.setFont(self._create_font("card_title", QFont.Weight.Bold, mono=True))
        title_label.setStyleSheet(f"""
            color: {accent_color};
            background: transparent;
            letter-spacing: 1px;
        """)
        title_label.setAttribute(Qt.WA_TransparentForMouseEvents)  # Allow clicks through
        card_layout.addWidget(title_label)
        
        # Separator
        sep = QFrame()
        sep.setFixedHeight(UI["separator_height"])
        sep.setStyleSheet(f"background: {accent_color}40; border: none;")
        sep.setAttribute(Qt.WA_TransparentForMouseEvents)  # Allow clicks through
        card_layout.addWidget(sep)
        
        # Features
        for feature in features:
            feat_label = QLabel(f"• {feature}")
            feat_label.setWordWrap(True)
            feat_label.setFont(self._create_font("feature", mono=False))
            feat_label.setStyleSheet(f"""
                color: {MATERIAL_COLORS['text_dim']};
                background: transparent;
                padding: 2px 0;
            """)
            feat_label.setAttribute(Qt.WA_TransparentForMouseEvents)  # Allow clicks through
            card_layout.addWidget(feat_label)
        
        return card

    def _add_cta(self, layout: QVBoxLayout):
        """Add call-to-action section"""
        layout.addSpacing(SPACING["md"] + 2)
        
        cta = ClickableCTA()
        cta.setObjectName("cta_section")
        cta.setCursor(Qt.PointingHandCursor)
        cta.setStyleSheet(f"""
            QFrame#cta_section {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 150, 199, 0.2),
                    stop:0.5 rgba(247, 37, 133, 0.2),
                    stop:1 rgba(255, 182, 0, 0.2)
                );
                border: {UI['card_border_width']}px solid rgba(247, 37, 133, 0.5);
                border-radius: {UI['cta_border_radius']}px;
                padding: {UI['cta_padding']}px;
            }}
            QFrame#cta_section:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 150, 199, 0.3),
                    stop:0.5 rgba(247, 37, 133, 0.3),
                    stop:1 rgba(255, 182, 0, 0.3)
                );
                border: 2px solid rgba(247, 37, 133, 0.9);
            }}
        """)
        
        cta_layout = QVBoxLayout(cta)
        cta_layout.setSpacing(SPACING["sm"])
        
        # CTA Title
        cta_title = QLabel(CTA_TITLE)
        cta_title.setAlignment(Qt.AlignCenter)
        cta_title.setFont(self._create_font("cta", QFont.Weight.Bold, mono=True))
        cta_title.setStyleSheet(f"""
            color: {MATERIAL_COLORS['accent']};
            background: transparent;
            letter-spacing: 2px;
        """)
        cta_title.setAttribute(Qt.WA_TransparentForMouseEvents)  # Allow clicks through
        cta_layout.addWidget(cta_title)
        
        # CTA Subtitle
        cta_text = QLabel(CTA_SUBTITLE)
        cta_text.setAlignment(Qt.AlignCenter)
        cta_text.setWordWrap(True)
        cta_text.setFont(self._create_font("cta_sub", mono=False))
        cta_text.setStyleSheet(f"""
            color: #C8C8C8;
            background: transparent;
        """)
        cta_text.setAttribute(Qt.WA_TransparentForMouseEvents)  # Allow clicks through
        cta_layout.addWidget(cta_text)
        
        layout.addWidget(cta)

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

def create_main_window_document() -> GlassmorphismDocument:
    """
    Create the main window welcome document with glassmorphism design
    
    Returns:
        Styled document widget
    """
    return GlassmorphismDocument()
