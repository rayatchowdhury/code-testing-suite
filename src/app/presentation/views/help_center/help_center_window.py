# this is the help center window
# it contains the two sections: sidebar and display area
# sidebar contains the following buttons:
# - Introduction
# - Comparison
# - Benchmarking
# - FAQ
# - Author description
# - Back button - goes back to the main window

"""
HELP CENTER DESIGN: Terminal/Glitch Aesthetic
Uses unified terminal docs style to match main window V1
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPushButton

from src.app.presentation.widgets.display_area import DisplayArea
from src.app.presentation.widgets.sidebar import Sidebar
from src.app.presentation.window_controller.base_window import SidebarWindowBase

from .content import get_document_data
from .document import create_help_document


class HelpCenterWindow(SidebarWindowBase):
    def __init__(self, parent=None):
        super().__init__(parent, title=None)

        # Create sidebar with sections and buttons
        self.sidebar = Sidebar("Help Center")

        main_section = self.sidebar.add_section("Help Topics")
        topics = [
            "Introduction",
            "Code Editor Guide",
            "Comparison Guide",
            "Benchmarking Guide",
            "Validation Guide",
            "Results Guide",
            "Configuration",
            "About",
        ]

        for button_text in topics:
            btn = self.sidebar.add_button(button_text, main_section)
            btn.clicked.connect(
                lambda _, text=button_text: self.load_help_content(text)
            )

        back_btn, options_btn = self.create_footer_buttons()
        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)

        # Create display area with document widget container
        self.display_area = DisplayArea()
        self.current_document = None

        # Setup splitter with sidebar and display area
        self.setup_splitter(self.sidebar, self.display_area)

        # Load initial content
        self.load_help_content("Introduction")

    def load_help_content(self, topic):
        """Load help content using terminal docs style"""
        # Clear existing content
        if self.current_document:
            self.display_area.layout.removeWidget(self.current_document)
            self.current_document.deleteLater()

        # Create new document widget
        data = get_document_data(topic)
        self.current_document = create_help_document(
            data["title"],
            data["sections"]
        )
        self.display_area.layout.addWidget(self.current_document)
