# this is the main window of the application
# it contains the two sections: sidebar and display area
# sidebar contains the following buttons:
# - Code Editor
# - Stress Tester
# - TLE Tester
# - Help Center
# - Exit
# display area will show description of the application

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
import markdown2
import os
from widgets.sidebar import Sidebar
from widgets.display_area import DisplayArea
from views.code_editor.code_editor_window import CodeEditorWindow
from views.stress_tester.stress_tester_window import StressTesterWindow
from views.tle_tester.tle_tester_window import TLETesterWindow
from views.help_center.help_center_window import HelpCenterWindow
from widgets.display_area_widgets.editor_window import EditorWindow
from views.base_window import SidebarWindowBase


class MainWindowContent(SidebarWindowBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create sidebar
        self.sidebar = Sidebar("Code Testing Suite")
        
        main_section = self.sidebar.add_section("Navigation")
        for button_text in ['Code Editor', 'Stress Tester', 'TLE Tester', 'Help Center']:
            self.sidebar.add_button(button_text, main_section)
            
        self.sidebar.add_spacer()
        exit_btn = self.sidebar.add_button("Exit")
        exit_btn.setObjectName("back_button")

        # Create display area with web view
        self.display_area = DisplayArea()
        self.web_view = QWebEngineView()
        
        # Load and display markdown
        current_dir = os.path.dirname(os.path.abspath(__file__))
        md_path = os.path.join(current_dir, 'main_window_md.md')
        base_url = QUrl.fromLocalFile(current_dir + "/")
        
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
            
        html_content = markdown2.markdown(
            md_content,
            extras=['fenced-code-blocks', 'tables', 'header-ids', 'metadata']
        )
        
        # Update the CSS styling for dark theme
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <base href="{base_url.toString()}">
        </head>
        <body>
            <style>
                body {{
                    font-family: 'Segoe UI', sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    line-height: 1.6;
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px;
                    border: 1px solid #333;
                }}
                h1, h2, h3, h4 {{
                    color: #58a6ff;
                    border-bottom: 1px solid #333;
                    padding-bottom: 8px;
                }}
                h1 {{
                    font-size: 2.5em;
                    text-align: center;
                    margin-bottom: 1em;
                }}
                ul {{
                    list-style-type: none;
                    padding-left: 20px;
                }}
                li {{
                    margin: 8px 0;
                    position: relative;
                }}
                li:before {{
                    content: "•";
                    color: #58a6ff;
                    font-weight: bold;
                    position: absolute;
                    left: -15px;
                }}
                .feature-section {{
                    background-color: #252525;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 15px 0;
                    border: 1px solid #333;
                }}
                .emoji {{
                    font-size: 1.5em;
                    margin-right: 10px;
                }}
            </style>
            {html_content}
        </body>
        </html>
        """
        
        self.web_view.setHtml(html_content, baseUrl=base_url)
        self.display_area.layout.addWidget(self.web_view)

        # Setup splitter
        self.setup_splitter(self.sidebar, self.display_area)

        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)

    def handle_button_click(self, button_text):
        if button_text == 'Exit':
            self.parent.close()
        elif button_text in ['Code Editor', 'Stress Tester', 'TLE Tester', 'Help Center']:
            # Remove current content
            self.web_view.setParent(None)
            self.display_area.setParent(None)
            self.splitter.setParent(None)
            
            # Create and show new window
            if button_text == 'Code Editor':
                window = CodeEditorWindow(self.parent)
            elif button_text == 'Stress Tester':
                window = StressTesterWindow(self.parent)
            elif button_text == 'TLE Tester':
                window = TLETesterWindow(self.parent)
            elif button_text == 'Help Center':
                window = HelpCenterWindow(self.parent)
                
            self.parent.setCentralWidget(window)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code Testing Suite")
        self.setMinimumSize(1000, 700)
        
        # Enable antialiasing
        self.setAttribute(Qt.WA_SetFont)
        self.setFont(QFont("Segoe UI", 10))
        
        # Create and set central widget
        self.central_widget = MainWindowContent(self)
        self.setCentralWidget(self.central_widget)
        
    def return_to_main(self):
        # Create and set new main content
        self.central_widget = MainWindowContent(self)
        self.setCentralWidget(self.central_widget)
