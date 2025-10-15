"""
ProcessExecutor - Common subprocess execution utilities.

This utility class consolidates common subprocess execution patterns
used across different tools, providing consistent timeout handling,
error reporting, and memory monitoring capabilities.
"""

import logging
import os
import subprocess
import tempfile
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import psutil

logger = logging.getLogger(__name__)


@dataclass
class ProcessResult:
    """Result of process execution with detailed information."""

    returncode: int
    stdout: str
    stderr: str
    execution_time: float
    memory_used: float  # Peak memory usage in MB
    timed_out: bool
    command: List[str]


class ProcessExecutor:
    """
    Utility class for consistent subprocess execution across tools.

    Provides common patterns for:
    - Process execution with timeout and memory monitoring
    - Temporary file handling for input/output
    - Consistent error handling and logging
    - Memory usage tracking for performance analysis
    """

    @staticmethod
    def run_with_monitoring(
        command: List[str],
        input_text: Optional[str] = None,
        timeout: float = 30.0,
        monitor_memory: bool = False,
        working_dir: Optional[str] = None,
    ) -> ProcessResult:
        """
        Run a command with optional memory monitoring and timeout.

        Args:
            command: Command and arguments to execute
            input_text: Optional input to send to process stdin
            timeout: Timeout in seconds
            monitor_memory: Whether to monitor peak memory usage
            working_dir: Optional working directory

        Returns:
            ProcessResult: Detailed result of process execution
        """
        start_time = time.time()
        max_memory_usage = 0.0
        timed_out = False

        try:
            # Start the process
            # Use numeric constant for CREATE_NO_WINDOW (0x08000000) to avoid
            # AttributeError on non-Windows platforms during testing
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE if input_text is not None else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=0x08000000 if os.name == "nt" else 0,
                text=True,
                cwd=working_dir,
            )

            # Monitor memory usage if requested
            psutil_process = None
            if monitor_memory:
                try:
                    psutil_process = psutil.Process(process.pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # For processes with input, use communicate() directly with timeout monitoring
            # For processes without input, monitor with polling loop
            if input_text is not None:
                # Use communicate for input handling - it properly closes stdin
                try:
                    stdout, stderr = process.communicate(input=input_text, timeout=timeout)
                    timed_out = False
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()
                    timed_out = True

                # Monitor memory for processes with input (after completion)
                if monitor_memory and psutil_process:
                    try:
                        memory_info = psutil_process.memory_info()
                        max_memory_usage = memory_info.rss / (1024 * 1024)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            else:
                # Monitor the process without input
                while process.poll() is None:
                    # Check timeout
                    if time.time() - start_time > timeout:
                        process.kill()
                        timed_out = True
                        break

                    # Monitor memory usage
                    if monitor_memory and psutil_process:
                        try:
                            memory_info = psutil_process.memory_info()
                            current_memory_mb = memory_info.rss / (1024 * 1024)
                            max_memory_usage = max(max_memory_usage, current_memory_mb)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            break

                    time.sleep(0.005)  # Check every 5ms

                # Get final result
                try:
                    stdout, stderr = process.communicate(timeout=1.0)
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()
                    timed_out = True

            execution_time = time.time() - start_time

            return ProcessResult(
                returncode=process.returncode,
                stdout=stdout or "",
                stderr=stderr or "",
                execution_time=execution_time,
                memory_used=max_memory_usage,
                timed_out=timed_out,
                command=command,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Process execution error: {e}")
            return ProcessResult(
                returncode=-1,
                stdout="",
                stderr=f"Execution error: {str(e)}",
                execution_time=execution_time,
                memory_used=max_memory_usage,
                timed_out=timed_out,
                command=command,
            )

    @staticmethod
    def run_with_temp_files(
        command: List[str],
        input_text: str,
        output_file_needed: bool = False,
        timeout: float = 30.0,
        cleanup: bool = True,
    ) -> Tuple[ProcessResult, Optional[str], Optional[str]]:
        """
        Run a command using temporary files for input/output.

        Args:
            command: Command and arguments to execute
            input_text: Input text to write to temporary file
            output_file_needed: Whether to create a temporary output file
            timeout: Timeout in seconds
            cleanup: Whether to clean up temporary files

        Returns:
            Tuple[ProcessResult, Optional[str], Optional[str]]:
            (result, input_file_path, output_file_path)
        """
        input_temp_path = None
        output_temp_path = None

        try:
            # Create temporary input file
            with tempfile.NamedTemporaryFile(
                mode="w+", suffix=".txt", delete=False, prefix="exec_in_"
            ) as input_temp:
                input_temp.write(input_text)
                input_temp.flush()
                os.fsync(input_temp.fileno())
                input_temp_path = input_temp.name

            # Create temporary output file if needed
            if output_file_needed:
                output_temp = tempfile.NamedTemporaryFile(
                    mode="w+", suffix=".txt", delete=False, prefix="exec_out_"
                )
                output_temp_path = output_temp.name
                output_temp.close()

            # Update command with temp file paths
            updated_command = []
            for arg in command:
                if arg == "{input_file}":
                    updated_command.append(input_temp_path)
                elif arg == "{output_file}":
                    updated_command.append(output_temp_path or "")
                else:
                    updated_command.append(arg)

            # Execute the command
            result = ProcessExecutor.run_with_monitoring(updated_command, timeout=timeout)

            return result, input_temp_path, output_temp_path

        finally:
            # Cleanup temporary files if requested
            if cleanup:
                for temp_path in [input_temp_path, output_temp_path]:
                    if temp_path and os.path.exists(temp_path):
                        try:
                            os.unlink(temp_path)
                        except OSError:
                            pass

    @staticmethod
    def run_pipeline(
        stages: List[Dict[str, Any]],
        timeout_per_stage: float = 30.0,
        stop_on_failure: bool = True,
    ) -> List[ProcessResult]:
        """
        Run multiple processes in a pipeline, passing output between stages.

        Args:
            stages: List of stage configurations, each containing:
                - 'command': List[str] - Command and arguments
                - 'input': Optional[str] - Input for first stage only
                - 'monitor_memory': bool - Whether to monitor memory
            timeout_per_stage: Timeout for each stage
            stop_on_failure: Whether to stop pipeline on first failure

        Returns:
            List[ProcessResult]: Results from each stage
        """
        results = []
        current_input = stages[0].get("input", "") if stages else ""

        for i, stage in enumerate(stages):
            command = stage["command"]
            monitor_memory = stage.get("monitor_memory", False)

            # Use output from previous stage as input (except for first stage)
            stage_input = current_input if i == 0 else results[-1].stdout

            result = ProcessExecutor.run_with_monitoring(
                command=command,
                input_text=stage_input,
                timeout=timeout_per_stage,
                monitor_memory=monitor_memory,
            )

            results.append(result)

            # Stop on failure if requested
            if stop_on_failure and result.returncode != 0:
                break

            current_input = result.stdout

        return results

    @staticmethod
    def get_memory_info(pid: int) -> Dict[str, float]:
        """
        Get detailed memory information for a process.

        Args:
            pid: Process ID

        Returns:
            Dict[str, float]: Memory information in MB
        """
        try:
            process = psutil.Process(pid)
            memory_info = process.memory_info()
            return {
                "rss": memory_info.rss / (1024 * 1024),  # Resident Set Size
                "vms": memory_info.vms / (1024 * 1024),  # Virtual Memory Size
                "percent": process.memory_percent(),  # Percentage of system memory
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {"rss": 0.0, "vms": 0.0, "percent": 0.0}

    @staticmethod
    def format_execution_summary(result: ProcessResult) -> str:
        """
        Format a human-readable execution summary.

        Args:
            result: ProcessResult to format

        Returns:
            str: Formatted summary
        """
        status = "SUCCESS" if result.returncode == 0 else "FAILED"
        if result.timed_out:
            status = "TIMEOUT"

        summary = [
            f"Command: {' '.join(result.command)}",
            f"Status: {status} (exit code: {result.returncode})",
            f"Execution time: {result.execution_time:.3f}s",
        ]

        if result.memory_used > 0:
            summary.append(f"Peak memory: {result.memory_used:.2f} MB")

        if result.stdout:
            summary.append(f"Output: {len(result.stdout)} characters")

        if result.stderr:
            summary.append(f"Error output: {result.stderr[:100]}...")

        return "\n".join(summary)
