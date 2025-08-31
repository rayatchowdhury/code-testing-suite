# TODO: Extract service interfaces from v1 tools to break circular dependencies
"""
Compilation Service Interfaces

Protocol definitions for compilation services to break tool→view dependencies.
Based on v1 tools/compiler_runner.py, tools/stresser.py, tools/tle_runner.py
"""
from typing import Protocol, AsyncIterator, Optional
from pathlib import Path
from domain.models.compilation import (
    CompilationResult, 
    StressTestResult, 
    TLETestResult,
    CompilationStatus,
    TestCase
)

class CompilationObserver(Protocol):
    """Observer interface for compilation events"""
    
    def on_compilation_started(self, file_name: str) -> None:
        """Called when compilation starts for a file"""
        ...
    
    def on_compilation_progress(self, file_name: str, progress: float) -> None:
        """Called during compilation progress"""
        ...
    
    def on_compilation_finished(self, file_name: str, result: CompilationResult) -> None:
        """Called when compilation completes"""
        ...
    
    def on_all_compilations_finished(self, success: bool, message: str) -> None:
        """Called when all compilations are complete"""
        ...

class StressTestObserver(Protocol):
    """Observer interface for stress testing events"""
    
    def on_test_started(self, test_number: int, total_tests: int) -> None:
        """Called when a stress test starts"""
        ...
    
    def on_test_completed(self, test_case: TestCase) -> None:
        """Called when a stress test completes"""
        ...
    
    def on_all_tests_completed(self, result: StressTestResult) -> None:
        """Called when all stress tests complete"""
        ...

class TLETestObserver(Protocol):
    """Observer interface for TLE testing events"""
    
    def on_tle_test_started(self, test_name: str) -> None:
        """Called when a TLE test starts"""
        ...
    
    def on_tle_test_completed(self, result: TLETestResult) -> None:
        """Called when a TLE test completes"""
        ...
    
    def on_all_tle_tests_completed(self, all_passed: bool) -> None:
        """Called when all TLE tests complete"""
        ...

class CompilationService(Protocol):
    """Service interface for compilation operations"""
    
    def add_observer(self, observer: CompilationObserver) -> None:
        """Add a compilation observer"""
        ...
    
    def remove_observer(self, observer: CompilationObserver) -> None:
        """Remove a compilation observer"""
        ...
    
    async def compile_file(self, file_path: Path) -> CompilationResult:
        """Compile a single file"""
        ...
    
    async def compile_files(self, file_paths: list[Path]) -> AsyncIterator[CompilationResult]:
        """Compile multiple files"""
        ...
    
    def cancel_compilation(self) -> None:
        """Cancel ongoing compilation"""
        ...

class StressTestService(Protocol):
    """Service interface for stress testing operations"""
    
    def add_observer(self, observer: StressTestObserver) -> None:
        """Add a stress test observer"""
        ...
    
    def remove_observer(self, observer: StressTestObserver) -> None:
        """Remove a stress test observer"""
        ...
    
    async def run_stress_tests(
        self, 
        generator_path: Path,
        solution_path: Path, 
        test_count: int
    ) -> StressTestResult:
        """Run stress tests between generator and solution"""
        ...
    
    def stop_stress_tests(self) -> None:
        """Stop ongoing stress tests"""
        ...

class TLETestService(Protocol):
    """Service interface for time-limit testing operations"""
    
    def add_observer(self, observer: TLETestObserver) -> None:
        """Add a TLE test observer"""
        ...
    
    def remove_observer(self, observer: TLETestObserver) -> None:
        """Remove a TLE test observer"""
        ...
    
    async def run_tle_test(
        self,
        generator_path: Path,
        solution_path: Path,
        time_limit: float
    ) -> list[TLETestResult]:
        """Run time-limit exceeded tests"""
        ...
    
    def stop_tle_tests(self) -> None:
        """Stop ongoing TLE tests"""
        ...

class WorkspaceService(Protocol):
    """Service interface for workspace operations"""
    
    def get_workspace_directory(self) -> Path:
        """Get current workspace directory"""
        ...
    
    def set_workspace_directory(self, path: Path) -> None:
        """Set workspace directory"""
        ...
    
    def get_source_files(self, extension: str = "cpp") -> list[Path]:
        """Get source files in workspace"""
        ...
    
    def create_temporary_files(self, content: dict[str, str]) -> dict[str, Path]:
        """Create temporary files for testing"""
        ...
