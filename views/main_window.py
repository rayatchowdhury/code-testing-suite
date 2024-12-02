# this is the main window of the application
# it contains the two sections: sidebar and display area
# sidebar contains the following buttons:
# - Code Editor
# - Stress Tester
# - TLE Tester
# - Help Center
# - Exit
# display area will show description of the application

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter, QPushButton
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QUrl, Signal
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
from styles.style import WEBVIEW_STYLE  # Add this import
from views.config_view import ConfigView  # Add at top with other imports


class MainWindowContent(SidebarWindowBase):
    button_clicked = Signal(str)  # Add this line at class level
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create sidebar
        self.sidebar = Sidebar("Code Testing Suite")
        
        # Add navigation buttons to content section
        main_section = self.sidebar.add_section("Navigation")
        for button_text in ['Code Editor', 'Stress Tester', 'TLE Tester']:
            self.sidebar.add_button(button_text, main_section)
        
        # Add footer items with Help Center
        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()
        
        # Create buttons
        exit_btn = QPushButton("Exit")
        exit_btn.setObjectName("back_button")
        exit_btn.clicked.connect(self.handle_exit)
        
        options_btn = QPushButton("⚙️")
        options_btn.setObjectName("back_button")
        options_btn.setFont(QFont('Segoe UI', 14))  # Increase font size for emoji
        options_btn.clicked.connect(lambda: self.handle_button_click("Options"))
        
        # Setup horizontal footer buttons
        self.sidebar.setup_horizontal_footer_buttons(exit_btn, options_btn)

        # Create display area with web view
        self.display_area = DisplayArea()
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet(WEBVIEW_STYLE)  # Add this line
        
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
            <style>
                ::-webkit-scrollbar {{
                    width: 8px;
                    height: 8px;
                }}
                
                ::-webkit-scrollbar-track {{
                    background: rgba(0, 0, 0, 0.1);
                }}
                
                ::-webkit-scrollbar-thumb {{
                    background: rgba(255, 255, 255, 0.08);
                    border-radius: 4px;
                }}
                
                ::-webkit-scrollbar-thumb:hover {{
                    background: rgba(255, 255, 255, 0.12);
                }}
                
                ::-webkit-scrollbar-corner {{
                    background: transparent;
                }}

                /* Rest of your existing CSS */
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
        </head>
        <body>
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

    def handle_exit(self):
        """Handle exit button click"""
        if self.parent:
            self.parent.close()

    def handle_button_click(self, button_text):
        if button_text == 'Exit':
            self.parent.close()
        elif button_text == 'Options':
            config_dialog = ConfigView(self)
            config_dialog.exec()
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
