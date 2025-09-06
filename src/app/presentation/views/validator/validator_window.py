# -*- coding: utf-8 -*-
from src.app.presentation.views.base_window import SidebarWindowBase
from src.app.widgets.sidebar import Sidebar
from PySide6.QtWidgets import QPushButton, QMessageBox
from PySide6.QtGui import QFont
from src.app.presentation.views.validator.validator_display_area import ValidatorDisplay
from src.app.presentation.views.validator.test_count_slider import TestCountSlider
# Lazy import to avoid circular dependency
# from src.app.core.tools.validator import Validator

class ValidatorWindow(SidebarWindowBase):
    def __init__(self, parent=None):
        # Initialize base class first
        super().__init__(parent, title=None)
        
        self.sidebar = Sidebar("Validator")
        
        # Replace options section with slider (exactly like comparator)
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
        self.display_area = ValidatorDisplay()

        # Setup splitter with sidebar and display area
        self.setup_splitter(self.sidebar, self.display_area)
        
        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)

        # Lazy import to avoid circular dependency
        from src.app.core.tools.validator import Validator
        self.validator = Validator()
        # Connect to console if it has displayOutput method
        if hasattr(self.display_area.console, 'displayOutput'):
            self.validator.validationComplete.connect(
                lambda result: self.display_area.console.displayOutput(f"Validation completed: Score {result.get('overall_score', 0)}/100")
            )

    # Remove the handle_edit_button method since we no longer have edit buttons

    def handle_validate_options(self):
        # Add your validate options handling logic here
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

            self.display_area.compile_and_run_code()
        elif button_text == 'Run':
            test_count = self.test_count_slider.get_value()
            self.run_validation(test_count)
        elif button_text == 'Results':
            # Navigate to results window
            if self.can_close():
                self.parent.window_manager.show_window('results')

    def run_validation(self, test_count):
        """Run validation (renamed from validation_level to test_count to match pattern)"""
        current_file = self.display_area.editor.currentFilePath
        if current_file:
            # Set validation strictness
            self.validator.set_strictness(test_count)
            
            # Run validation
            self.validator.validate_code(current_file)
        else:
            QMessageBox.warning(self, "No File", "Please load a file to validate first.")

    def handle_button_click(self, button_text):
        """Handle sidebar button clicks"""
        if button_text == 'Help Center':
            if self.can_close():
                self.parent.window_manager.show_window('help_center')
        else:
            super().handle_button_click(button_text)

    def handle_test_count_changed(self, value):
        """Handle test count slider change (renamed to match comparator pattern)"""
        if hasattr(self.validator, 'set_strictness'):
            self.validator.set_strictness(value)
        print(f"Test count (validation strictness) set to: {value}")

    def refresh_ai_panels(self):
        """Refresh AI panel visibility based on current configuration"""
        if hasattr(self.display_area, 'ai_panel'):
            self.display_area.ai_panel.refresh_visibility()
