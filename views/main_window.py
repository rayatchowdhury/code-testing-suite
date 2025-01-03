# this is the main window of the application
# it contains the two sections: sidebar and display area
# sidebar contains the following buttons:
# - Code Editor
# - Stress Tester
# - TLE Tester
# - Help Center
# - Exit
# display area will show description of the application

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter, QPushButton, QMessageBox
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QUrl, Signal, QTimer
from PySide6.QtWebEngineWidgets import QWebEngineView
import markdown2
import os
from widgets.sidebar import Sidebar
from widgets.display_area import DisplayArea
from views.code_editor.code_editor_window import CodeEditorWindow
from views.stress_tester.stress_tester_window import StressTesterWindow
from views.tle_tester.tle_tester_window import TLETesterWindow
from views.help_center.help_center_window import HelpCenterWindow
from views.base_window import SidebarWindowBase
from styles.style import WEBVIEW_STYLE  # Add this import
from views.config.config_view import ConfigView  # Add at top with other imports


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
        
        # Load HTML directly instead of converting markdown
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(current_dir, 'main_window.html')
        base_url = QUrl.fromLocalFile(current_dir + "/")
        
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        self.web_view.setHtml(html_content, baseUrl=base_url)
        self.display_area.layout.addWidget(self.web_view)

        # Setup splitter
        self.setup_splitter(self.sidebar, self.display_area)
        
        # Set initial splitter sizes after a short delay
        QTimer.singleShot(100, self.update_splitter_sizes)

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
            # Convert button text to window name
            window_name = button_text.lower().replace(' ', '_')
            self.parent.window_manager.show_window(window_name)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code Testing Suite")
        self.setMinimumSize(1100, 700)  # Increased from 1000 to 1150
        
        # Create window manager and set as central widget
        from utils.window_manager import WindowManager
        self.window_manager = WindowManager(self)
        self.setCentralWidget(self.window_manager)
        
        # Show main window content
        self.window_manager.show_window('main')
        
    def return_to_main(self):
        """Return to main window"""
        self.window_manager.show_window('main')

    def closeEvent(self, event):
        """Handle application close with improved unsaved changes check"""
        try:
            current = self.window_manager.get_current_window()
            
            # If current window is code editor, check for unsaved changes
            if current and isinstance(current, CodeEditorWindow):
                if current.editor_display.has_editor:
                    # Check for any unsaved changes
                    has_unsaved = any(
                        current.editor_display.tab_widget.widget(i).editor.codeEditor.document().isModified()
                        for i in range(current.editor_display.tab_widget.count())
                    )
                    
                    if has_unsaved:
                        # Count unsaved files
                        unsaved_count = sum(1 for i in range(current.editor_display.tab_widget.count())
                                          if current.editor_display.tab_widget.widget(i).editor.codeEditor.document().isModified())
                        
                        message = f'You have {unsaved_count} unsaved files. Do you want to save them?' if unsaved_count > 1 else 'Do you want to save your changes?'
                        
                        reply = QMessageBox.question(
                            self, 'Save Changes?', message,
                            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                        )
                        
                        if reply == QMessageBox.Cancel:
                            event.ignore()
                            return
                        elif reply == QMessageBox.Save:
                            # Try to save all modified files
                            success = True
                            for i in range(current.editor_display.tab_widget.count()):
                                tab = current.editor_display.tab_widget.widget(i)
                                if tab.editor.codeEditor.document().isModified():
                                    if not tab.editor.saveFile():
                                        success = False
                                        break
                            
                            if not success:
                                event.ignore()
                                return
            
            # Accept the event and cleanup
            event.accept()
            QTimer.singleShot(0, self.window_manager.cleanup_all)
            
        except RuntimeError:
            event.accept()
