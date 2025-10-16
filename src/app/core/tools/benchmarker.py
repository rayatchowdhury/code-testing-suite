"""
Benchmarker - Main controller for performance benchmarking workflow.

This module has been refactored as part of Phase 4 migration to inherit
from BaseRunner, eliminating ~100 lines of duplicate runner code while
maintaining 100% API compatibility.

Also contains BenchmarkCompilerRunner for specialized compilation handling.
"""

import json
import logging
import os
from datetime import datetime

from PySide6.QtCore import Signal

from src.app.core.tools.base.base_runner import BaseRunner
from src.app.core.tools.compiler_runner import CompilerRunner
from src.app.core.tools.specialized.benchmark_test_worker import BenchmarkTestWorker
from src.app.persistence.database import TestResult

logger = logging.getLogger(__name__)


class BenchmarkCompilerRunner(CompilerRunner):
    """Specialized compiler runner for benchmarking"""

    # Additional signals specific to benchmarking
    compilationStarted = Signal()
    compilationFinished = Signal(bool)  # True if successful
    outputAvailable = Signal(str, str)  # message, type

    def __init__(self, console_output):
        # Initialize the base compiler runner (which already handles threading)
        super().__init__(console_output)

        # Connect additional signals for benchmark-specific behavior
        if self.worker:
            self.worker.output.connect(self._handle_output_for_benchmark)
            self.worker.error.connect(self._handle_error_for_benchmark)

        logger.debug("BenchmarkCompilerRunner initialized")

    def _handle_output_for_benchmark(self, output_data):
        """Handle output with benchmark-specific signals"""
        if isinstance(output_data, tuple) and len(output_data) == 2:
            text, format_type = output_data
        else:
            text, format_type = str(output_data), "default"

        # Emit benchmark-specific signal
        self.outputAvailable.emit(text, format_type)

    def _handle_error_for_benchmark(self, error_data):
        """Handle error with benchmark-specific signals"""
        if isinstance(error_data, tuple) and len(error_data) == 2:
            text, format_type = error_data
        else:
            text, format_type = str(error_data), "error"

        # Emit benchmark-specific signal
        self.outputAvailable.emit(text, format_type)

    def compile_and_run_code(self, filepath):
        """Compile and run code for benchmarking"""
        logger.debug(f"Starting benchmark compilation for {filepath}")

        # Emit TLE-specific signal
        self.compilationStarted.emit()

        # Connect to finished signal to emit compilation result
        def on_finished():
            # Assume success if we get here without errors
            self.compilationFinished.emit(True)
            self.finished.disconnect(on_finished)

        self.finished.connect(on_finished)

        # Use base class method
        super().compile_and_run_code(filepath)

    def stop(self):
        """Stop any running process (alias for compatibility)"""
        self.stop_execution()


