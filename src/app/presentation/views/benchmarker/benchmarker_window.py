# -*- coding: utf-8 -*-
from src.app.presentation.views.base_window import SidebarWindowBase
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QShowEvent
from src.app.presentation.widgets.sidebar import Sidebar
from src.app.presentation.views.benchmarker.benchmarker_display_area import BenchmarkerDisplay
from src.app.presentation.widgets.sidebar_widgets import TestCountSlider, LimitsInputWidget
# Lazy import to avoid circular dependency
# from src.app.core.tools.benchmarker import Benchmarker

class BenchmarkerWindow(SidebarWindowBase):
    def __init__(self, parent=None):
        super().__init__(parent, title=None)
        
        self.sidebar = Sidebar("Benchmarker")
        
        # Add resource limits input section with parallel time and memory inputs
        limits_section = self.sidebar.add_section("Resource Limits")
        self.limits_widget = LimitsInputWidget()
        self.limits_widget.timeLimitChanged.connect(self.handle_time_limit_changed)
        self.limits_widget.memoryLimitChanged.connect(self.handle_memory_limit_changed)
        limits_section.layout().addWidget(self.limits_widget)
        
        # Add test count slider section below resource limits
        test_count_section = self.sidebar.add_section("Number of Tests")
        self.test_count_slider = TestCountSlider(mode="benchmarker")
        self.test_count_slider.valueChanged.connect(self.handle_test_count_changed)
        test_count_section.layout().addWidget(self.test_count_slider)
        
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
        self.display_area = BenchmarkerDisplay()

        # Setup splitter with sidebar and display area
        self.setup_splitter(self.sidebar, self.display_area)
        
        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)

        # Initialize tool with multi-language support
        self._initialize_tool()
        
        # Connect filesManifestChanged signal to reinitialize tool
        self.display_area.test_tabs.filesManifestChanged.connect(self._on_files_changed)
    
    def _initialize_tool(self):
        """Initialize or reinitialize the benchmarker tool with current file manifest."""
        # Load configuration
        config = self._load_config()
        
        # Get file manifest from test tabs
        manifest = self.display_area.test_tabs.get_compilation_manifest()
        files = manifest['files']
        
        # Lazy import to avoid circular dependency
        from src.app.core.tools.benchmarker import Benchmarker
        
        # Create benchmarker with multi-language support
        self.benchmarker = Benchmarker(
            workspace_dir=self.display_area.workspace_dir,
            files=files,
            config=config
        )
        self.benchmarker.compilationOutput.connect(self.display_area.console.displayOutput)
        
        # Set parent window for unified status view integration
        self.benchmarker.set_parent_window(self)
        
        # Connect runner signals for clean separation of concerns
        self.benchmarker.testingStarted.connect(self._switch_to_test_mode)
        self.benchmarker.testingCompleted.connect(self._on_tests_completed)
    
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

            self.benchmarker.compile_all()
        elif button_text == 'Run':
            time_limit = self.limits_widget.get_time_limit()
            memory_limit = self.limits_widget.get_memory_limit()
            test_count = self.test_count_slider.value()
            self.benchmarker.run_benchmark_test(time_limit, memory_limit, test_count)
        elif button_text == 'Stop':
            # Stop running tests
            if hasattr(self.benchmarker, 'stop'):
                self.benchmarker.stop()
        elif button_text == 'Results':
            # Navigate to results window
            if self.can_close():
                self.parent.window_manager.show_window('results')

    def handle_button_click(self, button_text):
        if button_text == 'Back':
            # If status view is active, restore it instead of navigating away
            if self.status_view_active:
                # Get the runner and call its back handler
                runner = self._get_runner()
                if runner and hasattr(runner, '_handle_back_request'):
                    runner._handle_back_request()
                    # Explicitly restore normal mode after back navigation
                    self._restore_normal_mode()
                return
        
        if button_text == 'Help Center':
            if self.can_close():
                self.parent.window_manager.show_window('help_center')
        else:
            super().handle_button_click(button_text)
    
    def _get_runner(self):
        """Get the test runner instance"""
        return self.benchmarker if hasattr(self, 'benchmarker') else None

    def handle_time_limit_changed(self, value):
        print(f"Time limit changed to: {value} ms")

    def handle_memory_limit_changed(self, value):
        print(f"Memory limit changed to: {value} MB")
    
    def handle_test_count_changed(self, value):
        print(f"Test count changed to: {value} tests")

    def showEvent(self, event):
        """Handle window show event - reload AI config and refresh AI panels"""
        super().showEvent(event)
        # Reload AI configuration to pick up any changes made while window was closed
        try:
            from src.app.core.ai import reload_ai_config
            reload_ai_config()
        except ImportError:
            pass  # AI module not available
    
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
    
    def _on_tests_completed(self):
        """Called when tests finish - show Run, hide Stop (Compile stays hidden until back to window)"""
        # Show Run button (can run again from status view)
        if self.run_btn:
            self.run_btn.show()
        
        # Hide Stop button (tests finished)
        if self.stop_btn:
            self.stop_btn.hide()
        
        # Note: Compile button stays hidden until back to test window
        # Refresh AI panels with current configuration
        self.refresh_ai_panels()
    
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
        
        # Refresh AI panels with current configuration
        self.refresh_ai_panels()

    def refresh_ai_panels(self):
        """Refresh AI panel visibility based on current configuration"""
        if hasattr(self.display_area, 'ai_panel'):
            self.display_area.ai_panel.refresh_visibility()
