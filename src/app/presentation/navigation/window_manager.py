"""
Window Management for Code Testing Suite.

This module provides window factory and manager functionality for creating
and managing application windows without circular import dependencies.
"""

import logging
from typing import Optional, Type

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QStackedWidget, QWidget

logger = logging.getLogger(__name__)


class ConfigChangeNotifier(QObject):
    """Global notifier for configuration changes."""
    configChanged = Signal(dict)  # Emits config dict when settings change
    
    _instance = None
    
    @classmethod
    def instance(cls):
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = ConfigChangeNotifier()
        return cls._instance
    
    def notify_config_changed(self, config: dict):
        """Notify all subscribers that config has changed."""
        self.configChanged.emit(config)


class WindowFactory:
    """
    Factory for creating window instances without circular imports.
    
    Responsibilities (Factory Pattern):
    - Register window class creators (lazy import functions)
    - Create window instances on demand
    - Handle import errors gracefully
    
    Note: This registry stores FUNCTIONS that return window CLASSES,
    not window instances. Actual instances are cached by WindowManager.
    """

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
    def create_window(
        cls, window_name: str, parent: Optional[QWidget] = None
    ) -> Optional[QWidget]:
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
            except (ImportError, AttributeError, RuntimeError) as e:
                logger.error(f"Error creating window '{window_name}': {e}", exc_info=True)
                return None

        logger.warning(f"Unknown window type: {window_name}")
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
            except (ImportError, AttributeError) as e:
                logger.error(f"Error getting window class '{window_name}': {e}", exc_info=True)
                return None
        return None

    @classmethod
    def _register_default_creators(cls):
        """Register default window creators with lazy imports."""

        def _create_main_window():
            from src.app.presentation.windows.main import (
                MainWindowContent,
            )

            return MainWindowContent

        def _create_code_editor():
            from src.app.presentation.windows.editor import (
                CodeEditorWindow,
            )

            return CodeEditorWindow

        def _create_comparator():
            from src.app.presentation.windows.tests.comparator import (
                ComparatorWindow,
            )

            return ComparatorWindow

        def _create_benchmarker():
            from src.app.presentation.windows.tests.benchmarker import (
                BenchmarkerWindow,
            )

            return BenchmarkerWindow

        def _create_validator():
            from src.app.presentation.windows.tests.validator import (
                ValidatorWindow,
            )

            return ValidatorWindow

        def _create_help_center():
            from src.app.presentation.windows.help_center import (
                HelpCenterWindow,
            )

            return HelpCenterWindow

        def _create_results():
            from src.app.presentation.windows.results import ResultsWindow

            return ResultsWindow

        # Register all default window creators
        cls._window_creators.update(
            {
                "main": _create_main_window,
                "code_editor": _create_code_editor,
                "comparator": _create_comparator,
                "benchmarker": _create_benchmarker,
                "validator": _create_validator,
                "help_center": _create_help_center,
                "results": _create_results,
            }
        )
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
    """
    Manages application window instances and navigation.
    
    Responsibilities (Manager Pattern):
    - Cache created window instances (avoid recreating)
    - Display windows in QStackedWidget
    - Track current window
    - Cleanup window resources
    
    Collaborates with:
    - WindowFactory: Creates window instances
    - NavigationRouter: Handles navigation history and routing
    
    Note: self.windows is an instance-level cache of CREATED WINDOW INSTANCES,
    different from WindowFactory's class-level registry of creation functions.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.windows: dict[str, QWidget] = {}  # Instance cache: {window_name: window_instance}
        self.current_window: Optional[str] = None
        self.router: Optional['NavigationRouter'] = None  # Will be set by MainWindow
    
    def get_navigation_router(self) -> Optional['NavigationRouter']:
        """
        Get the NavigationRouter instance if available.
        
        Returns:
            NavigationRouter instance or None
        """
        return self.router

    def show_window(self, window_name: str, _add_to_history: bool = True, **kwargs) -> bool:
        """
        Show a window, creating it if it doesn't exist.
        
        Args:
            window_name: Name of window to show
            _add_to_history: Internal flag used by NavigationRouter
            **kwargs: Additional arguments (reserved for future use)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get or create window instance
            window = self._get_or_create_window(window_name)
            if not window:
                return False

            # Display window
            window.show()
            self.setCurrentWidget(window)
            self.current_window = window_name
            return True

        except (RuntimeError, AttributeError, ValueError) as e:
            logger.error(f"Error showing window '{window_name}': {e}", exc_info=True)
            return False
    
    def _get_or_create_window(self, window_name: str) -> Optional[QWidget]:
        """
        Get cached window or create new instance.
        
        Separates window creation (Factory responsibility) from display (Manager responsibility).
        
        Args:
            window_name: Name of window to get/create
            
        Returns:
            Window instance or None if creation failed
        """
        # Return cached instance if exists
        if window_name in self.windows:
            return self.windows[window_name]
        
        # Create new instance using factory
        window = WindowFactory.create_window(window_name, self.parent())
        if not window:
            logger.error(f"WindowFactory failed to create window '{window_name}'")
            return None
        
        # Validate window type
        if not isinstance(window, QWidget):
            logger.error(f"Created window '{window_name}' is not a QWidget")
            return None
        
        # Cache and add to stack
        self.windows[window_name] = window
        self.addWidget(window)
        
        logger.debug(f"Created and cached new window: '{window_name}'")
        return window

    def get_current_window(self) -> Optional[QWidget]:
        """
        Get the currently active window instance.
        
        Returns:
            Current window instance or None
        """
        return self.windows.get(self.current_window)

    def cleanup_window(self, window_name: str) -> None:
        """
        Clean up a window's resources and remove from cache.
        
        Steps:
        1. Call window's cleanup() method if it exists
        2. Switch away from window if it's currently displayed
        3. Remove from Qt stack and cache
        4. Schedule Qt deletion
        
        Args:
            window_name: Name of window to cleanup
        """
        try:
            if window_name not in self.windows:
                return
            
            window = self.windows[window_name]
            
            # Call window-specific cleanup
            if hasattr(window, "cleanup"):
                try:
                    window.cleanup()
                except (RuntimeError, AttributeError) as e:
                    logger.warning(f"Error in window cleanup for '{window_name}': {e}")
            
            # Switch away from window if currently displayed
            if window == self.currentWidget():
                self._switch_to_fallback_window(window_name)
            
            # Remove from stack and cache
            self.removeWidget(window)
            window.deleteLater()
            del self.windows[window_name]
            
            logger.debug(f"Cleaned up window: '{window_name}'")
            
        except RuntimeError as e:
            logger.warning(f"Runtime error during cleanup of '{window_name}': {e}")
    
    def _switch_to_fallback_window(self, excluding_window: str) -> None:
        """
        Switch to a fallback window (preferably main).
        
        Args:
            excluding_window: Window name to exclude from fallback options
        """
        # Prefer main window
        if "main" in self.windows and excluding_window != "main":
            self.setCurrentWidget(self.windows["main"])
            self.current_window = "main"
        # Otherwise use any other window
        elif len(self.windows) > 1:
            fallback_name, fallback_window = next(
                (name, w) for name, w in self.windows.items() 
                if name != excluding_window
            )
            self.setCurrentWidget(fallback_window)
            self.current_window = fallback_name

    def cleanup_all(self) -> None:
        """
        Clean up all windows safely.
        
        Strategy: Cleanup non-main windows first, then main window last.
        This ensures the UI has a fallback during cleanup.
        """
        # Get list of window names (copy to avoid modification during iteration)
        window_names = sorted(
            list(self.windows.keys()),
            key=lambda x: 0 if x == "main" else 1,
            reverse=True,
        )
        
        logger.debug(f"Cleaning up {len(window_names)} windows")
        
        for window_name in window_names:
            self.cleanup_window(window_name)
    
    def apply_editor_settings_to_all(self, editor_settings: dict) -> None:
        """Apply editor settings to all cached windows with editors via hot reload."""
        logger.info("Applying editor settings to all windows")
        
        for window_name, window in self.windows.items():
            try:
                # Check if window has editor_widget attribute
                if hasattr(window, 'editor_widget') and window.editor_widget:
                    window.editor_widget.apply_settings(editor_settings)
                    logger.debug(f"Applied settings to {window_name}.editor_widget")
                
                # Check if window has editor_tab_widget attribute  
                if hasattr(window, 'editor_tab_widget') and window.editor_tab_widget:
                    if hasattr(window.editor_tab_widget, 'apply_settings_to_all'):
                        window.editor_tab_widget.apply_settings_to_all(editor_settings)
                        logger.debug(f"Applied settings to {window_name}.editor_tab_widget")
                
                # Check if window itself is an editor widget
                if hasattr(window, 'apply_settings') and callable(window.apply_settings):
                    window.apply_settings(editor_settings)
                    logger.debug(f"Applied settings to {window_name} directly")
                    
            except Exception as e:
                logger.error(f"Error applying settings to window '{window_name}': {e}", exc_info=True)
    
    def reload_all_configs(self, config: dict) -> None:
        """
        Reload configuration for all cached windows and their components.
        
        This triggers hot-reload of:
        - Editor settings (fonts, tabs, etc.)
        - Compiler settings (C++, Python, Java)
        - AI settings
        - Any other config-dependent components
        
        Args:
            config: Full configuration dictionary
        """
        logger.info("Reloading configuration for all windows")
        
        # Apply editor settings
        editor_settings = config.get("editor_settings", {})
        if editor_settings:
            self.apply_editor_settings_to_all(editor_settings)
        
        # Reload compiler settings in windows with compilation tools
        for window_name, window in self.windows.items():
            try:
                # Check for CompilerRunner instances
                if hasattr(window, 'compiler_runner') and window.compiler_runner:
                    if hasattr(window.compiler_runner, 'reload_config'):
                        window.compiler_runner.reload_config()
                        logger.debug(f"Reloaded compiler config for {window_name}")
                
                # Check for BaseRunner instances (Benchmarker, Comparator, Validator)
                if hasattr(window, 'tool') and window.tool:
                    if hasattr(window.tool, 'reload_config'):
                        window.tool.reload_config(config)
                        logger.debug(f"Reloaded tool config for {window_name}")
                
                # Check for nested display areas with compiler runners
                if hasattr(window, 'display_area') and window.display_area:
                    if hasattr(window.display_area, 'compiler_runner'):
                        if hasattr(window.display_area.compiler_runner, 'reload_config'):
                            window.display_area.compiler_runner.reload_config()
                            logger.debug(f"Reloaded compiler config for {window_name}.display_area")
                
            except Exception as e:
                logger.error(f"Error reloading config for window '{window_name}': {e}", exc_info=True)
        
        logger.info("Configuration reload completed for all windows")
