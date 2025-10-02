"""
Detail view dialogs for test cards.

Shows detailed information about a specific test when a card is clicked.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTextEdit, QFrame)
from PySide6.QtCore import Qt
from src.app.presentation.styles.style import MATERIAL_COLORS


class TestDetailDialog(QDialog):
    """
    Base detail view dialog for test cards.
    
    Shows test number, status, time, memory, and test-specific content.
    """
    
    def __init__(self, test_number: int, passed: bool, time: float, memory: float, parent=None):
        """
        Initialize test detail dialog.
        
        Args:
            test_number: Test case number
            passed: Whether test passed
            time: Execution time in seconds
            memory: Memory usage in MB
            parent: Parent widget
        """
        super().__init__(parent)
        self.test_number = test_number
        self.passed = passed
        self.time = time
        self.memory = memory
        
        self.setWindowTitle(f"Test #{test_number} Details")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        self._setup_ui()
        self._apply_styling()
        
    def _setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header section
        header = self._create_header()
        layout.addWidget(header)
        
        # Metrics section
        metrics = self._create_metrics()
        layout.addWidget(metrics)
        
        # Content section (override in subclasses)
        content = self._create_content()
        if content:
            layout.addWidget(content, stretch=1)
        
        # Button section
        buttons = self._create_buttons()
        layout.addWidget(buttons)
        
    def _create_header(self) -> QFrame:
        """Create header with test number and status"""
        header = QFrame()
        header.setFrameShape(QFrame.StyledPanel)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(12, 12, 12, 12)
        
        test_label = QLabel(f"Test #{self.test_number}")
        test_label.setStyleSheet("""
            font-weight: bold;
            font-size: 18px;
        """)
        
        status_text = "✓ Passed" if self.passed else "✗ Failed"
        status_color = MATERIAL_COLORS['primary'] if self.passed else MATERIAL_COLORS['error']
        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"""
            color: {status_color};
            font-weight: bold;
            font-size: 18px;
        """)
        
        layout.addWidget(test_label)
        layout.addStretch()
        layout.addWidget(status_label)
        
        # Style header
        bg_color = MATERIAL_COLORS.get('primary_container', MATERIAL_COLORS['surface_variant']) if self.passed else MATERIAL_COLORS['error_container']
        header.setStyleSheet(f"""
            QFrame {{
                background: {bg_color};
                border-radius: 8px;
            }}
        """)
        
        return header
        
    def _create_metrics(self) -> QFrame:
        """Create metrics panel with time and memory"""
        metrics = QFrame()
        layout = QHBoxLayout(metrics)
        layout.setContentsMargins(12, 8, 12, 8)
        
        time_label = QLabel(f"⏱️ Time: {self.time:.3f}s")
        memory_label = QLabel(f"💾 Memory: {self.memory:.1f} MB")
        
        for label in [time_label, memory_label]:
            label.setStyleSheet("""
                font-size: 14px;
                font-weight: 500;
            """)
            layout.addWidget(label)
        
        layout.addStretch()
        
        metrics.setStyleSheet(f"""
            QFrame {{
                background: {MATERIAL_COLORS['surface_variant']};
                border-radius: 6px;
            }}
        """)
        
        return metrics
        
    def _create_content(self) -> QFrame:
        """
        Create content section.
        
        Override in subclasses to show test-specific content.
        """
        return None
        
    def _create_buttons(self) -> QFrame:
        """Create button panel with Close button"""
        buttons = QFrame()
        layout = QHBoxLayout(buttons)
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.setMinimumWidth(100)
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet(f"""
            QPushButton {{
                background: {MATERIAL_COLORS['primary']};
                color: {MATERIAL_COLORS['on_primary']};
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {MATERIAL_COLORS['primary_dark']};
            }}
        """)
        
        layout.addWidget(close_button)
        
        return buttons
        
    def _apply_styling(self):
        """Apply dialog styling"""
        self.setStyleSheet(f"""
            QDialog {{
                background: {MATERIAL_COLORS['background']};
            }}
        """)


class ComparatorDetailDialog(TestDetailDialog):
    """Detail view for comparator test cards"""
    
    def __init__(self, test_number: int, passed: bool, time: float, memory: float,
                 input_text: str, correct_output: str, test_output: str, parent=None):
        """
        Initialize comparator detail dialog.
        
        Args:
            test_number: Test case number
            passed: Whether test passed
            time: Execution time in seconds
            memory: Memory usage in MB
            input_text: Test input
            correct_output: Expected output
            test_output: Actual program output
            parent: Parent widget
        """
        self.input_text = input_text
        self.correct_output = correct_output
        self.test_output = test_output
        super().__init__(test_number, passed, time, memory, parent)
        
    def _create_content(self) -> QFrame:
        """Create comparator-specific content with input/output panels"""
        content = QFrame()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Input section
        input_label = QLabel("📥 Input:")
        input_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(input_label)
        
        input_edit = QTextEdit()
        input_edit.setPlainText(self.input_text)
        input_edit.setReadOnly(True)
        input_edit.setMaximumHeight(120)
        self._style_text_edit(input_edit)
        layout.addWidget(input_edit)
        
        # Expected output section
        expected_label = QLabel("✅ Expected Output:")
        expected_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(expected_label)
        
        expected_edit = QTextEdit()
        expected_edit.setPlainText(self.correct_output)
        expected_edit.setReadOnly(True)
        self._style_text_edit(expected_edit)
        layout.addWidget(expected_edit)
        
        # Actual output section
        actual_label = QLabel("📤 Actual Output:")
        actual_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(actual_label)
        
        actual_edit = QTextEdit()
        actual_edit.setPlainText(self.test_output)
        actual_edit.setReadOnly(True)
        self._style_text_edit(actual_edit)
        layout.addWidget(actual_edit)
        
        return content
        
    def _style_text_edit(self, edit: QTextEdit):
        """Apply consistent styling to text edits"""
        edit.setStyleSheet(f"""
            QTextEdit {{
                background: {MATERIAL_COLORS['surface']};
                border: 1px solid {MATERIAL_COLORS['outline']};
                border-radius: 6px;
                padding: 8px;
                color: {MATERIAL_COLORS['text_primary']};
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }}
        """)


class ValidatorDetailDialog(TestDetailDialog):
    """Detail view for validator test cards"""
    
    def __init__(self, test_number: int, passed: bool, time: float, memory: float,
                 expected_output: str, actual_output: str, parent=None):
        """
        Initialize validator detail dialog.
        
        Args:
            test_number: Test case number
            passed: Whether test passed
            time: Execution time in seconds
            memory: Memory usage in MB
            expected_output: Expected output
            actual_output: Actual program output
            parent: Parent widget
        """
        self.expected_output = expected_output
        self.actual_output = actual_output
        super().__init__(test_number, passed, time, memory, parent)
        
    def _create_content(self) -> QFrame:
        """Create validator-specific content with output comparison"""
        content = QFrame()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Expected output section
        expected_label = QLabel("✅ Expected Output:")
        expected_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(expected_label)
        
        expected_edit = QTextEdit()
        expected_edit.setPlainText(self.expected_output)
        expected_edit.setReadOnly(True)
        self._style_text_edit(expected_edit)
        layout.addWidget(expected_edit)
        
        # Actual output section
        actual_label = QLabel("📤 Actual Output:")
        actual_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(actual_label)
        
        actual_edit = QTextEdit()
        actual_edit.setPlainText(self.actual_output)
        actual_edit.setReadOnly(True)
        self._style_text_edit(actual_edit)
        layout.addWidget(actual_edit)
        
        return content
        
    def _style_text_edit(self, edit: QTextEdit):
        """Apply consistent styling to text edits"""
        edit.setStyleSheet(f"""
            QTextEdit {{
                background: {MATERIAL_COLORS['surface']};
                border: 1px solid {MATERIAL_COLORS['outline']};
                border-radius: 6px;
                padding: 8px;
                color: {MATERIAL_COLORS['text_primary']};
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }}
        """)


class BenchmarkerDetailDialog(TestDetailDialog):
    """Detail view for benchmarker test cards"""
    
    def __init__(self, test_number: int, passed: bool, time: float, memory: float,
                 test_size: int, parent=None):
        """
        Initialize benchmarker detail dialog.
        
        Args:
            test_number: Test case number
            passed: Whether test passed (within limits)
            time: Execution time in seconds
            memory: Memory usage in MB
            test_size: Size of test input
            parent: Parent widget
        """
        self.test_size = test_size
        super().__init__(test_number, passed, time, memory, parent)
        
    def _create_content(self) -> QFrame:
        """Create benchmarker-specific content with performance metrics"""
        content = QFrame()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Performance metrics
        metrics_label = QLabel("📊 Performance Metrics:")
        metrics_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(metrics_label)
        
        # Metrics panel
        metrics_panel = QFrame()
        metrics_layout = QVBoxLayout(metrics_panel)
        metrics_layout.setContentsMargins(12, 12, 12, 12)
        metrics_layout.setSpacing(8)
        
        size_label = QLabel(f"Test Size: {self.test_size:,} elements")
        time_per_element = (self.time / self.test_size * 1000) if self.test_size > 0 else 0
        efficiency_label = QLabel(f"Time per Element: {time_per_element:.3f} ms")
        memory_per_element = (self.memory / self.test_size) if self.test_size > 0 else 0
        memory_efficiency_label = QLabel(f"Memory per Element: {memory_per_element:.3f} MB")
        
        for label in [size_label, efficiency_label, memory_efficiency_label]:
            label.setStyleSheet("font-size: 13px;")
            metrics_layout.addWidget(label)
        
        metrics_panel.setStyleSheet(f"""
            QFrame {{
                background: {MATERIAL_COLORS['surface_variant']};
                border-radius: 6px;
            }}
        """)
        
        layout.addWidget(metrics_panel)
        layout.addStretch()
        
        return content
