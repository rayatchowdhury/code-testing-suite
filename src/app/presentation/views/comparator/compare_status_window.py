# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QProgressBar, 
                              QPushButton, QTextEdit, QHBoxLayout, QWidget,
                              QScrollArea, QFrame, QSizePolicy, QApplication)  # Import QApplication here
from PySide6.QtCore import Qt, Signal, Slot, QThread
from src.app.presentation.styles.style import MATERIAL_COLORS
from src.app.presentation.styles.constants.status_colors import ERROR_COLOR_HEX
from src.app.presentation.styles.components.test_view_styles import (
    TEST_VIEW_STATUS_DIALOG_STYLE,
    get_running_status_style,
    get_test_view_error_status_style,
    get_test_view_success_status_style,
    TEST_VIEW_HISTORY_ITEM_STYLE,
    get_history_label_style
)

class CompareStatusWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compare Progress")
        self.setMinimumSize(600, 600)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        
        self._setup_ui()
        self._setup_styles()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Status section
        self.status_label = QLabel("Preparing Tests...")
        self.progress_bar = QProgressBar()
        
        # Current test section
        self.current_test_widget = QWidget()
        current_test_layout = QVBoxLayout(self.current_test_widget)
        current_test_layout.setContentsMargins(0, 0, 0, 0)
        current_test_layout.setSpacing(8)

        # Set size policy for current_test_widget
        self.current_test_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Text areas with labels
        for label_text, attr_name in [("Input:", "input_text"), ("Correct Output:", "correct_output"), ("Test Output:", "test_output")]:
            label = QLabel(label_text)
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            # Remove maximum height constraint
            # text_edit.setMaximumHeight(100)
            text_edit.setPlaceholderText("Waiting...")
            text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            setattr(self, attr_name, text_edit)
            current_test_layout.addWidget(label)
            current_test_layout.addWidget(text_edit)
        
        # History section (hidden initially)
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
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.current_test_widget)
        layout.setStretchFactor(self.current_test_widget, 1)  # Allow it to expand
        layout.addWidget(self.history_widget)
        layout.addWidget(self.close_button, alignment=Qt.AlignRight)
        
        # Initial state
        self.current_test_widget.hide()

    def _setup_styles(self):
        self.setStyleSheet(TEST_VIEW_STATUS_DIALOG_STYLE)

    @Slot(int, int)
    def show_test_running(self, current, total):
        """Show currently running test"""
        # Removed unnecessary thread check
        self.history_widget.hide()
        self.current_test_widget.show()
        
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Running Test {current}/{total}...")
        self.status_label.setStyleSheet(get_running_status_style())
        
        # Clear previous results
        for widget in [self.input_text, self.correct_output, self.test_output]:
            widget.clear()
            widget.setPlaceholderText("Running...")

    @Slot(int, bool, str, str, str)
    def show_test_complete(self, test_number, passed, input_text="", correct_output="", test_output=""):
        """Show completed test result"""
        # Removed unnecessary thread check
        if not passed:
            # Hide history when test fails
            self.history_widget.hide()
            # Show failure details
            self.status_label.setText(f"Test {test_number} Failed ✗")
            self.status_label.setStyleSheet(get_test_view_error_status_style())
            self.input_text.setText(input_text or "No input available")
            self.correct_output.setText(correct_output or "No correct output available")
            self.test_output.setText(test_output or "No test output available")
            self.current_test_widget.show()
        else:
            # Add passing test to history and show it
            self._add_to_history(test_number, passed)
            self.status_label.setText(f"Test {test_number} Passed ✓")
            self.status_label.setStyleSheet(get_test_view_success_status_style())
            self.current_test_widget.hide()
            self.history_widget.show()

    @Slot(bool)
    def show_all_passed(self, all_passed):
        """Show final state after all tests"""
        if all_passed:
            self.status_label.setText("All Tests Passed! ✓")
            self.status_label.setStyleSheet(get_test_view_success_status_style())
            self.history_widget.show()
            self.current_test_widget.hide()
        else:
            # Hide history and show current test widget if not all tests passed
            self.history_widget.hide()
            self.current_test_widget.show()
            # The status label and details are already set in `show_test_complete` for failed tests

    def _add_to_history(self, test_number, passed):
        """Add test result to history"""
        result = QFrame()
        result.setStyleSheet(TEST_VIEW_HISTORY_ITEM_STYLE)
        
        layout = QHBoxLayout(result)
        layout.setContentsMargins(4, 4, 4, 4)
        
        status = "✓" if passed else "✗"
        
        label = QLabel(f"Test {test_number}: {status}")
        label.setStyleSheet(get_history_label_style(passed))
        layout.addWidget(label)
        
        self.history_layout.insertWidget(0, result)  # Add newest at top
