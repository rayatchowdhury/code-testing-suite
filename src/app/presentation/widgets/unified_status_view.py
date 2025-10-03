"""
Unified Status View - Base widget for all test executions.
Embedded in display area, not a popup dialog.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PySide6.QtCore import Signal


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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Import here to avoid circular imports
        from src.app.presentation.widgets.status_view_widgets import (
            ControlsPanel,
            ProgressSection,
            CardsSection
        )
        
        # Control panel (file buttons only - stop button now in sidebar)
        self.controls_panel = ControlsPanel(self.test_type)
        # Note: stopClicked signal no longer connected - stop button in sidebar
        
        # Progress section
        self.progress_section = ProgressSection()
        
        # Test cards section
        self.cards_section = CardsSection()
        
        # Add to layout
        layout.addWidget(self.controls_panel)
        layout.addWidget(self.progress_section)
        layout.addWidget(self.cards_section, stretch=1)

        
    def _setup_styles(self):
        """Apply styling"""
        from src.app.presentation.styles.style import MATERIAL_COLORS
        self.setStyleSheet(f"""
            QWidget {{
                background: {MATERIAL_COLORS['surface']};
            }}
        """)
        
    def _handle_back(self):
        """Handle back button click - emit signal for window to handle"""
        if self.tests_running:
            # Confirm before going back during test execution
            reply = QMessageBox.question(
                self,
                "Tests Running",
                "Tests are still running. Stop and go back?",
                QMessageBox.Yes | QMessageBox.No
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
        self.controls_panel.update_stop_button_state(True)
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
            self.completed_tests,
            self.total_tests,
            self.passed_tests,
            self.failed_tests
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
        pass  # Override in subclasses
        
    def on_all_tests_completed(self, all_passed: bool):
        """Called when all tests complete"""
        self.tests_running = False
        self.controls_panel.update_stop_button_state(False)
        self.progress_section.mark_complete(all_passed)
        
    def is_tests_running(self) -> bool:
        """Check if tests are currently running"""
        return self.tests_running
