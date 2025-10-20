"""
Test execution service for coordinating test runs.

Coordinates test execution across multiple windows and tools.
"""

from typing import Optional
from PySide6.QtCore import QObject, Signal


class TestExecutionService(QObject):
    """
    Singleton service for test execution coordination.
    
    Coordinates test runs, manages execution state, and provides
    cross-window test management.
    
    Usage:
        from src.app.presentation.services.test_execution_service import (
            TestExecutionService
        )
        
        service = TestExecutionService.instance()
        service.register_runner("benchmarker", runner)
    """
    
    # Singleton instance
    _instance: Optional['TestExecutionService'] = None
    
    # Signals
    testingStarted = Signal(str)  # tool_name
    testingCompleted = Signal(str)  # tool_name
    
    @classmethod
    def instance(cls) -> 'TestExecutionService':
        """
        Get singleton instance.
        
        Returns:
            TestExecutionService singleton
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """
        Initialize TestExecutionService.
        
        Raises:
            RuntimeError: If called directly (use instance() instead)
        """
        if TestExecutionService._instance is not None:
            raise RuntimeError("Use TestExecutionService.instance()")
        super().__init__()
        # TODO: Implementation if needed
