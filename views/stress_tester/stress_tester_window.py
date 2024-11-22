from PySide6.QtWidgets import QWidget, QHBoxLayout
from widgets.sidebar import Sidebar
from widgets.display_area import DisplayArea

class StressTesterWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

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
