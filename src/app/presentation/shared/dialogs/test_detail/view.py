"""
Detail view dialogs for test cards.

Shows detailed information about a specific test when a card is clicked.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from src.app.presentation.shared.design_system.assets.fonts import set_emoji_font
from src.app.presentation.shared.design_system.tokens import MATERIAL_COLORS
from src.app.presentation.shared.design_system.styles.components.dialogs.test_detail_styles import (
    TEST_DETAIL_DIALOG_STYLE,
    TEST_DETAIL_METRICS_LABEL_STYLE,
    TEST_DETAIL_METRICS_FRAME_STYLE,
    TEST_DETAIL_CLOSE_BUTTON_STYLE,
    TEST_DETAIL_SECTION_LABEL_STYLE,
    TEST_DETAIL_TEXT_EDIT_MONOSPACE_STYLE,
    get_test_label_style,
    get_status_label_style,
    get_header_frame_style,
    get_validator_log_style,
    get_performance_summary_style,
)

class TestDetailDialog(QDialog):
    """
    Base detail view dialog for test cards.

    Shows test number, status, time, memory, and test-specific content.
    """

    __test__ = False  # Prevent pytest collection

    def __init__(
        self, test_number: int, passed: bool, time: float, memory: float, parent=None
    ):
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
        test_label.setStyleSheet(get_test_label_style())

        status_text = "✓ Passed" if self.passed else "✗ Failed"
        status_label = QLabel(status_text)
        status_label.setStyleSheet(get_status_label_style(self.passed))

        layout.addWidget(test_label)
        layout.addStretch()
        layout.addWidget(status_label)

        # Style header
        header.setStyleSheet(get_header_frame_style(self.passed))

        return header

    def _create_metrics(self) -> QFrame:
        """Create metrics panel with time and memory"""
        metrics = QFrame()
        layout = QHBoxLayout(metrics)
        layout.setContentsMargins(12, 8, 12, 8)

        time_label = QLabel(f"⏱️ Time: {self.time:.3f}s")
        memory_label = QLabel(f"💾 Memory: {self.memory:.1f} MB")

        for label in [time_label, memory_label]:
            set_emoji_font(label)
            label.setStyleSheet(TEST_DETAIL_METRICS_LABEL_STYLE)
            layout.addWidget(label)

        layout.addStretch()

        metrics.setStyleSheet(TEST_DETAIL_METRICS_FRAME_STYLE)

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
        close_button.setStyleSheet(TEST_DETAIL_CLOSE_BUTTON_STYLE)

        layout.addWidget(close_button)

        return buttons

    def _apply_styling(self):
        """Apply dialog styling"""
        self.setStyleSheet(TEST_DETAIL_DIALOG_STYLE)

class ComparatorDetailDialog(TestDetailDialog):
    """Detail view for comparator test cards"""

    def __init__(
        self,
        test_number: int,
        passed: bool,
        time: float,
        memory: float,
        input_text: str,
        correct_output: str,
        test_output: str,
        parent=None,
    ):
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
        set_emoji_font(input_label)
        input_label.setStyleSheet(TEST_DETAIL_SECTION_LABEL_STYLE)
        layout.addWidget(input_label)

        input_edit = QTextEdit()
        input_edit.setPlainText(self.input_text)
        input_edit.setReadOnly(True)
        input_edit.setMaximumHeight(120)
        self._style_text_edit(input_edit)
        layout.addWidget(input_edit)

        # Expected output section
        expected_label = QLabel("✅ Expected Output:")
        set_emoji_font(expected_label)
        expected_label.setStyleSheet(TEST_DETAIL_SECTION_LABEL_STYLE)
        layout.addWidget(expected_label)

        expected_edit = QTextEdit()
        expected_edit.setPlainText(self.correct_output)
        expected_edit.setReadOnly(True)
        self._style_text_edit(expected_edit)
        layout.addWidget(expected_edit)

        # Actual output section
        actual_label = QLabel("📤 Actual Output:")
        set_emoji_font(actual_label)
        actual_label.setStyleSheet(TEST_DETAIL_SECTION_LABEL_STYLE)
        layout.addWidget(actual_label)

        actual_edit = QTextEdit()
        actual_edit.setPlainText(self.test_output)
        actual_edit.setReadOnly(True)
        self._style_text_edit(actual_edit)
        layout.addWidget(actual_edit)

        return content

    def _style_text_edit(self, edit: QTextEdit):
        """Apply consistent styling to text edits"""
        edit.setStyleSheet(TEST_DETAIL_TEXT_EDIT_MONOSPACE_STYLE)

class ValidatorDetailDialog(TestDetailDialog):
    """Detail view for validator test cards"""

    def __init__(
        self,
        test_number: int,
        passed: bool,
        time: float,
        memory: float,
        input_data: str,
        test_output: str,
        validation_message: str,
        error_details: str,
        validator_exit_code: int,
        parent=None,
    ):
        """
        Initialize validator detail dialog.

        Args:
            test_number: Test case number
            passed: Whether test passed
            time: Execution time in seconds
            memory: Memory usage in MB
            input_data: Input generated for this test
            test_output: Output from test solution
            validation_message: Validation result (Correct/Wrong Answer/etc)
            error_details: Additional error information if failed
            validator_exit_code: Exit code from validator (0=Correct, 1=WA, 2=PE)
            parent: Parent widget
        """
        self.input_data = input_data
        self.test_output = test_output
        self.validation_message = validation_message
        self.error_details = error_details
        self.validator_exit_code = validator_exit_code
        super().__init__(test_number, passed, time, memory, parent)

    def _create_content(self) -> QFrame:
        """Create validator-specific content with 3 sections: Input, Output, Validator Log"""
        content = QFrame()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Section 1: Input
        input_label = QLabel("📥 Input:")
        set_emoji_font(input_label)
        input_label.setStyleSheet(TEST_DETAIL_SECTION_LABEL_STYLE)
        layout.addWidget(input_label)

        input_edit = QTextEdit()
        input_edit.setPlainText(self.input_data)
        input_edit.setReadOnly(True)
        self._style_text_edit(input_edit)
        layout.addWidget(input_edit)

        # Section 2: Output
        output_label = QLabel("📤 Output:")
        set_emoji_font(output_label)
        output_label.setStyleSheet(TEST_DETAIL_SECTION_LABEL_STYLE)
        layout.addWidget(output_label)

        output_edit = QTextEdit()
        output_edit.setPlainText(self.test_output)
        output_edit.setReadOnly(True)
        self._style_text_edit(output_edit)
        layout.addWidget(output_edit)

        # Section 3: Validator Log
        validator_label = QLabel("📋 Validator Log:")
        set_emoji_font(validator_label)
        validator_label.setStyleSheet(TEST_DETAIL_SECTION_LABEL_STYLE)
        layout.addWidget(validator_label)

        validator_edit = QTextEdit()
        validator_log = self._create_validator_log()
        validator_edit.setPlainText(validator_log)
        validator_edit.setReadOnly(True)
        self._style_text_edit(validator_edit, is_log=True)
        layout.addWidget(validator_edit)

        return content

    def _create_validator_log(self) -> str:
        """
        Create the validator log message based on test result.

        Returns:
            Formatted validator log string
        """
        if self.passed:
            return "✅ Valid output\n\nThe test solution produced correct output for the given input."

        # Failed case - explain why
        log_lines = [f"❌ {self.validation_message}"]

        # Add exit code interpretation
        if self.validator_exit_code == 1:
            log_lines.append("\nExit Code: 1 (Wrong Answer)")
            log_lines.append("The output is incorrect for the given input.")
        elif self.validator_exit_code == 2:
            log_lines.append("\nExit Code: 2 (Presentation Error)")
            log_lines.append(
                "The output has formatting issues (e.g., extra spaces, wrong line breaks)."
            )
        elif self.validator_exit_code == -1:
            log_lines.append("\nExit Code: -1 (Generator/Test Failed)")
            log_lines.append(
                "The generator or test solution failed to execute properly."
            )
        elif self.validator_exit_code == -2:
            log_lines.append("\nExit Code: -2 (Timeout)")
            log_lines.append("The execution exceeded the time limit.")
        elif self.validator_exit_code == -3:
            log_lines.append("\nExit Code: -3 (Execution Error)")
            log_lines.append("An unexpected error occurred during execution.")
        else:
            log_lines.append(f"\nExit Code: {self.validator_exit_code}")

        # Add error details if available
        if self.error_details:
            log_lines.append(f"\nDetails:\n{self.error_details}")

        return "\n".join(log_lines)

    def _style_text_edit(self, edit: QTextEdit, is_log: bool = False):
        """
        Apply consistent styling to text edits.

        Args:
            edit: The QTextEdit to style
            is_log: If True, use different styling for validator log section
        """
        if is_log:
            # Validator log gets special styling
            edit.setStyleSheet(get_validator_log_style(self.passed))
        else:
            # Input/Output sections use monospace font
            edit.setStyleSheet(TEST_DETAIL_TEXT_EDIT_MONOSPACE_STYLE)

class BenchmarkerDetailDialog(TestDetailDialog):
    """Detail view for benchmarker test cards"""

    def __init__(
        self,
        test_number: int,
        passed: bool,
        time: float,
        memory: float,
        test_size: int = 0,
        input_data: str = "",
        output_data: str = "",
        parent=None,
    ):
        """
        Initialize benchmarker detail dialog.

        Args:
            test_number: Test case number
            passed: Whether test passed (within limits)
            time: Execution time in seconds
            memory: Memory usage in MB
            test_size: Size of test input (number of lines)
            input_data: Input data for the test
            output_data: Output data from the test
            parent: Parent widget
        """
        self.test_size = test_size
        self.input_data = input_data
        self.output_data = output_data
        super().__init__(test_number, passed, time, memory, parent)

    def _create_content(self) -> QFrame:
        """Create benchmarker-specific content with Input, Output, and Summary sections"""
        content = QFrame()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Section 1: Input
        input_label = QLabel("📥 Input:")
        set_emoji_font(input_label)
        input_label.setStyleSheet(TEST_DETAIL_SECTION_LABEL_STYLE)
        layout.addWidget(input_label)

        input_edit = QTextEdit()
        input_edit.setPlainText(
            self.input_data if self.input_data else "No input data available"
        )
        input_edit.setReadOnly(True)
        input_edit.setMaximumHeight(150)
        self._style_text_edit(input_edit)
        layout.addWidget(input_edit)

        # Section 2: Output
        output_label = QLabel("📤 Output:")
        set_emoji_font(output_label)
        output_label.setStyleSheet(TEST_DETAIL_SECTION_LABEL_STYLE)
        layout.addWidget(output_label)

        output_edit = QTextEdit()
        output_edit.setPlainText(
            self.output_data if self.output_data else "No output data available"
        )
        output_edit.setReadOnly(True)
        output_edit.setMaximumHeight(150)
        self._style_text_edit(output_edit)
        layout.addWidget(output_edit)

        # Section 3: Performance Summary
        summary_label = QLabel("📊 Performance Summary:")
        set_emoji_font(summary_label)
        summary_label.setStyleSheet(TEST_DETAIL_SECTION_LABEL_STYLE)
        layout.addWidget(summary_label)

        summary_edit = QTextEdit()
        summary_text = self._create_performance_summary()
        summary_edit.setPlainText(summary_text)
        summary_edit.setReadOnly(True)
        self._style_summary_edit(summary_edit)
        layout.addWidget(summary_edit)

        return content

    def _create_performance_summary(self) -> str:
        """
        Create simplified performance summary.

        Returns:
            Formatted performance summary string
        """
        # Count input lines
        input_lines = len(self.input_data.strip().split("\n")) if self.input_data else 0

        summary_lines = []
        summary_lines.append(f"📝 Number of Input Lines: {input_lines:,}")

        # Performance verdict
        if self.passed:
            summary_lines.append("\n✅ Performance within acceptable limits")
        else:
            summary_lines.append("\n❌ Performance exceeded limits")

        return "\n".join(summary_lines)

    def _style_text_edit(self, edit: QTextEdit):
        """Apply monospace styling for input/output sections"""
        edit.setStyleSheet(TEST_DETAIL_TEXT_EDIT_MONOSPACE_STYLE)

    def _style_summary_edit(self, edit: QTextEdit):
        """Apply special styling for performance summary section"""
        edit.setStyleSheet(get_performance_summary_style(self.passed))
