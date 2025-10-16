"""
Test helper utilities and custom assertions.

Provides reusable test utilities, mock objects, and helper functions.
"""

import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional


class CompilationHelper:
    """Helper for compilation-related tests."""

    @staticmethod
    def create_source_file(directory: Path, filename: str, content: str) -> Path:
        """Create a source file for testing."""
        file_path = directory / filename
        file_path.write_text(content, encoding="utf-8")
        return file_path

    @staticmethod
    def check_executable_exists(executable_path: Path) -> bool:
        """Check if executable was created."""
        return executable_path.exists()

    @staticmethod
    def get_executable_path(source_path: Path) -> Path:
        """Get expected executable path from source path."""
        if os.name == "nt":
            return source_path.with_suffix(".exe")
        return source_path.with_suffix("")

    @staticmethod
    def create_test_files(
        workspace: Path, test_type: str, language: str = "cpp"
    ) -> Dict[str, Path]:
        """
        Create standard test files for a test type.

        Args:
            workspace: Workspace root directory
            test_type: Type of test (comparator, validator, benchmarker)
            language: Programming language (cpp, py, java)

        Returns:
            Dict with file paths: generator, test, correct, validator
        """
        test_dir = workspace / test_type
        test_dir.mkdir(parents=True, exist_ok=True)

        extensions = {"cpp": ".cpp", "py": ".py", "java": ".java"}
        ext = extensions.get(language, ".cpp")

        files = {}
        for file_type in ["generator", "test", "correct", "validator"]:
            file_path = test_dir / f"{file_type}{ext}"
            files[file_type] = file_path

        return files


class WorkspaceHelper:
    """Helper for workspace-related tests."""

    @staticmethod
    def create_test_workspace(
        base_dir: Path, test_type: str = "comparator"
    ) -> Dict[str, Path]:
        """
        Create a test workspace with all required directories.

        Returns dict with paths: workspace, test_dir, inputs, outputs
        """
        workspace = base_dir / "workspace"
        test_dir = workspace / test_type
        inputs = test_dir / "inputs"
        outputs = test_dir / "outputs"

        inputs.mkdir(parents=True, exist_ok=True)
        outputs.mkdir(parents=True, exist_ok=True)

        return {
            "workspace": workspace,
            "test_dir": test_dir,
            "inputs": inputs,
            "outputs": outputs,
        }

    @staticmethod
    def create_full_workspace(base_dir: Path) -> Dict[str, Path]:
        """
        Create a full workspace with all test types.

        Returns dict with paths for all test types.
        """
        workspaces = {}
        for test_type in ["comparator", "validator", "benchmarker"]:
            workspaces[test_type] = WorkspaceHelper.create_test_workspace(
                base_dir, test_type
            )
        return workspaces

    @staticmethod
    def verify_workspace_structure(workspace: Path, test_type: str) -> bool:
        """
        Verify workspace has correct structure.

        Returns True if structure is valid.
        """
        test_dir = workspace / test_type
        if not test_dir.exists():
            return False

        required_dirs = ["inputs", "outputs"]
        for dir_name in required_dirs:
            if not (test_dir / dir_name).exists():
                return False

        return True


class ProcessHelper:
    """Helper for process execution tests."""

    @staticmethod
    @contextmanager
    def timeout_context(seconds: float):
        """Context manager for timeout testing."""
        start = time.time()
        yield
        elapsed = time.time() - start
        assert (
            elapsed < seconds
        ), f"Operation took {elapsed:.2f}s, expected < {seconds}s"

    @staticmethod
    def create_temp_executable(directory: Path, name: str = "test") -> Path:
        """Create a dummy executable for testing."""
        if os.name == "nt":
            exe_path = directory / f"{name}.exe"
        else:
            exe_path = directory / name

        exe_path.write_text("dummy executable")
        if os.name != "nt":
            exe_path.chmod(0o755)

        return exe_path

    @staticmethod
    def create_simple_executable(
        directory: Path, name: str, language: str = "cpp"
    ) -> Path:
        """
        Create a simple executable that echoes input.

        Args:
            directory: Directory to create executable in
            name: Base name for executable
            language: Language to use (cpp, py)

        Returns:
            Path to created executable or script
        """
        if language == "cpp":
            source = directory / f"{name}.cpp"
            source.write_text(
                """
#include <iostream>
int main() {
    int n;
    std::cin >> n;
    std::cout << n * 2 << std::endl;
    return 0;
}
"""
            )
            return source
        elif language == "py":
            script = directory / f"{name}.py"
            script.write_text(
                """
n = int(input())
print(n * 2)
"""
            )
            return script

        return ProcessHelper.create_temp_executable(directory, name)