class Benchmarker(BaseRunner):
    """
    Main controller for benchmarking workflow.

    This class has been refactored to inherit from BaseRunner, eliminating
    duplicate runner code while maintaining exact API compatibility.
    """

    # Updated signal signature to include input/output data
    testCompleted = Signal(
        str, int, bool, float, float, bool, str, str, int
    )  # test name, test number, passed, execution time, memory used, memory passed, input_data, output_data, test_size

    def __init__(self, workspace_dir, files=None, config=None):
        # Define default files specific to TLE testing if not provided
        if files is None:
            files = {
                "generator": os.path.join(workspace_dir, "generator.cpp"),
                "test": os.path.join(workspace_dir, "test.cpp"),
            }

        # Initialize BaseRunner with benchmark-specific configuration
        super().__init__(workspace_dir, files, test_type="benchmark", config=config)

        # Store TLE-specific parameters
        self.time_limit = 0
        self.memory_limit = 0

    def _get_compiler_flags(self):
        """Get benchmark-specific compiler optimization flags"""
        return [
            "-O3",  # Maximum optimization for performance testing
            "-march=native",  # Optimize for current CPU architecture
            "-mtune=native",  # Tune for current CPU
            "-pipe",  # Use pipes instead of temporary files
            "-std=c++17",  # Use modern C++ standard
            "-Wall",  # Enable common warnings
            "-DNDEBUG",  # Disable debug assertions for maximum performance
        ]

    def _create_test_worker(
        self, test_count, time_limit=None, memory_limit=None, max_workers=None, **kwargs
    ):
        """Create BenchmarkTestWorker for performance testing"""
        # Store limits for database saving
        self.time_limit = time_limit or 1000  # Default 1000ms
        self.memory_limit = memory_limit or 256  # Default 256MB

        return BenchmarkTestWorker(
            self.workspace_dir,
            self.executables,
            self.time_limit,
            self.memory_limit,
            test_count,
            max_workers,
        )

    def _create_test_status_window(self):
        """Create benchmark-specific status window"""
        from src.app.presentation.views.benchmarker.benchmark_status_window import (
            BenchmarkStatusWindow,
        )

        status_window = BenchmarkStatusWindow()
        # Configure status window with benchmark-specific parameters
        status_window.workspace_dir = self.workspace_dir
        status_window.time_limit = self.time_limit / 1000.0  # Convert to seconds
        status_window.memory_limit = self.memory_limit
        status_window.test_count = self.test_count
        return status_window

    def _connect_worker_signals(self, worker):
        """Connect benchmark-specific signals"""
        # Call parent to connect common signals
        super()._connect_worker_signals(worker)

        # Connect benchmark-specific testCompleted signal
        if hasattr(worker, "testCompleted"):
            worker.testCompleted.connect(self.testCompleted)

    def _create_test_result(
        self, all_passed, test_results, passed_tests, failed_tests, total_time
    ):
        """
        Create benchmark-specific TestResult object.

        This method implements the template method pattern, providing
        benchmark-specific analysis and database result creation.
        """
        # Get the test file path
        test_file_path = self._get_test_file_path()

        # Create files snapshot
        files_snapshot = self._create_files_snapshot()

        # Compile benchmark-specific analysis
        benchmark_analysis = {
            "test_count": self.test_count,
            "time_limit_ms": self.time_limit,
            "memory_limit_mb": self.memory_limit,
            "performance_summary": {
                "accepted": sum(1 for r in test_results if r.get("passed", False)),
                "time_limit_exceeded": sum(
                    1 for r in test_results if not r.get("time_passed", True)
                ),
                "memory_limit_exceeded": sum(
                    1 for r in test_results if not r.get("memory_passed", True)
                ),
                "runtime_errors": sum(
                    1
                    for r in test_results
                    if r.get("error_details", "").startswith("Runtime Error")
                ),
                "system_errors": sum(
                    1
                    for r in test_results
                    if "Execution error" in r.get("error_details", "")
                ),
            },
            "performance_metrics": {
                "avg_execution_time": (
                    sum(r.get("execution_time", 0) for r in test_results)
                    / len(test_results)
                    if test_results
                    else 0
                ),
                "max_execution_time": max(
                    (r.get("execution_time", 0) for r in test_results), default=0
                ),
                "avg_memory_usage": (
                    sum(r.get("memory_used", 0) for r in test_results)
                    / len(test_results)
                    if test_results
                    else 0
                ),
                "max_memory_usage": max(
                    (r.get("memory_used", 0) for r in test_results), default=0
                ),
            },
            "failed_tests": [r for r in test_results if not r.get("passed", True)],
        }

        # Create and return TestResult object
        return TestResult(
            test_type="benchmark",
            file_path=test_file_path,
            test_count=self.test_count,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_time=total_time,
            timestamp=datetime.now().isoformat(),
            test_details=json.dumps(test_results),
            project_name=os.path.basename(self.workspace_dir),
            files_snapshot=json.dumps(files_snapshot),
            mismatch_analysis=json.dumps(benchmark_analysis),
        )

    def run_benchmark_test(
        self, test_count, time_limit=1000, memory_limit=256, max_workers=None
    ):
        """
        Start benchmark tests - maintains original API.

        This method preserves the original public API while using
        the BaseRunner infrastructure for thread management.

        Args:
            test_count: Number of tests to run
            time_limit: Time limit in milliseconds
            memory_limit: Memory limit in MB
            max_workers: Maximum number of parallel workers
        """
        # Use BaseRunner's run_tests method with TLE-specific parameters
        self.run_tests(
            test_count,
            time_limit=time_limit,
            memory_limit=memory_limit,
            max_workers=max_workers,
        )
