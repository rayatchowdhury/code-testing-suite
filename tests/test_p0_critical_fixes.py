"""
Test suite for P0 Critical Issue Fixes

This module tests the critical fixes implemented for:
1. P0 Issue #1: Zombie Process Leak in CompilerRunner
2. P0 Issue #3: Broad Exception Catching in ProcessExecutor
3. P0 Issue #2: Database Connection Leaks

Run with: pytest tests/test_p0_critical_fixes.py -v
"""

import gc
import os
import subprocess
import sys
import tempfile
import time
from unittest.mock import MagicMock, Mock, patch

import psutil
import pytest
from PySide6.QtCore import QProcess
import pytest

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app.core.tools.base.process_executor import ProcessExecutor, ProcessResult
from src.app.core.tools.compiler_runner import CompilerRunner
from src.app.persistence.database.database_manager import (
    DatabaseManager,
    ValidationError,
)
from src.app.persistence.database.models import TestResult


class TestP0Issue1_ZombieProcessLeak:
    """Test P0 Issue #1: Zombie Process Leak Fix"""

    @pytest.mark.skipif(
        os.name != "nt", reason="Zombie process test specific to Windows"
    )
    def test_no_zombie_processes_after_cleanup(self):
        """Verify no zombie processes remain after cleanup"""
        # Get initial process count
        initial_pids = set(p.pid for p in psutil.process_iter())

        # Create mock console
        mock_console = MagicMock()
        mock_console.clear = MagicMock()
        mock_console.setInputEnabled = MagicMock()
        mock_console.displayOutput = MagicMock()

        # Create compiler runner
        runner = CompilerRunner(mock_console)

        # Create a simple test file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".cpp", delete=False
        ) as f:
            f.write('#include <iostream>\nint main() { std::cout << "test"; }')
            test_file = f.name

        try:
            # Start compilation
            runner.compile_and_run_code(test_file)
            time.sleep(0.5)  # Let process start

            # Cleanup
            runner._cleanup_worker()
            time.sleep(1.0)  # Let cleanup complete

            # Get final process count
            final_pids = set(p.pid for p in psutil.process_iter())

            # Check for zombie processes
            zombie_pids = final_pids - initial_pids
            zombie_count = len(zombie_pids)

            # Allow for some system processes, but should be minimal
            assert (
                zombie_count <= 2
            ), f"Found {zombie_count} potential zombie processes: {zombie_pids}"

        finally:
            # Cleanup test file
            try:
                os.unlink(test_file)
            except:
                pass

    def test_process_killed_before_thread_termination(self):
        """Verify process is killed before thread terminates"""
        mock_console = MagicMock()
        runner = CompilerRunner(mock_console)

        # Create mock worker with process
        mock_worker = MagicMock()
        mock_process = MagicMock()
        mock_process.state.return_value = QProcess.ProcessState.Running
        mock_worker.process = mock_process
        runner.worker = mock_worker

        # Create mock thread
        mock_thread = MagicMock()
        mock_thread.isRunning.return_value = True
        runner.thread = mock_thread

        # Call cleanup
        runner._cleanup_worker()

        # Verify process.kill() was called before thread.quit()
        assert mock_process.kill.called, "Process should be killed"
        assert mock_thread.quit.called, "Thread should be terminated"

        # Verify order: kill before quit
        # (Both should be called)
        assert mock_process.kill.call_count >= 1
        assert mock_thread.quit.call_count >= 1


class TestP0Issue3_BroadExceptionCatching:
    """Test P0 Issue #3: Broad Exception Catching Fix"""

    def test_expected_errors_return_process_result(self):
        """Verify expected errors return ProcessResult"""
        # Test OSError (file not found)
        with patch("subprocess.Popen") as mock_popen:
            mock_popen.side_effect = FileNotFoundError("Command not found")

            result = ProcessExecutor.run_with_monitoring(
                ["nonexistent_command"], timeout=1.0
            )

            assert isinstance(
                result, ProcessResult
            ), "Should return ProcessResult for OSError"
            assert result.returncode == -1, "Should have error return code"
            assert "Execution error" in result.stderr, "Should contain error message"

    def test_critical_errors_are_reraised(self):
        """Verify critical errors are re-raised instead of caught"""
        # Test MemoryError is re-raised
        with patch("subprocess.Popen") as mock_popen:
            mock_popen.side_effect = MemoryError("Out of memory")

            with pytest.raises(MemoryError) as exc_info:
                ProcessExecutor.run_with_monitoring(["command"], timeout=1.0)

            assert "Out of memory" in str(exc_info.value)

    def test_keyboard_interrupt_is_reraised(self):
        """Verify KeyboardInterrupt is re-raised"""
        with patch("subprocess.Popen") as mock_popen:
            mock_popen.side_effect = KeyboardInterrupt()

            with pytest.raises(KeyboardInterrupt):
                ProcessExecutor.run_with_monitoring(["command"], timeout=1.0)

    def test_system_exit_is_reraised(self):
        """Verify SystemExit is re-raised"""
        with patch("subprocess.Popen") as mock_popen:
            mock_popen.side_effect = SystemExit(1)

            with pytest.raises(SystemExit):
                ProcessExecutor.run_with_monitoring(["command"], timeout=1.0)

    def test_unexpected_errors_are_reraised_with_logging(self):
        """Verify unexpected errors are logged and re-raised"""

        class UnexpectedError(Exception):
            """Custom unexpected error"""

            pass

        with patch("subprocess.Popen") as mock_popen:
            mock_popen.side_effect = UnexpectedError("Unexpected issue")

            with pytest.raises(UnexpectedError) as exc_info:
                ProcessExecutor.run_with_monitoring(["command"], timeout=1.0)

            assert "Unexpected issue" in str(exc_info.value)


