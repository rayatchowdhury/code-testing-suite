"""
Navigation service for window management.

Provides centralized navigation without parent.window_manager coupling.
"""

from typing import Optional
from PySide6.QtCore import QObject, Signal


class NavigationService(QObject):
    """
    Singleton service for window navigation.
    
    Decouples windows from direct WindowManager access, enabling:
    - Testable navigation
    - No parent coupling
    - Centralized navigation logic
    
    Usage:
        # In any window or widget
        from src.app.presentation.services.navigation_service import NavigationService
        
        NavigationService.instance().navigate_to("benchmarker")
        NavigationService.instance().go_back()
    
    Setup (in MainWindow):
        nav_service = NavigationService.instance()
        nav_service.set_window_manager(self.window_manager)
    """
    
    # Singleton instance
    _instance: Optional['NavigationService'] = None
    
    # Signals
    windowChangeRequested = Signal(str, dict)  # window_name, kwargs
    
    @classmethod
    def instance(cls) -> 'NavigationService':
        """
        Get singleton instance.
        
        Returns:
            NavigationService singleton
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """
        Initialize NavigationService.
        
        Raises:
            RuntimeError: If called directly (use instance() instead)
        """
        if NavigationService._instance is not None:
            raise RuntimeError("Use NavigationService.instance()")
        super().__init__()
        self._window_manager = None
        # TODO: Implementation in Phase 1C
    
    def set_window_manager(self, manager):
        """
        Register the WindowManager.
        
        Called by MainWindow during initialization.
        
        Args:
            manager: WindowManager instance
        """
        # TODO: Implementation in Phase 1C
        pass
    
    def navigate_to(self, window_name: str, **kwargs):
        """
        Navigate to a window.
        
        Args:
            window_name: Name of window to show
            **kwargs: Window initialization arguments
        """
        # TODO: Implementation in Phase 1C
        pass
    
    def go_back(self):
        """Navigate to previous window in history."""
        # TODO: Implementation in Phase 1C
        pass
    
    def current_window(self) -> Optional[str]:
        """
        Get name of currently displayed window.
        
        Returns:
            Window name or None
        """
        # TODO: Implementation in Phase 1C
        pass
