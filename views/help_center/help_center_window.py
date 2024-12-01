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
        super().__init__(parent)

        # Create sidebar with sections and buttons
        self.sidebar = Sidebar("Help Center")
        
        main_section = self.sidebar.add_section("Help Topics")
        for button_text in ['Introduction', 'Stress Testing', 'TLE Testing', 'FAQ', 'Author Description']:
            self.sidebar.add_button(button_text, main_section)
            
        # Add footer divider
        self.sidebar.add_footer_divider()
        
        # Create buttons
        back_btn = QPushButton("Back")
        back_btn.setObjectName("back_button")
        back_btn.clicked.connect(lambda: self.handle_button_click("Back"))
        
        options_btn = QPushButton("⚙️")
        options_btn.setObjectName("back_button")
        options_btn.setFont(QFont('Segoe UI', 14))  # Increase font size for emoji
        options_btn.clicked.connect(lambda: self.handle_button_click("Options"))
        
        # Setup horizontal footer buttons
        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)

        # Create display area
        self.display_area = DisplayArea()

        # Setup splitter with sidebar and display area
        self.setup_splitter(self.sidebar, self.display_area)

        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)

    def handle_button_click(self, button_text):
        if button_text == 'Back':
            self.parent.return_to_main()
        # Handle other button clicks here
        pass