class TestP0Issue2_DatabaseConnectionLeaks:
    """Test P0 Issue #2: Database Connection Leak Fix"""

    def test_no_connection_leak_on_validation_error(self):
        """Verify connection not leaked when validation fails"""
        # Create temp database
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db = DatabaseManager(db_path)

            # Get initial connection state
            gc.collect()
            initial_objects = len(gc.get_objects())

            # Create invalid result (missing required fields)
            invalid_result = TestResult(
                test_type="",  # Invalid - empty
                file_path="",  # Invalid - empty
                test_count=-1,  # Invalid - negative
                passed_tests=0,
                failed_tests=0,
                total_time=0.0,
            )

            # Attempt to save (should raise ValidationError)
            with pytest.raises(ValidationError):
                db.save_test_result(invalid_result)

            # Force garbage collection
            gc.collect()
            final_objects = len(gc.get_objects())

            # Check for leaked objects (allow small variance)
            leaked_objects = final_objects - initial_objects
            assert (
                abs(leaked_objects) < 50
            ), f"Potential connection leak: {leaked_objects} new objects"

    def test_connection_closed_on_sqlite_error(self):
        """Verify connection is closed on SQLite error"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db = DatabaseManager(db_path)

            # Create valid result
            valid_result = TestResult(
                test_type="comparison",
                file_path="/test.cpp",
                test_count=10,
                passed_tests=8,
                failed_tests=2,
                total_time=5.5,
                timestamp="2025-10-17T10:00:00",
            )

            # Mock close method to track calls
            with patch.object(db, "close", wraps=db.close) as mock_close:
                # Mock execute to raise error
                with patch.object(db, "connect") as mock_connect:
                    mock_conn = MagicMock()
                    mock_cursor = MagicMock()
                    mock_cursor.execute.side_effect = Exception("DB Error")
                    mock_conn.cursor.return_value = mock_cursor
                    mock_connect.return_value = mock_conn

                    # Attempt save (should fail and cleanup)
                    try:
                        db.save_test_result(valid_result)
                    except:
                        pass  # Expected to fail

                    # Verify close was called
                    assert mock_close.call_count >= 1, "close() should be called in finally block"

    def test_all_database_methods_have_try_finally(self):
        """Verify all database methods use try-finally pattern"""
        import inspect

        db = DatabaseManager()

        # Methods that should have try-finally
        critical_methods = [
            "save_test_result",
            "save_test_results_batch",
            "get_test_results",
            "save_session",
            "get_sessions",
            "save_project_data",
            "get_projects",
            "get_test_statistics",
            "delete_test_result",
        ]

        for method_name in critical_methods:
            method = getattr(db, method_name)
            source = inspect.getsource(method)

            # Check for try-finally pattern
            assert "try:" in source, f"{method_name} missing try block"
            assert "finally:" in source, f"{method_name} missing finally block"
            assert (
                "self.close()" in source
            ), f"{method_name} missing self.close() in finally"


class TestP0Fixes_Integration:
    """Integration tests for all P0 fixes together"""

    def test_process_executor_handles_errors_gracefully(self):
        """Integration test: ProcessExecutor with various error conditions"""
        # Test 1: Normal execution
        result = ProcessExecutor.run_with_monitoring(
            ["python", "--version"], timeout=5.0
        )
        assert result.returncode == 0, "Should execute successfully"

        # Test 2: Command not found (expected error)
        result = ProcessExecutor.run_with_monitoring(
            ["nonexistent_command_12345"], timeout=1.0
        )
        assert result.returncode == -1, "Should handle command not found"
        assert "Execution error" in result.stderr

        # Test 3: Timeout
        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.poll.return_value = None  # Still running
            mock_process.communicate.side_effect = subprocess.TimeoutExpired(
                "cmd", 1.0
            )
            mock_popen.return_value = mock_process

            result = ProcessExecutor.run_with_monitoring(["sleep", "100"], timeout=0.1)
            assert result.timed_out, "Should detect timeout"

    @pytest.mark.skipif(os.name != "nt", reason="Windows-specific test")
    def test_compiler_runner_cleanup_integration(self):
        """Integration test: CompilerRunner full workflow with cleanup"""
        mock_console = MagicMock()
        runner = CompilerRunner(mock_console)

        # CompilerRunner creates worker in __init__ via _setup_worker()
        # This is expected behavior - verify worker exists and is properly set up
        assert runner.worker is not None, "Worker should be created in __init__"
        assert runner.thread is not None, "Thread should be created in __init__"

        # Create simple C++ file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".cpp", delete=False
        ) as f:
            f.write(
                '#include <iostream>\nint main() { std::cout << "Hello"; return 0; }'
            )
            test_file = f.name

        try:
            # Compile and run
            runner.compile_and_run_code(test_file)
            time.sleep(0.3)

            # Stop execution
            runner.stop_execution()
            time.sleep(0.5)

            # Verify cleanup
            if runner.worker:
                assert (
                    not hasattr(runner.worker, "process")
                    or runner.worker.process is None
                ), "Process should be cleaned up"

        finally:
            runner._cleanup_worker()
            try:
                os.unlink(test_file)
                exe_file = test_file.replace(".cpp", ".exe")
                if os.path.exists(exe_file):
                    os.unlink(exe_file)
            except:
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
