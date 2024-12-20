from views.base_window import SidebarWindowBase
from widgets.sidebar import Sidebar
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QFont
from views.stress_tester.stress_tester_display_area import StressTesterDisplay
from views.stress_tester.test_count_slider import TestCountSlider
from tools.stresser import Stresser

class StressTesterWindow(SidebarWindowBase):
    def __init__(self, parent=None):
        # Initialize base class first
        super().__init__(parent, title=None)
        
        self.sidebar = Sidebar("Stress Tester")
        
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
        self.display_area = StressTesterDisplay()

        # Setup splitter with sidebar and display area
        self.setup_splitter(self.sidebar, self.display_area)
        
        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)

        self.stresser = Stresser(self.display_area.workspace_dir)
        self.stresser.compilationOutput.connect(self.display_area.console.displayOutput)

    # Remove the handle_edit_button method since we no longer have edit buttons

    def handle_stress_options(self):
        # Add your stress options handling logic here
        pass

    def handle_action_button(self, button_text):
        if button_text == 'Compile':
            self.stresser.compile_all()
        elif button_text == 'Run':
            test_count = self.test_count_slider.value()
            self.stresser.run_stress_test(test_count)
        # Add your action button handling logic here
        pass

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
