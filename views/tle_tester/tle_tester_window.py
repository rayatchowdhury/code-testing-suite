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
from views.help_center.help_center_window import HelpCenterWindow  # Fix the import path

class TLETesterWindow(SidebarWindowBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create sidebar with sections and buttons
        self.sidebar = Sidebar("TLE Tester")
        
        edit_section = self.sidebar.add_section("Edit Code")
        for button_text in ['Edit Generator', 'Edit Test Code']:
            self.sidebar.add_button(button_text, edit_section)
            
        options_section = self.sidebar.add_section("Test Options")
        self.sidebar.add_button('TLE Options', options_section)
        
        action_section = self.sidebar.add_section("Actions")
        for button_text in ['Compile', 'Run', 'Results']:
            self.sidebar.add_button(button_text, action_section)
            
        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()
        self.sidebar.add_back_button()

        # Create display area
        self.display_area = DisplayArea()

        # Setup splitter with sidebar and display area
        self.setup_splitter(self.sidebar, self.display_area)

        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)

    def handle_button_click(self, button_text):
        if button_text == 'Back':
            self.parent.return_to_main()
        elif button_text == 'Help Center':
            self.parent.setCentralWidget(HelpCenterWindow(self.parent))
        # Handle other button clicks here
        pass
