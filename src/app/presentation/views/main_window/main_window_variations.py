"""
Main Window Content - Primary Glassmorphism Terminal/Glitch Design
Features tech-focused aesthetic with Consolas monospace typography and terminal-style indicators
"""

from typing import List, Tuple
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from src.app.presentation.window_controller.qt_doc_engine import (
    AppTheme,
    FontUtils,
    GradientText,
    DocumentWidget,
    StyleSheet,
)


# =============================================================================
# VARIATION 1: GLASSMORPHISM (Original Enhanced Design)
# =============================================================================

class Variation1_Glassmorphism(DocumentWidget):
    """Enhanced glassmorphism with gradient cards"""
    
    FEATURE_DATA: List[Tuple[str, str, str, List[str]]] = [
        (
            "📝", "Code Editor", "#0096C7",
            [
                "Advanced multi-tab code editing environment",
                "AI-powered code assistance (Analysis, Fix, Optimize, Document)",
                "Integrated compiler and execution console",
                "Auto-save and session restoration",
            ],
        ),
        (
            "🔨", "Compare", "#F72585",
            [
                "Separate code generators, correct solutions, and test solutions",
                "Customizable comparison testing options",
                "Real-time comparison of outputs",
                "Detailed test results analysis",
            ],
        ),
        (
            "⏱️", "Benchmark", "#ffb600",
            [
                "Time limit execution testing",
                "Memory usage monitoring",
                "Multiple test case execution",
                "Performance optimization insights",
            ],
        ),
        (
            "✅", "Validate", "#4CAF50",
            [
                "Automated code validation and testing",
                "Custom validation rules and constraints",
                "Input/output format verification",
                "Edge case detection and testing",
            ],
        ),
        (
            "📊", "Results & Analytics", "#00D9FF",
            [
                "Comprehensive test result history",
                "Performance analytics and trends",
                "Success rate tracking",
                "Detailed test execution reports",
            ],
        ),
        (
            "⚙️", "Configuration", "#B565D8",
            [
                "Customizable C++ version settings",
                "Workspace folder management",
                "Editor preferences configuration",
                "AI integration settings",
            ],
        ),
    ]

    def build_content(self) -> QWidget:
        content = QWidget()
        content.setObjectName("content_container")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(25, 20, 25, 25)
        layout.setSpacing(0)

        self._add_hero(layout)
        self._add_features_grid(layout)
        self._add_cta_enhanced(layout)

        return content

    def _add_hero(self, layout: QVBoxLayout):
        hero = QWidget()
        hero.setObjectName("hero_section")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setSpacing(6)
        hero_layout.setContentsMargins(0, 10, 0, 18)
        
        # Main title with glitch effect (layered approach)
        title_container = QWidget()
        title_container.setStyleSheet("background: transparent;")
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        title = QLabel("CODE TESTING SUITE")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        title.setFont(QFont("Consolas", 26, QFont.Weight.ExtraBold))
        title.setStyleSheet("""
            color: #F72585;
            background: transparent;
            letter-spacing: 3px;
        """)
        title_layout.addWidget(title)
        hero_layout.addWidget(title_container)
        
        # Glitch line
        glitch = QLabel(">> SYSTEM READY")
        glitch.setAlignment(Qt.AlignCenter)
        glitch.setFont(QFont("Consolas", 11))
        glitch.setStyleSheet("color: #4CAF50; background: transparent; letter-spacing: 2px;")
        hero_layout.addWidget(glitch)
        
        layout.addWidget(hero)

    def _add_features_grid(self, layout: QVBoxLayout):
        grid = QGridLayout()
        grid.setSpacing(14)
        grid.setContentsMargins(0, 0, 0, 0)
        
        for i, (icon, title, color, features) in enumerate(self.FEATURE_DATA):
            card = self._create_glass_card(icon, title, color, features)
            row = i // 2
            col = i % 2
            grid.addWidget(card, row, col)
        
        layout.addLayout(grid)

    def _create_glass_card(self, icon: str, title: str, accent_color: str, features: List[str]) -> QFrame:
        card = QFrame()
        card.setObjectName("glass_card")
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame#glass_card {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.08),
                    stop:1 rgba(255, 255, 255, 0.03));
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-left: 3px solid {accent_color};
                border-radius: 10px;
                padding: 14px;
            }}
            QFrame#glass_card:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.12),
                    stop:1 rgba(255, 255, 255, 0.06));
                border: 1px solid {accent_color}80;
                border-left: 3px solid {accent_color};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        # Title only (no icon)
        title_label = QLabel(title.upper())
        title_label.setFont(QFont("Consolas", 15, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {accent_color}; background: transparent; letter-spacing: 1px;")
        layout.addWidget(title_label)
        
        # Separator line
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {accent_color}40; border: none;")
        layout.addWidget(sep)
        
        # Features
        for feature in features:
            feat_label = QLabel(f"• {feature}")
            feat_label.setWordWrap(True)
            feat_label.setFont(QFont("Segoe UI", 11))
            feat_label.setStyleSheet("color: #d8d8d8; background: transparent; padding: 2px 0;")
            layout.addWidget(feat_label)
        
        return card

    def _add_cta_enhanced(self, layout: QVBoxLayout):
        layout.addSpacing(18)
        
        cta = QFrame()
        cta.setObjectName("cta_enhanced")
        cta.setCursor(Qt.PointingHandCursor)
        cta.setStyleSheet("""
            QFrame#cta_enhanced {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 150, 199, 0.2),
                    stop:0.5 rgba(247, 37, 133, 0.2),
                    stop:1 rgba(255, 182, 0, 0.2));
                border: 2px solid rgba(247, 37, 133, 0.5);
                border-radius: 12px;
                padding: 18px;
            }
            QFrame#cta_enhanced:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 150, 199, 0.3),
                    stop:0.5 rgba(247, 37, 133, 0.3),
                    stop:1 rgba(255, 182, 0, 0.3));
                border: 2px solid rgba(247, 37, 133, 0.9);
            }
        """)
        
        cta_layout = QVBoxLayout(cta)
        cta_layout.setSpacing(8)
        
        cta_title = QLabel(">> SELECT FEATURE TO BEGIN")
        cta_title.setAlignment(Qt.AlignCenter)
        cta_title.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        cta_title.setStyleSheet("color: #F72585; background: transparent; letter-spacing: 2px;")
        cta_layout.addWidget(cta_title)
        
        cta_text = QLabel("Choose any tool from the sidebar to start")
        cta_text.setAlignment(Qt.AlignCenter)
        cta_text.setWordWrap(True)
        cta_text.setFont(QFont("Segoe UI", 11))
        cta_text.setStyleSheet("color: #C8C8C8; background: transparent;")
        cta_layout.addWidget(cta_text)
        
        layout.addWidget(cta)

    def get_additional_styles(self) -> str:
        return """
            QWidget#content_container {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a1c,
                    stop:0.5 #1e1e20,
                    stop:1 #1a1a1c);
                border: 2px solid #F72585;
                border-radius: 8px;
            }
        """


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_variation(variation_number: int = 1):
    """
    Create a main window variation by number
    
    Args:
        variation_number: Always returns Variation 1 (primary design)
        
    Returns:
        DocumentWidget instance
    """
    return Variation1_Glassmorphism()

