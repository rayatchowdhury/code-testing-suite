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
    
    def show_error(
        self,
        title: str,
        message: str,
        parent: Optional[QWidget] = None,
        log: bool = True
    ):
        """
        Show error dialog (convenience method).
        
        Args:
            title: Dialog title
            message: Error message
            parent: Parent widget for dialog
            log: Whether to log the error
        """
        if log:
            logging.error(f"{title}: {message}")
        
        self.errorOccurred.emit(title, message, ErrorSeverity.ERROR)
        
        if parent:
            QMessageBox.critical(parent, title, message)
    
    def show_warning(
        self,
        title: str,
        message: str,
        parent: Optional[QWidget] = None,
        log: bool = True
    ):
        """
        Show warning dialog (convenience method).
        
        Args:
            title: Dialog title
            message: Warning message
            parent: Parent widget for dialog
            log: Whether to log the warning
        """
        if log:
            logging.warning(f"{title}: {message}")
        
        self.errorOccurred.emit(title, message, ErrorSeverity.WARNING)
        
        if parent:
            QMessageBox.warning(parent, title, message)
    
    def show_info(
        self,
        title: str,
        message: str,
        parent: Optional[QWidget] = None,
        log: bool = True
    ):
        """
        Show information dialog (convenience method).
        
        Args:
            title: Dialog title
            message: Information message
            parent: Parent widget for dialog
            log: Whether to log the message
        """
        if log:
            logging.info(f"{title}: {message}")
        
        self.errorOccurred.emit(title, message, ErrorSeverity.INFO)
        
        if parent:
            QMessageBox.information(parent, title, message)
    
    def show_success(
        self,
        title: str,
        message: str,
        parent: Optional[QWidget] = None,
        log: bool = True
    ):
        """
        Show success message (convenience method, uses information dialog).
        
        Args:
            title: Dialog title
            message: Success message
            parent: Parent widget for dialog
            log: Whether to log the message
        """
        if log:
            logging.info(f"{title}: {message}")
        
        self.errorOccurred.emit(title, message, ErrorSeverity.INFO)
        
        if parent:
            QMessageBox.information(parent, title, message)
    
    def ask_question(
        self,
        title: str,
        message: str,
        buttons: QMessageBox.StandardButtons = QMessageBox.Yes | QMessageBox.No,
        default_button: QMessageBox.StandardButton = QMessageBox.No,
        parent: Optional[QWidget] = None
    ) -> int:
        """
        Show question dialog and return user choice.
        
        Args:
            title: Dialog title
            message: Question message
            buttons: Button combination (e.g., Yes|No, Ok|Cancel)
            default_button: Default selected button
            parent: Parent widget for dialog
            
        Returns:
            QMessageBox.StandardButton value (Yes, No, Ok, Cancel, etc.)
        """
        if parent:
            return QMessageBox.question(
                parent,
                title,
                message,
                buttons,
                default_button
            )
        return QMessageBox.No  # Safe default if no parent
    
    def ask_save_discard_cancel(
        self,
        title: str,
        message: str,
        parent: Optional[QWidget] = None
    ) -> int:
        """
        Show save/discard/cancel dialog (convenience method).
        
        Args:
            title: Dialog title
            message: Message asking about saving
            parent: Parent widget for dialog
            
        Returns:
            QMessageBox.Save, QMessageBox.Discard, or QMessageBox.Cancel
        """
        if parent:
            return QMessageBox.question(
                parent,
                title,
                message,
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
        return QMessageBox.Cancel  # Safe default if no parent
