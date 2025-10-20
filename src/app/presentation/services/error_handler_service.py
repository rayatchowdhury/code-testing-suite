"""
Error handler service for centralized error management.

Replaces scattered print statements and QMessageBox calls with
consistent error handling, logging, and user feedback.
"""

from enum import Enum
from typing import Optional
from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtCore import QObject, Signal
import logging


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "information"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorHandlerService(QObject):
    """
    Singleton service for error handling.
    
    Provides:
    - Consistent error logging
    - User-facing error dialogs
    - Severity-based handling
    - Error event notifications
    
    Usage:
        from src.app.presentation.services.error_handler_service import (
            ErrorHandlerService, ErrorSeverity
        )
        
        try:
            risky_operation()
        except Exception as e:
            ErrorHandlerService.instance().handle_error(
                e,
                title="Operation Failed",
                severity=ErrorSeverity.ERROR,
                parent=self
            )
    """
    
    # Singleton instance
    _instance: Optional['ErrorHandlerService'] = None
    
    # Signals
    errorOccurred = Signal(str, str, ErrorSeverity)  # title, message, severity
    
    @classmethod
    def instance(cls) -> 'ErrorHandlerService':
        """
        Get singleton instance.
        
        Returns:
            ErrorHandlerService singleton
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """
        Initialize ErrorHandlerService.
        
        Raises:
            RuntimeError: If called directly (use instance() instead)
        """
        if ErrorHandlerService._instance is not None:
            raise RuntimeError("Use ErrorHandlerService.instance()")
        super().__init__()
        ErrorHandlerService._instance = self
    
    def handle_error(
        self,
        error: Exception,
        title: str = "Error",
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        parent: Optional[QWidget] = None,
        log: bool = True
    ):
        """
        Handle an error with logging and user notification.
        
        Args:
            error: The exception that occurred
            title: Dialog title
            severity: Error severity level
            parent: Parent widget for dialog
            log: Whether to log the error
        """
        message = str(error)
        
        # Log the error
        if log:
            if severity == ErrorSeverity.CRITICAL:
                logging.critical(f"{title}: {message}", exc_info=error)
            elif severity == ErrorSeverity.ERROR:
                logging.error(f"{title}: {message}", exc_info=error)
            elif severity == ErrorSeverity.WARNING:
                logging.warning(f"{title}: {message}")
            else:
                logging.info(f"{title}: {message}")
        
        # Emit signal for event tracking
        self.errorOccurred.emit(title, message, severity)
        
        # Show dialog to user
        if parent:
            if severity in (ErrorSeverity.CRITICAL, ErrorSeverity.ERROR):
                QMessageBox.critical(parent, title, message)
            elif severity == ErrorSeverity.WARNING:
                QMessageBox.warning(parent, title, message)
            else:
                QMessageBox.information(parent, title, message)
