from PySide6.QtWidgets import QWidget, QStackedWidget
from PySide6.QtCore import Qt, QTimer
from views.code_editor.code_editor_window import CodeEditorWindow
from views.stress_tester.stress_tester_window import StressTesterWindow
from views.tle_tester.tle_tester_window import TLETesterWindow
from views.help_center.help_center_window import HelpCenterWindow
from views.main_window import MainWindowContent

class WindowManager(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.windows = {}
        self.current_window = None
        self.window_classes = {
            'main': MainWindowContent,
            'code_editor': CodeEditorWindow,
            'stress_tester': StressTesterWindow,
            'tle_tester': TLETesterWindow,
            'help_center': HelpCenterWindow
        }

    def show_window(self, window_name, **kwargs):
        """Show a window, create if doesn't exist"""
        try:
            if window_name not in self.windows:
                window_class = self.window_classes.get(window_name)
                if not window_class:
                    return False
                
                window = window_class(self.parent(), **kwargs)
                self.windows[window_name] = window
                self.addWidget(window)
            
            window = self.windows[window_name]
            self.setCurrentWidget(window)
            self.current_window = window_name
            return True
        except RuntimeError:
            return False

    def get_current_window(self):
        """Get the currently active window"""
        return self.windows.get(self.current_window)

    def cleanup_window(self, window_name):
        """Clean up a window's resources"""
        try:
            if window_name in self.windows:
                window = self.windows[window_name]
                if hasattr(window, 'cleanup'):
                    window.cleanup()
                if window == self.currentWidget():
                    self.setCurrentWidget(None)
                self.removeWidget(window)
                window.deleteLater()
                del self.windows[window_name]
        except RuntimeError:
            pass

    def cleanup_all(self):
        """Clean up all windows safely"""
        for window_name in list(self.windows.keys()):
            self.cleanup_window(window_name)
