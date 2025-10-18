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
HELP CENTER VARIATION SELECTOR:
Change ACTIVE_HELP_VARIATION to switch designs (1-4):
    1 = Terminal Docs (matches main window V1) ⭐
    2 = Clean Modern (minimal with whitespace)
    3 = Card Style (colorful bordered cards)
    4 = Developer Docs (code/syntax style)
"""

# ============== CHANGE THIS NUMBER TO SWITCH HELP VARIATIONS ==============
ACTIVE_HELP_VARIATION = 1  # Change to 1, 2, 3, or 4
# ==========================================================================

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPushButton

from src.app.presentation.widgets.display_area import DisplayArea
from src.app.presentation.widgets.sidebar import Sidebar
from src.app.presentation.window_controller.base_window import SidebarWindowBase

from .help_content import get_document_data
from .help_center_variations import create_help_variation


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
        """Load help content using variations"""
        # Clear existing content
        if self.current_document:
            self.display_area.layout.removeWidget(self.current_document)
            self.current_document.deleteLater()

        # Create new document widget using variation
        data = get_document_data(topic)
        self.current_document = create_help_variation(
            ACTIVE_HELP_VARIATION,
            data["title"],
            data["sections"]
        )
        self.display_area.layout.addWidget(self.current_document)
