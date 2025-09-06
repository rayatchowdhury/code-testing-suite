#this is the help center window
#it contains the two sections: sidebar and display area
#sidebar contains the following buttons:
# - Introduction
# - Comparison
# - Benchmarking
# - FAQ
# - Author description
# - Back button - goes back to the main window

from ...views.base_window import SidebarWindowBase
from ...widgets.sidebar import Sidebar
from ...widgets.display_area import DisplayArea
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QFont
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
import os

class HelpCenterWindow(SidebarWindowBase):
    def __init__(self, parent=None):
        super().__init__(parent, title=None)

        # Create sidebar with sections and buttons
        self.sidebar = Sidebar("Help Center")
        
        main_section = self.sidebar.add_section("Help Topics")
        topics = [
            'Introduction',
            'Code Editor Guide',
            'Comparison Guide', 
            'Benchmarking Guide',
            'Validation Guide',
            'Configuration',
            'About'
        ]
        
        for button_text in topics:
            btn = self.sidebar.add_button(button_text, main_section)
            btn.clicked.connect(lambda checked, text=button_text: self.load_help_content(text))
        
        back_btn, options_btn = self.create_footer_buttons()
        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)

        # Create display area with web view
        self.display_area = DisplayArea()
        self.web_view = QWebEngineView()
        self.display_area.layout.addWidget(self.web_view)

        # Setup splitter with sidebar and display area
        self.setup_splitter(self.sidebar, self.display_area)
        
        # Load initial content
        self.load_help_content('Introduction')

    def load_help_content(self, topic):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_name = topic.lower().replace(' ', '_') + '.html'
        html_path = os.path.join(current_dir, 'content', file_name)
        
        # Get path to styles directory (2 levels up from help_center + styles)
        styles_path = os.path.normpath(os.path.join(current_dir, '..', '..', 'styles'))
        base_url = QUrl.fromLocalFile(styles_path + "/")
        
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                
            # Update style path in HTML content
            html_content = html_content.replace(
                'href="../../../styles/',
                'href="'
            )
            
            self.web_view.setHtml(html_content, baseUrl=base_url)
        except FileNotFoundError:
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <link rel="stylesheet" href="html.css">
            </head>
            <body>
                <div class="heading--large text-gradient">Content Not Found</div>
                <section class="feature">
                    <h3 class="heading">
                        <span class="feature__icon">⚠️</span> 
                        <span class="text-gradient">{topic}</span>
                    </h3>
                    <p>This help section is currently under development.</p>
                </section>
            </body>
            </html>
            """
            self.web_view.setHtml(error_html, baseUrl=base_url)