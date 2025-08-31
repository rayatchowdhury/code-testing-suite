# TODO: Extract view interfaces from v1 views to break tool→view dependencies
"""
Status View Interfaces

Protocol definitions for status windows to break tool→view circular dependencies.
Based on v1 views/stress_tester/compilation_status_window.py and related status windows.
"""
from typing import Protocol
from domain.models.compilation import CompilationStatus, CompilationResult, TestCase

class StatusView(Protocol):
    """Base interface for status display windows"""
    
    def show(self) -> None:
        """Show the status window"""
        ...
    
    def hide(self) -> None:
        """Hide the status window"""
        ...
    
    def close(self) -> None:
        """Close the status window"""
        ...

class CompilationStatusView(StatusView, Protocol):
    """Interface for compilation status display"""
    
    def update_file_status(self, file_name: str, status: CompilationStatus) -> None:
        """Update status for a specific file"""
        ...
    
    def show_compilation_output(self, file_name: str, output: str, is_error: bool = False) -> None:
        """Show compilation output for a file"""
        ...
    
    def show_final_result(self, success: bool, message: str) -> None:
        """Show final compilation result"""
        ...

class StressTestStatusView(StatusView, Protocol):
    """Interface for stress test status display"""
    
    def show_test_running(self, test_number: int, total_tests: int) -> None:
        """Show that a test is currently running"""
        ...
    
    def show_test_complete(self, test_case: TestCase) -> None:
        """Show completion of a single test"""
        ...
    
    def show_all_passed(self, all_passed: bool) -> None:
        """Show final result of all tests"""
        ...
    
    def update_progress(self, completed: int, total: int) -> None:
        """Update overall progress"""
        ...

class TLETestStatusView(StatusView, Protocol):
    """Interface for TLE test status display"""
    
    def show_test_running(self, test_name: str) -> None:
        """Show that a TLE test is running"""
        ...
    
    def show_test_complete(self, test_name: str, passed: bool, execution_time: float) -> None:
        """Show completion of a TLE test"""
        ...
    
    def show_all_passed(self, all_passed: bool) -> None:
        """Show final TLE test results"""
        ...

class StatusViewFactory(Protocol):
    """Factory interface for creating status views"""
    
    def create_compilation_status_view(self) -> CompilationStatusView:
        """Create compilation status view"""
        ...
    
    def create_stress_test_status_view(self) -> StressTestStatusView:
        """Create stress test status view"""
        ...
    
    def create_tle_test_status_view(self) -> TLETestStatusView:
        """Create TLE test status view"""
        ...
