from PySide6.QtWidgets import QWidget, QStackedWidget
from PySide6.QtCore import Qt, QTimer
from utils.window_factory import WindowFactory

class WindowManager(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.windows = {}
        self.current_window = None
        self.window_history = []  # Add navigation history

    def show_window(self, window_name, **kwargs):
        """Show a window, create if doesn't exist"""
        try:
            if window_name not in self.windows:
                # Use factory to create window instead of direct imports
                window = WindowFactory.create_window(window_name, self.parent())
                if not window:
                    return False
                
                # Validate window is a QWidget
                if not isinstance(window, QWidget):
                    print(f"Error: Created window '{window_name}' is not a QWidget")
                    return False
                
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
            
        except Exception as e:
            print(f"Error showing window '{window_name}': {e}")
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
