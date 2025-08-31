"""
Status view factory implementations.

Provides both Qt and mock implementations of status view creation.
"""

from domain.views.view_factory import StatusViewFactory
from domain.views.status_view import (
    CompilationStatusView,
    StressTestStatusView, 
    TLETestStatusView
)
from domain.models.compilation import CompilationResult


class QtStatusViewFactory(StatusViewFactory):
    """Qt implementation of status view factory"""
    
    def __init__(self):
        # TODO: Initialize Qt application context if needed
        pass
    
    def create_compilation_status_view(self) -> CompilationStatusView:
        """Create Qt compilation status view"""
        # TODO: Return actual Qt widget when GUI is ready
        from .status_window_adapter import CompilationStatusWindowAdapter
        return CompilationStatusWindowAdapter()
    
    def create_stress_test_status_view(self) -> StressTestStatusView:
        """Create Qt stress test status view"""
        # TODO: Return actual Qt widget when GUI is ready
        from .status_window_adapter import StressTestStatusWindowAdapter
        return StressTestStatusWindowAdapter()
    
    def create_tle_test_status_view(self) -> TLETestStatusView:
        """Create Qt TLE test status view"""
        # TODO: Return actual Qt widget when GUI is ready
        from .status_window_adapter import MockTLEStatusWindowAdapter
        return MockTLEStatusWindowAdapter()


class MockStatusViewFactory(StatusViewFactory):
    """Mock implementation of status view factory for testing"""
    
    def __init__(self):
        pass
    
    def create_compilation_status_view(self) -> CompilationStatusView:
        """Create mock compilation status view"""
        return MockCompilationStatusView()
    
    def create_stress_test_status_view(self) -> StressTestStatusView:
        """Create mock stress test status view"""
        return MockStressTestStatusView()
    
    def create_tle_test_status_view(self) -> TLETestStatusView:
        """Create mock TLE test status view"""
        return MockTLETestStatusView()


class MockCompilationStatusView(CompilationStatusView):
    """Mock compilation status view for testing"""
    
    def show(self) -> None:
        """Mock show"""
        print("📺 Mock: Showing compilation status view")
    
    def hide(self) -> None:
        """Mock hide"""
        print("📺 Mock: Hiding compilation status view")
    
    def close(self) -> None:
        """Mock close"""
        print("📺 Mock: Closing compilation status view")
    
    def show_compilation_started(self, file_name: str) -> None:
        """Mock show compilation started"""
        print(f"🔨 Mock: Compilation started for {file_name}")
    
    def show_compilation_result(self, result: CompilationResult) -> None:
        """Mock show compilation result"""
        status = "✅ Success" if result.success else "❌ Failed"
        print(f"🔨 Mock: Compilation result - {status}")
        if result.output:
            print(f"📄 Mock: Output: {result.output}")
        if result.error_message:
            print(f"⚠️ Mock: Error: {result.error_message}")
    
    def show_compilation_output(self, output: str, is_error: bool = False) -> None:
        """Mock show compilation output"""
        prefix = "⚠️ Error" if is_error else "📄 Output"
        print(f"{prefix} Mock: {output}")


class MockStressTestStatusView(StressTestStatusView):
    """Mock stress test status view for testing"""
    
    def show(self) -> None:
        """Mock show"""
        print("📺 Mock: Showing stress test status view")
    
    def hide(self) -> None:
        """Mock hide"""
        print("📺 Mock: Hiding stress test status view")
    
    def close(self) -> None:
        """Mock close"""
        print("📺 Mock: Closing stress test status view")
    
    def show_test_started(self, total_tests: int) -> None:
        """Mock show test started"""
        print(f"🧪 Mock: Stress test started with {total_tests} tests")
    
    def show_test_progress(self, completed: int, total: int) -> None:
        """Mock show test progress"""
        percentage = (completed / total * 100) if total > 0 else 0
        print(f"📊 Mock: Progress {completed}/{total} ({percentage:.1f}%)")
    
    def show_test_completed(self) -> None:
        """Mock show test completed"""
        print("✅ Mock: Stress test completed")
    
    def show_test_result(self, test_number: int, passed: bool, output: str) -> None:
        """Mock show test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"🧪 Mock: Test {test_number}: {status}")


class MockTLETestStatusView(TLETestStatusView):
    """Mock TLE test status view for testing"""
    
    def show(self) -> None:
        """Mock show"""
        print("📺 Mock: Showing TLE test status view")
    
    def hide(self) -> None:
        """Mock hide"""
        print("📺 Mock: Hiding TLE test status view")
    
    def close(self) -> None:
        """Mock close"""
        print("📺 Mock: Closing TLE test status view")
    
    def show_tle_test_started(self, time_limit: float) -> None:
        """Mock show TLE test started"""
        print(f"⏱️ Mock: TLE test started with {time_limit}s limit")
    
    def show_tle_test_completed(self, execution_time: float, timed_out: bool) -> None:
        """Mock show TLE test completed"""
        status = "⏰ TIMEOUT" if timed_out else "✅ COMPLETED"
        print(f"⏱️ Mock: TLE test {status} in {execution_time:.3f}s")
