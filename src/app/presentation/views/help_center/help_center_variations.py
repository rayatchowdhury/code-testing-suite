"""
Help Center Window Variations - 4 Different Design Styles
Each variation offers a unique way to present help documentation
"""

from typing import List
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from src.app.presentation.window_controller.qt_doc_engine import (
    HelpSectionData,
    DocumentWidget,
    AppTheme,
    FontUtils,
    GradientText,
    ListItem,
)


# =============================================================================
# VARIATION 1: TERMINAL DOCS (Matches Main Window V1)
# =============================================================================

class Variation1_TerminalDocs(DocumentWidget):
    """Terminal-style documentation with monospace fonts and glitch aesthetic"""
    
    def __init__(self, title: str, sections: List[HelpSectionData], parent: QWidget = None):
        self.title = title
        self.sections_data = sections
        super().__init__(parent)

    def build_content(self) -> QWidget:
        content = QWidget()
        content.setObjectName("terminal_docs_container")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(0)

        self._add_terminal_header(layout)
        self._add_terminal_sections(layout)

        return content

    def _add_terminal_header(self, layout: QVBoxLayout):
        """Add terminal-style header"""
        header = QWidget()
        h_layout = QVBoxLayout(header)
        h_layout.setSpacing(8)
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        # Terminal prompt indicator
        prompt = QLabel(">> HELP DOCUMENTATION")
        prompt.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        prompt.setStyleSheet("""
            color: #F72585;
            background: transparent;
            letter-spacing: 2px;
        """)
        h_layout.addWidget(prompt)
        
        # Title with monospace font
        title_label = QLabel(self.title.upper())
        title_label.setFont(QFont("Consolas", 22, QFont.Weight.ExtraBold))
        title_label.setWordWrap(True)
        title_label.setStyleSheet("""
            color: #FFFFFF;
            background: transparent;
            letter-spacing: 1px;
        """)
        h_layout.addWidget(title_label)
        
        # Separator line
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background: #F7258540; border: none;")
        h_layout.addWidget(separator)
        
        layout.addWidget(header)
        layout.addSpacing(20)

    def _add_terminal_sections(self, layout: QVBoxLayout):
        """Add sections with terminal styling"""
        for i, section_data in enumerate(self.sections_data):
            if i > 0:
                layout.addSpacing(24)
            
            section = self._create_terminal_section(
                section_data.icon,
                section_data.title,
                section_data.content,
                section_data.items or []
            )
            layout.addWidget(section)

    def _create_terminal_section(self, icon: str, title: str, content: str, items: List[str]) -> QFrame:
        """Create terminal-style section"""
        section = QFrame()
        section.setObjectName("terminal_section")
        section.setStyleSheet(f"""
            QFrame#terminal_section {{
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-left: 3px solid #F72585;
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        
        s_layout = QVBoxLayout(section)
        s_layout.setSpacing(12)
        s_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header: icon + title in monospace
        header = QWidget()
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(10)
        
        # Icon (if not emoji, show ▸)
        icon_text = icon if len(icon) <= 2 else "▸"
        icon_label = QLabel(icon_text)
        icon_label.setFont(QFont("Segoe UI", 18))
        icon_label.setStyleSheet("color: #F72585; background: transparent;")
        h_layout.addWidget(icon_label)
        
        # Title in Consolas uppercase
        title_label = QLabel(title.upper())
        title_label.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            color: #FFFFFF;
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
            content_label.setFont(QFont("Segoe UI", 11))
            content_label.setStyleSheet("color: #B3B3B3; background: transparent; line-height: 1.6;")
            s_layout.addWidget(content_label)
        
        # List items with >> bullets
        if items:
            for item in items:
                item_widget = QWidget()
                item_layout = QHBoxLayout(item_widget)
                item_layout.setContentsMargins(0, 0, 0, 0)
                item_layout.setSpacing(8)
                
                bullet = QLabel(">>")
                bullet.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
                bullet.setStyleSheet("color: #F72585; background: transparent;")
                item_layout.addWidget(bullet)
                
                text = QLabel(item)
                text.setWordWrap(True)
                text.setFont(QFont("Segoe UI", 11))
                text.setStyleSheet("color: #e0e0e0; background: transparent;")
                item_layout.addWidget(text, 1)
                
                s_layout.addWidget(item_widget)
        
        return section

    def get_additional_styles(self) -> str:
        return """
            QWidget#terminal_docs_container {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a1c,
                    stop:1 #1e1e20);
                border: 2px solid #F72585;
                border-radius: 8px;
            }
        """


# =============================================================================
# VARIATION 2: CLEAN MODERN
# =============================================================================

class Variation2_CleanModern(DocumentWidget):
    """Clean, minimal design with plenty of whitespace"""
    
    def __init__(self, title: str, sections: List[HelpSectionData], parent: QWidget = None):
        self.title = title
        self.sections_data = sections
        super().__init__(parent)

    def build_content(self) -> QWidget:
        content = QWidget()
        content.setObjectName("clean_docs_container")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 32, 40, 40)
        layout.setSpacing(0)

        self._add_clean_header(layout)
        self._add_clean_sections(layout)

        return content

    def _add_clean_header(self, layout: QVBoxLayout):
        """Add minimal clean header"""
        # Small subtitle
        subtitle = QLabel("Documentation")
        subtitle.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        subtitle.setStyleSheet("color: #0096C7; background: transparent;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(4)
        
        # Large title
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        title_label.setWordWrap(True)
        title_label.setStyleSheet("color: #FFFFFF; background: transparent;")
        layout.addWidget(title_label)
        
        layout.addSpacing(32)

    def _add_clean_sections(self, layout: QVBoxLayout):
        """Add sections with clean spacing"""
        for i, section_data in enumerate(self.sections_data):
            if i > 0:
                layout.addSpacing(40)
            
            section = self._create_clean_section(
                section_data.icon,
                section_data.title,
                section_data.content,
                section_data.items or []
            )
            layout.addWidget(section)

    def _create_clean_section(self, icon: str, title: str, content: str, items: List[str]) -> QWidget:
        """Create clean minimal section"""
        section = QWidget()
        s_layout = QVBoxLayout(section)
        s_layout.setSpacing(16)
        s_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with icon and title
        header = QWidget()
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(12)
        
        # Large icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 28))
        icon_label.setStyleSheet("background: transparent;")
        h_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 20, QFont.Weight.DemiBold))
        title_label.setStyleSheet("color: #FFFFFF; background: transparent;")
        h_layout.addWidget(title_label)
        h_layout.addStretch()
        
        s_layout.addWidget(header)
        
        # Content
        if content:
            content_label = QLabel(content)
            content_label.setWordWrap(True)
            content_label.setFont(QFont("Segoe UI", 13))
            content_label.setStyleSheet("""
                color: #B3B3B3;
                background: transparent;
                line-height: 1.8;
                padding-left: 52px;
            """)
            s_layout.addWidget(content_label)
        
        # List items
        if items:
            list_container = QWidget()
            list_layout = QVBoxLayout(list_container)
            list_layout.setContentsMargins(52, 0, 0, 0)
            list_layout.setSpacing(10)
            
            for item in items:
                item_widget = QWidget()
                item_l = QHBoxLayout(item_widget)
                item_l.setContentsMargins(0, 0, 0, 0)
                item_l.setSpacing(12)
                
                # Circle bullet
                bullet = QLabel("●")
                bullet.setFont(QFont("Segoe UI", 8))
                bullet.setStyleSheet("color: #0096C7; background: transparent;")
                item_l.addWidget(bullet)
                
                text = QLabel(item)
                text.setWordWrap(True)
                text.setFont(QFont("Segoe UI", 13))
                text.setStyleSheet("color: #e0e0e0; background: transparent;")
                item_l.addWidget(text, 1)
                
                list_layout.addWidget(item_widget)
            
            s_layout.addWidget(list_container)
        
        return section

    def get_additional_styles(self) -> str:
        return """
            QWidget#clean_docs_container {
                background: #1e1e1e;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }
        """


# =============================================================================
# VARIATION 3: CARD STYLE
# =============================================================================

class Variation3_CardStyle(DocumentWidget):
    """Each section as a distinct card with colored accents"""
    
    SECTION_COLORS = ["#0096C7", "#F72585", "#ffb600", "#4CAF50", "#00D9FF", "#B565D8"]
    
    def __init__(self, title: str, sections: List[HelpSectionData], parent: QWidget = None):
        self.title = title
        self.sections_data = sections
        super().__init__(parent)

    def build_content(self) -> QWidget:
        content = QWidget()
        content.setObjectName("card_docs_container")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(0)

        self._add_card_header(layout)
        self._add_card_sections(layout)

        return content

    def _add_card_header(self, layout: QVBoxLayout):
        """Add header with gradient title"""
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 28, QFont.Weight.ExtraBold))
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            color: #FFFFFF;
            background: transparent;
            padding: 12px;
        """)
        layout.addWidget(title_label)
        layout.addSpacing(24)

    def _add_card_sections(self, layout: QVBoxLayout):
        """Add sections as cards"""
        for i, section_data in enumerate(self.sections_data):
            if i > 0:
                layout.addSpacing(16)
            
            color = self.SECTION_COLORS[i % len(self.SECTION_COLORS)]
            card = self._create_card(
                section_data.icon,
                section_data.title,
                section_data.content,
                section_data.items or [],
                color
            )
            layout.addWidget(card)

    def _create_card(self, icon: str, title: str, content: str, items: List[str], color: str) -> QFrame:
        """Create a card section"""
        card = QFrame()
        card.setObjectName("help_card")
        card.setStyleSheet(f"""
            QFrame#help_card {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 30, 33, 0.9),
                    stop:1 rgba(40, 40, 43, 0.9));
                border: 2px solid {color}60;
                border-radius: 12px;
                padding: 20px;
            }}
            QFrame#help_card:hover {{
                border: 2px solid {color};
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(35, 35, 38, 0.95),
                    stop:1 rgba(45, 45, 48, 0.95));
            }}
        """)
        card.setCursor(Qt.PointingHandCursor)
        
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(14)
        
        # Header
        header = QWidget()
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(12)
        
        # Icon box
        icon_box = QLabel(icon)
        icon_box.setFixedSize(48, 48)
        icon_box.setAlignment(Qt.AlignCenter)
        icon_box.setFont(QFont("Segoe UI", 22))
        icon_box.setStyleSheet(f"""
            background: transparent;
            border: 2px solid {color};
            border-radius: 8px;
            color: {color};
        """)
        h_layout.addWidget(icon_box)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {color}; background: transparent;")
        h_layout.addWidget(title_label)
        h_layout.addStretch()
        
        c_layout.addWidget(header)
        
        # Content
        if content:
            content_label = QLabel(content)
            content_label.setWordWrap(True)
            content_label.setFont(QFont("Segoe UI", 12))
            content_label.setStyleSheet("color: #CCCCCC; background: transparent; line-height: 1.6;")
            c_layout.addWidget(content_label)
        
        # Items
        if items:
            for item in items:
                item_widget = QWidget()
                item_l = QHBoxLayout(item_widget)
                item_l.setContentsMargins(0, 0, 0, 0)
                item_l.setSpacing(10)
                
                bullet = QLabel("▸")
                bullet.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
                bullet.setStyleSheet(f"color: {color}; background: transparent;")
                item_l.addWidget(bullet)
                
                text = QLabel(item)
                text.setWordWrap(True)
                text.setFont(QFont("Segoe UI", 12))
                text.setStyleSheet("color: #e0e0e0; background: transparent;")
                item_l.addWidget(text, 1)
                
                c_layout.addWidget(item_widget)
        
        return card

    def get_additional_styles(self) -> str:
        return """
            QWidget#card_docs_container {
                background: #1a1a1c;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 10px;
            }
        """


