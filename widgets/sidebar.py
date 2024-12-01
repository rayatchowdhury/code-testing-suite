from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QSpacerItem, 
                             QSizePolicy, QLabel, QFrame, QScrollArea, QComboBox,
                             QSpinBox, QSlider)
from PySide6.QtCore import Qt, Signal
from styles.style import SIDEBAR_STYLE, SIDEBAR_BUTTON_STYLE

class SidebarSection(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar_section")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 12)
        layout.setSpacing(6)
        
        # Add section title
        if title:
            title_label = QLabel(title)
            title_label.setObjectName("section_title")
            layout.addWidget(title_label)
    
    def add_widget(self, widget):
        self.layout().addWidget(widget)

class Sidebar(QWidget):
    button_clicked = Signal(str)
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setStyleSheet(SIDEBAR_STYLE)
        # Remove setFixedWidth and set minimum/maximum instead
        self.setMinimumWidth(200)
        self.setMaximumWidth(400)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add title if provided
        if title:
            title_label = QLabel(title)
            title_label.setObjectName("sidebar_title")
            main_layout.addWidget(title_label)
        
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Enhance scroll area
        scroll.setObjectName("sidebar_scroll")
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QWidget#sidebar_content {
                background-color: transparent;
            }
        """)
        
        # Create content widget
        self.content = QWidget()
        self.content.setObjectName("sidebar_content")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(2)
        
        scroll.setWidget(self.content)
        main_layout.addWidget(scroll)
        
        # Store back button reference
        self.back_button = None
    
    def add_section(self, title=None):
        section = SidebarSection(title)
        self.content_layout.addWidget(section)
        return section
    
    def add_button(self, text, section=None):
        btn = QPushButton(text)
        btn.setObjectName("sidebar_button")
        btn.clicked.connect(lambda: self.button_clicked.emit(text))
        
        if section:
            section.add_widget(btn)
        else:
            self.content_layout.addWidget(btn)
        return btn
    
    def add_spacer(self):
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.content_layout.addItem(spacer)
    
    def add_back_button(self):
        self.add_spacer()
        self.back_button = self.add_button("Back")
        self.back_button.setObjectName("back_button")