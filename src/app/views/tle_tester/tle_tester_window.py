# -*- coding: utf-8 -*-
from ...views.base_window import SidebarWindowBase
from PySide6.QtWidgets import QMessageBox
from ...widgets.sidebar import Sidebar
from ...views.tle_tester.tle_tester_display_area import TLETesterDisplay
from ...views.tle_tester.time_limit_slider import TimeLimitSlider
from ...tools.tle_runner import TLERunner

class TLETesterWindow(SidebarWindowBase):
    def __init__(self, parent=None):
        super().__init__(parent, title=None)
        
        self.sidebar = Sidebar("TLE Tester")
        
        # Add time limit slider section (now in milliseconds)
        options_section = self.sidebar.add_section("Time Limit (ms)")
        self.time_limit_slider = TimeLimitSlider()
        self.time_limit_slider.valueChanged.connect(self.handle_time_limit_changed)
        options_section.layout().addWidget(self.time_limit_slider)
        
        action_section = self.sidebar.add_section("Actions")
        for button_text in ['Compile', 'Run', 'Results']:
            btn = self.sidebar.add_button(button_text, action_section)
            btn.clicked.connect(lambda checked, text=button_text: self.handle_action_button(text))
            
        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()

        back_btn, options_btn = self.create_footer_buttons()
        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)

        # Create display area
        self.display_area = TLETesterDisplay()

        # Setup splitter with sidebar and display area
        self.setup_splitter(self.sidebar, self.display_area)
        
        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)

        self.tle_runner = TLERunner(self.display_area.workspace_dir)
        self.tle_runner.compilationOutput.connect(self.display_area.console.displayOutput)

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

            self.tle_runner.compile_all()
        elif button_text == 'Run':
            time_limit = self.time_limit_slider.value()
            self.tle_runner.run_tle_test(time_limit)
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

    def refresh_ai_panels(self):
        """Refresh AI panel visibility based on current configuration"""
        if hasattr(self.display_area, 'ai_panel'):
            self.display_area.ai_panel.refresh_visibility()
