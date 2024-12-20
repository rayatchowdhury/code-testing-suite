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
        self.window_history = []  # Add navigation history
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
                
                window = window_class(self.parent())
                self.windows[window_name] = window
                self.addWidget(window)
            
            window = self.windows[window_name]
            window.show()
            self.setCurrentWidget(window)
            
            # Only add to history if there's a current window and it's different
            if self.current_window and self.current_window != window_name:
                # Add to history unless it would create a duplicate with the last entry
                if not self.window_history or self.window_history[-1] != self.current_window:
                    self.window_history.append(self.current_window)
            
            self.current_window = window_name
            return True
            
        except RuntimeError:
            return False

    def go_back(self):
        if not self.window_history:
            return False
            
        previous_window = self.window_history.pop()
        self.show_window(previous_window)
        self.current_window = previous_window
        # Remove the last entry to prevent duplicates
        self.window_history = self.window_history[:-1]
        return True

    def get_current_window(self):
        """Get the currently active window"""
        return self.windows.get(self.current_window)

    def cleanup_window(self, window_name):
        """Clean up a window's resources"""
        try:
            if window_name in self.windows:
                # Also clean up from history
                self.window_history = [w for w in self.window_history if w != window_name]
                window = self.windows[window_name]
                if hasattr(window, 'cleanup'):
                    window.cleanup()
                # Don't try to set current widget to None
                if window == self.currentWidget():
                    # If removing current widget, switch to main window if possible
                    if 'main' in self.windows and window_name != 'main':
                        self.setCurrentWidget(self.windows['main'])
                    # Otherwise try to switch to any other available window
                    elif len(self.windows) > 1:
                        other_window = next(w for name, w in self.windows.items() if name != window_name)
                        self.setCurrentWidget(other_window)
                self.removeWidget(window)
                window.deleteLater()
                del self.windows[window_name]
        except RuntimeError:
            pass

    def cleanup_all(self):
        """Clean up all windows safely"""
        # Cleanup in reverse order, leaving main window for last if it exists
        window_names = sorted(list(self.windows.keys()), 
                            key=lambda x: 0 if x == 'main' else 1, 
                            reverse=True)
        for window_name in window_names:
            self.cleanup_window(window_name)
