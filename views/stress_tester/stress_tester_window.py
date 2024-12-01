from views.base_window import SidebarWindowBase
from widgets.sidebar import Sidebar
from widgets.display_area import DisplayArea

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
            
        self.sidebar.add_back_button()

        # Add footer items
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
        # Handle other button clicks here
        pass
