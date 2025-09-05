
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QProgressBar, 
                              QPushButton, QTextEdit, QHBoxLayout, QWidget,
                              QScrollArea, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, Slot
from ...styles.style import MATERIAL_COLORS
from ...styles.constants.status_colors import ERROR_COLOR_HEX
from ...styles.components.tle_tester import (
    TLE_TEST_STATUS_WINDOW_STYLE,
    TLE_STATUS_LABEL_STYLE,
    TLE_TIME_LABEL_STYLE,
    TLE_HISTORY_FRAME_STYLE,
    get_status_label_style,
    get_passed_status_style,
    get_failed_status_style
)

class TLETestStatusWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TLE Test Progress")
        self.setMinimumSize(600, 600)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        
        self._setup_ui()
        self._setup_styles()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Status section
        self.status_label = QLabel("Preparing Test...")
        self.status_label.setStyleSheet(TLE_STATUS_LABEL_STYLE)
        
        # Current test section
        self.current_test_widget = QWidget()
        current_test_layout = QVBoxLayout(self.current_test_widget)
        current_test_layout.setContentsMargins(0, 0, 0, 0)
        current_test_layout.setSpacing(8)
        
        # Text areas with labels
        for label_text, attr_name in [("Input:", "input_text"), ("Output:", "output_text")]:
            label = QLabel(label_text)
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            text_edit.setPlaceholderText("Waiting...")
            setattr(self, attr_name, text_edit)
            current_test_layout.addWidget(label)
            current_test_layout.addWidget(text_edit)
        
        # Time taken section
        self.time_label = QLabel("Time taken: 0.0s")
        self.time_label.setStyleSheet(TLE_TIME_LABEL_STYLE)
        
        # History section
        self.history_widget = QWidget()
        self.history_widget.hide()
        history_layout = QVBoxLayout(self.history_widget)
        
        history_label = QLabel("Test History")
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setMinimumHeight(100)
        
        self.history_content = QWidget()
        self.history_layout = QVBoxLayout(self.history_content)
        self.history_layout.setAlignment(Qt.AlignTop)
        self.history_layout.setSpacing(4)
        self.history_scroll.setWidget(self.history_content)
        
        history_layout.addWidget(history_label)
        history_layout.addWidget(self.history_scroll)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        
        # Add all widgets to main layout
        layout.addWidget(self.status_label)
        layout.addWidget(self.current_test_widget)
        layout.addWidget(self.time_label)
        layout.addWidget(self.history_widget)
        layout.addWidget(self.close_button, alignment=Qt.AlignRight)

    def _setup_styles(self):
        self.setStyleSheet(TLE_TEST_STATUS_WINDOW_STYLE)

    @Slot(str)
    def show_test_running(self, test_name):
        """Show currently running test"""
        self.history_widget.hide()
        self.current_test_widget.show()
        self.status_label.setText(f"Running {test_name}...")
        self.time_label.setText("Time taken: 0.0s")
        
        # Clear previous results
        for widget in [self.input_text, self.output_text]:
            widget.clear()
            widget.setPlaceholderText("Running...")

    @Slot(str, bool, str, str, float)
    def show_test_complete(self, test_name, passed, input_text="", output="", time_taken=0.0):
        """Show completed test result"""
        status = "Passed" if passed else "Time Limit Exceeded"
        color = MATERIAL_COLORS['primary'] if passed else ERROR_COLOR_HEX
        
        self.status_label.setText(f"{test_name} {status}")
        self.status_label.setStyleSheet(get_status_label_style(color))
        
        self.input_text.setText(input_text or "No input available")
        self.output_text.setText(output or "No output available")
        self.time_label.setText(f"Time taken: {time_taken:.2f}s")
        self.time_label.setStyleSheet(get_status_label_style(color))
        
        self._add_to_history(test_name, passed, time_taken)
        if passed:
            self.current_test_widget.hide()
            self.history_widget.show()

    @Slot(bool)
    def show_all_passed(self, all_passed):
        """Show final state after all tests"""
        if all_passed:
            self.status_label.setText("All Tests Passed Within Time Limit! ✓")
            self.status_label.setStyleSheet(get_passed_status_style())
            self.history_widget.show()
            self.current_test_widget.hide()
        else:
            self.history_widget.hide()
            self.current_test_widget.show()

    def _add_to_history(self, test_name, passed, time_taken):
        """Add test result to history"""
        result = QFrame()
        result.setStyleSheet(TLE_HISTORY_FRAME_STYLE)
        
        layout = QHBoxLayout(result)
        layout.setContentsMargins(4, 4, 4, 4)
        
        status = "✓" if passed else "✗ TLE"
        color = MATERIAL_COLORS['primary'] if passed else ERROR_COLOR_HEX
        
        label = QLabel(f"{test_name}: {status} ({time_taken:.2f}s)")
        label.setStyleSheet(get_status_label_style(color))
        layout.addWidget(label)
        
        self.history_layout.insertWidget(0, result)  # Add newest at top