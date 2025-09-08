"""
Help Center Document Engine - Specialized document components for help content
Extends Qt Document Engine for help-specific layouts and components
"""

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from typing import List, Tuple

from ..qt_doc_engine import (
    AppTheme, StyleSheet, FontUtils, GradientText, 
    FeatureCard, ListItem
)


class HelpTheme(AppTheme):
    """Extended theme for help center documents"""
    
    # Override some layout values for help content
    LAYOUT = {
        **AppTheme.LAYOUT,
        'section_spacing': 30,      # More spacing between sections
        'content_padding': 30,      # Slightly less padding for help content
        'header_bottom_margin': 20, # Space below main header
    }


class HelpSection(QFrame):
    """A help section with icon, title and content"""
    
    def __init__(self, icon: str, title: str, content: str = "", items: List[str] = None, parent: QWidget = None):
        super().__init__(parent)
        self.setObjectName("help_section")
        self._setup_content(icon, title, content, items or [])
        
    def _setup_content(self, icon: str, title: str, content: str, items: List[str]):
        """Build section content"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Header with icon and title
        layout.addWidget(self._create_header(icon, title))
        
        # Content paragraph if provided
        if content:
            layout.addWidget(self._create_content(content))
            
        # List items if provided
        if items:
            layout.addWidget(self._create_item_list(items))
            
    def _create_header(self, icon: str, title: str) -> QWidget:
        """Create section header"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(FontUtils.create('title'))
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Gradient title
        title_label = GradientText(title)
        title_label.setFont(FontUtils.create('title', QFont.Weight.DemiBold))
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        layout.addStretch()
        return header
        
    def _create_content(self, content: str) -> QLabel:
        """Create content paragraph"""
        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setFont(FontUtils.create('description'))
        content_label.setStyleSheet(f"""
            color: {AppTheme.COLORS['text']};
            line-height: 1.6;
            margin: 10px 0;
        """)
        return content_label
        
    def _create_item_list(self, items: List[str]) -> QWidget:
        """Create indented item list"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 0, 0, 0)  # Indent for help content
        layout.setSpacing(8)
        
        for item in items:
            layout.addWidget(ListItem(item))
            
        return container


class HelpDocument(QWidget):
    """Base class for help center documents"""
    
    def __init__(self, title: str, sections: List[Tuple], parent: QWidget = None):
        """
        Initialize help document
        
        Args:
            title: Main document title
            sections: List of (icon, title, content, items) tuples
        """
        super().__init__(parent)
        self.title = title
        self.sections_data = sections
        self._init_ui()
        self._apply_styles()
        self._setup_entrance_animation()
        
    def _init_ui(self):
        """Initialize UI structure"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._create_scroll_container())
        
    def _create_scroll_container(self) -> QScrollArea:
        """Create scrollable container"""
        scroll = QScrollArea()
        scroll.setObjectName("main_scroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(self._create_content())
        return scroll
        
    def _create_content(self) -> QWidget:
        """Create main content widget"""
        content = QWidget()
        content.setObjectName("content_container")
        layout = QVBoxLayout(content)
        
        padding = HelpTheme.LAYOUT['content_padding']
        layout.setContentsMargins(padding, 20, padding, padding)
        layout.setSpacing(0)
        
        # Add title
        self._add_title(layout)
        
        # Add sections
        self._add_sections(layout)
        
        return content
        
    def _add_title(self, layout: QVBoxLayout):
        """Add main document title"""
        title_label = GradientText(self.title)
        title_label.setAlignment(Qt.AlignLeft)  # Left-align for help docs
        title_label.setWordWrap(True)
        title_label.setFont(FontUtils.create('large', QFont.Weight.Bold))
        title_label.setStyleSheet("background: transparent;")
        layout.addWidget(title_label)
        
        layout.addSpacing(HelpTheme.LAYOUT['header_bottom_margin'])
        
    def _add_sections(self, layout: QVBoxLayout):
        """Add all help sections"""
        section_spacing = HelpTheme.LAYOUT['section_spacing']
        
        for i, section_data in enumerate(self.sections_data):
            if i > 0:
                layout.addSpacing(section_spacing)
                
            # Handle different tuple lengths
            if len(section_data) == 3:
                icon, title, content = section_data
                items = []
            elif len(section_data) == 4:
                icon, title, content, items = section_data
            else:
                continue  # Skip malformed data
                
            section = HelpSection(icon, title, content, items)
            layout.addWidget(section)
            
    def _apply_styles(self):
        """Apply document styles"""
        styles = [
            StyleSheet.base(),
            StyleSheet.scrollarea(),
            self._get_help_styles()
        ]
        self.setStyleSheet(''.join(styles))
        
    def _get_help_styles(self) -> str:
        """Help-specific styles"""
        return f"""
            QWidget#content_container {{
                background-color: {AppTheme.COLORS['background']};
            }}
            
            QFrame#help_section {{
                background: transparent;
                border: none;
                margin-bottom: 10px;
            }}
        """
        
    def _setup_entrance_animation(self):
        """Setup fade-in animation"""
        self.setWindowOpacity(0)
        
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(AppTheme.ANIMATION['duration'])
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        
        QTimer.singleShot(50, self.fade_in.start)
