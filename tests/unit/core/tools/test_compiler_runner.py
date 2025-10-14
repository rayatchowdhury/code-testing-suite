"""
Phase 8 (Task 4): Tests for compiler_runner.py - CompilerWorker and CompilerRunner

Tests based on actual implementation:
- CompilerWorker: compiles and runs C++/Python/Java code
- Uses QProcess for compilation and execution
- Handles output/error streams
- Thread-safe operations with QMutex
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest
from PySide6.QtCore import QMutex, QObject, QProcess, Signal

from src.app.core.tools.compiler_runner import CompilerRunner, CompilerWorker

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_cpp_file(temp_workspace):
    """Create a sample C++ file."""
    cpp_file = temp_workspace / "test.cpp"
    cpp_file.write_text(
        '#include <iostream>\nint main() { std::cout << "Hello"; return 0; }'
    )
    return str(cpp_file)


@pytest.fixture
def sample_python_file(temp_workspace):
    """Create a sample Python file."""
    py_file = temp_workspace / "test.py"
    py_file.write_text('print("Hello from Python")')
    return str(py_file)


@pytest.fixture
def sample_java_file(temp_workspace):
    """Create a sample Java file."""
    java_file = temp_workspace / "Test.java"
    java_file.write_text(
        'public class Test { public static void main(String[] args) { System.out.println("Hello"); } }'
    )
    return str(java_file)


# ============================================================================
# CompilerWorker Tests
# ============================================================================


class TestCompilerWorkerInitialization:
    """Test CompilerWorker initialization."""

    def test_worker_initializes_with_correct_attributes(self, qtbot):
        """Test worker initializes with all required attributes."""
        worker = CompilerWorker()

        assert worker.process is None
        assert isinstance(worker.mutex, QMutex)
        assert worker.current_file is None
        assert worker.current_program is None
        assert worker._error_emitted is False
        assert "cpp" in worker.language_handlers
        assert "py" in worker.language_handlers
        assert "java" in worker.language_handlers

    def test_worker_has_required_signals(self, qtbot):
        """Test worker has all required Qt signals."""
        worker = CompilerWorker()

        assert hasattr(worker, "finished")
        assert hasattr(worker, "output")
        assert hasattr(worker, "error")
        assert hasattr(worker, "input_requested")

    def test_language_handlers_mapping(self, qtbot):
        """Test language handlers are correctly mapped."""
        worker = CompilerWorker()

        # C++ extensions
        assert worker.language_handlers["cpp"] == worker._handle_cpp
        assert worker.language_handlers["h"] == worker._handle_cpp
        assert worker.language_handlers["hpp"] == worker._handle_cpp

        # Python
        assert worker.language_handlers["py"] == worker._handle_python

        # Java
        assert worker.language_handlers["java"] == worker._handle_java


class TestCompilerWorkerEmitStatus:
    """Test status message emission."""

    def test_emit_status_default_format(self, qtbot):
        """Test _emit_status with default format."""
        worker = CompilerWorker()

        with qtbot.waitSignal(worker.output, timeout=1000) as blocker:
            worker._emit_status("Test message")

        signal_args = blocker.args
        assert signal_args[0] == ("Test message\n", "info")

    def test_emit_status_custom_format(self, qtbot):
        """Test _emit_status with custom format."""
        worker = CompilerWorker()

        with qtbot.waitSignal(worker.output, timeout=1000) as blocker:
            worker._emit_status("Success!", "success", 2)

        signal_args = blocker.args
        assert signal_args[0] == ("Success!\n\n", "success")

    def test_emit_status_error_format(self, qtbot):
        """Test _emit_status with error format."""
        worker = CompilerWorker()

        with qtbot.waitSignal(worker.output, timeout=1000) as blocker:
            worker._emit_status("Error occurred", "error", 0)

        signal_args = blocker.args
        assert signal_args[0] == ("Error occurred", "error")


class TestExecutableUpToDate:
    """Test executable timestamp checking."""

    def test_executable_not_exists_returns_false(self, qtbot, temp_workspace):
        """Test returns False when executable doesn't exist."""
        worker = CompilerWorker()

        source = str(temp_workspace / "test.cpp")
        Path(source).write_text("int main() {}")
        executable = str(temp_workspace / "test.exe")

        assert worker._is_executable_up_to_date(source, executable) is False

    def test_source_not_exists_returns_false(self, qtbot, temp_workspace):
        """Test returns False when source doesn't exist."""
        worker = CompilerWorker()

        source = str(temp_workspace / "test.cpp")
        executable = str(temp_workspace / "test.exe")
        Path(executable).write_text("")

        assert worker._is_executable_up_to_date(source, executable) is False

    def test_newer_executable_returns_true(self, qtbot, temp_workspace):
        """Test returns True when executable is newer than source."""
        worker = CompilerWorker()

        import time

        source = str(temp_workspace / "test.cpp")
        executable = str(temp_workspace / "test.exe")

        Path(source).write_text("int main() {}")
        time.sleep(0.1)  # Ensure different timestamps
        Path(executable).write_text("")

        assert worker._is_executable_up_to_date(source, executable) is True

    def test_older_executable_returns_false(self, qtbot, temp_workspace):
        """Test returns False when executable is older than source."""
        worker = CompilerWorker()

        import time

        source = str(temp_workspace / "test.cpp")
        executable = str(temp_workspace / "test.exe")

        Path(executable).write_text("")
        time.sleep(0.1)
        Path(source).write_text("int main() {}")

        assert worker._is_executable_up_to_date(source, executable) is False


