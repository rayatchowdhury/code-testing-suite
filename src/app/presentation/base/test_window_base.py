"""
Base class for test tool windows (Benchmarker, Validator, Comparator).

TestWindowBase consolidates 588 lines of duplicated code from test windows,
providing template methods for subclasses to customize behavior.
"""

import logging
from abc import abstractmethod
from typing import Optional
from PySide6.QtWidgets import QWidget, QPushButton
from PySide6.QtGui import QShowEvent
from .content_window_base import ContentWindowBase
from .protocols import TestRunner

logger = logging.getLogger(__name__)

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
        super().__init__(parent)
        self._runner: Optional[TestRunner] = None
        self.compile_btn: Optional['QPushButton'] = None
        self.run_btn: Optional['QPushButton'] = None
        self.stop_btn: Optional['QPushButton'] = None
        self.rerun_btn: Optional['QPushButton'] = None
        self.status_view_active = False
        self.current_status_view: Optional['QWidget'] = None
        self._original_display_content: Optional['QWidget'] = None
    
    # ===== TEMPLATE METHODS (must override) =====
    
    @abstractmethod
    def _create_runner(self) -> TestRunner:
        """Create specific runner (Benchmarker, Validator, Comparator)."""
        pass
    
    @abstractmethod
    def _create_status_view(self) -> 'QWidget':
        """Create specific status view."""
        pass
    
    @abstractmethod
    def _get_runner_attribute_name(self) -> str:
        """Return runner attribute name: 'benchmarker', 'validator_runner', or 'comparator'."""
        pass
    
    @abstractmethod
    def _get_run_method_name(self) -> str:
        """Return run method name: 'run_benchmark_test', 'run_validation_test', or 'run_comparison_test'."""
        pass
    
    # ===== SHARED IMPLEMENTATION (588 lines extracted) =====
    
    def _setup_standard_sidebar(self, action_section):
        """Setup standard sidebar buttons (Compile, Run, Results, Help, Back, Options)."""
        for button_text in ["Compile", "Run"]:
            btn = self.sidebar.add_button(button_text, action_section)
            btn.clicked.connect(
                lambda _, text=button_text: self.handle_action_button(text)
            )
            if button_text == "Compile":
                self.compile_btn = btn
            elif button_text == "Run":
                self.run_btn = btn

        self.sidebar.add_results_button()
        self.sidebar.add_footer_button_divider()
        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()

        back_btn, options_btn = self.create_footer_buttons()
        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)
    
    def _check_unsaved_changes(self) -> bool:
        """Check for unsaved changes and prompt user to save.
        
        Returns:
            True if should proceed (saved/discarded), False if cancelled
        """
        from src.app.presentation.services import ErrorHandlerService
        error_service = ErrorHandlerService.instance()
        
        for btn_name, btn in self.testing_content.file_buttons.items():
            if btn.property("hasUnsavedChanges"):
                from PySide6.QtWidgets import QMessageBox
                
                reply = error_service.ask_save_discard_cancel(
                    "Unsaved Changes",
                    f"Do you want to save changes to {btn_name}?",
                    self
                )

                if reply == QMessageBox.Save:
                    self.testing_content._handle_file_button(
                        btn_name, skip_save_prompt=True
                    )
                    if not self.testing_content.editor.saveFile():
                        return False
                elif reply == QMessageBox.Cancel:
                    return False
        
        return True
    
    def _finalize_window_setup(self):
        """Finalize window setup - connect signals and initialize tool."""
        self.setup_splitter(self.sidebar, self.display_area)

        self.sidebar.button_clicked.connect(self.handle_button_click)

        self._initialize_tool()

        self.testing_content.test_tabs.filesManifestChanged.connect(self._on_files_changed)
    
    def _initialize_tool(self):
        # Disconnect old runner's signals if it exists
        runner_attr = self._get_runner_attribute_name()
        old_runner = getattr(self, runner_attr, None)
        if old_runner is not None:
            try:
                old_runner.compilationOutput.disconnect()
                old_runner.testingStarted.disconnect()
                old_runner.testingCompleted.disconnect()
            except (RuntimeError, TypeError):
                # Signals may already be disconnected or object deleted
                pass

        config = self._load_config()

        manifest = self.testing_content.test_tabs.get_compilation_manifest()
        files = manifest["files"]

        runner = self._create_runner()
        
        # Store runner with appropriate attribute name
        setattr(self, runner_attr, runner)
        self._runner = runner
        
        runner.compilationOutput.connect(
            self.testing_content.console.displayOutput
        )

        runner.testingStarted.connect(self._on_testing_started)
        runner.testingCompleted.connect(self._on_testing_completed)
    
    def _load_config(self):
        try:
            from src.app.core.config import ConfigManager

            config_manager = ConfigManager()
            return config_manager.load_config()
        except (ImportError, AttributeError, FileNotFoundError, OSError) as e:
            # Fallback to empty config if loading fails
            return {}
    
    def _on_files_changed(self):
        # Reinitialize tool with new file configuration
        self._initialize_tool()
    
    def showEvent(self, event: 'QShowEvent'):
        """Reload AI config and refresh AI panels."""
        super().showEvent(event)
        # Reload AI configuration to pick up any changes made while window was closed
        try:
            from src.app.core.ai import reload_ai_config

            reload_ai_config()
        except ImportError:
            pass  # AI module not available
    
    def _on_testing_started(self):
        # Create status view using template method
        status_view = self._create_status_view()

        # Set runner for on-demand saving (Issue #39)
        runner = getattr(self, self._get_runner_attribute_name())
        status_view.set_runner(runner)

        # Replace Results button with Save button (Phase 2: Issue #39)
        self.sidebar.replace_results_with_save_button()

        self.current_status_view = status_view

        worker = runner.get_current_worker()
        if worker and status_view:
            self._connect_worker_to_status_view(worker, status_view)

            try:
                # Connect allTestsCompleted signal if it exists
                worker.allTestsCompleted.connect(self._switch_to_completed_mode)
            except (RuntimeError, AttributeError):
                pass  # Worker deleted or signal doesn't exist, ignore

            # Notify view that tests are starting
            try:
                status_view.on_tests_started(self.test_count_slider.value())
            except AttributeError:
                pass  # Method doesn't exist on this status view

        # Integrate status view into display area
        self._integrate_status_view(status_view)

        # Switch to test mode (hide compile/run, show stop)
        self._switch_to_test_mode()
    
    def _on_testing_completed(self):
        # When tests are stopped, switch to Run button but keep status view open
        self._switch_to_completed_mode()
    
    def _switch_to_test_mode(self):
        """Switch UI to test execution mode: show Stop, hide Compile/Run/Rerun."""
        self.status_view_active = True

        # Hide normal buttons
        for btn in [self.compile_btn, self.run_btn, self.rerun_btn]:
            if btn:
                btn.hide()

        # Create and show Stop button
        if not self.stop_btn:
            self.stop_btn = self.sidebar.add_button("Stop", self.action_section)
            self.stop_btn.clicked.connect(lambda: self.handle_action_button("Stop"))
        self.stop_btn.show()
    
    def _switch_to_completed_mode(self):
        """Switch UI to completed mode: show Rerun, hide Stop."""
        # Hide Stop button
        if self.stop_btn:
            self.stop_btn.hide()

        # Create and show Rerun button
        if not self.rerun_btn:
            self.rerun_btn = self.sidebar.add_button("Run", self.action_section)
            self.rerun_btn.clicked.connect(self._handle_rerun_tests)
        self.rerun_btn.show()
    
    def _handle_rerun_tests(self):
        if self.current_status_view is not None:
            # Emit runRequested signal from status view
            self.current_status_view.runRequested.emit()
            # Switch back to test mode (show Stop button)
            self._switch_to_test_mode()
    
    def _restore_normal_mode(self):
        """Restore UI to normal mode: show Compile/Run, hide Stop/Rerun, restore Results button."""
        self.status_view_active = False

        # Restore Results button (Phase 2: Issue #39)
        self.sidebar.restore_results_button()

        # Show normal buttons
        for btn in [self.compile_btn, self.run_btn]:
            if btn:
                btn.show()

        # Hide test execution buttons
        for btn in [self.stop_btn, self.rerun_btn]:
            if btn:
                btn.hide()

        # Refresh AI panels with current configuration
        self.refresh_ai_panels()
    
    def enable_save_button(self):
        self.sidebar.enable_save_button()
    
    def mark_results_saved(self):
        self.sidebar.mark_results_saved()
    
    def refresh_ai_panels(self):
        # testing_content always has ai_panel attribute
        if self.testing_content.ai_panel is not None:
            self.testing_content.ai_panel.refresh_visibility()
    
    def handle_button_click(self, button_text: str):
        # Back button when status view is active - restore display instead of navigating
        if button_text == "Back" and self.status_view_active:
            # Check if tests are running and show warning
            if self._is_test_running():
                logger.debug("Back from status view blocked - tests running")
                from src.app.presentation.services import ErrorHandlerService
                error_service = ErrorHandlerService.instance()
                error_service.show_warning(
                    "Tests Running",
                    "Cannot navigate while tests are running.\n\nPlease stop the current test execution first.",
                    self
                )
                return
            self._on_back_requested()
            return

        # Save button - save current test results to database
        if button_text == "Save":
            if self.current_status_view:
                self.current_status_view.save_to_database()
            return

        # Help Center - check if tests running before navigating
        if button_text == "Help Center":
            if self._is_test_running():
                logger.debug("Help Center navigation blocked - tests running")
                from src.app.presentation.services import ErrorHandlerService
                error_service = ErrorHandlerService.instance()
                error_service.show_warning(
                    "Tests Running",
                    "Cannot navigate while tests are running.\n\nPlease stop the current test execution first.",
                    self
                )
                return
            if self.can_close() and self.router:
                self.router.navigate_to("help_center")
            return
        
        # Delegate other buttons to parent
        super().handle_button_click(button_text)
    
    def _get_runner(self) -> Optional[TestRunner]:
        """Get the test runner instance (unified access point)."""
        return self._runner
    
    def _integrate_status_view(self, status_view):
        """Integrate status view into display area (hides testing content without deleting)."""
        # display_area always exists from ContentWindowBase
        # Swap content and store original for restoration
        if status_view:
            old_widget = self.display_area.swap_content(status_view)
            # Only store if not already stored
            if self._original_display_content is None:
                self._original_display_content = old_widget
    
    def _restore_display_area(self):
        """Restore original display area content (without recreating)."""
        # display_area always exists from ContentWindowBase
        if self._original_display_content is None:
            return

        # Swap back to original content (status view is removed but not deleted)
        self.display_area.swap_content(self._original_display_content)
    
    def _connect_worker_to_status_view(self, worker, status_view):
        """Connect worker signals to status view."""
        # Check if worker is valid (not deleted)
        if not worker:
            return

        try:
            # Connect to view lifecycle methods
            # Use try-except instead of hasattr for Qt signals
            try:
                worker.testStarted.connect(status_view.on_test_running)
            except AttributeError:
                pass  # Signal/slot doesn't exist
            
            try:
                worker.testCompleted.connect(status_view.on_test_completed)
            except AttributeError:
                pass
            
            try:
                worker.allTestsCompleted.connect(status_view.on_all_tests_completed)
            except AttributeError:
                pass

            # Connect worker tracking signals for real-time worker status
            try:
                worker.workerBusy.connect(status_view.on_worker_busy)
            except AttributeError:
                pass
            
            try:
                worker.workerIdle.connect(status_view.on_worker_idle)
            except AttributeError:
                pass
        except RuntimeError:
            # Worker was deleted before we could connect - this is OK, just skip
            pass

        # Connect stop and back signals (these are safe as they're on the status view)
        try:
            status_view.stopRequested.connect(self._on_stop_requested)
        except AttributeError:
            pass
        
        try:
            status_view.backRequested.connect(self._on_back_requested)
        except AttributeError:
            pass

        # Connect run signal for re-running tests
        try:
            status_view.runRequested.connect(self._on_run_requested)
        except AttributeError:
            pass
    
    def _on_stop_requested(self):
        runner = self._get_runner()
        if runner is not None:
            try:
                runner.stop()
            except AttributeError:
                pass  # Runner doesn't have stop method
    
    def _on_back_requested(self):
        self._restore_display_area()
        self._restore_normal_mode()
    
    def _on_run_requested(self):
        """Override in subclasses to implement test execution."""
        # Override in subclasses
        pass
