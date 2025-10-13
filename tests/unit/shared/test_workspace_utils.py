"""
Test suite for workspace utility functions.

Tests workspace directory structure creation, test type detection,
flat-to-nested migration, and file management utilities.
"""

import pytest
import os
from pathlib import Path
from typing import Dict, List

from src.app.shared.utils.workspace_utils import (
    ensure_workspace_structure,
    get_test_type_from_path,
    is_flat_workspace_structure,
    get_file_language_extension,
    get_file_role,
    list_workspace_files,
    clean_workspace_io_files,
    ensure_test_type_directory,
)


class TestEnsureWorkspaceStructure:
    """Test workspace structure creation."""

    def test_creates_complete_workspace_structure(self, temp_dir):
        """Should create all test type directories with subdirectories."""
        workspace = temp_dir / "workspace"

        ensure_workspace_structure(str(workspace))

        # Check root exists
        assert workspace.exists()

        # Check test type directories
        assert (workspace / "comparator").exists()
        assert (workspace / "validator").exists()
        assert (workspace / "benchmarker").exists()

        # Check subdirectories
        assert (workspace / "comparator" / "inputs").exists()
        assert (workspace / "comparator" / "outputs").exists()
        assert (workspace / "validator" / "inputs").exists()
        assert (workspace / "validator" / "outputs").exists()
        assert (workspace / "benchmarker" / "inputs").exists()
        assert (workspace / "benchmarker" / "outputs").exists()

    def test_handles_existing_directories(self, temp_dir):
        """Should not fail if directories already exist."""
        workspace = temp_dir / "workspace"
        workspace.mkdir()
        (workspace / "comparator").mkdir()

        ensure_workspace_structure(str(workspace))

        # Should still succeed
        assert (workspace / "comparator" / "inputs").exists()

    def test_handles_empty_workspace_dir(self):
        """Should handle empty workspace_dir gracefully."""
        # Should not raise exception
        ensure_workspace_structure("")
        ensure_workspace_structure(None)


class TestGetTestTypeFromPath:
    """Test test type extraction from file paths."""

    @pytest.mark.parametrize(
        "file_path,expected_type",
        [
            ("/workspace/comparator/generator.cpp", "comparator"),
            ("/workspace/validator/test.py", "validator"),
            ("/workspace/benchmarker/generator.java", "benchmarker"),
            ("comparator/inputs/input_1.txt", "comparator"),
            ("validator/outputs/output_5.txt", "validator"),
            ("/workspace/generator.cpp", None),  # No test type in path
            ("random/path/file.txt", None),
        ],
    )
    def test_extracts_test_type_from_path(self, file_path, expected_type):
        """Should extract test type from file path."""
        result = get_test_type_from_path(file_path)
        assert result == expected_type

    def test_handles_absolute_paths(self):
        """Should work with absolute paths."""
        path = "C:\\Users\\workspace\\validator\\test.cpp"
        result = get_test_type_from_path(path)
        assert result == "validator"

    def test_handles_relative_paths(self):
        """Should work with relative paths."""
        path = "comparator/generator.cpp"
        result = get_test_type_from_path(path)
        assert result == "comparator"


class TestIsFlatWorkspaceStructure:
    """Test detection of flat workspace structure."""

    def test_detects_flat_structure_with_cpp_files(self, temp_dir):
        """Should detect flat structure when source files in root."""
        workspace = temp_dir / "workspace"
        workspace.mkdir()
        (workspace / "generator.cpp").write_text("code")
        (workspace / "test.cpp").write_text("code")

        result = is_flat_workspace_structure(str(workspace))

        assert result is True

    def test_detects_flat_structure_with_python_files(self, temp_dir):
        """Should detect flat structure with Python files."""
        workspace = temp_dir / "workspace"
        workspace.mkdir()
        (workspace / "generator.py").write_text("code")

        result = is_flat_workspace_structure(str(workspace))

        assert result is True

    def test_detects_flat_structure_with_java_files(self, temp_dir):
        """Should detect flat structure with Java files."""
        workspace = temp_dir / "workspace"
        workspace.mkdir()
        (workspace / "Generator.java").write_text("code")

        result = is_flat_workspace_structure(str(workspace))

        assert result is True

    def test_detects_flat_structure_with_io_files(self, temp_dir):
        """Should detect flat structure with I/O files in root."""
        workspace = temp_dir / "workspace"
        workspace.mkdir()
        (workspace / "input_1.txt").write_text("data")
        (workspace / "output_1.txt").write_text("data")

        result = is_flat_workspace_structure(str(workspace))

        assert result is True

    def test_not_flat_with_nested_structure(self, temp_dir):
        """Should not detect flat structure with nested directories."""
        workspace = temp_dir / "workspace"
        comparator = workspace / "comparator"
        comparator.mkdir(parents=True)
        (comparator / "generator.cpp").write_text("code")

        result = is_flat_workspace_structure(str(workspace))

        assert result is False

    def test_not_flat_for_empty_workspace(self, temp_dir):
        """Should not detect flat structure for empty workspace."""
        workspace = temp_dir / "workspace"
        workspace.mkdir()

        result = is_flat_workspace_structure(str(workspace))

        assert result is False

    def test_not_flat_for_nonexistent_workspace(self):
        """Should return False for nonexistent workspace."""
        result = is_flat_workspace_structure("/nonexistent/workspace")

        assert result is False


