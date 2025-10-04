# -*- coding: utf-8 -*-
from src.app.presentation.window_controller.base_window import SidebarWindowBase
from src.app.presentation.widgets.sidebar import Sidebar
from PySide6.QtWidgets import QPushButton, QMessageBox
from PySide6.QtGui import QFont, QShowEvent
from src.app.presentation.views.comparator.comparator_display_area import ComparatorDisplay
from src.app.presentation.widgets.sidebar_widgets import TestCountSlider
# Lazy import to avoid circular dependency
# from src.app.core.tools.comparator import Comparator

class ComparatorWindow(SidebarWindowBase):
    def __init__(self, parent=None):
        # Initialize base class first
        super().__init__(parent, title=None)
        
        self.sidebar = Sidebar("Comparator")
        
        # Replace options section with slider
        options_section = self.sidebar.add_section("Number of Tests")
        self.test_count_slider = TestCountSlider(mode="comparator")
        self.test_count_slider.valueChanged.connect(self.handle_test_count_changed)
        options_section.layout().addWidget(self.test_count_slider)
        
        # Split actions into two sections
        self.action_section = self.sidebar.add_section("Actions")
        self.compile_btn = None
        self.run_btn = None
        self.stop_btn = None
        self.status_view_active = False  # Track if status view is active
        
        for button_text in ['Compile', 'Run']:
            btn = self.sidebar.add_button(button_text, self.action_section)
            btn.clicked.connect(lambda checked, text=button_text: self.handle_action_button(text))
            if button_text == 'Compile':
                self.compile_btn = btn
            elif button_text == 'Run':
                self.run_btn = btn
            
        history_section = self.sidebar.add_section("History")
        results_btn = self.sidebar.add_button('Results', history_section)
        results_btn.clicked.connect(lambda checked: self.handle_action_button('Results'))
            
        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()

        back_btn, options_btn = self.create_footer_buttons()
        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)

        # Create display area
        self.display_area = ComparatorDisplay()

        # Setup splitter with sidebar and display area
        self.setup_splitter(self.sidebar, self.display_area)
        
        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)

        # Initialize tool with multi-language support
        self._initialize_tool()
        
        # Connect filesManifestChanged signal to reinitialize tool
        self.display_area.test_tabs.filesManifestChanged.connect(self._on_files_changed)
    
    def _initialize_tool(self):
        """Initialize or reinitialize the comparator tool with current file manifest."""
        # Disconnect old comparator's signals if it exists
        if hasattr(self, 'comparator') and self.comparator:
            try:
                self.comparator.compilationOutput.disconnect()
                self.comparator.testingStarted.disconnect()
                self.comparator.testingCompleted.disconnect()
            except (RuntimeError, TypeError):
                # Signals may already be disconnected or object deleted
                pass
        
        # Load configuration
        config = self._load_config()
        
        # Get file manifest from test tabs
        manifest = self.display_area.test_tabs.get_compilation_manifest()
        files = manifest['files']
        
        # Lazy import to avoid circular dependency
        from src.app.core.tools.comparator import Comparator
        
        # Create comparator with multi-language support
        self.comparator = Comparator(
            workspace_dir=self.display_area.workspace_dir,
            files=files,
            config=config
        )
        self.comparator.compilationOutput.connect(self.display_area.console.displayOutput)
        
        # Connect runner signals to handle UI state changes
        self.comparator.testingStarted.connect(self._on_testing_started)
        self.comparator.testingCompleted.connect(self._on_testing_completed)
    
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

    # Remove the handle_edit_button method since we no longer have edit buttons

    def handle_compare_options(self):
        # Add your compare options handling logic here
        pass

    def handle_action_button(self, button_text):
        if button_text == 'Compile':
            # Clear console before compilation
            self.display_area.console.clear()
            
            # Check all files for unsaved changes
            for btn_name, btn in self.display_area.file_buttons.items():
                if btn.property("hasUnsavedChanges"):
                    reply = QMessageBox.question(
                        self,
                        "Unsaved Changes",
                        f"Do you want to save changes to {btn_name}?",
                        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                    )
                    
                    if reply == QMessageBox.Save:
                        # Switch to this file (skip save prompt since we already handled it)
                        self.display_area._handle_file_button(btn_name, skip_save_prompt=True)
                        if not self.display_area.editor.saveFile():
                            return
                    elif reply == QMessageBox.Cancel:
                        return

            self.comparator.compile_all()
        elif button_text == 'Run':
            # Run comparison tests
            test_count = self.test_count_slider.value()
            self.comparator.run_comparison_test(test_count)
        elif button_text == 'Stop':
            # Stop running tests
            if hasattr(self.comparator, 'stop'):
                self.comparator.stop()
        elif button_text == 'Results':
            # Navigate to results window
            if self.can_close():
                self.parent.window_manager.show_window('results')

    def handle_button_click(self, button_text):
        if button_text == 'Back':
            # If status view is active, restore it instead of navigating away
            if self.status_view_active:
                self._on_back_requested()
                return
        
        if (button_text == 'Help Center'):
            if self.can_close():
                self.parent.window_manager.show_window('help_center')
        else:
            super().handle_button_click(button_text)
    
    def _get_runner(self):
        """Get the test runner instance"""
        return self.comparator if hasattr(self, 'comparator') else None

    def handle_test_count_changed(self, value):
        # Handle the slider value change
        print(f"Test count changed to: {value}")
        # You can store this value or use it in your comparison testing logic

    def showEvent(self, event):
        """Handle window show event - reload AI config and refresh AI panels"""
        super().showEvent(event)
        # Reload AI configuration to pick up any changes made while window was closed
        try:
            from src.app.core.ai import reload_ai_config
            reload_ai_config()
        except ImportError:
            pass  # AI module not available
    
    def _on_testing_started(self):
        """Handle testing started signal - create and show status view"""
        # Create status view
        from src.app.presentation.views.comparator.comparator_status_view import ComparatorStatusView
        status_view = ComparatorStatusView(parent=self)
        
        # Store reference
        self.status_view = status_view
        self.current_status_view = status_view
        
        # Get worker and connect signals
        worker = self.comparator.get_current_worker()
        if worker and status_view:
            self._connect_worker_to_status_view(worker, status_view)
            
            # Connect allTestsCompleted to switch buttons
            try:
                if hasattr(worker, 'allTestsCompleted'):
                    worker.allTestsCompleted.connect(self._switch_to_completed_mode)
            except RuntimeError:
                pass  # Worker deleted, ignore
            
            # Notify view that tests are starting
            if hasattr(status_view, 'on_tests_started'):
                status_view.on_tests_started(self.test_count_slider.value())
        
        # Integrate status view into display area
        self._integrate_status_view(status_view)
        
        # Switch to test mode (hide compile/run, show stop)
        self._switch_to_test_mode()
    
    def _on_testing_completed(self):
        """Handle testing completed signal - switch to completed mode but stay in status view"""
        # When tests are stopped, switch to Run button but keep status view open
        self._switch_to_completed_mode()
    
    def _switch_to_test_mode(self):
        """Hide Compile and Run buttons, show Stop button when tests start"""
        self.status_view_active = True
        
        # Hide Compile button during test execution
        if self.compile_btn:
            self.compile_btn.hide()
        
        # Hide Run button
        if self.run_btn:
            self.run_btn.hide()
        
        if not self.stop_btn:
            # Create Stop button dynamically
            self.stop_btn = self.sidebar.add_button('Stop', self.action_section)
            self.stop_btn.clicked.connect(lambda: self.handle_action_button('Stop'))
        
        if self.stop_btn:
            self.stop_btn.show()
            
        # Hide rerun button during test execution
        if hasattr(self, 'rerun_btn') and self.rerun_btn:
            self.rerun_btn.hide()
    
    def _switch_to_completed_mode(self):
        """Show Run button after tests complete (while viewing status)"""
        # Hide Stop button
        if self.stop_btn:
            self.stop_btn.hide()
        
        # Create and show Rerun button
        if not hasattr(self, 'rerun_btn') or not self.rerun_btn:
            self.rerun_btn = self.sidebar.add_button('Run', self.action_section)
            self.rerun_btn.clicked.connect(self._handle_rerun_tests)
        
        if self.rerun_btn:
            self.rerun_btn.show()
    
    def _handle_rerun_tests(self):
        """Handle rerun button click - trigger test execution again"""
        if hasattr(self, 'current_status_view') and self.current_status_view:
            # Emit runRequested signal from status view
            self.current_status_view.runRequested.emit()
            # Switch back to test mode (show Stop button)
            self._switch_to_test_mode()
    
    def _on_run_requested(self):
        """Handle run request from status view - re-run comparison tests"""
        # Run comparison tests with same test count
        test_count = self.test_count_slider.value()
        self.comparator.run_comparison_test(test_count)
    
    def _restore_normal_mode(self):
        """Full restoration when returning to test window - show all buttons"""
        self.status_view_active = False
        
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
        if hasattr(self, 'rerun_btn') and self.rerun_btn:
            self.rerun_btn.hide()
        
        # Refresh AI panels with current configuration
        self.refresh_ai_panels()

    def refresh_ai_panels(self):
        """Refresh AI panel visibility based on current configuration"""
        if hasattr(self.display_area, 'ai_panel'):
            self.display_area.ai_panel.refresh_visibility()
