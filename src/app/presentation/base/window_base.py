"""
Root base class for all presentation windows.

WindowBase provides fundamental lifecycle management, error handling
integration, and signal management for all windows.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal


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
        # TODO: Implementation in Phase 1B
    
    def showEvent(self, event):
        """
        Handle window show event.
        
        Emits windowShown signal and performs initialization.
        
        Args:
            event: QShowEvent
        """
        # TODO: Implementation in Phase 1B
        pass
    
    def closeEvent(self, event):
        """
        Handle window close event.
        
        Emits windowClosed signal and performs cleanup.
        
        Args:
            event: QCloseEvent
        """
        # TODO: Implementation in Phase 1B
        pass
    
    def handle_error(self, error: Exception, title: str = "Error"):
        """
        Handle an error using the error handler service.
        
        Args:
            error: The exception that occurred
            title: Error dialog title
        """
        # TODO: Implementation in Phase 1C (after ErrorHandlerService)
        pass
