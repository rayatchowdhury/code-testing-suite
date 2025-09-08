"""
Qt Document Engine - Core components and utilities for Qt-based document widgets
Provides reusable theme system, styling utilities, and base components
"""

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from typing import List


class AppTheme:
    """Centralized theme configuration with complete design system"""
    
    # Color palette
    COLORS = {
        'background': "#1e1e1e",
        'surface': "#252525", 
        'surface_hover': "rgba(42, 42, 45, 0.98)",
        'text': "#e0e0e0",
        'primary': "#0096C7", 
        'accent': "#F72585",
        'secondary': "#ffb600",
        'border': "#333333",
        'card_normal': "rgba(37, 37, 37, 0.95)",
        'card_border': "rgba(255, 255, 255, 0.1)",
        'card_border_hover': "rgba(255, 255, 255, 0.25)",
        'cta_border': "rgba(0, 150, 199, 0.3)",
        'cta_border_hover': "rgba(0, 150, 199, 0.5)",
        'scrollbar_bg': "rgba(0, 0, 0, 0.1)",
        'scrollbar_handle': "rgba(255, 255, 255, 0.08)",
        'scrollbar_handle_hover': "rgba(255, 255, 255, 0.12)",
    }
    
    # Typography
    FONTS = {
        'family': "'Segoe UI', system-ui, -apple-system, sans-serif",
        'sizes': {
            'large': 36,        # Main title
            'medium': 22,       # Subtitle 
            'title': 26,        # Card titles
            'description': 19,  # Description text
            'item': 15,         # List items
            'icon': 46,         # Icon size
            'arrow': 14,        # Arrow bullets
        }
    }
    
    # Animation settings
    ANIMATION = {
        'duration': 300,      # 0.3s
        'hover_scale': 1.2,
        'hover_rotation': 5.0,
    }
    
    # Layout dimensions
    LAYOUT = {
        'card_margin': 25,
        'card_spacing': 15, 
        'card_radius': 16,
        'card_padding': 25,
        'content_padding': 40,
        'icon_size': 80,
        'arrow_width': 25,
        'header_spacing': 12,
        'list_indent': 22,
    }


class StyleSheet:
    """Centralized stylesheet generation with reusable components"""
    
    @staticmethod
    def base() -> str:
        """Base application styles"""
        return f"""
            QWidget {{
                background-color: {AppTheme.COLORS['background']};
                color: {AppTheme.COLORS['text']};
                font-family: {AppTheme.FONTS['family']};
            }}
        """
    
    @staticmethod 
    def scrollarea() -> str:
        """Scrollbar and scroll area styles"""
        return f"""
            QScrollArea#main_scroll {{
                border: none;
                background-color: {AppTheme.COLORS['background']};
            }}
            
            QScrollArea QWidget {{
                background-color: transparent;
            }}
            
            QScrollBar:vertical {{
                background: {AppTheme.COLORS['scrollbar_bg']};
                width: 8px;
                border-radius: 4px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {AppTheme.COLORS['scrollbar_handle']};
                border-radius: 4px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {AppTheme.COLORS['scrollbar_handle_hover']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
                width: 0;
            }}
        """
    
    @staticmethod
    def cards() -> str:
        """Card component styles"""
        return f"""
            QWidget#content_container {{
                background-color: {AppTheme.COLORS['background']};
            }}
            
            QFrame#feature_card {{
                background: {AppTheme.COLORS['card_normal']};
                border: 1px solid {AppTheme.COLORS['card_border']};
                border-radius: {AppTheme.LAYOUT['card_radius']}px;
            }}
            
            QFrame#cta_section {{
                background: {AppTheme.COLORS['card_normal']};
                border: 2px solid {AppTheme.COLORS['cta_border']};
                border-radius: {AppTheme.LAYOUT['card_radius']}px;
            }}
            
            QFrame#cta_section:hover {{
                border: 2px solid {AppTheme.COLORS['cta_border_hover']};
                background: {AppTheme.COLORS['surface_hover']};
            }}
        """
    
    @staticmethod
    def list_item() -> str:
        """List item text styling"""
        return f"""
            color: {AppTheme.COLORS['text']};
            padding-left: 5px;
            padding: 2px;
        """
    
    @staticmethod
    def arrow_bullet() -> str:
        """Arrow bullet styling"""
        return f"""
            color: {AppTheme.COLORS['accent']};
            font-weight: bold;
            font-size: {AppTheme.FONTS['sizes']['arrow']}px;
        """
    
    @staticmethod
    def feature_card_hover() -> str:
        """Feature card hover state"""
        return f"""
            QFrame#feature_card {{
                background: {AppTheme.COLORS['surface_hover']};
                border: 1px solid {AppTheme.COLORS['card_border_hover']};
                border-radius: {AppTheme.LAYOUT['card_radius']}px;
            }}
        """
        
    @staticmethod
    def feature_card_normal() -> str:
        """Feature card normal state"""
        return f"""
            QFrame#feature_card {{
                background: {AppTheme.COLORS['card_normal']};
                border: 1px solid {AppTheme.COLORS['card_border']};
                border-radius: {AppTheme.LAYOUT['card_radius']}px;
            }}
        """


