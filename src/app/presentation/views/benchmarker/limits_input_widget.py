from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QGroupBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator
from src.app.presentation.styles.style import MATERIAL_COLORS

class LimitsInputWidget(QWidget):
    timeLimitChanged = Signal(int)  # Time limit in ms
    memoryLimitChanged = Signal(int)  # Memory limit in MB
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """Setup the UI layout - clean and simple"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 4, 12, 4)  # Match sidebar button margins exactly (4px 12px)
        main_layout.setSpacing(6)  # Reduced spacing from 8 to 6
        
        # Horizontal container for time and memory inputs
        inputs_layout = QHBoxLayout()
        inputs_layout.setSpacing(8)  # Reduced spacing between sections
        
        # Time limit section with titled border
        self.time_group = QGroupBox("Time")
        time_container = QVBoxLayout(self.time_group)
        time_container.setSpacing(4)
        time_container.setContentsMargins(8, 12, 8, 8)
        
        self.time_input = QLineEdit()
        self.time_input.setText("1000")
        self.time_input.setValidator(QIntValidator(10, 60000))
        self.time_input.setPlaceholderText("1000")
        # Remove fixed width to allow stretching
        
        time_container.addWidget(self.time_input)
        
        # Simple vertical divider aligned with input fields only
        divider = QWidget()
        divider.setFixedWidth(1)
        divider.setFixedHeight(50)  # Adjusted height for group boxes
        divider.setContentsMargins(0, 8, 0, 0)  # Align with group box content
        
        # Memory limit section with titled border
        self.memory_group = QGroupBox("Memory")
        memory_container = QVBoxLayout(self.memory_group)
        memory_container.setSpacing(4)
        memory_container.setContentsMargins(8, 12, 8, 8)
        
        self.memory_input = QLineEdit()
        self.memory_input.setText("256")
        self.memory_input.setValidator(QIntValidator(1, 8192))
        self.memory_input.setPlaceholderText("256")
        # Remove fixed width to allow stretching
        
        memory_container.addWidget(self.memory_input)
        
        # Add to horizontal layout
        inputs_layout.addWidget(self.time_group)
        inputs_layout.addWidget(divider)
        inputs_layout.addWidget(self.memory_group)
        
        # Add to main layout
        main_layout.addLayout(inputs_layout)
        
        # Store divider for styling
        self.divider = divider
        
        # Connect signals
        self.time_input.textChanged.connect(self._on_time_changed)
        self.memory_input.textChanged.connect(self._on_memory_changed)
        
    def setup_styles(self):
        """Apply consistent styling based on app design patterns"""
        
        # Main widget - subtle background matching sidebar sections
        self.setStyleSheet(f"""
            LimitsInputWidget {{
                background: transparent;
            }}
        """)
        
        # Group box styling - modern titled borders with reduced margin
        group_style = f"""
            QGroupBox {{
                font-size: 11px;
                font-weight: 600;
                color: {MATERIAL_COLORS['primary']};
                border: 1px solid {MATERIAL_COLORS['outline']};
                border-radius: 8px;
                margin: 4px 0px;
                padding-top: 6px;
                background: transparent;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0px 6px 0px 6px;
                color: {MATERIAL_COLORS['primary']};
                font-weight: 600;
            }}
        """
        self.time_group.setStyleSheet(group_style)
        self.memory_group.setStyleSheet(group_style)
        
        # Input fields - following config styles pattern with more rounded corners
        input_style = f"""
            QLineEdit {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                           stop:0 rgba(20, 24, 28, 0.8),
                           stop:1 rgba(14, 17, 20, 0.8));
                border: 1px solid {MATERIAL_COLORS['outline']};
                border-radius: 12px;
                color: {MATERIAL_COLORS['text_primary']};
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 500;
                selection-background-color: {MATERIAL_COLORS['primary']}40;
                selection-color: {MATERIAL_COLORS['on_primary']};
            }}
            
            QLineEdit:hover {{
                border: 1px solid {MATERIAL_COLORS['primary']};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                           stop:0 {MATERIAL_COLORS['primary']}10,
                           stop:1 rgba(255, 255, 255, 0.08));
            }}
            
            QLineEdit:focus {{
                border: 2px solid {MATERIAL_COLORS['primary']};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                           stop:0 {MATERIAL_COLORS['primary']}15,
                           stop:1 rgba(255, 255, 255, 0.08));
                outline: none;
            }}
        """
        self.time_input.setStyleSheet(input_style)
        self.memory_input.setStyleSheet(input_style)
        
        # Simple divider - following sidebar divider pattern
        self.divider.setStyleSheet(f"""
            QWidget {{
                background-color: {MATERIAL_COLORS['outline_variant']};
            }}
        """)
    
    def _on_time_changed(self, text):
        """Handle time input change with validation feedback"""
        try:
            if text and text.isdigit():
                value = int(text)
                if 10 <= value <= 60000:
                    self.timeLimitChanged.emit(value)
        except ValueError:
            pass
    
    def _on_memory_changed(self, text):
        """Handle memory input change with validation feedback"""
        try:
            if text and text.isdigit():
                value = int(text)
                if 1 <= value <= 8192:
                    self.memoryLimitChanged.emit(value)
        except ValueError:
            pass
    
    def get_time_limit(self):
        """Get current time limit value"""
        try:
            return int(self.time_input.text()) if self.time_input.text() else 1000
        except ValueError:
            return 1000
    
    def get_memory_limit(self):
        """Get current memory limit value"""
        try:
            return int(self.memory_input.text()) if self.memory_input.text() else 256
        except ValueError:
            return 256
    
    def set_time_limit(self, value):
        """Set time limit value"""
        self.time_input.setText(str(value))
    
    def set_memory_limit(self, value):
        """Set memory limit value"""
        self.memory_input.setText(str(value))
