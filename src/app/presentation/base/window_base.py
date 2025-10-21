"""
Root base class for all presentation windows.

WindowBase provides fundamental lifecycle management, error handling
integration, and signal management for all windows.
"""

import logging

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal

logger = logging.getLogger(__name__)

class WindowBase(QWidget):
    """
    Base class for all windows in the presentation layer.
    
    Responsibilities:
    - Window lifecycle management (show, close events)
    - Error handling service integration
    - Signal management utilities
    - Common window behaviors
    
    Subclasses:
    - ContentWindowBase: Windows with sidebar layout
    
    Usage:
        class MyWindow(WindowBase):
            def __init__(self, parent=None):
                super().__init__(parent)
                # Initialize window-specific logic
    """
    
    # Signals
    windowShown = Signal()
    windowClosed = Signal()
    
    def __init__(self, parent=None):
        """
        Initialize WindowBase.
        
        Args:
            parent: Parent widget (typically MainWindow)
        """
        super().__init__(parent)
        self.parent = parent
        self._is_initialized = False
        self.has_unsaved_changes = False
    
    def showEvent(self, event):
        """
        Handle window show event.
        
        Emits windowShown signal and performs first-time initialization.
        
        Args:
            event: QShowEvent
        """
        super().showEvent(event)
        if not self._is_initialized:
            self._on_first_show()
            self._is_initialized = True
        self.windowShown.emit()
    
    def closeEvent(self, event):
        """
        Handle window close event.
        
        Emits windowClosed signal and performs cleanup.
        
        Args:
            event: QCloseEvent
        """
        self.windowClosed.emit()
        self.cleanup()
        super().closeEvent(event)
    
    def _on_first_show(self):
        """
        Called once when window is first shown.
        
        Override in subclasses to perform one-time initialization
        that requires the window to be visible (e.g., geometry calculations).
        """
        pass
    
    def cleanup(self):
        """
        Clean up resources when window is closed.
        
        Override in subclasses to release resources, disconnect signals,
        stop background tasks, etc.
        """
        pass
    
    def can_close(self):
        """
        Check if window can be closed safely.
        
        Returns:
            bool: True if window can close, False to prevent closing
            
        Override in subclasses to check for unsaved changes or
        confirm dangerous operations.
        """
        return not self.has_unsaved_changes
    
    def handle_error(self, error: Exception, title: str = "Error"):
        """
        Handle an error using the error handler service.
        
        Args:
            error: The exception that occurred
            title: Error dialog title
        """
        try:
            from ..services.error_handler_service import ErrorHandlerService, ErrorSeverity
            ErrorHandlerService.instance().handle_error(
                error,
                title=title,
                severity=ErrorSeverity.ERROR,
                parent=self,
                log=True
            )
        except ImportError:
            # Fallback if service not available
            logger.error(f"{title}: {error}", exc_info=True)
    
    @property
    def router(self):
        """
        Get navigation router via parent traversal.
        
        Enables nested widgets to access router without direct injection.
        Traverses up the parent chain to find a widget with a router.
        
        Returns:
            NavigationRouter or None if not found
            
        Usage:
            # In any window or nested widget:
            if self.router:
                self.router.navigate_to("main")
        """
        # Check if we have our own router
        if hasattr(self, '_router'):
            return self._router
        
        # Traverse up the parent chain to find router
        # parent() is a QWidget method, not a property
        current = self.parent() if callable(getattr(self, 'parent', None)) else getattr(self, 'parent', None)
        while current:
            if hasattr(current, 'router') and current.router is not None:
                return current.router
            if hasattr(current, '_router') and current._router is not None:
                return current._router
            # Get next parent - check if parent() is callable
            if hasattr(current, 'parent'):
                parent_method = getattr(current, 'parent')
                current = parent_method() if callable(parent_method) else parent_method
            else:
                current = None
        
        # No router found
        return None
    
    @router.setter
    def router(self, value):
        """
        Set navigation router.
        
        Args:
            value: NavigationRouter instance
        """
        self._router = value
