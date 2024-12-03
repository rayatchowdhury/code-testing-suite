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
from widgets.display_area import DisplayArea

class TLETesterWindow(SidebarWindowBase):
    def __init__(self, parent=None):
        # Initialize base class first
        super().__init__(parent, title=None)

        # Create sidebar with sections and buttons
        self.sidebar = Sidebar("TLE Tester")
        
        edit_section = self.sidebar.add_section("Edit Code")
        for button_text in ['Edit Generator', 'Edit Test Code']:
            btn = self.sidebar.add_button(button_text, edit_section)
            btn.clicked.connect(lambda checked, text=button_text: self.handle_edit_button(text))
            
        options_section = self.sidebar.add_section("Test Options")
        tle_btn = self.sidebar.add_button('TLE Options', options_section)
        tle_btn.clicked.connect(self.handle_tle_options)
        
        action_section = self.sidebar.add_section("Actions")
        for button_text in ['Compile', 'Run', 'Results']:
            btn = self.sidebar.add_button(button_text, action_section)
            btn.clicked.connect(lambda checked, text=button_text: self.handle_action_button(text))
            
        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()

        back_btn, options_btn = self.create_footer_buttons()
        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)

        # Create display area
        self.display_area = DisplayArea()

        # Setup splitter with sidebar and display area
        self.setup_splitter(self.sidebar, self.display_area)
        
        # Connect signals - moved from handle_action_button
        self.sidebar.button_clicked.connect(self.handle_button_click)

    def handle_edit_button(self, button_text):
        # Add your edit button handling logic here
        pass

    def handle_tle_options(self):
        # Add your TLE options handling logic here
        pass

    def handle_action_button(self, button_text):
        # Add your action button handling logic here
        pass

    def handle_button_click(self, button_text):
        if button_text == 'Help Center':
            if self.can_close():
                self.parent.window_manager.show_window('help_center')
        else:
            super().handle_button_click(button_text)
