#this is the help center window
#it contains the two sections: sidebar and display area
#sidebar contains the following buttons:
# - Introduction
# - Stress Testing
# - TLE Testing
# - FAQ
# - Author description
# - Back button - goes back to the main window

from views.base_window import SidebarWindowBase
from widgets.sidebar import Sidebar
from widgets.display_area import DisplayArea
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QFont  # Changed import location and using PySide6

class HelpCenterWindow(SidebarWindowBase):
    def __init__(self, parent=None):
        # Initialize base class first
        super().__init__(parent, title=None)

        # Create sidebar with sections and buttons
        self.sidebar = Sidebar("Help Center")
        
        main_section = self.sidebar.add_section("Help Topics")
        for button_text in ['Introduction', 'Stress Testing', 'TLE Testing', 'FAQ', 'Author Description']:
            btn = self.sidebar.add_button(button_text, main_section)
            btn.clicked.connect(lambda checked, text=button_text: self.load_help_content(text))
        
        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()
        
        back_btn, options_btn = self.create_footer_buttons()
        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)

        # Create display area
        self.display_area = DisplayArea()

        # Setup splitter with sidebar and display area
        self.setup_splitter(self.sidebar, self.display_area)

    def load_help_content(self, topic):
        # Add your help content loading logic here
        pass