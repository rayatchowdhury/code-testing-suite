#this is the help center window
#it contains the two sections: sidebar and display area
#sidebar contains the following buttons:
# - Introduction
# - Stress Testing
# - TLE Testing
# - FAQ
# - Author description
# - Back button - goes back to the main window

from PySide6.QtWidgets import QWidget, QHBoxLayout
from widgets.sidebar import Sidebar
from widgets.display_area import DisplayArea

class HelpCenterWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create sidebar with sections and buttons
        self.sidebar = Sidebar("Help Center")
        
        main_section = self.sidebar.add_section("Help Topics")
        for button_text in ['Introduction', 'Stress Testing', 'TLE Testing', 'FAQ', 'Author Description']:
            self.sidebar.add_button(button_text, main_section)
            
        self.sidebar.add_back_button()

        self.display_area = DisplayArea()

        layout.addWidget(self.sidebar)
        layout.addWidget(self.display_area)

        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)

    def handle_button_click(self, button_text):
        if button_text == 'Back':
            self.parent.return_to_main()
        # Handle other button clicks here
        pass