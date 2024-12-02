from views.base_window import SidebarWindowBase
from widgets.sidebar import Sidebar
from widgets.display_area import DisplayArea
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QFont

class StressTesterWindow(SidebarWindowBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create sidebar with sections and buttons
        self.sidebar = Sidebar("Stress Tester")
        
        edit_section = self.sidebar.add_section("Edit Code")
        for button_text in ['Edit Generator', 'Edit Correct Code', 'Edit Test Code']:
            self.sidebar.add_button(button_text, edit_section)
            
        options_section = self.sidebar.add_section("Test Options")
        self.sidebar.add_button('Stress Options', options_section)
        
        action_section = self.sidebar.add_section("Actions")
        for button_text in ['Compile', 'Run', 'Results']:
            self.sidebar.add_button(button_text, action_section)


        # Add footer items
        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()
        
        # Create buttons
        back_btn = QPushButton("Back")
        back_btn.setObjectName("back_button")
        back_btn.clicked.connect(lambda: self.handle_button_click("Back"))
        
        options_btn = QPushButton("⚙️")
        options_btn.setObjectName("back_button")
        options_btn.setFont(QFont('Segoe UI', 14))
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
        elif button_text == 'Help Center':
            from views.help_center.help_center_window import HelpCenterWindow
            self.parent.setCentralWidget(HelpCenterWindow(self.parent, self))
        elif button_text == 'Options':
            super().handle_button_click(button_text)
        # Handle other button clicks here
        pass
