"""
Test card widgets for unified status view.

Cards display individual test results with time/memory metrics.
Clicking a card shows detailed test information.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from src.app.presentation.styles.components.status_view_styles import (
    TEST_CARD_LABEL_HEADER_STYLE,
    TEST_CARD_LABEL_METRIC_STYLE,
    TEST_CARD_LABEL_STATUS_FAILED_STYLE,
    TEST_CARD_LABEL_STATUS_PASSED_STYLE,
    get_test_card_style,
)
from src.app.presentation.styles.fonts.emoji import set_emoji_font
from src.app.presentation.styles.style import MATERIAL_COLORS


class BaseTestCard(QFrame):
    """
    Base test card widget.

    Displays test number, pass/fail status, and time/memory metrics.
    Emits clicked signal when clicked to show detail view.
    """

    clicked = Signal(int)  # Emits test number when clicked

    def __init__(
        self, test_number: int, passed: bool, time: float, memory: float, parent=None
    ):
        """
        Initialize test card.

        Args:
            test_number: Test case number (1-indexed)
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

        self._setup_ui()
        self._apply_styling()

    def _setup_ui(self):
        """Setup card UI with header and metrics"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        # Header row: Test # | Status
        header_layout = QHBoxLayout()

        self.test_label = QLabel(f"Test #{self.test_number}")
        self.test_label.setStyleSheet(TEST_CARD_LABEL_HEADER_STYLE)

        self.status_label = QLabel("✓ Passed" if self.passed else "✗ Failed")
        status_style = (
            TEST_CARD_LABEL_STATUS_PASSED_STYLE
            if self.passed
            else TEST_CARD_LABEL_STATUS_FAILED_STYLE
        )
        self.status_label.setStyleSheet(status_style)

        header_layout.addWidget(self.test_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)

        # Metrics row: Time | Memory
        metrics_layout = QHBoxLayout()

        self.time_label = QLabel(f"⏱️ {self.time:.3f}s")
        self.memory_label = QLabel(f"💾 {self.memory:.1f} MB")

        for label in [self.time_label, self.memory_label]:
            set_emoji_font(label)
            label.setStyleSheet(TEST_CARD_LABEL_METRIC_STYLE)

        metrics_layout.addWidget(self.time_label)
        metrics_layout.addWidget(self.memory_label)
        metrics_layout.addStretch()

        layout.addLayout(header_layout)
        layout.addLayout(metrics_layout)

        # Make clickable
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)

    def _apply_styling(self):
        """Apply card styling with gradient background based on pass/fail"""
        self.setStyleSheet(get_test_card_style(self.passed))

    def mousePressEvent(self, event):
        """Handle mouse click to emit signal"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.test_number)
        super().mousePressEvent(event)

    def update_metrics(self, time: float, memory: float):
        """
        Update time and memory metrics.

        Args:
            time: New execution time in seconds
            memory: New memory usage in MB
        """
        self.time = time
        self.memory = memory
        self.time_label.setText(f"⏱️ {self.time:.3f}s")
        self.memory_label.setText(f"💾 {self.memory:.1f} MB")
        set_emoji_font(self.time_label)
        set_emoji_font(self.memory_label)


class ComparatorTestCard(BaseTestCard):
    """
    Comparator-specific test card.

    Stores input, expected output, and actual output for comparison tests.
    """

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
        Initialize comparator test card.

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


class ValidatorTestCard(BaseTestCard):
    """
    Validator-specific test card.

    Stores expected output and actual output for validator tests.
    """

    def __init__(
        self,
        test_number: int,
        passed: bool,
        time: float,
        memory: float,
        expected_output: str,
        actual_output: str,
        parent=None,
    ):
        """
        Initialize validator test card.

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


class BenchmarkerTestCard(BaseTestCard):
    """
    Benchmarker-specific test card.

    Stores additional performance metrics for benchmark tests.
    """

    def __init__(
        self,
        test_number: int,
        passed: bool,
        time: float,
        memory: float,
        test_size: int,
        parent=None,
    ):
        """
        Initialize benchmarker test card.

        Args:
            test_number: Test case number
            passed: Whether test passed (time/memory within limits)
            time: Execution time in seconds
            memory: Memory usage in MB
            test_size: Size of test input
            parent: Parent widget
        """
        self.test_size = test_size
        super().__init__(test_number, passed, time, memory, parent)