class FontUtils:
    """Utility for consistent font creation"""
    
    @staticmethod
    def create(size_key: str, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
        """Create font with size from theme and specified weight"""
        font = QFont("Segoe UI", -1, weight)
        font.setPixelSize(AppTheme.FONTS['sizes'][size_key])
        return font


class GradientText(QLabel):
    """Label with gradient text effect matching original design"""
    
    def __init__(self, text: str = "", parent: QWidget = None):
        super().__init__(text, parent)
        self.gradient_colors = [
            QColor(AppTheme.COLORS['primary']),
            QColor(AppTheme.COLORS['accent'])
        ]
        self.setAttribute(Qt.WA_TranslucentBackground)
        
    def paintEvent(self, event):
        """Custom paint with 135-degree gradient"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create 135-degree gradient
        gradient = QLinearGradient(0, 0, self.width() * 0.7071, self.height() * 0.7071)
        gradient.setColorAt(0, self.gradient_colors[0])
        gradient.setColorAt(1, self.gradient_colors[1])
        
        brush = QBrush(gradient)
        painter.setBrush(brush)
        painter.setPen(QPen(brush, 1))
        painter.setFont(self.font())
        painter.drawText(self.rect(), self.alignment(), self.text())


class AnimatedIcon(QLabel):
    """Icon with hover scale and rotation animations"""
    
    def __init__(self, text: str = "", parent: QWidget = None):
        super().__init__(text, parent)
        self._rotation = 0.0
        self._init_animations()
        self._init_styling()
        
    def _init_animations(self):
        """Initialize animation objects"""
        self.base_size = AppTheme.FONTS['sizes']['icon']
        self.hover_size = int(self.base_size * AppTheme.ANIMATION['hover_scale'])
        
        self.scale_anim = QPropertyAnimation(self, b"font_size")
        self.scale_anim.setDuration(AppTheme.ANIMATION['duration'])
        
        self.rotation_anim = QPropertyAnimation(self, b"rotation_angle")  
        self.rotation_anim.setDuration(AppTheme.ANIMATION['duration'])
        
    def _init_styling(self):
        """Setup basic styling"""
        self.setStyleSheet("background: transparent; border: none;")
        self.setAlignment(Qt.AlignCenter)
        
    def start_hover(self):
        """Begin hover animations"""
        self._animate(self.scale_anim, self.base_size, self.hover_size)
        self._animate(self.rotation_anim, 0.0, AppTheme.ANIMATION['hover_rotation'])
        
    def end_hover(self):
        """End hover animations"""
        self._animate(self.scale_anim, self.hover_size, self.base_size)
        self._animate(self.rotation_anim, AppTheme.ANIMATION['hover_rotation'], 0.0)
        
    def _animate(self, animation: QPropertyAnimation, start: float, end: float):
        """Helper to run animation with values"""
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.start()
    
    def paintEvent(self, event):
        """Custom paint with rotation support"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self._rotation != 0:
            center = self.width() / 2, self.height() / 2
            painter.translate(*center)
            painter.rotate(self._rotation)
            painter.translate(-center[0], -center[1])
        
        painter.setFont(self.font())
        painter.setPen(self.palette().text().color())
        painter.drawText(self.rect(), self.alignment() | Qt.AlignVCenter, self.text())
        
    # Animation properties for QPropertyAnimation
    def _get_font_size(self) -> int:
        return self.font().pixelSize()
        
    def _set_font_size(self, size: int):
        font = self.font()
        font.setPixelSize(size)
        self.setFont(font)
        
    def _get_rotation(self) -> float:
        return self._rotation
        
    def _set_rotation(self, angle: float):
        self._rotation = angle
        self.update()
        
    font_size = Property(int, _get_font_size, _set_font_size)
    rotation_angle = Property(float, _get_rotation, _set_rotation)


class ListItem(QWidget):
    """Individual list item with arrow bullet and hover effect"""
    
    def __init__(self, text: str, parent: QWidget = None):
        super().__init__(parent)
        self._setup_layout(text)
        
    def _setup_layout(self, text: str):
        """Create list item layout with arrow and text"""
        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Arrow bullet
        arrow = QLabel("→")
        arrow.setFixedWidth(AppTheme.LAYOUT['arrow_width'])
        arrow.setStyleSheet(StyleSheet.arrow_bullet())
        arrow.setAlignment(Qt.AlignTop)
        layout.addWidget(arrow)
        
        # Item text with hover effect
        self.text_label = QLabel(text)
        self.text_label.setWordWrap(True)
        self.text_label.setFont(FontUtils.create('item'))
        self.text_label.setStyleSheet(StyleSheet.list_item())
        self.text_label.installEventFilter(self)
        layout.addWidget(self.text_label)
        
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Handle text hover color changes"""
        if obj == self.text_label:
            if event.type() == QEvent.Type.Enter:
                obj.setStyleSheet(StyleSheet.list_item() + 
                                f"color: {AppTheme.COLORS['primary']};")
            elif event.type() == QEvent.Type.Leave:
                obj.setStyleSheet(StyleSheet.list_item())
        return super().eventFilter(obj, event)


class FeatureCard(QFrame):
    """Feature card component with icon, title and feature list"""
    
    def __init__(self, icon: str, title: str, features: List[str], parent: QWidget = None):
        super().__init__(parent)
        self.setObjectName("feature_card")
        self.setAttribute(Qt.WA_Hover, True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self._setup_content(icon, title, features)
        
    def _setup_content(self, icon: str, title: str, features: List[str]):
        """Build card content structure"""
        layout = QVBoxLayout(self)
        margin = AppTheme.LAYOUT['card_padding']
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.setSpacing(AppTheme.LAYOUT['card_spacing'])
        
        # Header with icon and title
        layout.addWidget(self._create_header(icon, title))
        
        # Feature list
        layout.addWidget(self._create_feature_list(features))
        
    def _create_header(self, icon: str, title: str) -> QWidget:
        """Create header section with icon and gradient title"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(AppTheme.LAYOUT['header_spacing'])
        
        # Animated icon
        self.icon = AnimatedIcon(icon)
        icon_size = AppTheme.LAYOUT['icon_size']
        self.icon.setFixedSize(icon_size, icon_size)
        self.icon.setFont(FontUtils.create('icon'))
        layout.addWidget(self.icon)
        
        # Gradient title
        title_label = GradientText(title)
        title_label.setFont(FontUtils.create('title', QFont.Weight.DemiBold))
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        layout.addStretch()
        return header
        
    def _create_feature_list(self, features: List[str]) -> QWidget:
        """Create indented feature list"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(AppTheme.LAYOUT['list_indent'], 0, 0, 0)
        layout.setSpacing(10)
        
        for feature in features:
            layout.addWidget(ListItem(feature))
            
        return container
        
    def enterEvent(self, event):
        """Handle hover enter"""
        self.setStyleSheet(StyleSheet.feature_card_hover())
        self.icon.start_hover()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle hover leave"""
        self.setStyleSheet(StyleSheet.feature_card_normal())
        self.icon.end_hover()
        super().leaveEvent(event)


class CallToActionSection(QFrame):
    """CTA section with centered title, emoji and description"""
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setObjectName("cta_section")
        self._setup_content()
        
    def _setup_content(self):
        """Build CTA section content"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        
        layout.addWidget(self._create_header())
        layout.addWidget(self._create_description())
        
    def _create_header(self) -> QWidget:
        """Create centered header with title and emoji"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        layout.addStretch()
        
        # Gradient title
        title = GradientText("Ready to Code?")
        title.setFont(FontUtils.create('medium', QFont.Weight.DemiBold))
        layout.addWidget(title)
        
        # Animated emoji
        self.emoji = AnimatedIcon("🎯")
        self.emoji.setFont(FontUtils.create('icon'))
        icon_size = AppTheme.LAYOUT['icon_size']
        self.emoji.setFixedSize(icon_size, icon_size)
        layout.addWidget(self.emoji)
        
        layout.addStretch()
        return header
        
    def _create_description(self) -> QLabel:
        """Create centered description text"""
        desc = QLabel("Select any option from the sidebar to begin your coding journey!")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setFont(FontUtils.create('description'))
        desc.setStyleSheet(f"""
            color: {AppTheme.COLORS['text']};
            margin: 15px 0 0 0;
            line-height: 1.6;
        """)
        return desc
        
    def enterEvent(self, event):
        """Start emoji animation on hover"""
        self.emoji.start_hover()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """End emoji animation"""
        self.emoji.end_hover()
        super().leaveEvent(event)
