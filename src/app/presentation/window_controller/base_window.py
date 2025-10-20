from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSplitter, QWidget

from src.app.presentation.styles.fonts.emoji import set_emoji_font
from src.app.presentation.styles.style import SPLITTER_STYLE


class SidebarWindowBase(QWidget):
    def __init__(self, parent=None, title=None):
        super().__init__(parent)
        self.parent = parent
        self.has_unsaved_changes = False

        # Setup layout
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        # Create splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet(SPLITTER_STYLE)  # Add this line
        self.layout().addWidget(self.splitter)

        # Initialize sidebar and display area if title is provided
        if title:
            self.init_sidebar(title)

    def init_sidebar(self, title):
        """Initialize sidebar with title and common features"""
        # Import here to avoid circular imports
        from src.app.presentation.widgets.display_area import DisplayArea
        from src.app.presentation.widgets.sidebar import Sidebar

        self.sidebar = Sidebar(title)
        self.display_area = DisplayArea()

        back_btn, options_btn = self.create_footer_buttons()
        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()
        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)

        self.setup_splitter(self.sidebar, self.display_area)
        self.sidebar.button_clicked.connect(self.handle_button_click)

    def create_footer_buttons(self):
        back_btn = QPushButton("Back")
        back_btn.setObjectName("back_button")
        back_btn.clicked.connect(lambda: self.handle_button_click("Back"))

        options_btn = QPushButton("⚙️")
        options_btn.setObjectName("back_button")
        set_emoji_font(options_btn)
        options_btn.setFont(QFont("Segoe UI", 14))
        options_btn.clicked.connect(lambda: self.handle_button_click("Options"))

        return back_btn, options_btn

    def setup_splitter(self, sidebar, content):
        self.splitter.addWidget(sidebar)
        self.splitter.addWidget(content)
        sidebar.setMinimumWidth(250)
        content.setMinimumWidth(600)
        self.update_splitter_sizes()

    def update_splitter_sizes(self):
        """Update splitter sizes to maintain proper proportions"""
        total_width = self.width()
        if total_width > 0:
            self.splitter.setSizes([250, 850])

    def resizeEvent(self, event):
        """Handle resize events to maintain splitter proportions"""
        super().resizeEvent(event)
        self.update_splitter_sizes()

    def cleanup(self):
        """Clean up resources. Override in subclasses if needed."""

    def can_close(self):
        """Check if window can be closed. Override to check for unsaved changes."""
        return not self.has_unsaved_changes

    def handle_button_click(self, button_text):
        if button_text == "Back":
            if self.can_close():
                from src.app.presentation.services.navigation_service import NavigationService
                if not NavigationService.instance().go_back():
                    NavigationService.instance().navigate_to("main")
        elif button_text == "Options":
            # Lazy import to avoid slow startup
            from src.app.core.config import ConfigView

            config_dialog = ConfigView(self)
            config_dialog.configSaved.connect(self._on_config_changed)
            config_dialog.exec()

    def _on_config_changed(self, config):
        """
        Handle configuration changes - reload AI config, refresh AI panels, and reinitialize tools.

        This enables hot-reload of configuration changes without requiring app restart.
        When compilation flags, compiler settings, or other config changes are saved,
        the tools (comparator/validator/benchmarker) are automatically reinitialized
        to use the new settings.

        Args:
            config: The new configuration dictionary
        """
        # Reload AI configuration to pick up changes
        try:
            from src.app.core.ai import reload_ai_config

            reload_ai_config()
        except ImportError:
            pass  # AI module not available

        # Refresh AI panels with new configuration
        if hasattr(self, "refresh_ai_panels"):
            self.refresh_ai_panels()

        # Reinitialize tools (comparator/validator/benchmarker) to pick up new compilation settings
        # This allows compilation flags, compiler selection, optimization levels, etc. to take
        # effect immediately without restarting the application
        if hasattr(self, "_initialize_tool"):
            self._initialize_tool()

            # Inform user that tools have been reloaded (optional visual feedback)
            if hasattr(self, "display_area") and hasattr(self.display_area, "console"):
                self.display_area.console.displayOutput(
                    "✓ Configuration updated - compilation settings reloaded", "success"
                )

    # ===== UI State Management Methods for Test Execution =====
    # These methods handle UI coordination when tests are running

    def _switch_to_test_mode(self):
        """
        Switch UI to test mode - hide compile/run buttons, show stop button.

        This method should be called by subclasses when tests start.
        Subclasses should override to implement their specific button management.
        """
        # Override in subclasses

    def _restore_normal_mode(self):
        """
        Restore UI to normal mode - show compile/run buttons, hide stop button.

        This method should be called by subclasses when tests complete.
        Subclasses should override to implement their specific button management.
        """
        # Override in subclasses

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
        """Handle stop request from status view - stop the runner"""
        runner = self._get_runner()
        if runner and hasattr(runner, "stop"):
            runner.stop()

    def _on_back_requested(self):
        """Handle back request from status view - restore display area"""
        self._restore_display_area()
        self._restore_normal_mode()

    def _on_run_requested(self):
        """
        Handle run request from status view - re-run tests.

        Subclasses should override to implement their specific test execution.
        """
        # Override in subclasses

    def _get_runner(self):
        """
        Get the test runner instance.

        Should be overridden by subclasses to return their specific runner.

        Returns:
            Test runner instance or None
        """
        return None  # Override in subclasses