# =============================================================================
# VARIATION 4: DEVELOPER DOCS (Code-style)
# =============================================================================

class Variation4_DeveloperDocs(DocumentWidget):
    """Code documentation style with syntax-highlighted appearance"""
    
    def __init__(self, title: str, sections: List[HelpSectionData], parent: QWidget = None):
        self.title = title
        self.sections_data = sections
        super().__init__(parent)

    def build_content(self) -> QWidget:
        content = QWidget()
        content.setObjectName("dev_docs_container")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)

        self._add_dev_header(layout)
        self._add_dev_sections(layout)

        return content

    def _add_dev_header(self, layout: QVBoxLayout):
        """Add code-style header"""
        # Comment-style title
        header = QWidget()
        h_layout = QVBoxLayout(header)
        h_layout.setSpacing(4)
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        comment_line = QLabel("/**")
        comment_line.setFont(QFont("Consolas", 11))
        comment_line.setStyleSheet("color: #6A9955; background: transparent;")
        h_layout.addWidget(comment_line)
        
        title_line = QLabel(f" * {self.title}")
        title_line.setFont(QFont("Consolas", 18, QFont.Weight.Bold))
        title_line.setWordWrap(True)
        title_line.setStyleSheet("color: #4EC9B0; background: transparent;")
        h_layout.addWidget(title_line)
        
        desc = QLabel(" * Help Documentation")
        desc.setFont(QFont("Consolas", 11))
        desc.setStyleSheet("color: #6A9955; background: transparent;")
        h_layout.addWidget(desc)
        
        close_comment = QLabel(" */")
        close_comment.setFont(QFont("Consolas", 11))
        close_comment.setStyleSheet("color: #6A9955; background: transparent;")
        h_layout.addWidget(close_comment)
        
        layout.addWidget(header)
        layout.addSpacing(20)

    def _add_dev_sections(self, layout: QVBoxLayout):
        """Add code-style sections"""
        for i, section_data in enumerate(self.sections_data):
            if i > 0:
                layout.addSpacing(20)
            
            section = self._create_dev_section(
                section_data.icon,
                section_data.title,
                section_data.content,
                section_data.items or [],
                i
            )
            layout.addWidget(section)

    def _create_dev_section(self, icon: str, title: str, content: str, items: List[str], index: int) -> QFrame:
        """Create developer docs style section"""
        section = QFrame()
        section.setObjectName("dev_section")
        section.setStyleSheet("""
            QFrame#dev_section {
                background: rgba(30, 30, 30, 0.8);
                border: 1px solid #3C3C3C;
                border-left: 4px solid #4EC9B0;
                border-radius: 4px;
                padding: 14px;
            }
        """)
        
        s_layout = QVBoxLayout(section)
        s_layout.setSpacing(10)
        s_layout.setContentsMargins(0, 0, 0, 0)
        
        # Function-style header
        header = QLabel(f"function section_{index + 1}() {{  // {title}")
        header.setFont(QFont("Consolas", 13, QFont.Weight.Bold))
        header.setStyleSheet("color: #DCDCAA; background: transparent;")
        s_layout.addWidget(header)
        
        # Content as comment
        if content:
            content_label = QLabel(f"  /* {content} */")
            content_label.setWordWrap(True)
            content_label.setFont(QFont("Consolas", 10))
            content_label.setStyleSheet("color: #6A9955; background: transparent; line-height: 1.6;")
            s_layout.addWidget(content_label)
        
        # Items as code lines
        if items:
            for item in items:
                item_label = QLabel(f"  ✓ {item}")
                item_label.setWordWrap(True)
                item_label.setFont(QFont("Consolas", 10))
                item_label.setStyleSheet("color: #CE9178; background: transparent;")
                s_layout.addWidget(item_label)
        
        # Closing brace
        close = QLabel("}")
        close.setFont(QFont("Consolas", 13, QFont.Weight.Bold))
        close.setStyleSheet("color: #DCDCAA; background: transparent;")
        s_layout.addWidget(close)
        
        return section

    def get_additional_styles(self) -> str:
        return """
            QWidget#dev_docs_container {
                background: #1E1E1E;
                border: 1px solid #3C3C3C;
                border-radius: 6px;
            }
        """


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_help_variation(variation_number: int, title: str, sections: List[HelpSectionData]):
    """
    Create a help center variation by number
    
    Args:
        variation_number: 1-4
        title: Document title
        sections: List of HelpSectionData
        
    Returns:
        DocumentWidget instance
    """
    variations = {
        1: Variation1_TerminalDocs,
        2: Variation2_CleanModern,
        3: Variation3_CardStyle,
        4: Variation4_DeveloperDocs,
    }
    
    variation_class = variations.get(variation_number, Variation1_TerminalDocs)
    return variation_class(title, sections)
