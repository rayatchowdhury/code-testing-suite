# this is the main window of the application
# it contains the two sections: sidebar and display area
# sidebar contains the following buttons:
# - Code Editor
# - Stress Tester
# - TLE Tester
# - Help Center
# - Exit
# display area will show description of the application

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from widgets.sidebar import Sidebar
from widgets.display_area import DisplayArea
from views.code_editor.code_editor_window import CodeEditorWindow
from views.stress_tester.stress_tester_window import StressTesterWindow
from views.tle_tester.tle_tester_window import TLETesterWindow
from views.help_center.help_center_window import HelpCenterWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code Testing Suite")
        self.setMinimumSize(1000, 666)

        # Enable antialiasing for the application
        self.setAttribute(Qt.WA_SetFont)  # Enable custom font
        self.setFont(QFont("Segoe UI", 10))

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Store main layout and widgets as class attributes
        self.main_widget = main_widget
        self.main_layout = layout

        # Create sidebar and add buttons
        self.sidebar = Sidebar("Code Testing Suite")
        main_section = self.sidebar.add_section("Navigation")
        for button_text in ['Code Editor', 'Stress Tester', 'TLE Tester', 'Help Center']:
            self.sidebar.add_button(button_text, main_section)

        # Add exit button at bottom
        self.sidebar.add_spacer()
        exit_btn = self.sidebar.add_button("Exit")
        # Using same style as back button
        exit_btn.setObjectName("back_button")

        self.display_area = DisplayArea()

        # Add widgets to layout
        layout.addWidget(self.sidebar)
        layout.addWidget(self.display_area)

        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_navigation)

    def handle_navigation(self, button_text):
        if button_text == 'Exit':
            self.close()
        elif button_text == 'Code Editor':
            self.sidebar.setParent(None)
            self.display_area.setParent(None)
            code_editor = CodeEditorWindow(self)
            self.main_layout.addWidget(code_editor)
        elif button_text == 'Stress Tester':
            self.sidebar.setParent(None)
            self.display_area.setParent(None)
            stress_tester = StressTesterWindow(self)
            self.main_layout.addWidget(stress_tester)
        elif button_text == 'TLE Tester':
            self.sidebar.setParent(None)
            self.display_area.setParent(None)
            tle_tester = TLETesterWindow(self)
            self.main_layout.addWidget(tle_tester)
        elif button_text == 'Help Center':
            self.sidebar.setParent(None)
            self.display_area.setParent(None)
            help_center = HelpCenterWindow(self)
            self.main_layout.addWidget(help_center)

    def return_to_main(self):
        # Remove the current widget
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Restore the original sidebar and display area
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.display_area)
