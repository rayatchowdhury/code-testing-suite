# -*- coding: utf-8 -*-
from src.app.presentation.views.base_window import SidebarWindowBase
from PySide6.QtWidgets import QMessageBox
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
        action_section = self.sidebar.add_section("Actions")
        for button_text in ['Compile', 'Run']:
            btn = self.sidebar.add_button(button_text, action_section)
            btn.clicked.connect(lambda checked, text=button_text: self.handle_action_button(text))
            
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

        # Lazy import to avoid circular dependency
        from src.app.core.tools.benchmarker import Benchmarker
        self.benchmarker = Benchmarker(self.display_area.workspace_dir)
        self.benchmarker.compilationOutput.connect(self.display_area.console.displayOutput)

    def handle_action_button(self, button_text):
        if button_text == 'Compile':
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
                        # Switch to this file
                        self.display_area._handle_file_button(btn_name)
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
        elif button_text == 'Results':
            # Navigate to results window
            if self.can_close():
                self.parent.window_manager.show_window('results')

    def handle_button_click(self, button_text):
        if button_text == 'Help Center':
            if self.can_close():
                self.parent.window_manager.show_window('help_center')
        else:
            super().handle_button_click(button_text)

    def handle_time_limit_changed(self, value):
        print(f"Time limit changed to: {value} ms")

    def handle_memory_limit_changed(self, value):
        print(f"Memory limit changed to: {value} MB")
    
    def handle_test_count_changed(self, value):
        print(f"Test count changed to: {value} tests")

    def refresh_ai_panels(self):
        """Refresh AI panel visibility based on current configuration"""
        if hasattr(self.display_area, 'ai_panel'):
            self.display_area.ai_panel.refresh_visibility()
