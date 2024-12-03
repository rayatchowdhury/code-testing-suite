from PySide6.QtWidgets import QFileDialog, QMessageBox, QPushButton
from PySide6.QtGui import QFont
from widgets.sidebar import Sidebar
from views.base_window import SidebarWindowBase
from views.code_editor.code_editor_display_area import CodeEditorDisplay
import os

class CodeEditorWindow(SidebarWindowBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create sidebar
        self.sidebar = Sidebar("Code Editor")
        
        main_section = self.sidebar.add_section("File Operations")
        for button_text in ['New File', 'Open File', 'Save File']:  # Removed 'Run Code'
            self.sidebar.add_button(button_text, main_section)
        
        # Add footer items
        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()
        
        # Create buttons
        back_btn = QPushButton("Back")
        back_btn.setObjectName("back_button")
        back_btn.clicked.connect(lambda: self.handle_button_click("Back"))
        
        options_btn = QPushButton("⚙️")
        options_btn.setObjectName("back_button")
        options_btn.setFont(QFont('Segoe UI', 14))
        options_btn.clicked.connect(lambda: self.handle_button_click("Options"))
        
        # Setup horizontal footer buttons
        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)

        # Create editor display
        self.editor_display = CodeEditorDisplay()

        # Setup splitter
        self.setup_splitter(self.sidebar, self.editor_display)

        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)
        self.editor_display.saveRequested.connect(self.save_file)

    def handle_button_click(self, button_text):
        if button_text == 'Back':
            if self.editor_display.isCurrentFileModified():
                self.handle_unsaved_changes()
            self.parent.return_to_main()
        elif button_text == 'New File':
            if self.editor_display.isCurrentFileModified():
                self.handle_unsaved_changes()
            self.editor_display.add_new_tab()
        elif button_text == 'Open File':
            self.open_file()
        elif button_text == 'Save File':
            self.save_file()
        elif button_text == 'Help Center':
            from views.help_center.help_center_window import HelpCenterWindow
            self.parent.setCentralWidget(HelpCenterWindow(self.parent, self))
        elif button_text == 'Options':
            super().handle_button_click(button_text)

    def handle_unsaved_changes(self):
        reply = QMessageBox.question(
            self, 'Save Changes?',
            'Do you want to save your changes?',
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )

        if reply == QMessageBox.Save:
            self.save_file()
        return reply != QMessageBox.Cancel

    def save_file(self):
        editor = self.editor_display.getCurrentEditor()
        if not editor:
            return False

        if not editor.currentFilePath:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save File", "",
                "C++ Files (*.cpp *.h);;All Files (*)"
            )
            if not file_name:
                return False
            editor.currentFilePath = file_name
            editor.updateTitleBar()

        try:
            with open(editor.currentFilePath, 'w') as file:
                file.write(editor.getCode())
            editor.codeEditor.document().setModified(False)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
            return False

    def open_file(self):
        if self.editor_display.isCurrentFileModified():
            if not self.handle_unsaved_changes():
                return

        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "C++ Files (*.cpp *.h);;All Files (*)"
        )
        
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    new_tab = self.editor_display.add_new_tab(os.path.basename(file_name))
                    new_tab.editor.codeEditor.setPlainText(file.read())
                    new_tab.editor.currentFilePath = file_name
                    new_tab.editor.updateTitleBar()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