class AssertionHelper:
    """Custom assertions for domain-specific checks."""

    @staticmethod
    def assert_test_result_valid(result: Dict[str, Any]):
        """Assert test result has required fields."""
        required_fields = ["test_number", "passed", "total_time", "memory"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

        assert isinstance(result["test_number"], int)
        assert isinstance(result["passed"], bool)
        assert isinstance(result["total_time"], (int, float))
        assert isinstance(result["memory"], (int, float))

    @staticmethod
    def assert_compilation_success(result: tuple):
        """Assert compilation result indicates success."""
        assert len(result) == 2, "Compilation result should be (success, message)"
        success, message = result
        assert success is True, f"Compilation failed: {message}"
        assert isinstance(message, str)

    @staticmethod
    def assert_compilation_failure(result: tuple):
        """Assert compilation result indicates failure."""
        assert len(result) == 2, "Compilation result should be (success, message)"
        success, message = result
        assert success is False, f"Expected compilation to fail, but it succeeded"
        assert isinstance(message, str)

    @staticmethod
    def assert_file_structure_exists(workspace: Path, test_type: str):
        """Assert workspace has correct structure."""
        test_dir = workspace / test_type
        assert test_dir.exists(), f"{test_type} directory not found"
        assert (test_dir / "inputs").exists(), f"{test_type}/inputs not found"
        assert (test_dir / "outputs").exists(), f"{test_type}/outputs not found"

    @staticmethod
    def assert_valid_test_execution(result: Dict[str, Any]):
        """
        Assert test execution result is valid.

        Checks for:
        - Required fields present
        - Valid data types
        - Logical consistency (e.g., time >= 0)
        """
        required_fields = ["passed", "total_time", "memory"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

        assert isinstance(result["passed"], bool)
        assert isinstance(result["total_time"], (int, float))
        assert result["total_time"] >= 0, "Time cannot be negative"
        assert isinstance(result["memory"], (int, float))
        assert result["memory"] >= 0, "Memory cannot be negative"

    @staticmethod
    def assert_signal_emitted(signal_spy, expected_args: Optional[List] = None):
        """
        Assert Qt signal was emitted with expected arguments.

        Args:
            signal_spy: Qt signal spy object
            expected_args: Optional list of expected arguments
        """
        assert len(signal_spy) > 0, "Signal was not emitted"

        if expected_args is not None:
            actual_args = signal_spy[0]
            assert (
                actual_args == expected_args
            ), f"Signal emitted with wrong args. Expected {expected_args}, got {actual_args}"


class MockHelper:
    """Helper for creating mock objects."""

    @staticmethod
    def create_mock_test_result(
        test_number: int = 1,
        passed: bool = True,
        total_time: float = 0.5,
        memory: float = 10.0,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a mock test result dictionary.

        Args:
            test_number: Test case number
            passed: Whether test passed
            total_time: Execution time in seconds
            memory: Memory usage in MB
            **kwargs: Additional fields

        Returns:
            Mock test result dictionary
        """
        result = {
            "test_number": test_number,
            "passed": passed,
            "total_time": total_time,
            "memory": memory,
            "exit_code": 0 if passed else 1,
        }
        result.update(kwargs)
        return result

    @staticmethod
    def create_mock_compilation_result(
        success: bool = True, message: str = "Compilation successful"
    ) -> tuple:
        """Create a mock compilation result tuple."""
        return (success, message)