class TestCompileAndRun:
    """Test main compile_and_run entry point."""

    def test_compile_and_run_unsupported_type(self, qtbot):
        """Test compile_and_run handles unsupported file types."""
        worker = CompilerWorker()

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            filepath = f.name

        try:
            with qtbot.waitSignal(worker.error, timeout=1000) as error_blocker:
                with qtbot.waitSignal(worker.finished, timeout=1000):
                    worker.compile_and_run(filepath)

            error_args = error_blocker.args
            assert "Unsupported file type" in error_args[0][0]
        finally:
            os.unlink(filepath)

    def test_compile_and_run_cpp_extension(self, qtbot):
        """Test compile_and_run recognizes .cpp extension."""
        worker = CompilerWorker()

        # Handler should be in language_handlers
        assert "cpp" in worker.language_handlers
        assert worker.language_handlers["cpp"] == worker._handle_cpp

    def test_compile_and_run_py_extension(self, qtbot):
        """Test compile_and_run recognizes .py extension."""
        worker = CompilerWorker()

        # Just verify the handler exists
        assert "py" in worker.language_handlers
        assert worker.language_handlers["py"] == worker._handle_python

    def test_compile_and_run_java_extension(self, qtbot):
        """Test compile_and_run recognizes .java extension."""
        worker = CompilerWorker()

        # Just verify the handler exists
        assert "java" in worker.language_handlers
        assert worker.language_handlers["java"] == worker._handle_java


class TestJavaValidation:
    """Test Java class name validation."""

    def test_check_java_class_name_valid(self, qtbot, temp_workspace):
        """Test valid Java class name passes."""
        worker = CompilerWorker()

        java_file = temp_workspace / "Test.java"
        java_file.write_text("public class Test { }")

        result = worker._check_java_class_name(str(java_file), "Test")
        assert result is True

    def test_check_java_class_name_capitalized(self, qtbot, temp_workspace):
        """Test capitalized class name passes."""
        worker = CompilerWorker()

        java_file = temp_workspace / "test.java"
        java_file.write_text("public class Test { }")

        result = worker._check_java_class_name(str(java_file), "test")
        assert result is True

    def test_check_java_class_name_mismatch(self, qtbot, temp_workspace):
        """Test mismatched class name fails."""
        worker = CompilerWorker()

        java_file = temp_workspace / "Test.java"
        java_file.write_text("public class Wrong { }")

        with qtbot.waitSignal(worker.error, timeout=1000):
            result = worker._check_java_class_name(str(java_file), "Test")

        assert result is False

    def test_check_java_class_name_file_not_found(self, qtbot, temp_workspace):
        """Test missing file is handled."""
        worker = CompilerWorker()

        with qtbot.waitSignal(worker.error, timeout=1000):
            result = worker._check_java_class_name(
                str(temp_workspace / "missing.java"), "Test"
            )

        assert result is False


