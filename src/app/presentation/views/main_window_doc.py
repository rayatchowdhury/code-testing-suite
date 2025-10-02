"""
Main Window Document - Application-specific main window implementation
All components now imported from unified qt_doc_engine
"""

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from typing import List, Tuple

from .qt_doc_engine import (
    AppTheme, StyleSheet, FontUtils, GradientText, 
    FeatureCard, CallToActionSection, DocumentWidget
)


class MainWindow(DocumentWidget):
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
    
    def build_content(self) -> QWidget:
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
        
    def get_additional_styles(self) -> str:
        """Get additional stylesheet for main window"""
        return StyleSheet.cards()


def create_qt_main_window() -> MainWindow:
    """Factory function for creating the main window widget"""
    return MainWindow()
