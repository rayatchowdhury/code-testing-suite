# this is the help center window
# it contains the two sections: sidebar and display area
# sidebar contains the following buttons:
# - Introduction
# - Comparison
# - Benchmarking
# - FAQ
# - Author description
# - Back button - goes back to the main window

from src.app.presentation.window_controller.base_window import SidebarWindowBase
from src.app.presentation.widgets.sidebar import Sidebar
from src.app.presentation.widgets.display_area import DisplayArea
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QFont
from src.app.presentation.window_controller.qt_doc_engine import HelpDocument
from .help_content import get_document_data


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
            "Configuration",
            "About",
        ]

        for button_text in topics:
            btn = self.sidebar.add_button(button_text, main_section)
            btn.clicked.connect(
                lambda checked, text=button_text: self.load_help_content(text)
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
        """Load help content using Qt document widgets"""
        # Clear existing content
        if self.current_document:
            self.display_area.layout.removeWidget(self.current_document)
            self.current_document.deleteLater()

        # Create new document widget directly
        data = get_document_data(topic)
        self.current_document = HelpDocument(data["title"], data["sections"])
        self.display_area.layout.addWidget(self.current_document)