class TestGetFileLanguageExtension:
    """Test language detection from filename."""

    @pytest.mark.parametrize(
        "filename,expected_lang",
        [
            ("generator.cpp", "cpp"),
            ("test.py", "py"),
            ("Main.java", "java"),
            ("program.exe", "cpp"),  # Assume C++ executable
            ("Test.class", "java"),  # Java bytecode
            ("readme.txt", None),
            ("file.unknown", None),
        ],
    )
    def test_detects_language_from_extension(self, filename, expected_lang):
        """Should detect language from file extension."""
        result = get_file_language_extension(filename)
        assert result == expected_lang

    def test_handles_case_insensitive(self):
        """Should handle case-insensitive extensions."""
        assert get_file_language_extension("TEST.CPP") == "cpp"
        assert get_file_language_extension("Main.JAVA") == "java"


class TestGetFileRole:
    """Test file role detection from filename."""

    @pytest.mark.parametrize(
        "filename,expected_role",
        [
            ("generator.cpp", "generator"),
            ("Generator.java", "generator"),
            ("gen.py", "generator"),
            ("correct.cpp", "correct"),
            ("solution.py", "correct"),
            ("sol.java", "correct"),
            ("test.cpp", "test"),
            ("brute.py", "test"),
            ("validator.cpp", "validator"),
            ("checker.py", "validator"),
            ("Validator.java", "validator"),
            ("unknown.cpp", None),
            ("main.py", None),
        ],
    )
    def test_detects_file_role_from_name(self, filename, expected_role):
        """Should detect file role from basename."""
        result = get_file_role(filename)
        assert result == expected_role

    def test_handles_case_insensitive(self):
        """Should handle case-insensitive filenames."""
        assert get_file_role("GENERATOR.cpp") == "generator"
        assert get_file_role("Correct.py") == "correct"
        assert get_file_role("TEST.java") == "test"


class TestListWorkspaceFiles:
    """Test workspace file listing."""

    def test_lists_files_by_test_type(self, temp_dir):
        """Should list files organized by test type."""
        workspace = temp_dir / "workspace"
        ensure_workspace_structure(str(workspace))

        # Create test files
        (workspace / "comparator" / "generator.cpp").write_text("code")
        (workspace / "comparator" / "test.cpp").write_text("code")
        (workspace / "validator" / "validator.py").write_text("code")

        result = list_workspace_files(str(workspace))

        assert "comparator" in result
        assert "validator" in result
        assert len(result["comparator"]) == 2
        assert len(result["validator"]) == 1
        # Check that generator.cpp is in the list (use os-agnostic check)
        assert any("generator.cpp" in f for f in result["comparator"])

    def test_lists_specific_test_type(self, temp_dir):
        """Should filter by specific test type."""
        workspace = temp_dir / "workspace"
        ensure_workspace_structure(str(workspace))

        (workspace / "comparator" / "generator.cpp").write_text("code")
        (workspace / "validator" / "validator.py").write_text("code")

        result = list_workspace_files(str(workspace), test_type="comparator")

        assert "comparator" in result
        assert "validator" not in result

    def test_returns_empty_for_nonexistent_workspace(self):
        """Should return empty dict for nonexistent workspace."""
        result = list_workspace_files("/nonexistent/workspace")

        assert result == {}

    def test_returns_empty_for_empty_workspace(self, temp_dir):
        """Should return empty dict for empty workspace."""
        workspace = temp_dir / "workspace"
        ensure_workspace_structure(str(workspace))

        result = list_workspace_files(str(workspace))

        assert result == {}

    def test_ignores_subdirectories(self, temp_dir):
        """Should only list files, not subdirectories."""
        workspace = temp_dir / "workspace"
        ensure_workspace_structure(str(workspace))

        (workspace / "comparator" / "generator.cpp").write_text("code")
        # Subdirectories should be ignored

        result = list_workspace_files(str(workspace))

        # Should not include 'inputs' or 'outputs' directories
        assert all(
            "inputs" not in f and "outputs" not in f
            for files in result.values()
            for f in files
        )


