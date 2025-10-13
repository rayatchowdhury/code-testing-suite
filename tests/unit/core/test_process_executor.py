"""
Unit tests for ProcessExecutor.

Tests the subprocess execution utility class that provides consistent
process execution with timeout handling, memory monitoring, temporary
file management, and pipeline support across all tools.
"""

import pytest
import os
import time
import psutil
from unittest.mock import Mock, patch, MagicMock, mock_open
from subprocess import TimeoutExpired

from src.app.core.tools.base.process_executor import ProcessExecutor, ProcessResult


class TestProcessResult:
    """Test ProcessResult dataclass."""

    def test_process_result_creation(self):
        """Should create ProcessResult with all fields."""
        result = ProcessResult(
            returncode=0,
            stdout="output",
            stderr="",
            execution_time=1.5,
            memory_used=10.5,
            timed_out=False,
            command=["python", "test.py"],
        )

        assert result.returncode == 0
        assert result.stdout == "output"
        assert result.stderr == ""
        assert result.execution_time == 1.5
        assert result.memory_used == 10.5
        assert result.timed_out is False
        assert result.command == ["python", "test.py"]

    def test_process_result_timeout_flag(self):
        """Should set timeout flag correctly."""
        result = ProcessResult(
            returncode=-1,
            stdout="",
            stderr="",
            execution_time=30.0,
            memory_used=0.0,
            timed_out=True,
            command=["sleep", "100"],
        )

        assert result.timed_out is True