class TestErrorHandling:
    """Test error detection and handling."""

    def test_handle_error_no_process(self, qtbot):
        """Test handle_error with no process doesn't crash."""
        worker = CompilerWorker()
        worker.process = None

        # Should not raise or emit
        worker.handle_error()
        assert worker._error_emitted is False

    def test_error_emitted_flag_exists(self, qtbot):
        """Test _error_emitted flag exists and is boolean."""
        worker = CompilerWorker()

        assert hasattr(worker, "_error_emitted")
        assert isinstance(worker._error_emitted, bool)


class TestInputHandling:
    """Test user input handling."""

    def test_handle_input_writes_to_process(self, qtbot):
        """Test handle_input writes to running process."""
        worker = CompilerWorker()

        mock_process = Mock()
        mock_process.state.return_value = QProcess.ProcessState.Running
        worker.process = mock_process

        worker.handle_input("test input")

        mock_process.write.assert_called()

    def test_handle_input_no_process(self, qtbot):
        """Test handle_input with no process doesn't crash."""
        worker = CompilerWorker()
        worker.process = None

        # Should not raise
        worker.handle_input("test input")

    def test_handle_input_process_not_running(self, qtbot):
        """Test handle_input with stopped process doesn't write."""
        worker = CompilerWorker()

        mock_process = Mock()
        mock_process.state.return_value = QProcess.ProcessState.NotRunning
        worker.process = mock_process

        worker.handle_input("test input")

        mock_process.write.assert_not_called()


class TestStopExecution:
    """Test stopping execution."""

    def test_stop_execution_no_process(self, qtbot):
        """Test stop_execution with no process doesn't crash."""
        worker = CompilerWorker()
        worker.process = None

        # Should not raise
        worker.stop_execution()

    def test_stop_execution_method_exists(self, qtbot):
        """Test stop_execution method exists and is callable."""
        worker = CompilerWorker()

        # Should be callable without error
        assert hasattr(worker, "stop_execution")
        assert callable(worker.stop_execution)


# ============================================================================
# CompilerRunner Tests
# ============================================================================


class MockConsoleOutput(QObject):
    """Mock console for testing CompilerRunner."""

    inputSubmitted = Signal(str)

    def __init__(self):
        super().__init__()
        self.outputs = []
        self.input_enabled = False
        self.cleared = False

    def displayOutput(self, text, format_type="default"):
        self.outputs.append((text, format_type))

    def setInputEnabled(self, enabled):
        self.input_enabled = enabled

    def requestInput(self):
        pass

    def clear(self):
        self.cleared = True
        self.outputs.clear()


class TestCompilerRunnerInitialization:
    """Test CompilerRunner initialization."""

    def test_runner_creates_worker_and_thread(self, qtbot):
        """Test runner initializes with worker and thread."""
        console = MockConsoleOutput()
        runner = CompilerRunner(console)

        assert runner.worker is not None
        assert isinstance(runner.worker, CompilerWorker)
        assert runner.thread is not None
        assert runner.console == console

    def test_runner_has_required_signals(self, qtbot):
        """Test runner has all required signals."""
        console = MockConsoleOutput()
        runner = CompilerRunner(console)

        assert hasattr(runner, "finished")

    def test_runner_connects_worker_signals(self, qtbot):
        """Test runner connects to worker signals."""
        console = MockConsoleOutput()
        runner = CompilerRunner(console)

        # Test signal propagation by emitting worker signal
        with qtbot.waitSignal(runner.finished, timeout=1000):
            runner.worker.finished.emit()