class TestCleanWorkspaceIOFiles:
    """Test I/O file cleanup."""

    def test_cleans_input_files(self, temp_dir):
        """Should remove all .txt files from inputs directory."""
        workspace = temp_dir / "workspace"
        ensure_workspace_structure(str(workspace))

        inputs_dir = workspace / "comparator" / "inputs"
        (inputs_dir / "input_1.txt").write_text("data")
        (inputs_dir / "input_2.txt").write_text("data")

        count = clean_workspace_io_files(str(workspace), "comparator")

        assert count == 2
        assert not (inputs_dir / "input_1.txt").exists()
        assert not (inputs_dir / "input_2.txt").exists()

    def test_cleans_output_files(self, temp_dir):
        """Should remove all .txt files from outputs directory."""
        workspace = temp_dir / "workspace"
        ensure_workspace_structure(str(workspace))

        outputs_dir = workspace / "comparator" / "outputs"
        (outputs_dir / "output_1.txt").write_text("data")
        (outputs_dir / "output_2.txt").write_text("data")

        count = clean_workspace_io_files(str(workspace), "comparator")

        assert count == 2
        assert not (outputs_dir / "output_1.txt").exists()

    def test_cleans_both_inputs_and_outputs(self, temp_dir):
        """Should clean both inputs and outputs."""
        workspace = temp_dir / "workspace"
        ensure_workspace_structure(str(workspace))

        inputs_dir = workspace / "validator" / "inputs"
        outputs_dir = workspace / "validator" / "outputs"
        (inputs_dir / "input_1.txt").write_text("data")
        (outputs_dir / "output_1.txt").write_text("data")

        count = clean_workspace_io_files(str(workspace), "validator")

        assert count == 2

    def test_only_removes_txt_files(self, temp_dir):
        """Should only remove .txt files, not other types."""
        workspace = temp_dir / "workspace"
        ensure_workspace_structure(str(workspace))

        inputs_dir = workspace / "comparator" / "inputs"
        (inputs_dir / "input_1.txt").write_text("data")
        (inputs_dir / "readme.md").write_text("data")

        count = clean_workspace_io_files(str(workspace), "comparator")

        assert count == 1
        assert (inputs_dir / "readme.md").exists()

    def test_returns_zero_for_empty_directories(self, temp_dir):
        """Should return 0 if no files to clean."""
        workspace = temp_dir / "workspace"
        ensure_workspace_structure(str(workspace))

        count = clean_workspace_io_files(str(workspace), "comparator")

        assert count == 0


class TestEnsureTestTypeDirectory:
    """Test test type directory creation."""

    def test_creates_test_type_directory(self, temp_dir):
        """Should create test type directory and subdirectories."""
        workspace = temp_dir / "workspace"
        workspace.mkdir()

        test_dir = ensure_test_type_directory(str(workspace), "comparator")

        assert Path(test_dir).exists()
        assert (Path(test_dir) / "inputs").exists()
        assert (Path(test_dir) / "outputs").exists()

    def test_returns_correct_path(self, temp_dir):
        """Should return path to test type directory."""
        workspace = temp_dir / "workspace"
        workspace.mkdir()

        test_dir = ensure_test_type_directory(str(workspace), "validator")

        assert "validator" in test_dir

    def test_handles_existing_directory(self, temp_dir):
        """Should not fail if directory already exists."""
        workspace = temp_dir / "workspace"
        ensure_workspace_structure(str(workspace))

        # Call twice - should not raise exception
        test_dir1 = ensure_test_type_directory(str(workspace), "comparator")
        test_dir2 = ensure_test_type_directory(str(workspace), "comparator")

        assert test_dir1 == test_dir2

    @pytest.mark.parametrize(
        "test_type",
        [
            "comparator",
            "validator",
            "benchmarker",
            "comparison",  # Alias
            "validation",  # Alias
            "benchmark",  # Alias
        ],
    )
    def test_handles_all_test_types(self, temp_dir, test_type):
        """Should handle all test types and aliases."""
        workspace = temp_dir / "workspace"
        workspace.mkdir()

        test_dir = ensure_test_type_directory(str(workspace), test_type)

        assert Path(test_dir).exists()


class TestWorkspaceUtilsIntegration:
    """Integration tests for workspace utilities."""

    def test_complete_workspace_workflow(self, temp_dir):
        """Test complete workspace setup and usage workflow."""
        workspace = temp_dir / "workspace"

        # 1. Create structure
        ensure_workspace_structure(str(workspace))

        # 2. Verify structure
        assert not is_flat_workspace_structure(str(workspace))

        # 3. Create test files
        comparator_dir = workspace / "comparator"
        (comparator_dir / "generator.cpp").write_text("code")
        (comparator_dir / "test.py").write_text("code")

        # 4. List files
        files = list_workspace_files(str(workspace))
        assert "comparator" in files
        assert len(files["comparator"]) == 2

        # 5. Create I/O files
        inputs_dir = comparator_dir / "inputs"
        (inputs_dir / "input_1.txt").write_text("data")

        # 6. Clean I/O files
        count = clean_workspace_io_files(str(workspace), "comparator")
        assert count == 1
        assert not (inputs_dir / "input_1.txt").exists()

    def test_handles_mixed_language_workspace(self, temp_dir):
        """Test workspace with multiple languages."""
        workspace = temp_dir / "workspace"
        ensure_workspace_structure(str(workspace))

        # Create files in different languages
        (workspace / "comparator" / "generator.cpp").write_text("cpp")
        (workspace / "validator" / "test.py").write_text("py")
        (workspace / "benchmarker" / "Generator.java").write_text("java")

        files = list_workspace_files(str(workspace))

        assert len(files) == 3
        assert "comparator" in files
        assert "validator" in files
        assert "benchmarker" in files
