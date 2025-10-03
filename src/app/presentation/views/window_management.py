"""
Window Management for Code Testing Suite.

This module provides window factory and manager functionality for creating
and managing application windows without circular import dependencies.
"""

from typing import Type, Optional, Any
from PySide6.QtWidgets import QWidget, QStackedWidget
from PySide6.QtCore import Qt, QTimer


class WindowFactory:
    """Factory for creating window instances without circular imports."""
    
    # Registry of window creators - populated lazily to avoid imports
    _window_creators = {}
    _registered = False
    
    @classmethod
    def _ensure_registered(cls):
        """Ensure default creators are registered."""
        if not cls._registered:
            cls._register_default_creators()
            cls._registered = True
    
    @classmethod
    def register_window_creator(cls, window_name: str, creator_func):
        """
        Register a window creator function.
        
        Args:
            window_name: Name of the window type (e.g., 'main', 'code_editor')
            creator_func: Function that returns the window class
        """
        cls._window_creators[window_name] = creator_func
    
    @classmethod
    def create_window(cls, window_name: str, parent: Optional[QWidget] = None) -> Optional[QWidget]:
        """
        Create a window instance by name.
        
        Args:
            window_name: Name of the window to create
            parent: Parent widget for the window
            
        Returns:
            Window instance or None if window type not found
        """
        cls._ensure_registered()
        
        creator = cls._window_creators.get(window_name)
        if creator:
            try:
                window_class = creator()
                return window_class(parent)
            except Exception as e:
                print(f"Error creating window '{window_name}': {e}")
                return None
        
        print(f"Unknown window type: {window_name}")
        return None
    
    @classmethod
    def get_window_class(cls, window_name: str) -> Optional[Type]:
        """
        Get the window class without creating an instance.
        
        Args:
            window_name: Name of the window
            
        Returns:
            Window class or None if not found
        """
        cls._ensure_registered()
            
        creator = cls._window_creators.get(window_name)
        if creator:
            try:
                return creator()
            except Exception as e:
                print(f"Error getting window class '{window_name}': {e}")
                return None
        return None
    
    @classmethod
    def _register_default_creators(cls):
        """Register default window creators with lazy imports."""
        
        def _create_main_window():
            from src.app.presentation.views.main_window import MainWindowContent
            return MainWindowContent
        
        def _create_code_editor():
            from src.app.presentation.views.code_editor.code_editor_window import CodeEditorWindow
            return CodeEditorWindow
        
        def _create_comparator():
            from src.app.presentation.views.comparator.comparator_window import ComparatorWindow
            return ComparatorWindow
        
        def _create_benchmarker():
            from src.app.presentation.views.benchmarker.benchmarker_window import BenchmarkerWindow
            return BenchmarkerWindow
        
        def _create_validator():
            from src.app.presentation.views.validator.validator_window import ValidatorWindow
            return ValidatorWindow
        
        def _create_help_center():
            from src.app.presentation.views.help_center.help_center_window import HelpCenterWindow
            return HelpCenterWindow
        
        def _create_results():
            from src.app.presentation.views.results.results_window import ResultsWindow
            return ResultsWindow
        
        # Register all default window creators
        cls._window_creators.update({
            'main': _create_main_window,
            'code_editor': _create_code_editor,
            'comparator': _create_comparator,
            'benchmarker': _create_benchmarker,
            'validator': _create_validator,
            'help_center': _create_help_center,
            'results': _create_results
        })
        cls._registered = True
    
    @classmethod
    def list_available_windows(cls) -> list:
        """
        Get list of available window types.
        
        Returns:
            List of window type names
        """
        cls._ensure_registered()
        return list(cls._window_creators.keys())
    
    @classmethod
    def clear_registry(cls):
        """Clear the window creator registry. Useful for testing."""
        cls._window_creators.clear()
        cls._registered = False


class WindowManager(QStackedWidget):
    """Manages application window instances and navigation."""
    
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
        """Navigate back to previous window"""
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