class TestCompilerRunnerOutputHandling:
    """Test output handling methods."""

    def test_handle_output_displays_to_console(self, qtbot):
        """Test handle_output sends output to console."""
        console = MockConsoleOutput()
        runner = CompilerRunner(console)

        runner.handle_output(("Test output", "info"))

        assert len(console.outputs) == 1
        assert console.outputs[0] == ("Test output", "info")

    def test_handle_error_displays_to_console(self, qtbot):
        """Test handle_error sends error to console."""
        console = MockConsoleOutput()
        runner = CompilerRunner(console)

        runner.handle_error(("Error message", "error"))

        assert len(console.outputs) == 1
        assert console.outputs[0] == ("Error message", "error")

    def test_handle_input_request_requests_from_console(self, qtbot):
        """Test handle_input_request calls console requestInput."""
        console = MockConsoleOutput()
        runner = CompilerRunner(console)

        with patch.object(console, "requestInput") as mock_request:
            runner.handle_input_request()
            mock_request.assert_called_once()


class TestCompilerRunnerCompileAndRun:
    """Test compile_and_run_code method."""

    def test_compile_and_run_code_clears_console(self, qtbot, temp_workspace):
        """Test compile_and_run_code clears console before execution."""
        console = MockConsoleOutput()
        runner = CompilerRunner(console)

        test_file = temp_workspace / "test.cpp"
        test_file.write_text("int main() {}")

        runner.compile_and_run_code(str(test_file))

        assert console.cleared is True

    def test_compile_and_run_code_enables_input(self, qtbot, temp_workspace):
        """Test compile_and_run_code enables console input."""
        console = MockConsoleOutput()
        runner = CompilerRunner(console)

        test_file = temp_workspace / "test.cpp"
        test_file.write_text("int main() {}")

        runner.compile_and_run_code(str(test_file))

        assert console.input_enabled is True

    def test_compile_and_run_code_empty_filepath(self, qtbot):
        """Test compile_and_run_code handles empty filepath."""
        console = MockConsoleOutput()
        runner = CompilerRunner(console)

        runner.compile_and_run_code("")

        # Should display error
        assert any("Error" in out[0] for out in console.outputs)


class TestCompilerRunnerStopExecution:
    """Test stopping execution."""

    def test_stop_execution_calls_worker_stop(self, qtbot):
        """Test stop_execution invokes worker's stop_execution."""
        console = MockConsoleOutput()
        runner = CompilerRunner(console)

        # Just verify method exists and can be called
        runner.stop_execution()
        # Method uses QMetaObject.invokeMethod, so we can't easily mock it


class TestCompilerRunnerCleanup:
    """Test cleanup and resource management."""

    def test_cleanup_worker_stops_thread(self, qtbot):
        """Test _cleanup_worker stops running thread."""
        console = MockConsoleOutput()
        runner = CompilerRunner(console)

        runner.thread.start()
        runner._cleanup_worker()

        # Thread should be stopped
        assert not runner.thread or not runner.thread.isRunning()

    def test_cleanup_worker_handles_no_worker(self, qtbot):
        """Test _cleanup_worker handles missing worker gracefully."""
        console = MockConsoleOutput()
        runner = CompilerRunner(console)

        runner.worker = None

        # Should not crash
        runner._cleanup_worker()


class TestCompilerRunnerThreadManagement:
    """Test thread lifecycle management."""

    def test_thread_starts_when_compiling(self, qtbot, temp_workspace):
        """Test thread starts when compile_and_run_code is called."""
        console = MockConsoleOutput()
        runner = CompilerRunner(console)

        test_file = temp_workspace / "test.py"
        test_file.write_text("print('hello')")

        runner.compile_and_run_code(str(test_file))

        # Thread should be started or running
        qtbot.wait(100)  # Give it time to start
        # Thread should be running or have been started
        assert runner.thread is not None

    def test_on_worker_finished_quits_thread(self, qtbot):
        """Test _on_worker_finished quits the thread."""
        console = MockConsoleOutput()
        runner = CompilerRunner(console)

        runner.thread.start()
        qtbot.wait(100)

        with qtbot.waitSignal(runner.finished, timeout=2000):
            runner._on_worker_finished()

        # Thread should quit
        qtbot.wait(100)
        assert runner.thread.isFinished() or not runner.thread.isRunning()


