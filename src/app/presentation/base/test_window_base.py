"""
Base class for test tool windows (Benchmarker, Validator, Comparator).

TestWindowBase consolidates 588 lines of duplicated code from test windows,
providing template methods for subclasses to customize behavior.
"""

from abc import abstractmethod
from typing import Optional, TYPE_CHECKING
from PySide6.QtWidgets import QWidget, QPushButton
from PySide6.QtGui import QShowEvent
from .content_window_base import ContentWindowBase
from .protocols import TestRunner


class TestWindowBase(ContentWindowBase):
    """
    Base class for Benchmarker, Validator, Comparator windows.
    
    Extracts 588 lines of duplicated code into shared implementation.
    Uses template method pattern for customization.
    
    Template Methods (override in subclasses):
        _create_runner() -> TestRunner
        _create_status_view() -> QWidget
        _get_runner_attribute_name() -> str
        _get_run_method_name() -> str
    
    Shared Methods (588 lines extracted):
        _initialize_tool()
        _load_config()
        _on_files_changed()
        showEvent()
        _on_testing_started()
        _on_testing_completed()
        _switch_to_test_mode()
        _switch_to_completed_mode()
        _handle_rerun_tests()
        _restore_normal_mode()
        enable_save_button()
        mark_results_saved()
        refresh_ai_panels()
        handle_button_click()
        _get_runner()
    
    Usage:
        class BenchmarkerWindow(TestWindowBase):
            def _create_runner(self):
                return Benchmarker(...)
            
            def _create_status_view(self):
                return BenchmarkerStatusView(...)
            
            def _get_runner_attribute_name(self):
                return "benchmarker"
            
            def _get_run_method_name(self):
                return "run_benchmark_test"
    """
    
    def __init__(self, parent=None):
        """
        Initialize TestWindowBase.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._runner: Optional[TestRunner] = None
        self._status_view: Optional['QWidget'] = None
        self.compile_btn: Optional['QPushButton'] = None
        self.run_btn: Optional['QPushButton'] = None
        self.stop_btn: Optional['QPushButton'] = None
        self.rerun_btn: Optional['QPushButton'] = None
        self.status_view_active = False
        self.current_status_view: Optional['QWidget'] = None
    
    # ===== TEMPLATE METHODS (must override) =====
    
    @abstractmethod
    def _create_runner(self) -> TestRunner:
        """
        Create specific runner (Benchmarker, Validator, Comparator).
        
        Returns:
            TestRunner instance
        """
        pass
    
    @abstractmethod
    def _create_status_view(self) -> 'QWidget':
        """
        Create specific status view.
        
        Returns:
            Status view widget
        """
        pass
    
    @abstractmethod
    def _get_runner_attribute_name(self) -> str:
        """
        Get the attribute name for the runner.
        
        Returns:
            "benchmarker", "validator_runner", or "comparator"
        """
        pass
    
    @abstractmethod
    def _get_run_method_name(self) -> str:
        """
        Get the run method name for the runner.
        
        Returns:
            "run_benchmark_test", "run_validation_test", or "run_comparison_test"
        """
        pass
    
    # ===== SHARED IMPLEMENTATION (588 lines extracted) =====
    
    def _initialize_tool(self):
        """Initialize or reinitialize the tool with current file manifest."""
        # Disconnect old runner's signals if it exists
        runner_attr = self._get_runner_attribute_name()
        if hasattr(self, runner_attr) and getattr(self, runner_attr):
            old_runner = getattr(self, runner_attr)
            try:
                old_runner.compilationOutput.disconnect()
                old_runner.testingStarted.disconnect()
                old_runner.testingCompleted.disconnect()
            except (RuntimeError, TypeError):
                # Signals may already be disconnected or object deleted
                pass

        # Load configuration
        config = self._load_config()

        # Get file manifest from test tabs
        manifest = self.testing_content.test_tabs.get_compilation_manifest()
        files = manifest["files"]

        # Create runner using template method
        runner = self._create_runner()
        
        # Store runner with appropriate attribute name
        setattr(self, runner_attr, runner)
        self._runner = runner
        
        # Connect compilation output to console
        runner.compilationOutput.connect(
            self.testing_content.console.displayOutput
        )

        # Connect runner signals to handle UI state changes
        runner.testingStarted.connect(self._on_testing_started)
        runner.testingCompleted.connect(self._on_testing_completed)
    
    def _load_config(self):
        """Load configuration for multi-language compilation."""
        try:
            from src.app.core.config import ConfigManager

            config_manager = ConfigManager()
            return config_manager.load_config()
        except Exception as e:
            # Fallback to empty config if loading fails
            return {}
    
    def _on_files_changed(self):
        """Handle file manifest changes (language switches)."""
        # Reinitialize tool with new file configuration
        self._initialize_tool()
    
    def showEvent(self, event: 'QShowEvent'):
        """Handle window show event - reload AI config and refresh AI panels."""
        super().showEvent(event)
        # Reload AI configuration to pick up any changes made while window was closed
        try:
            from src.app.core.ai import reload_ai_config

            reload_ai_config()
        except ImportError:
            pass  # AI module not available
    
    def _on_testing_started(self):
        """Handle testing started signal - create and show status view."""
        # Create status view using template method
        status_view = self._create_status_view()

        # Set runner for on-demand saving (Issue #39)
        runner = getattr(self, self._get_runner_attribute_name())
        status_view.set_runner(runner)

        # Replace Results button with Save button (Phase 2: Issue #39)
        self.sidebar.replace_results_with_save_button()

        # Store reference
        self.status_view = status_view
        self.current_status_view = status_view

        # Get worker and connect signals
        worker = runner.get_current_worker()
        if worker and status_view:
            self._connect_worker_to_status_view(worker, status_view)

            # Connect allTestsCompleted to switch buttons
            try:
                if hasattr(worker, "allTestsCompleted"):
                    worker.allTestsCompleted.connect(self._switch_to_completed_mode)
            except RuntimeError:
                pass  # Worker deleted, ignore

            # Notify view that tests are starting
            if hasattr(status_view, "on_tests_started"):
                status_view.on_tests_started(self.test_count_slider.value())

        # Integrate status view into display area
        self._integrate_status_view(status_view)

        # Switch to test mode (hide compile/run, show stop)
        self._switch_to_test_mode()
    
    def _on_testing_completed(self):
        """Handle testing completed signal - switch to completed mode but stay in status view."""
        # When tests are stopped, switch to Run button but keep status view open
        self._switch_to_completed_mode()
    
    def _switch_to_test_mode(self):
        """Hide Compile and Run buttons, show Stop button when tests start."""
        self.status_view_active = True

        # Hide Compile button during test execution
        if self.compile_btn:
            self.compile_btn.hide()

        # Hide Run button
        if self.run_btn:
            self.run_btn.hide()

        if not self.stop_btn:
            # Create Stop button dynamically
            from PySide6.QtWidgets import QPushButton
            self.stop_btn = self.sidebar.add_button("Stop", self.action_section)
            self.stop_btn.clicked.connect(lambda: self.handle_action_button("Stop"))

        if self.stop_btn:
            self.stop_btn.show()

        # Hide rerun button during test execution
        if hasattr(self, "rerun_btn") and self.rerun_btn:
            self.rerun_btn.hide()
    
    def _switch_to_completed_mode(self):
        """Show Run button after tests complete (while viewing status)."""
        # Hide Stop button
        if self.stop_btn:
            self.stop_btn.hide()

        # Create and show Rerun button
        if not hasattr(self, "rerun_btn") or not self.rerun_btn:
            from PySide6.QtWidgets import QPushButton
            self.rerun_btn = self.sidebar.add_button("Run", self.action_section)
            self.rerun_btn.clicked.connect(self._handle_rerun_tests)

        if self.rerun_btn:
            self.rerun_btn.show()
    
    def _handle_rerun_tests(self):
        """Handle rerun button click - trigger test execution again."""
        if hasattr(self, "current_status_view") and self.current_status_view:
            # Emit runRequested signal from status view
            self.current_status_view.runRequested.emit()
            # Switch back to test mode (show Stop button)
            self._switch_to_test_mode()
    
    def _restore_normal_mode(self):
        """Full restoration when returning to test window - show all buttons."""
        self.status_view_active = False

        # Restore Results button (Phase 2: Issue #39)
        self.sidebar.restore_results_button()

        # Show Compile button (back in test window)
        if self.compile_btn:
            self.compile_btn.show()

        # Show Run button
        if self.run_btn:
            self.run_btn.show()

        # Hide Stop button
        if self.stop_btn:
            self.stop_btn.hide()

        # Hide rerun button (back in test window)
        if hasattr(self, "rerun_btn") and self.rerun_btn:
            self.rerun_btn.hide()

        # Refresh AI panels with current configuration
        self.refresh_ai_panels()
    
    def enable_save_button(self):
        """Enable the Save button after tests complete (Phase 2: Issue #39)."""
        self.sidebar.enable_save_button()
    
    def mark_results_saved(self):
        """Mark results as saved in the UI (Phase 2: Issue #39)."""
        self.sidebar.mark_results_saved()
    
    def refresh_ai_panels(self):
        """Refresh AI panel visibility based on current configuration."""
        if hasattr(self.testing_content, "ai_panel"):
            self.testing_content.ai_panel.refresh_visibility()
    
    def handle_button_click(self, button_text: str):
        """Handle sidebar button clicks."""
        if button_text == "Back":
            # If status view is active, restore it instead of navigating away
            if self.status_view_active:
                self._on_back_requested()
                return

        # Handle Save button (Phase 2: Issue #39)
        if button_text == "Save":
            if self.status_view:
                self.status_view.save_to_database()
            return

        if button_text == "Help Center":
            if self.can_close():
                from src.app.presentation.services.navigation_service import NavigationService
                NavigationService.instance().navigate_to("help_center")
        else:
            super().handle_button_click(button_text)
    
    def _get_runner(self):
        """Get the test runner instance."""
        runner_attr = self._get_runner_attribute_name()
        return getattr(self, runner_attr) if hasattr(self, runner_attr) else None
    
    def _integrate_status_view(self, status_view):
        """
        Integrate status view into display area.

        This method handles the display area manipulation when switching to
        test execution view. Hides the testing content without deleting it.

        Args:
            status_view: The status view widget to display
        """
        if not hasattr(self, "display_area"):
            return

        # Store original content for restoration (only if not already stored)
        if (
            not hasattr(self, "_original_display_content")
            or self._original_display_content is None
        ):
            # Get the layout reference (new architecture uses property, old uses method)
            layout = self.display_area.layout if hasattr(self.display_area, "layout") and not callable(self.display_area.layout) else self.display_area.layout()
            if layout and layout.count() > 0:
                self._original_display_content = layout.itemAt(0).widget()

        # Remove current widget from layout without deleting it
        layout = self.display_area.layout if hasattr(self.display_area, "layout") and not callable(self.display_area.layout) else self.display_area.layout()
        if layout and layout.count() > 0:
            current_widget = layout.itemAt(0).widget()
            if current_widget:
                layout.removeWidget(current_widget)
                current_widget.setParent(None)
                current_widget.hide()

        # Add status view to display area
        if status_view:
            layout.addWidget(status_view)
            status_view.show()
    
    def _restore_display_area(self):
        """
        Restore original display area content.

        This method handles the display area manipulation when returning from
        test execution view. Restores the testing content without recreating it.
        """
        if not hasattr(self, "display_area"):
            return

        if not (
            hasattr(self, "_original_display_content")
            and self._original_display_content
        ):
            return

        # Remove status view from layout
        layout = self.display_area.layout if hasattr(self.display_area, "layout") and not callable(self.display_area.layout) else self.display_area.layout()
        if layout and layout.count() > 0:
            current_widget = layout.itemAt(0).widget()
            if current_widget:
                layout.removeWidget(current_widget)
                current_widget.setParent(None)
                current_widget.hide()

        # Restore original display content
        layout.addWidget(self._original_display_content)
        self._original_display_content.show()
    
    def _connect_worker_to_status_view(self, worker, status_view):
        """
        Connect worker signals to status view.

        This centralizes the signal connection logic for status views.

        Args:
            worker: Test worker instance
            status_view: Status view widget instance
        """
        # Check if worker is valid (not deleted)
        if not worker:
            return

        try:
            # Connect to view lifecycle methods
            if hasattr(worker, "testStarted") and hasattr(
                status_view, "on_test_running"
            ):
                worker.testStarted.connect(status_view.on_test_running)

            if hasattr(worker, "testCompleted") and hasattr(
                status_view, "on_test_completed"
            ):
                worker.testCompleted.connect(status_view.on_test_completed)

            if hasattr(worker, "allTestsCompleted") and hasattr(
                status_view, "on_all_tests_completed"
            ):
                worker.allTestsCompleted.connect(status_view.on_all_tests_completed)

            # Connect worker tracking signals for real-time worker status
            if hasattr(worker, "workerBusy") and hasattr(
                status_view, "on_worker_busy"
            ):
                worker.workerBusy.connect(status_view.on_worker_busy)

            if hasattr(worker, "workerIdle") and hasattr(
                status_view, "on_worker_idle"
            ):
                worker.workerIdle.connect(status_view.on_worker_idle)
        except RuntimeError:
            # Worker was deleted before we could connect - this is OK, just skip
            pass

        # Connect stop and back signals (these are safe as they're on the status view)
        if hasattr(status_view, "stopRequested"):
            status_view.stopRequested.connect(self._on_stop_requested)

        if hasattr(status_view, "backRequested"):
            status_view.backRequested.connect(self._on_back_requested)

        # Connect run signal for re-running tests
        if hasattr(status_view, "runRequested"):
            status_view.runRequested.connect(self._on_run_requested)
    
    def _on_stop_requested(self):
        """Handle stop request from status view - stop the runner."""
        runner = self._get_runner()
        if runner and hasattr(runner, "stop"):
            runner.stop()
    
    def _on_back_requested(self):
        """Handle back request from status view - restore display area."""
        self._restore_display_area()
        self._restore_normal_mode()
    
    def _on_run_requested(self):
        """
        Handle run request from status view - re-run tests.

        Subclasses should override to implement their specific test execution.
        """
        # Override in subclasses
        pass
