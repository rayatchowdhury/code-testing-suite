"""
State service for application-wide state management.

Manages global UI state that multiple windows need to access.
"""

from typing import Any, Dict, Optional
from PySide6.QtCore import QObject, Signal


class StateService(QObject):
    """
    Singleton service for application state.
    
    Manages shared state across windows and widgets.
    
    Usage:
        from src.app.presentation.services.state_service import StateService
        
        state = StateService.instance()
        state.set("last_test_run", datetime.now())
        last_run = state.get("last_test_run")
    """
    
    # Singleton instance
    _instance: Optional['StateService'] = None
    
    # Signals
    stateChanged = Signal(str, object)  # key, value
    
    @classmethod
    def instance(cls) -> 'StateService':
        """
        Get singleton instance.
        
        Returns:
            StateService singleton
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """
        Initialize StateService.
        
        Raises:
            RuntimeError: If called directly (use instance() instead)
        """
        if StateService._instance is not None:
            raise RuntimeError("Use StateService.instance()")
        super().__init__()
        self._state: Dict[str, Any] = {}
        # TODO: Implementation if needed
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get state value.
        
        Args:
            key: State key
            default: Default value if key not found
        
        Returns:
            State value
        """
        return self._state.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Set state value.
        
        Args:
            key: State key
            value: New value
        """
        self._state[key] = value
        self.stateChanged.emit(key, value)
