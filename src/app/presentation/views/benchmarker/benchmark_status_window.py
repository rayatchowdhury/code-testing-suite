
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QProgressBar, 
                              QPushButton, QTextEdit, QHBoxLayout, QWidget,
                              QScrollArea, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, Slot
from src.app.presentation.styles.style import MATERIAL_COLORS
from src.app.presentation.styles.constants.status_colors import ERROR_COLOR_HEX
from src.app.presentation.styles.components.test_view_styles import (
    TEST_VIEW_STATUS_DIALOG_STYLE,
    TEST_VIEW_STATUS_LABEL_STYLE,
    TEST_VIEW_TIME_LABEL_STYLE,
    TEST_VIEW_HISTORY_ITEM_STYLE,
    get_status_label_style,
    get_passed_status_style,
    get_failed_status_style
)

class BenchmarkStatusWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Benchmark Progress")
        self.setMinimumSize(600, 600)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        
        # Default limits (can be overridden)
        self.time_limit = 1.0  # Default 1 second
        self.memory_limit = 256  # Default 256 MB
        self.test_count = 1  # Default 1 test
        self.workspace_dir = ""  # Will be set by TLE runner
        
        self._setup_ui()
        self._setup_styles()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Status section with progress
        self.status_label = QLabel("Preparing Tests...")
        self.status_label.setStyleSheet(TEST_VIEW_STATUS_LABEL_STYLE)
        
        # Progress bar for multiple tests
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()  # Hidden until multiple tests run
        
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
        
        # Time and memory taken section
        self.time_label = QLabel("Time taken: 0.0s")
        self.time_label.setStyleSheet(TEST_VIEW_TIME_LABEL_STYLE)
        
        self.memory_label = QLabel("Memory used: 0.0 MB")
        self.memory_label.setStyleSheet(TEST_VIEW_TIME_LABEL_STYLE)
        
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
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.current_test_widget)
        layout.addWidget(self.time_label)
        layout.addWidget(self.memory_label)
        layout.addWidget(self.history_widget)
        layout.addWidget(self.close_button, alignment=Qt.AlignRight)

    def _setup_styles(self):
        self.setStyleSheet(TEST_VIEW_STATUS_DIALOG_STYLE)

    @Slot(int, int)
    def show_test_running(self, current_test, total_tests):
        """Show currently running test with progress"""
        self.history_widget.hide()
        self.current_test_widget.show()
        
        if total_tests > 1:
            self.progress_bar.show()
            self.progress_bar.setMaximum(total_tests)
            self.progress_bar.setValue(current_test)
            self.status_label.setText(f"Running Test {current_test}/{total_tests}")
        else:
            self.progress_bar.hide()
            self.status_label.setText(f"Running Test {current_test}...")
        
        self.time_label.setText("Time taken: 0.0s")
        self.memory_label.setText("Memory used: 0.0 MB")
        
        # Clear previous results
        for widget in [self.input_text, self.output_text]:
            widget.clear()
            widget.setPlaceholderText("Running...")

    @Slot(str, int, bool, float, float, bool)
    def show_test_complete(self, test_name, test_number, passed, time_taken, memory_used, memory_passed):
        """Show completed test result with memory information"""
        time_exceeded = time_taken > self.time_limit
        
        if passed:
            status = "Passed"
            color = MATERIAL_COLORS['primary']
        else:
            if not memory_passed:
                status = "Failed - Memory Limit Exceeded"
            elif time_exceeded:
                status = "Failed - Time Limit Exceeded"
            else:
                status = "Failed"
            color = ERROR_COLOR_HEX
        
        self.status_label.setText(f"{test_name} {status}")
        self.status_label.setStyleSheet(get_status_label_style(color))
        
        # Update time and memory labels
        self.time_label.setText(f"Time taken: {time_taken:.3f}s (limit: {self.time_limit:.3f}s)")
        self.memory_label.setText(f"Memory used: {memory_used:.2f} MB (limit: {self.memory_limit} MB)")
        
        # Set color based on whether limits were exceeded
        time_color = MATERIAL_COLORS['primary'] if not time_exceeded else ERROR_COLOR_HEX
        memory_color = MATERIAL_COLORS['primary'] if memory_passed else ERROR_COLOR_HEX
        
        self.time_label.setStyleSheet(get_status_label_style(time_color))
        self.memory_label.setStyleSheet(get_status_label_style(memory_color))
        
        # Read and display input/output if available (use latest test files)
        try:
            if self.workspace_dir:
                # Use nested benchmarker directory structure for I/O files
                from src.app.shared.constants.paths import get_input_file_path, get_output_file_path
                
                # Try nested structure first (new format)
                input_file = get_input_file_path(self.workspace_dir, 'benchmarker', f"input_{test_number}.txt")
                output_file = get_output_file_path(self.workspace_dir, 'benchmarker', f"output_{test_number}.txt")
                
                # Fallback to non-numbered files in nested structure
                if not os.path.exists(input_file):
                    input_file = get_input_file_path(self.workspace_dir, 'benchmarker', "input.txt")
                if not os.path.exists(output_file):
                    output_file = get_output_file_path(self.workspace_dir, 'benchmarker', "output.txt")
                
                # Final fallback to flat structure (for migration/backward compatibility)
                if not os.path.exists(input_file):
                    input_file = os.path.join(self.workspace_dir, f"input_{test_number}.txt")
                    if not os.path.exists(input_file):
                        input_file = os.path.join(self.workspace_dir, "input.txt")
                
                if not os.path.exists(output_file):
                    output_file = os.path.join(self.workspace_dir, f"output_{test_number}.txt")
                    if not os.path.exists(output_file):
                        output_file = os.path.join(self.workspace_dir, "output.txt")
                
                if os.path.exists(input_file):
                    with open(input_file, 'r') as f:
                        self.input_text.setText(f.read())
                else:
                    self.input_text.setText("No input file available")
                
                if os.path.exists(output_file):
                    with open(output_file, 'r') as f:
                        self.output_text.setText(f.read())
                else:
                    self.output_text.setText("No output file available")
        except Exception as e:
            self.input_text.setText(f"Error reading input file: {str(e)}")
            self.output_text.setText(f"Error reading output file: {str(e)}")
        
        self._add_to_history(test_name, test_number, passed, time_taken, memory_used, memory_passed, time_exceeded)
        
        # For multiple tests, only show history when generator tests are done, keep showing current for solution tests
        if "Generator" in test_name and self.test_count > 1:
            # Don't hide current widget for generator, wait for solution
            pass
        elif "Solution" in test_name or self.test_count == 1:
            if passed and self.test_count > 1:
                self.current_test_widget.hide()
                self.history_widget.show()
            elif self.test_count == 1:
                if passed:
                    self.current_test_widget.hide()
                    self.history_widget.show()

    @Slot(bool)
    def show_all_passed(self, all_passed):
        """Show final state after all tests"""
        if self.test_count > 1:
            self.progress_bar.setValue(self.progress_bar.maximum())
        
        if all_passed:
            if self.test_count > 1:
                self.status_label.setText(f"All {self.test_count} Tests Passed Within Limits! ✓")
            else:
                self.status_label.setText("Test Passed Within Limits! ✓")
            self.status_label.setStyleSheet(get_passed_status_style())
            self.history_widget.show()
            self.current_test_widget.hide()
        else:
            if self.test_count > 1:
                self.status_label.setText("Some tests failed or exceeded limits")
            else:
                self.status_label.setText("Test failed or exceeded limits")
            self.history_widget.show()
            # Keep current test widget visible for failed tests to show details

    def _add_to_history(self, test_name, test_number, passed, time_taken, memory_used, memory_passed, time_exceeded):
        """Add test result to history with memory information"""
        result = QFrame()
        result.setStyleSheet(TEST_VIEW_HISTORY_ITEM_STYLE)
        
        layout = QVBoxLayout(result)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Main status line
        status = "✓" if passed else "✗"
        color = MATERIAL_COLORS['primary'] if passed else ERROR_COLOR_HEX
        
        main_label = QLabel(f"{test_name}: {status}")
        main_label.setStyleSheet(get_status_label_style(color))
        layout.addWidget(main_label)
        
        # Details line with time and memory
        details_layout = QHBoxLayout()
        
        time_color = MATERIAL_COLORS['primary'] if not time_exceeded else ERROR_COLOR_HEX
        memory_color = MATERIAL_COLORS['primary'] if memory_passed else ERROR_COLOR_HEX
        
        time_label = QLabel(f"Time: {time_taken:.3f}s")
        time_label.setStyleSheet(get_status_label_style(time_color))
        
        memory_label = QLabel(f"Memory: {memory_used:.2f} MB")
        memory_label.setStyleSheet(get_status_label_style(memory_color))
        
        details_layout.addWidget(time_label)
        details_layout.addWidget(memory_label)
        details_layout.addStretch()
        
        layout.addLayout(details_layout)
        
        self.history_layout.insertWidget(0, result)  # Add newest at top