class TestRunWithMonitoring:
    """Test basic process execution with monitoring."""

    @pytest.mark.skipif(os.name != "nt", reason="Windows-specific test")
    def test_run_simple_command_windows(self):
        """Should execute simple command on Windows."""
        result = ProcessExecutor.run_with_monitoring(
            command=["cmd", "/c", "echo", "Hello"]
        )

        assert result.returncode == 0
        assert "Hello" in result.stdout
        assert result.timed_out is False
        assert result.execution_time > 0

    @pytest.mark.skipif(os.name == "nt", reason="Unix-specific test")
    def test_run_simple_command_unix(self):
        """Should execute simple command on Unix."""
        result = ProcessExecutor.run_with_monitoring(command=["echo", "Hello"])

        assert result.returncode == 0
        assert "Hello" in result.stdout
        assert result.timed_out is False

    def test_run_with_input_text(self):
        """Should send input text to process stdin."""
        # Use Python to echo input back
        result = ProcessExecutor.run_with_monitoring(
            command=["python", "-c", "import sys; print(sys.stdin.read())"],
            input_text="test input",
        )

        assert result.returncode == 0
        assert "test input" in result.stdout

    def test_run_with_timeout_success(self):
        """Should complete before timeout."""
        result = ProcessExecutor.run_with_monitoring(
            command=["python", "-c", 'print("fast")'], timeout=5.0
        )

        assert result.returncode == 0
        assert result.timed_out is False
        assert result.execution_time < 5.0

    def test_run_with_timeout_exceeded(self):
        """Should timeout long-running process."""
        result = ProcessExecutor.run_with_monitoring(
            command=["python", "-c", "import time; time.sleep(10)"], timeout=0.5
        )

        assert result.timed_out is True
        assert result.execution_time >= 0.5

    def test_run_with_memory_monitoring(self):
        """Should monitor peak memory usage."""
        # Run a simple Python command
        result = ProcessExecutor.run_with_monitoring(
            command=["python", "-c", 'x = [i for i in range(1000)]; print("done")'],
            monitor_memory=True,
        )

        assert result.returncode == 0
        assert result.memory_used >= 0.0  # Should record some memory

    def test_run_with_working_directory(self, tmp_path):
        """Should execute in specified working directory."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        if os.name == "nt":
            cmd = ["cmd", "/c", "dir", "test.txt"]
        else:
            cmd = ["ls", "test.txt"]

        result = ProcessExecutor.run_with_monitoring(
            command=cmd, working_dir=str(tmp_path)
        )

        assert result.returncode == 0
        assert "test.txt" in result.stdout

    def test_run_command_with_error(self):
        """Should capture stderr output."""
        result = ProcessExecutor.run_with_monitoring(
            command=[
                "python",
                "-c",
                'import sys; sys.stderr.write("error"); sys.exit(1)',
            ]
        )

        assert result.returncode == 1
        assert "error" in result.stderr

    def test_run_nonexistent_command(self):
        """Should handle nonexistent command gracefully."""
        result = ProcessExecutor.run_with_monitoring(
            command=["nonexistent_command_xyz"]
        )

        assert result.returncode == -1
        assert "error" in result.stderr.lower()

    def test_execution_time_recorded(self):
        """Should record accurate execution time."""
        result = ProcessExecutor.run_with_monitoring(
            command=["python", "-c", "import time; time.sleep(0.1)"]
        )

        assert result.execution_time >= 0.1
        assert result.execution_time < 1.0  # Should not take too long


class TestRunWithTempFiles:
    """Test process execution with temporary file handling."""

    def test_run_with_input_file(self):
        """Should create temporary input file."""
        result, input_file, output_file = ProcessExecutor.run_with_temp_files(
            command=[
                "python",
                "-c",
                "import sys; print(open(sys.argv[1]).read())",
                "{input_file}",
            ],
            input_text="test content",
            cleanup=False,
        )

        assert result.returncode == 0
        assert "test content" in result.stdout
        assert input_file is not None
        assert os.path.exists(input_file)

        # Cleanup
        if input_file and os.path.exists(input_file):
            os.unlink(input_file)

    def test_run_with_output_file(self):
        """Should create temporary output file."""
        result, input_file, output_file = ProcessExecutor.run_with_temp_files(
            command=[
                "python",
                "-c",
                'import sys; open(sys.argv[2], "w").write("output")',
                "{input_file}",
                "{output_file}",
            ],
            input_text="input",
            output_file_needed=True,
            cleanup=False,
        )

        assert result.returncode == 0
        assert output_file is not None
        assert os.path.exists(output_file)

        with open(output_file, "r") as f:
            assert f.read() == "output"

        # Cleanup
        for temp_file in [input_file, output_file]:
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_temp_file_cleanup(self):
        """Should cleanup temporary files when requested."""
        result, input_file, output_file = ProcessExecutor.run_with_temp_files(
            command=["python", "-c", 'print("test")'],
            input_text="content",
            cleanup=True,
        )

        assert result.returncode == 0
        # Files should be cleaned up
        if input_file:
            assert not os.path.exists(input_file)

    def test_temp_file_no_cleanup(self):
        """Should preserve temporary files when cleanup=False."""
        result, input_file, output_file = ProcessExecutor.run_with_temp_files(
            command=["python", "-c", 'print("test")'],
            input_text="content",
            cleanup=False,
        )

        assert result.returncode == 0
        assert input_file is not None
        assert os.path.exists(input_file)

        # Manual cleanup
        if input_file and os.path.exists(input_file):
            os.unlink(input_file)

    def test_temp_file_with_timeout(self):
        """Should respect timeout with temporary files."""
        result, input_file, output_file = ProcessExecutor.run_with_temp_files(
            command=["python", "-c", "import time; time.sleep(10)"],
            input_text="test",
            timeout=0.5,
            cleanup=True,
        )

        assert result.timed_out is True


class TestRunPipeline:
    """Test multi-stage pipeline execution."""

    def test_single_stage_pipeline(self):
        """Should execute single-stage pipeline."""
        stages = [{"command": ["python", "-c", 'print("stage1")'], "input": ""}]

        results = ProcessExecutor.run_pipeline(stages)

        assert len(results) == 1
        assert results[0].returncode == 0
        assert "stage1" in results[0].stdout

    def test_two_stage_pipeline(self):
        """Should pass output between pipeline stages."""
        stages = [
            {"command": ["python", "-c", 'print("hello")'], "input": ""},
            {
                "command": [
                    "python",
                    "-c",
                    "import sys; print(sys.stdin.read().upper())",
                ],
            },
        ]

        results = ProcessExecutor.run_pipeline(stages)

        assert len(results) == 2
        assert results[0].returncode == 0
        assert results[1].returncode == 0
        assert "HELLO" in results[1].stdout

    def test_three_stage_pipeline(self):
        """Should chain multiple pipeline stages."""
        stages = [
            {"command": ["python", "-c", 'print("1")'], "input": ""},
            {
                "command": [
                    "python",
                    "-c",
                    "import sys; print(int(sys.stdin.read()) * 2)",
                ],
            },
            {
                "command": [
                    "python",
                    "-c",
                    "import sys; print(int(sys.stdin.read()) + 10)",
                ],
            },
        ]

        results = ProcessExecutor.run_pipeline(stages)

        assert len(results) == 3
        assert all(r.returncode == 0 for r in results)
        assert "12" in results[2].stdout  # 1 * 2 + 10 = 12

    def test_pipeline_stop_on_failure(self):
        """Should stop pipeline on first failure."""
        stages = [
            {"command": ["python", "-c", 'print("stage1")'], "input": ""},
            {
                "command": ["python", "-c", "import sys; sys.exit(1)"],  # Fails
            },
            {
                "command": ["python", "-c", 'print("stage3")'],  # Should not execute
            },
        ]

        results = ProcessExecutor.run_pipeline(stages, stop_on_failure=True)

        assert len(results) == 2  # Only first two stages
        assert results[0].returncode == 0
        assert results[1].returncode == 1

    def test_pipeline_continue_on_failure(self):
        """Should continue pipeline despite failures."""
        stages = [
            {"command": ["python", "-c", 'print("stage1")'], "input": ""},
            {
                "command": ["python", "-c", "import sys; sys.exit(1)"],  # Fails
            },
            {
                "command": ["python", "-c", 'print("stage3")'],  # Should execute
            },
        ]

        results = ProcessExecutor.run_pipeline(stages, stop_on_failure=False)

        assert len(results) == 3
        assert results[0].returncode == 0
        assert results[1].returncode == 1
        assert results[2].returncode == 0

    def test_pipeline_with_memory_monitoring(self):
        """Should monitor memory in pipeline stages."""
        stages = [
            {
                "command": [
                    "python",
                    "-c",
                    'x = [i for i in range(100)]; print("done")',
                ],
                "input": "",
                "monitor_memory": True,
            }
        ]

        results = ProcessExecutor.run_pipeline(stages)

        assert len(results) == 1
        assert results[0].memory_used >= 0.0

    def test_pipeline_timeout_per_stage(self):
        """Should timeout individual pipeline stages."""
        stages = [
            {"command": ["python", "-c", 'print("fast")'], "input": ""},
            {
                "command": ["python", "-c", "import time; time.sleep(10)"],  # Too slow
            },
        ]

        results = ProcessExecutor.run_pipeline(stages, timeout_per_stage=0.5)

        assert len(results) == 2
        assert results[0].returncode == 0
        assert results[1].timed_out is True

    def test_empty_pipeline(self):
        """Should handle empty pipeline."""
        results = ProcessExecutor.run_pipeline([])

        assert results == []


class TestGetMemoryInfo:
    """Test memory information retrieval."""

    def test_get_memory_info_current_process(self):
        """Should get memory info for current process."""
        pid = os.getpid()
        mem_info = ProcessExecutor.get_memory_info(pid)

        assert "rss" in mem_info
        assert "vms" in mem_info
        assert "percent" in mem_info
        assert mem_info["rss"] > 0
        assert mem_info["vms"] > 0

    def test_get_memory_info_child_process(self):
        """Should get memory info for child process."""
        import subprocess

        # Start a simple Python process
        proc = subprocess.Popen(
            ["python", "-c", "import time; time.sleep(1)"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            time.sleep(0.1)  # Give process time to start
            mem_info = ProcessExecutor.get_memory_info(proc.pid)

            assert mem_info["rss"] > 0
            assert mem_info["vms"] > 0
        finally:
            proc.kill()
            proc.wait()

    def test_get_memory_info_invalid_pid(self):
        """Should handle invalid process ID."""
        mem_info = ProcessExecutor.get_memory_info(999999)

        assert mem_info["rss"] == 0.0
        assert mem_info["vms"] == 0.0
        assert mem_info["percent"] == 0.0


class TestFormatExecutionSummary:
    """Test execution summary formatting."""

    def test_format_success_summary(self):
        """Should format successful execution summary."""
        result = ProcessResult(
            returncode=0,
            stdout="output data",
            stderr="",
            execution_time=1.234,
            memory_used=15.5,
            timed_out=False,
            command=["python", "test.py"],
        )

        summary = ProcessExecutor.format_execution_summary(result)

        assert "SUCCESS" in summary
        assert "exit code: 0" in summary
        assert "1.234s" in summary
        assert "15.50 MB" in summary
        assert "python test.py" in summary

    def test_format_failure_summary(self):
        """Should format failed execution summary."""
        result = ProcessResult(
            returncode=1,
            stdout="",
            stderr="error message",
            execution_time=0.5,
            memory_used=0.0,
            timed_out=False,
            command=["python", "test.py"],
        )

        summary = ProcessExecutor.format_execution_summary(result)

        assert "FAILED" in summary
        assert "exit code: 1" in summary
        assert "0.500s" in summary
        assert "error message" in summary

    def test_format_timeout_summary(self):
        """Should format timeout summary."""
        result = ProcessResult(
            returncode=-1,
            stdout="",
            stderr="",
            execution_time=30.0,
            memory_used=5.0,
            timed_out=True,
            command=["python", "-c", "import time; time.sleep(100)"],
        )

        summary = ProcessExecutor.format_execution_summary(result)

        assert "TIMEOUT" in summary
        assert "30.000s" in summary

    def test_format_summary_with_output(self):
        """Should include output length in summary."""
        result = ProcessResult(
            returncode=0,
            stdout="x" * 1000,
            stderr="",
            execution_time=1.0,
            memory_used=0.0,
            timed_out=False,
            command=["echo", "test"],
        )

        summary = ProcessExecutor.format_execution_summary(result)

        assert "1000 characters" in summary

    def test_format_summary_no_memory(self):
        """Should handle zero memory usage."""
        result = ProcessResult(
            returncode=0,
            stdout="output",
            stderr="",
            execution_time=1.0,
            memory_used=0.0,
            timed_out=False,
            command=["echo", "test"],
        )

        summary = ProcessExecutor.format_execution_summary(result)

        assert "Peak memory" not in summary


class TestProcessExecutorIntegration:
    """Integration tests for ProcessExecutor."""

    def test_real_python_execution(self):
        """Should execute real Python code."""
        result = ProcessExecutor.run_with_monitoring(
            command=["python", "-c", "for i in range(5): print(i)"]
        )

        assert result.returncode == 0
        assert "0" in result.stdout
        assert "4" in result.stdout

    def test_real_compilation_simulation(self, tmp_path):
        """Should simulate compilation-like workflow."""
        # Create a simple Python file
        source_file = tmp_path / "test.py"
        source_file.write_text('print("Hello, World!")')

        # "Compile" (validate syntax)
        compile_result = ProcessExecutor.run_with_monitoring(
            command=["python", "-m", "py_compile", str(source_file)]
        )

        assert compile_result.returncode == 0

        # Execute
        run_result = ProcessExecutor.run_with_monitoring(
            command=["python", str(source_file)]
        )

        assert run_result.returncode == 0
        assert "Hello, World!" in run_result.stdout

    def test_stress_test_multiple_executions(self):
        """Should handle multiple sequential executions."""
        results = []

        for i in range(10):
            result = ProcessExecutor.run_with_monitoring(
                command=["python", "-c", f"print({i})"]
            )
            results.append(result)

        assert len(results) == 10
        assert all(r.returncode == 0 for r in results)

    def test_error_recovery(self):
        """Should recover from failed executions."""
        # First execution fails
        fail_result = ProcessExecutor.run_with_monitoring(
            command=["python", "-c", "import sys; sys.exit(1)"]
        )

        assert fail_result.returncode == 1

        # Second execution succeeds
        success_result = ProcessExecutor.run_with_monitoring(
            command=["python", "-c", 'print("recovered")']
        )

        assert success_result.returncode == 0
        assert "recovered" in success_result.stdout
