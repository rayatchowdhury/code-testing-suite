"""
Unified Status View - Base widget for all test executions.
Embedded in display area, not a popup dialog.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.app.presentation.styles.components.status_view_styles import (
    STATUS_VIEW_CONTAINER_STYLE,
)


class BaseStatusView(QWidget):
    """
    Base unified status view for test execution.

    Signals:
        stopRequested: User clicked stop button
        backRequested: User clicked back button
        runRequested: User clicked run button to re-run tests
    """

    stopRequested = Signal()
    backRequested = Signal()
    runRequested = Signal()

    def __init__(self, test_type: str, parent=None):
        """
        Args:
            test_type: 'comparator', 'validator', or 'benchmarker'
            parent: Parent widget
        """
        super().__init__(parent)
        self.test_type = test_type
        self.parent_window = parent

        # Store test state
        self.tests_running = False
        self.total_tests = 0
        self.completed_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

        self._setup_ui()
        self._setup_styles()

    def _setup_ui(self):
        """Setup the main UI structure - content only, no sidebar"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Import here to avoid circular imports
        from src.app.presentation.widgets.status_view_widgets import (
            CardsSection,
            ProgressSection,
        )

        # Progress section
        self.progress_section = ProgressSection()

        # Test cards section
        self.cards_section = CardsSection()

        # Add to layout (no footer - sidebar handles save button)
        layout.addWidget(self.progress_section)
        layout.addWidget(self.cards_section, stretch=1)

    def _setup_styles(self):
        """Apply modern gradient-based styling"""
        self.setStyleSheet(STATUS_VIEW_CONTAINER_STYLE)

    def _handle_back(self):
        """Handle back button click - emit signal for window to handle"""
        if self.tests_running:
            # Confirm before going back during test execution
            reply = QMessageBox.question(
                self,
                "Tests Running",
                "Tests are still running. Stop and go back?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self._handle_stop()
                self.backRequested.emit()
        else:
            self.backRequested.emit()

    def _handle_stop(self):
        """Handle stop button click"""
        if self.tests_running:
            self.tests_running = False
            self.stopRequested.emit()
            self.controls_panel.update_stop_button_state(False)

    # Signal handlers for test execution

    def on_tests_started(self, total: int):
        """Called when tests start"""
        self.tests_running = True
        self.total_tests = total
        self.completed_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.progress_section.reset(total)
        self.cards_section.clear()

    def on_test_running(self, current: int, total: int):
        """Called when a test starts"""
        self.progress_section.update_current_test(current, total)

    def on_test_completed(self, test_number: int, passed: bool, **kwargs):
        """
        Called when a test completes.

        Subclasses should override to create specific card types.
        This base implementation updates counters and progress.

        Args:
            test_number: Test case number (1-indexed)
            passed: Whether test passed
            **kwargs: Additional test data (time, memory, etc.)
        """
        self.completed_tests += 1
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

        self.progress_section.add_test_result(passed)
        self.progress_section.update_stats(
            self.completed_tests, self.total_tests, self.passed_tests, self.failed_tests
        )

    def add_test_card(self, card):
        """
        Add a test card to the cards section.

        Args:
            card: TestCard widget to add
        """
        self.cards_section.add_card(card, card.passed)

        # Connect card click to show detail view
        card.clicked.connect(self.show_test_detail)

    def show_test_detail(self, test_number: int):
        """
        Show detail view for a test.

        Subclasses should override to show test-specific details.

        Args:
            test_number: Test case number to show details for
        """
        # Override in subclasses

    def on_all_tests_completed(self, all_passed: bool):
        """Called when all tests complete - notify parent to enable save button"""
        self.tests_running = False
        self.progress_section.mark_complete(all_passed)

        # Notify parent window to enable save button in sidebar (Issue #39)
        if self.parent_window and hasattr(self.parent_window, "enable_save_button"):
            self.parent_window.enable_save_button()

    def save_to_database(self):
        """Save current test results to database (Issue #39 - on-demand saving)"""
        # Get runner from parent window
        runner = None
        if hasattr(self, "runner"):
            runner = self.runner
        elif self.parent_window and hasattr(self.parent_window, "runner"):
            runner = self.parent_window.runner
        elif self.parent_window and hasattr(
            self.parent_window, f"{self.test_type}_runner"
        ):
            runner = getattr(self.parent_window, f"{self.test_type}_runner")

        if not runner:
            QMessageBox.critical(
                self, "Error", "Runner not found - cannot save results"
            )
            return -1

        try:
            result_id = runner.save_test_results_to_database()

            if result_id > 0:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Results saved successfully!\nDatabase ID: {result_id}",
                )
                # Notify parent to update button text
                if self.parent_window and hasattr(
                    self.parent_window, "mark_results_saved"
                ):
                    self.parent_window.mark_results_saved()
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to save results to database"
                )

            return result_id

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving results:\n{str(e)}")
            return -1

    def set_runner(self, runner):
        """Set the runner instance for saving results"""
        self.runner = runner

    def is_tests_running(self) -> bool:
        """Check if tests are currently running"""
        return self.tests_running