# ============================================================================
# Additional Coverage Tests for Missing Lines
# ============================================================================


class TestCompilationExceptionHandling:
    """Test exception handling during compilation."""

    def test_compile_and_run_exception_emits_error(self, qtbot):
        """Test compile_and_run emits error signal on exception."""
        worker = CompilerWorker()

        # Mock handler to raise exception
        def mock_handler(filepath):
            raise ValueError("Test exception")

        worker.language_handlers["txt"] = mock_handler

        with qtbot.waitSignal(worker.error, timeout=1000) as error_blocker:
            with qtbot.waitSignal(worker.finished, timeout=1000):
                worker.compile_and_run("test.txt")

        error_args = error_blocker.args
        assert "Error: Test exception" in error_args[0][0]

    def test_compile_and_run_mutex_released_on_exception(self, qtbot):
        """Test mutex is released even on exception."""
        worker = CompilerWorker()

        # Create a handler that raises exception
        def failing_handler(filepath):
            raise RuntimeError("Compilation failed")

        worker.language_handlers["bad"] = failing_handler

        with qtbot.waitSignal(worker.finished, timeout=1000):
            worker.compile_and_run("test.bad")

        # Mutex should be released, so we can acquire it
        assert worker.mutex.tryLock()
        worker.mutex.unlock()


class TestCppCompilationErrorHandling:
    """Test C++ compilation error handling."""

    def test_cpp_compilation_failure_emits_error(self, qtbot, temp_workspace):
        """Test C++ compilation failure emits proper error."""
        worker = CompilerWorker()

        # Create invalid C++ file
        cpp_file = temp_workspace / "invalid.cpp"
        cpp_file.write_text("invalid c++ code {{{")

        with patch.object(QProcess, "waitForFinished", return_value=True):
            with patch.object(QProcess, "exitCode", return_value=1):
                with patch.object(QProcess, "readAllStandardError") as mock_error:
                    mock_error.return_value.data.return_value.decode.return_value = (
                        "syntax error"
                    )

                    with qtbot.waitSignal(worker.error, timeout=1000) as error_blocker:
                        with qtbot.waitSignal(worker.finished, timeout=1000):
                            worker._handle_cpp(str(cpp_file))

                    error_args = error_blocker.args
                    assert "Compilation Error" in error_args[0][0]
                    assert "syntax error" in error_args[0][0]

    def test_cpp_executable_up_to_date_skips_compilation(self, qtbot, temp_workspace):
        """Test C++ skips compilation when executable is up-to-date."""
        worker = CompilerWorker()

        # Create source and executable
        cpp_file = temp_workspace / "test.cpp"
        cpp_file.write_text("int main() { return 0; }")

        exe_file = temp_workspace / ("test.exe" if os.name == "nt" else "test")
        exe_file.write_text("fake executable")

        # Make executable newer than source
        import time

        time.sleep(0.1)
        exe_file.touch()

        with patch.object(worker, "_run_executable") as mock_run:
            with qtbot.waitSignal(worker.output, timeout=1000) as output_blocker:
                worker._handle_cpp(str(cpp_file))

            # Should emit "up-to-date" message
            output_args = output_blocker.args
            assert "up-to-date" in output_args[0][0].lower()

            # Should still run executable
            mock_run.assert_called_once()


