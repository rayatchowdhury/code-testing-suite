"""
Window Factory for Code Testing Suite.

This module provides a factory pattern to create window instances
without creating circular import dependencies. The factory centralizes
window creation logic and allows the WindowManager to create windows
without directly importing view modules.
"""

from typing import Type, Optional, Any
from PySide6.QtWidgets import QWidget


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
            from views.main_window import MainWindowContent
            return MainWindowContent
        
        def _create_code_editor():
            from views.code_editor.code_editor_window import CodeEditorWindow
            return CodeEditorWindow
        
        def _create_stress_tester():
            from views.stress_tester.stress_tester_window import StressTesterWindow
            return StressTesterWindow
        
        def _create_tle_tester():
            from views.tle_tester.tle_tester_window import TLETesterWindow
            return TLETesterWindow
        
        def _create_help_center():
            from views.help_center.help_center_window import HelpCenterWindow
            return HelpCenterWindow
        
        # Register all default window creators
        cls._window_creators.update({
            'main': _create_main_window,
            'code_editor': _create_code_editor,
            'stress_tester': _create_stress_tester,
            'tle_tester': _create_tle_tester,
            'help_center': _create_help_center
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
