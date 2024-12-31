#this is the main window for the tle tester application
#it contains the two sections: sidebar and display area
#sidebar contains 6 sections:
# 1. edit code section  
# ---edit generator code
# ---edit test code
# 2. tle options section
# ---here you can set the number of tests to run
# ---set the time limit for each test
# 3. compile section
# ---compile the code
# 4. run section
# ---run the stress test, if a test takes longer than the time limit, it'll be stopped
# 5. results section
# ---goes to the results window
# 6. back button
# ---goes back to the main menu
#
# the display area will show as per the button clicked

from views.base_window import SidebarWindowBase
from widgets.sidebar import Sidebar
from views.tle_tester.tle_tester_display_area import TLETesterDisplay
from views.tle_tester.time_limit_slider import TimeLimitSlider
from tools.tle_runner import TLERunner

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
            self.tle_runner.compile_all()
        elif button_text == 'Run':
            time_limit = self.time_limit_slider.value()
            self.tle_runner.run_tle_test(time_limit)
        pass

    def handle_button_click(self, button_text):
        if button_text == 'Help Center':
            if self.can_close():
                self.parent.window_manager.show_window('help_center')
        else:
            super().handle_button_click(button_text)

    def handle_time_limit_changed(self, value):
        print(f"Time limit changed to: {value} ms")