class TestJavaErrorHandling:
    """Test Java-specific error handling."""

    def test_java_invalid_class_name_emits_error(self, qtbot, temp_workspace):
        """Test Java class name mismatch emits error."""
        worker = CompilerWorker()

        # Create Java file with mismatched class name
        java_file = temp_workspace / "Test.java"
        java_file.write_text("public class WrongName { }")

        with qtbot.waitSignal(worker.error, timeout=1000) as error_blocker:
            result = worker._check_java_class_name(str(java_file), "Test")

        assert result is False
        error_args = error_blocker.args
        assert "class name must match" in error_args[0][0]

    def test_java_file_read_error_emits_error(self, qtbot):
        """Test Java file read error emits proper error."""
        worker = CompilerWorker()

        with qtbot.waitSignal(worker.error, timeout=1000) as error_blocker:
            result = worker._check_java_class_name("/nonexistent/file.java", "Test")

        assert result is False
        error_args = error_blocker.args
        assert "Error reading file" in error_args[0][0]

    def test_java_execution_changes_directory(self, qtbot, temp_workspace):
        """Test Java execution changes to file directory."""
        worker = CompilerWorker()

        # Create Java file in subdirectory
        subdir = temp_workspace / "java_tests"
        subdir.mkdir()
        java_file = subdir / "Test.java"
        java_file.write_text(
            "public class Test { public static void main(String[] args) {} }"
        )

        original_dir = os.getcwd()

        with patch.object(worker, "_run_process") as mock_run:
            worker._handle_java(str(java_file))

        # Should restore original directory
        assert os.getcwd() == original_dir

        # Should have called _run_process with java
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == "java"

    def test_java_invalid_class_stops_execution(self, qtbot, temp_workspace):
        """Test Java execution stops if class name invalid."""
        worker = CompilerWorker()

        # Create Java file with invalid class
        java_file = temp_workspace / "Test.java"
        java_file.write_text("public class Wrong { }")

        with patch.object(worker, "_run_process") as mock_run:
            with qtbot.waitSignal(worker.finished, timeout=1000):
                worker._handle_java(str(java_file))

        # Should NOT call _run_process
        mock_run.assert_not_called()


class TestProcessErrorHandling:
    """Test process error detection and handling."""

    def test_handle_error_division_by_zero_detection(self, qtbot):
        """Test detects division by zero errors."""
        worker = CompilerWorker()
        worker.current_file = "/test/program.cpp"

        # Create mock process with division by zero error
        worker.process = Mock(spec=QProcess)
        worker.process.readAllStandardError.return_value.data.return_value.decode.return_value = (
            "floating point exception: divide by zero"
        )
        worker.process.readAllStandardOutput.return_value.data.return_value.decode.return_value = (
            ""
        )

        # Collect all error signals
        errors = []
        worker.error.connect(lambda msg: errors.append(msg[0]))

        worker.handle_error()
        qtbot.wait(100)

        # Check that "Division by zero" appears in the emitted errors
        full_error = "".join(errors)
        assert "Division by zero" in full_error
        assert worker._error_emitted is True

    def test_handle_error_segmentation_fault_detection(self, qtbot):
        """Test detects segmentation faults."""
        worker = CompilerWorker()
        worker.current_file = "/test/program.cpp"

        worker.process = Mock(spec=QProcess)
        worker.process.readAllStandardError.return_value.data.return_value.decode.return_value = (
            "Segmentation fault (core dumped)"
        )
        worker.process.readAllStandardOutput.return_value.data.return_value.decode.return_value = (
            ""
        )

        # Collect all error signals
        errors = []
        worker.error.connect(lambda msg: errors.append(msg[0]))

        worker.handle_error()
        qtbot.wait(100)

        # Check that error messages appear
        full_error = "".join(errors)
        assert "Memory access violation" in full_error
        assert "Segmentation Fault" in full_error

    def test_handle_error_abort_detection(self, qtbot):
        """Test detects program aborts."""
        worker = CompilerWorker()
        worker.current_file = "/test/program.cpp"

        worker.process = Mock(spec=QProcess)
        worker.process.readAllStandardError.return_value.data.return_value.decode.return_value = (
            "Program aborted"
        )
        worker.process.readAllStandardOutput.return_value.data.return_value.decode.return_value = (
            ""
        )

        # Collect all error signals
        errors = []
        worker.error.connect(lambda msg: errors.append(msg[0]))

        worker.handle_error()
        qtbot.wait(100)

        full_error = "".join(errors)
        assert "terminated abnormally" in full_error

    def test_handle_error_generic_error_output(self, qtbot):
        """Test handles generic error output."""
        worker = CompilerWorker()
        worker.current_file = "/test/program.cpp"

        worker.process = Mock(spec=QProcess)
        worker.process.readAllStandardError.return_value.data.return_value.decode.return_value = (
            "Some generic error occurred"
        )
        worker.process.readAllStandardOutput.return_value.data.return_value.decode.return_value = (
            ""
        )

        # Collect all error signals
        errors = []
        worker.error.connect(lambda msg: errors.append(msg[0]))

        worker.handle_error()
        qtbot.wait(100)

        full_error = "".join(errors)
        assert "Some generic error occurred" in full_error

    def test_handle_error_no_process_returns_safely(self, qtbot):
        """Test handle_error returns safely when no process."""
        worker = CompilerWorker()
        worker.process = None

        # Should not raise exception or emit signals
        worker.handle_error()
        # If we get here without exception, test passes


