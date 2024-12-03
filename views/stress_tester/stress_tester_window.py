from views.base_window import SidebarWindowBase
from widgets.sidebar import Sidebar
from widgets.display_area import DisplayArea
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QFont

class StressTesterWindow(SidebarWindowBase):
    def __init__(self, parent=None):
        # Initialize base class first
        super().__init__(parent, title=None)
        
        self.sidebar = Sidebar("Stress Tester")
        
        edit_section = self.sidebar.add_section("Edit Code")
        for button_text in ['Edit Generator', 'Edit Correct Code', 'Edit Test Code']:
            btn = self.sidebar.add_button(button_text, edit_section)
            btn.clicked.connect(lambda checked, text=button_text: self.handle_edit_button(text))
            
        options_section = self.sidebar.add_section("Test Options")
        stress_btn = self.sidebar.add_button('Stress Options', options_section)
        stress_btn.clicked.connect(self.handle_stress_options)
        
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
        
        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)

    def handle_edit_button(self, button_text):
        # Add your edit button handling logic here
        pass

    def handle_stress_options(self):
        # Add your stress options handling logic here
        pass

    def handle_action_button(self, button_text):
        # Add your action button handling logic here
        pass

    def handle_button_click(self, button_text):
        if button_text == 'Help Center':
            self.parent.window_manager.show_window('help_center')
        else:
            super().handle_button_click(button_text)
