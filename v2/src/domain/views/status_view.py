"""
Domain view interfaces for status displays.

These define the contracts for showing compilation and test status
without coupling to any specific UI framework.
"""

from abc import ABC, abstractmethod
from typing import Optional
from domain.models.compilation import CompilationResult


class StatusView(ABC):
    """Base interface for status views"""
    
    @abstractmethod
    def show(self) -> None:
        """Show the status view"""
        pass
    
    @abstractmethod
    def hide(self) -> None:
        """Hide the status view"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the status view"""
        pass


class CompilationStatusView(StatusView):
    """Interface for compilation status display"""
    
    @abstractmethod
    def show_compilation_started(self, file_name: str) -> None:
        """Show that compilation has started for a file"""
        pass
    
    @abstractmethod
    def show_compilation_result(self, result: CompilationResult) -> None:
        """Show the result of compilation"""
        pass
    
    @abstractmethod
    def show_compilation_output(self, output: str, is_error: bool = False) -> None:
        """Show compilation output or error"""
        pass


class StressTestStatusView(StatusView):
    """Interface for stress test status display"""
    
    @abstractmethod
    def show_test_started(self, total_tests: int) -> None:
        """Show that stress testing has started"""
        pass
    
    @abstractmethod
    def show_test_progress(self, completed: int, total: int) -> None:
        """Show progress of stress testing"""
        pass
    
    @abstractmethod
    def show_test_completed(self) -> None:
        """Show that stress testing has completed"""
        pass
    
    @abstractmethod
    def show_test_result(self, test_number: int, passed: bool, output: str) -> None:
        """Show result of a specific test"""
        pass


class TLETestStatusView(StatusView):
    """Interface for TLE test status display"""
    
    @abstractmethod
    def show_tle_test_started(self, time_limit: float) -> None:
        """Show that TLE testing has started"""
        pass
    
    @abstractmethod
    def show_tle_test_completed(self, execution_time: float, timed_out: bool) -> None:
        """Show TLE test completion with timing results"""
        pass
