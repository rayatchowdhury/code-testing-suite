"""
Domain interface for creating status views.

This allows services to request status views without knowing
about the specific UI framework being used.
"""

from abc import ABC, abstractmethod
from domain.views.status_view import (
    CompilationStatusView,
    StressTestStatusView,
    TLETestStatusView
)


class StatusViewFactory(ABC):
    """Interface for creating status view instances"""
    
    @abstractmethod
    def create_compilation_status_view(self) -> CompilationStatusView:
        """Create a compilation status view"""
        pass
    
    @abstractmethod
    def create_stress_test_status_view(self) -> StressTestStatusView:
        """Create a stress test status view"""
        pass
    
    @abstractmethod
    def create_tle_test_status_view(self) -> TLETestStatusView:
        """Create a TLE test status view"""
        pass
