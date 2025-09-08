"""
Main Window Document - Application-specific main window implementation
Uses Qt Document Engine components to create the welcome screen
"""

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from typing import List, Tuple

from .qt_doc_engine import (
    AppTheme, StyleSheet, FontUtils, GradientText, 
    FeatureCard, CallToActionSection
)


class MainWindow(QWidget):
    """Main application window with scrollable content"""
    
    # Application feature data
    FEATURE_DATA: List[Tuple[str, str, List[str]]] = [
        ("📝", "Code Editor", [
            "Advanced multi-tab code editing environment",
            "AI-powered code assistance (Analysis, Fix, Optimize, Document)", 
            "Integrated compiler and execution console",
            "Auto-save and session restoration"
        ]),
        ("🔨", "Compare", [
            "Separate code generators, correct solutions, and test solutions",
            "Customizable comparison testing options",
            "Real-time comparison of outputs", 
            "Detailed test results analysis"
        ]),
        ("⏱️", "Benchmark", [
            "Time limit execution testing",
            "Memory usage monitoring",
            "Multiple test case execution",
            "Performance optimization insights"
        ]),
        ("📊", "Results & Analytics", [
            "Comprehensive test result history",
            "Performance analytics and trends", 
            "Success rate tracking",
            "Detailed test execution reports"
        ]),
        ("⚙️", "Configuration", [
            "Customizable C++ version settings",
            "Workspace folder management",
            "Editor preferences configuration",
            "AI integration settings"
        ])
    ]
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._init_ui()
        self._apply_styles()
        self._setup_entrance_animation()
        
    def _init_ui(self):
        """Initialize the main UI structure"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._create_scroll_container())
        
    def _create_scroll_container(self) -> QScrollArea:
        """Create scrollable container for content"""
        scroll = QScrollArea()
        scroll.setObjectName("main_scroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(self._create_content())
        return scroll
        
    def _create_content(self) -> QWidget:
        """Create the main content widget with all sections"""
        content = QWidget()
        content.setObjectName("content_container")
        layout = QVBoxLayout(content)
        
        padding = AppTheme.LAYOUT['content_padding']
        layout.setContentsMargins(padding, 0, padding, padding)
        layout.setSpacing(0)
        
        # Add all content sections
        self._add_header(layout)
        self._add_features(layout)
        self._add_cta(layout)
        
        return content
        
    def _add_header(self, layout: QVBoxLayout):
        """Add header section with main and subtitle"""
        layout.addSpacing(10)
        
        # Main title
        main_title = GradientText("Welcome to Code Testing Suite!")
        main_title.setAlignment(Qt.AlignCenter)
        main_title.setWordWrap(True)
        main_title.setFont(FontUtils.create('large', QFont.Weight.Bold))
        main_title.setStyleSheet("background: transparent;")
        layout.addWidget(main_title)
        
        layout.addSpacing(5)
        
        # Subtitle
        subtitle = GradientText("Your All-in-One Competitive Programming Companion")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setFont(FontUtils.create('medium'))
        subtitle.setStyleSheet("background: transparent;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(15)
        
    def _add_features(self, layout: QVBoxLayout):
        """Add all feature cards"""
        card_margin = AppTheme.LAYOUT['card_margin']
        for i, (icon, title, features) in enumerate(self.FEATURE_DATA):
            if i > 0:
                layout.addSpacing(card_margin)
            layout.addWidget(FeatureCard(icon, title, features))
            
    def _add_cta(self, layout: QVBoxLayout):
        """Add call-to-action section"""
        layout.addSpacing(AppTheme.LAYOUT['card_margin'])
        layout.addWidget(CallToActionSection())
        
    def _apply_styles(self):
        """Apply consolidated stylesheets"""
        styles = [
            StyleSheet.base(),
            StyleSheet.scrollarea(), 
            StyleSheet.cards()
        ]
        self.setStyleSheet(''.join(styles))
        
    def _setup_entrance_animation(self):
        """Setup fade-in animation on window show"""
        self.setWindowOpacity(0)
        
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(AppTheme.ANIMATION['duration'])
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        
        QTimer.singleShot(50, self.fade_in.start)


def create_qt_main_window() -> MainWindow:
    """Factory function for creating the main window widget"""
    return MainWindow()