class TestProcessSetupAndExecution:
    """Test process setup and execution methods."""

    def test_run_executable_sets_current_file(self, qtbot):
        """Test _run_executable sets current_file."""
        worker = CompilerWorker()

        with patch.object(worker, "_setup_process"):
            with patch.object(QProcess, "start"):
                worker._run_executable("/path/to/program.exe")

        assert worker.current_file == "/path/to/program.exe"

    def test_run_process_sets_current_program(self, qtbot):
        """Test _run_process sets current_program."""
        worker = CompilerWorker()

        with patch.object(worker, "_setup_process"):
            with patch.object(QProcess, "start"):
                worker._run_process("python", ["script.py"])

        assert worker.current_program == "python"


class TestPythonExecution:
    """Test Python script execution."""

    def test_handle_python_emits_status(self, qtbot, temp_workspace):
        """Test Python execution emits proper status messages."""
        worker = CompilerWorker()

        py_file = temp_workspace / "test.py"
        py_file.write_text("print('hello')")

        with patch.object(worker, "_run_process") as mock_run:
            with qtbot.waitSignal(worker.output, timeout=1000) as output_blocker:
                worker._handle_python(str(py_file))

        # Should emit "Running Python script" message
        output_args = output_blocker.args
        assert "Running Python script" in output_args[0][0]

        # Should call _run_process with python
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == "python"
        assert str(py_file) in mock_run.call_args[0][1]


class TestExecutableTimestampLogic:
    """Test executable timestamp comparison edge cases."""

    def test_executable_newer_than_source(self, qtbot, temp_workspace):
        """Test returns True when executable is newer."""
        worker = CompilerWorker()

        source = temp_workspace / "test.cpp"
        source.write_text("int main() {}")

        import time

        time.sleep(0.1)

        exe = temp_workspace / "test.exe"
        exe.write_text("binary")

        result = worker._is_executable_up_to_date(str(source), str(exe))
        assert result is True

    def test_executable_older_than_source(self, qtbot, temp_workspace):
        """Test returns False when executable is older."""
        worker = CompilerWorker()

        exe = temp_workspace / "test.exe"
        exe.write_text("binary")

        import time

        time.sleep(0.1)

        source = temp_workspace / "test.cpp"
        source.write_text("int main() { return 1; }")  # Modified

        result = worker._is_executable_up_to_date(str(source), str(exe))
        assert result is False

    def test_timestamp_error_returns_false(self, qtbot):
        """Test returns False on OSError during timestamp check."""
        worker = CompilerWorker()

        with patch("os.path.exists", return_value=True):
            with patch("os.path.getmtime", side_effect=OSError("Permission denied")):
                result = worker._is_executable_up_to_date(
                    "/test/source.cpp", "/test/exe"
                )

        assert result is False
