# -*- coding: utf-8 -*-
from src.app.presentation.views.base_window import SidebarWindowBase
from src.app.widgets.sidebar import Sidebar
from PySide6.QtWidgets import QPushButton, QMessageBox
from PySide6.QtGui import QFont
from src.app.presentation.views.comparator.comparator_display_area import ComparatorDisplay
from src.app.presentation.views.comparator.test_count_slider import TestCountSlider
# Lazy import to avoid circular dependency
# from src.app.core.tools.stresser import Stresser

class ComparatorWindow(SidebarWindowBase):
    def __init__(self, parent=None):
        # Initialize base class first
        super().__init__(parent, title=None)
        
        self.sidebar = Sidebar("Comparator")
        
        # Replace options section with slider
        options_section = self.sidebar.add_section("Number of Tests")
        self.test_count_slider = TestCountSlider()
        self.test_count_slider.valueChanged.connect(self.handle_test_count_changed)
        options_section.layout().addWidget(self.test_count_slider)
        
        action_section = self.sidebar.add_section("Actions")
        for button_text in ['Compile', 'Run', 'Results']:
            btn = self.sidebar.add_button(button_text, action_section)
            btn.clicked.connect(lambda checked, text=button_text: self.handle_action_button(text))
            
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

        # Lazy import to avoid circular dependency
        from src.app.core.tools.stresser import Stresser
        self.stresser = Stresser(self.display_area.workspace_dir)
        self.stresser.compilationOutput.connect(self.display_area.console.displayOutput)

    # Remove the handle_edit_button method since we no longer have edit buttons

    def handle_compare_options(self):
        # Add your compare options handling logic here
        pass

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

            self.stresser.compile_all()
        elif button_text == 'Run':
            test_count = self.test_count_slider.value()
            self.stresser.run_stress_test(test_count)
        elif button_text == 'Results':
            # Navigate to results window
            if self.can_close():
                self.parent.window_manager.show_window('results')

    def handle_button_click(self, button_text):
        if (button_text == 'Help Center'):
            if self.can_close():
                self.parent.window_manager.show_window('help_center')
        else:
            super().handle_button_click(button_text)

    def handle_test_count_changed(self, value):
        # Handle the slider value change
        print(f"Test count changed to: {value}")
        # You can store this value or use it in your stress testing logic

    def refresh_ai_panels(self):
        """Refresh AI panel visibility based on current configuration"""
        if hasattr(self.display_area, 'ai_panel'):
            self.display_area.ai_panel.refresh_visibility()
