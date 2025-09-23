# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from src.app.presentation.styles.style import MATERIAL_COLORS
from src.app.presentation.styles.constants.status_colors import ERROR_COLOR_HEX
from src.app.presentation.styles.components.test_view_styles import (
    TEST_VIEW_COMPILATION_STATUS_DIALOG_STYLE,
    TEST_VIEW_COMPILATION_STATUS_LABEL_STYLE,
    TEST_VIEW_COMPILATION_PROGRESS_BAR_STYLE,
    TEST_VIEW_COMPILATION_DETAIL_LABEL_STYLE,
    TEST_VIEW_COMPILATION_CLOSE_BUTTON_STYLE,
    get_compilation_status_style
)

class ValidatorStatusWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Validation Status")
        self.setFixedSize(500, 400)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Main status label
        self.status_label = QLabel("Running Validation Tests...")
        self.status_label.setStyleSheet(TEST_VIEW_COMPILATION_STATUS_LABEL_STYLE)
        
        # Progress bar for overall test progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(TEST_VIEW_COMPILATION_PROGRESS_BAR_STYLE)
        
        # Stage indicators layout
        stage_layout = QHBoxLayout()
        stage_layout.setSpacing(20)
        
        # Generator stage
        self.generator_label = QLabel("🔄 Generator")
        self.generator_label.setAlignment(Qt.AlignCenter)
        self.generator_label.setStyleSheet("color: #666; font-weight: bold; padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        stage_layout.addWidget(self.generator_label)
        
        # Arrow
        arrow1 = QLabel("→")
        arrow1.setAlignment(Qt.AlignCenter)
        arrow1.setStyleSheet("font-size: 16px; font-weight: bold; color: #666;")
        stage_layout.addWidget(arrow1)
        
        # Test stage
        self.test_label = QLabel("🔄 Test")
        self.test_label.setAlignment(Qt.AlignCenter)
        self.test_label.setStyleSheet("color: #666; font-weight: bold; padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        stage_layout.addWidget(self.test_label)
        
        # Arrow
        arrow2 = QLabel("→")
        arrow2.setAlignment(Qt.AlignCenter)
        arrow2.setStyleSheet("font-size: 16px; font-weight: bold; color: #666;")
        stage_layout.addWidget(arrow2)
        
        # Validator stage
        self.validator_label = QLabel("🔄 Validator")
        self.validator_label.setAlignment(Qt.AlignCenter)
        self.validator_label.setStyleSheet("color: #666; font-weight: bold; padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        stage_layout.addWidget(self.validator_label)
        
        # Test results area
        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        self.results_area.setMaximumHeight(150)
        self.results_area.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
        """)
        
        # Summary label
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet(TEST_VIEW_COMPILATION_DETAIL_LABEL_STYLE)
        self.summary_label.setWordWrap(True)
        self.summary_label.setAlignment(Qt.AlignCenter)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.setVisible(False)
        self.close_button.clicked.connect(self.accept)
        self.close_button.setStyleSheet(TEST_VIEW_COMPILATION_CLOSE_BUTTON_STYLE)
        
        # Add all widgets to layout
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(stage_layout)
        layout.addWidget(QLabel("Test Results:"))
        layout.addWidget(self.results_area)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.close_button, alignment=Qt.AlignCenter)
        
        self.setStyleSheet(TEST_VIEW_COMPILATION_STATUS_DIALOG_STYLE)
        
        # Initialize state
        self.current_test = 0
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    def show_test_running(self, test_number, total_tests):
        """Show that a test is starting"""
        self.current_test = test_number
        self.total_tests = total_tests
        
        # Update progress
        progress = int((test_number - 1) / total_tests * 100)
        self.progress_bar.setValue(progress)
        
        # Update status
        self.status_label.setText(f"Running Test {test_number}/{total_tests}...")
        
        # Reset stage indicators
        self._reset_stage_indicators()
        self._update_stage_indicator("generator", "running")

    def show_test_complete(self, test_number, passed, input_data, test_output, validation_message, error_details, validator_exit_code):
        """Show that a test has completed"""
        # Update stage indicators based on result
        if passed:
            self._update_stage_indicator("generator", "success")
            self._update_stage_indicator("test", "success") 
            self._update_stage_indicator("validator", "success")
            self.passed_tests += 1
        else:
            # Determine which stage failed based on validator exit code
            if validator_exit_code == -1:  # Generator failed
                self._update_stage_indicator("generator", "error")
                self._update_stage_indicator("test", "pending")
                self._update_stage_indicator("validator", "pending")
            elif "Test solution failed" in validation_message:  # Test failed  
                self._update_stage_indicator("generator", "success")
                self._update_stage_indicator("test", "error")
                self._update_stage_indicator("validator", "pending")
            else:  # Validator failed or returned invalid
                self._update_stage_indicator("generator", "success")
                self._update_stage_indicator("test", "success")
                if validator_exit_code == 1:
                    self._update_stage_indicator("validator", "invalid")
                else:
                    self._update_stage_indicator("validator", "error")
            self.failed_tests += 1
        
        # Add result to results area
        status_icon = "✅" if passed else "❌"
        result_text = f"Test {test_number}: {status_icon} {validation_message}"
        if error_details:
            result_text += f" ({error_details})"
        self.results_area.append(result_text)
        
        # Update progress
        progress = int(test_number / self.total_tests * 100)
        self.progress_bar.setValue(progress)

    def show_all_passed(self, all_passed):
        """Show final results"""
        if all_passed:
            self.status_label.setText("🎉 All Tests Passed!")
            self.status_label.setStyleSheet(TEST_VIEW_COMPILATION_STATUS_LABEL_STYLE + "color: #28a745;")
        else:
            self.status_label.setText("❌ Some Tests Failed")
            self.status_label.setStyleSheet(TEST_VIEW_COMPILATION_STATUS_LABEL_STYLE + "color: #dc3545;")
        
        # Update summary
        self.summary_label.setText(f"Results: {self.passed_tests} passed, {self.failed_tests} failed out of {self.total_tests} tests")
        
        # Show close button
        self.close_button.setVisible(True)
        self.progress_bar.setValue(100)

    def _reset_stage_indicators(self):
        """Reset all stage indicators to pending state"""
        self._update_stage_indicator("generator", "pending")
        self._update_stage_indicator("test", "pending")
        self._update_stage_indicator("validator", "pending")

    def _update_stage_indicator(self, stage, status):
        """Update a stage indicator with the given status"""
        if stage == "generator":
            label = self.generator_label
            stage_name = "Generator"
        elif stage == "test":
            label = self.test_label
            stage_name = "Test"
        elif stage == "validator":
            label = self.validator_label
            stage_name = "Validator"
        else:
            return
        
        if status == "pending":
            icon = "⏳"
            color = "#666"
            bg_color = "#f8f9fa"
            border_color = "#ddd"
        elif status == "running":
            icon = "🔄"
            color = "#007bff"
            bg_color = "#e3f2fd"
            border_color = "#007bff"
        elif status == "success":
            icon = "✅"
            color = "#28a745"
            bg_color = "#d4edda"
            border_color = "#28a745"
        elif status == "invalid":
            icon = "❌"
            color = "#ffc107"
            bg_color = "#fff3cd"
            border_color = "#ffc107"
        elif status == "error":
            icon = "💥"
            color = "#dc3545"
            bg_color = "#f8d7da"
            border_color = "#dc3545"
        else:
            return
        
        label.setText(f"{icon} {stage_name}")
        label.setStyleSheet(f"""
            color: {color};
            background-color: {bg_color};
            border: 2px solid {border_color};
            border-radius: 6px;
            padding: 8px;
            font-weight: bold;
            font-size: 12px;
        """)