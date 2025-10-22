"""
Navigation Router for window management.

Provides injectable navigation without singleton coupling.
"""

import logging
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class NavigationRouter(QObject):
    """
    Injectable navigation router with history tracking.

    Replaces the singleton NavigationService with a testable, injectable router.
    
    Features:
    - Injectable window_manager dependency
    - Navigation history tracking
    - Back button support
    - Signal-based navigation events
    
    Usage:
        # In MainWindow initialization:
        router = NavigationRouter(self.window_manager)
        self.window_manager.router = router
        
        # In any child window/widget with parent access:
        self.router.navigate_to("benchmarker")
        self.router.go_back()
    
    Design:
    - No singleton pattern - instance is passed via constructor injection
    - Parent widgets access router via parent traversal
    - Testable via mock window_manager
    """
    
    # Signals
    windowChangeRequested = Signal(str, dict)  # window_name, kwargs
    navigationCompleted = Signal(str)  # window_name
    navigationFailed = Signal(str, str)  # window_name, error
    
    def __init__(self, window_manager, parent: Optional[QObject] = None):
        """
        Initialize NavigationRouter.
        
        Args:
            window_manager: WindowManager instance for window operations
            parent: Optional parent QObject
        """
        super().__init__(parent)
        self._window_manager = window_manager
        self._history: list[str] = []
        self._max_history_size = 50  # Prevent unbounded growth
    
    def navigate_to(self, window_name: str, **kwargs: Any) -> bool:
        """
        Navigate to a window.
        
        Args:
            window_name: Name of window to show (e.g., "main", "benchmarker", "results")
            **kwargs: Window initialization arguments
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        if not self._window_manager:
            logger.warning(
                f"NavigationRouter: Cannot navigate to '{window_name}' - no window_manager"
            )
            self.windowChangeRequested.emit(window_name, kwargs)
            self.navigationFailed.emit(window_name, "No window manager")
            return False
        
        try:
            # Track current window in history before navigation
            current = self.current_window()
            
            # Perform navigation
            success = self._window_manager.show_window(window_name, **kwargs)
            
            if success:
                # Add to history only if navigation was successful and it's a different window
                if current and current != window_name:
                    self._add_to_history(current)
                
                logger.debug(f"NavigationRouter: Navigated to '{window_name}'")
                self.navigationCompleted.emit(window_name)
                return True
            else:
                logger.warning(f"NavigationRouter: Failed to navigate to '{window_name}'")
                self.navigationFailed.emit(window_name, "show_window returned False")
                return False
                
        except (AttributeError, RuntimeError, ValueError) as e:
            logger.error(
                f"NavigationRouter: Error navigating to '{window_name}': {e}",
                exc_info=True
            )
            self.navigationFailed.emit(window_name, str(e))
            return False
    
    def go_back(self) -> bool:
        """
        Navigate to previous window in history.
        
        Returns:
            bool: True if navigation successful, False if no history or navigation failed
        """
        if not self.can_go_back():
            logger.debug("NavigationRouter: Cannot go back - no history")
            return False
        
        try:
            # Get previous window from history
            previous_window = self._history.pop()
            
            # Navigate without adding to history (_add_to_history=False)
            if self._window_manager:
                success = self._window_manager.show_window(previous_window, _add_to_history=False)
                
                if success:
                    logger.debug(f"NavigationRouter: Navigated back to '{previous_window}'")
                    self.navigationCompleted.emit(previous_window)
                    return True
                else:
                    # If navigation failed, restore history
                    self._history.append(previous_window)
                    logger.warning(
                        f"NavigationRouter: Failed to navigate back to '{previous_window}'"
                    )
                    return False
            
            return False
            
        except (AttributeError, RuntimeError, IndexError) as e:
            logger.error(f"NavigationRouter: Error going back: {e}", exc_info=True)
            return False
    
    def can_go_back(self) -> bool:
        """
        Check if back navigation is available.
        
        Returns:
            bool: True if there is history to navigate back to
        """
        return len(self._history) > 0
    
    def current_window(self) -> Optional[str]:
        """
        Get name of currently displayed window.
        
        Returns:
            Window name or None if not available
        """
        if self._window_manager:
            return getattr(self._window_manager, 'current_window', None)
        return None
    
    def clear_history(self):
        """
        Clear navigation history.
        
        Useful for resetting navigation state (e.g., after logout).
        """
        self._history.clear()
        logger.debug("NavigationRouter: History cleared")
    
    def get_history(self) -> list[str]:
        """
        Get copy of navigation history.
        
        Returns:
            List of window names in history (most recent last)
        """
        return self._history.copy()
    
    def _add_to_history(self, window_name: str):
        """
        Add window to navigation history.
        
        Args:
            window_name: Name of window to add
        """
        # Avoid duplicate consecutive entries
        if self._history and self._history[-1] == window_name:
            return
        
        self._history.append(window_name)
        
        # Trim history if it exceeds max size
        if len(self._history) > self._max_history_size:
            self._history = self._history[-self._max_history_size:]
            logger.debug(f"NavigationRouter: Trimmed history to {self._max_history_size} entries")
