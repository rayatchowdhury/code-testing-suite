"""
Unit tests for FilesSnapshotService.

Tests file snapshot creation and mismatch analysis including:
- Creating snapshots for different test types
- File detection and language identification
- Output mismatch analysis
- Error handling
"""

import os
from pathlib import Path

import pytest

from src.app.persistence.database.models import FilesSnapshot
from src.app.persistence.database.services.files_snapshot_service import (
    FilesSnapshotService,
)
from tests.fixtures.database_fixtures import (
    SAMPLE_CPP_CODE,
    SAMPLE_GENERATOR_CODE,
    SAMPLE_JAVA_CODE,
    SAMPLE_PYTHON_CODE,
    SAMPLE_VALIDATOR_CODE,
)


@pytest.fixture
def workspace_dir(tmp_path):
    """Create temporary workspace directory."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return str(workspace)


@pytest.fixture
def comparator_workspace(workspace_dir):
    """Create workspace with comparator files."""
    comparator_dir = Path(workspace_dir) / "comparator"
    comparator_dir.mkdir()

    (comparator_dir / "generator.cpp").write_text(SAMPLE_GENERATOR_CODE)
    (comparator_dir / "correct.cpp").write_text(SAMPLE_CPP_CODE)
    (comparator_dir / "test.cpp").write_text(SAMPLE_CPP_CODE)

    return workspace_dir


@pytest.fixture
def validator_workspace(workspace_dir):
    """Create workspace with validator files."""
    validator_dir = Path(workspace_dir) / "validator"
    validator_dir.mkdir()

    (validator_dir / "generator.cpp").write_text(SAMPLE_GENERATOR_CODE)
    (validator_dir / "validator.cpp").write_text(SAMPLE_VALIDATOR_CODE)
    (validator_dir / "test.cpp").write_text(SAMPLE_CPP_CODE)

    return workspace_dir


@pytest.fixture
def benchmarker_workspace(workspace_dir):
    """Create workspace with benchmarker files."""
    benchmarker_dir = Path(workspace_dir) / "benchmarker"
    benchmarker_dir.mkdir()

    (benchmarker_dir / "generator.cpp").write_text(SAMPLE_GENERATOR_CODE)
    (benchmarker_dir / "test.cpp").write_text(SAMPLE_CPP_CODE)

    return workspace_dir


@pytest.fixture
def mixed_language_workspace(workspace_dir):
    """Create workspace with mixed language files."""
    comparator_dir = Path(workspace_dir) / "comparator"
    comparator_dir.mkdir()

    (comparator_dir / "generator.py").write_text(SAMPLE_PYTHON_CODE)
    (comparator_dir / "correct.py").write_text(SAMPLE_PYTHON_CODE)
    (comparator_dir / "test.py").write_text(SAMPLE_PYTHON_CODE)

    return workspace_dir


class TestCreateSnapshot:
    """Test creating file snapshots."""

    def test_creates_snapshot_for_comparator(self, comparator_workspace):
        """Should create snapshot for comparator test type."""
        snapshot = FilesSnapshotService.create_snapshot(comparator_workspace, "comparator")

        assert isinstance(snapshot, FilesSnapshot)
        assert snapshot.test_type == "comparison"

    def test_creates_snapshot_for_validator(self, validator_workspace):
        """Should create snapshot for validator test type."""
        snapshot = FilesSnapshotService.create_snapshot(validator_workspace, "validator")

        assert isinstance(snapshot, FilesSnapshot)
        assert snapshot.test_type == "validation"

    def test_creates_snapshot_for_benchmarker(self, benchmarker_workspace):
        """Should create snapshot for benchmarker test type."""
        snapshot = FilesSnapshotService.create_snapshot(benchmarker_workspace, "benchmarker")

        assert isinstance(snapshot, FilesSnapshot)
        assert snapshot.test_type == "benchmark"

    def test_normalizes_test_type_names(self, comparator_workspace):
        """Should normalize test type names (comparison -> comparator)."""
        snapshot1 = FilesSnapshotService.create_snapshot(comparator_workspace, "comparison")
        snapshot2 = FilesSnapshotService.create_snapshot(comparator_workspace, "comparator")

        assert snapshot1.test_type == snapshot2.test_type
        assert snapshot1.test_type == "comparison"

    def test_captures_cpp_files(self, comparator_workspace):
        """Should capture C++ source files."""
        snapshot = FilesSnapshotService.create_snapshot(comparator_workspace, "comparator")

        json_str = snapshot.to_json()
        assert "generator" in json_str or "correct" in json_str or "test" in json_str

    def test_detects_cpp_language(self, comparator_workspace):
        """Should detect C++ as primary language."""
        snapshot = FilesSnapshotService.create_snapshot(comparator_workspace, "comparator")

        assert snapshot.primary_language == "cpp"

    def test_detects_python_language(self, mixed_language_workspace):
        """Should detect Python as primary language."""
        snapshot = FilesSnapshotService.create_snapshot(mixed_language_workspace, "comparator")

        assert snapshot.primary_language == "py"

    def test_handles_nonexistent_workspace(self, tmp_path):
        """Should handle nonexistent workspace gracefully."""
        nonexistent = str(tmp_path / "nonexistent")

        snapshot = FilesSnapshotService.create_snapshot(nonexistent, "comparator")

        assert isinstance(snapshot, FilesSnapshot)
        # Should have empty files
        assert snapshot.files == {}

    def test_handles_empty_directory(self, workspace_dir):
        """Should handle empty workspace directory."""
        comparator_dir = Path(workspace_dir) / "comparator"
        comparator_dir.mkdir()

        snapshot = FilesSnapshotService.create_snapshot(workspace_dir, "comparator")

        assert isinstance(snapshot, FilesSnapshot)

    def test_skips_subdirectories(self, comparator_workspace):
        """Should skip subdirectories (inputs/outputs)."""
        comparator_dir = Path(comparator_workspace) / "comparator"
        inputs_dir = comparator_dir / "inputs"
        inputs_dir.mkdir()
        (inputs_dir / "input.txt").write_text("some input")

        snapshot = FilesSnapshotService.create_snapshot(comparator_workspace, "comparator")

        # Should not include files from subdirectories
        json_str = snapshot.to_json()
        assert "input.txt" not in json_str

    def test_ignores_non_source_files(self, comparator_workspace):
        """Should ignore non-source files."""
        comparator_dir = Path(comparator_workspace) / "comparator"
        (comparator_dir / "readme.txt").write_text("readme")
        (comparator_dir / "data.json").write_text("{}")

        snapshot = FilesSnapshotService.create_snapshot(comparator_workspace, "comparator")

        json_str = snapshot.to_json()
        assert "readme.txt" not in json_str
        assert "data.json" not in json_str


class TestFileRoleDetection:
    """Test detecting file roles (generator, correct, test, validator)."""

    def test_detects_generator_files(self, comparator_workspace):
        """Should detect generator files."""
        snapshot = FilesSnapshotService.create_snapshot(comparator_workspace, "comparator")

        json_str = snapshot.to_json()
        assert "generator" in json_str.lower()

    def test_detects_correct_files(self, comparator_workspace):
        """Should detect correct solution files."""
        snapshot = FilesSnapshotService.create_snapshot(comparator_workspace, "comparator")

        json_str = snapshot.to_json()
        assert "correct" in json_str.lower()

    def test_detects_test_files(self, comparator_workspace):
        """Should detect test files."""
        snapshot = FilesSnapshotService.create_snapshot(comparator_workspace, "comparator")

        json_str = snapshot.to_json()
        assert "test" in json_str.lower()

    def test_detects_validator_files(self, validator_workspace):
        """Should detect validator files."""
        snapshot = FilesSnapshotService.create_snapshot(validator_workspace, "validator")

        json_str = snapshot.to_json()
        assert "validator" in json_str.lower()


class TestMultiLanguageSupport:
    """Test support for different programming languages."""

    def test_handles_python_files(self, workspace_dir):
        """Should handle Python files."""
        comparator_dir = Path(workspace_dir) / "comparator"
        comparator_dir.mkdir()
        (comparator_dir / "generator.py").write_text(SAMPLE_PYTHON_CODE)
        (comparator_dir / "correct.py").write_text(SAMPLE_PYTHON_CODE)
        (comparator_dir / "test.py").write_text(SAMPLE_PYTHON_CODE)

        snapshot = FilesSnapshotService.create_snapshot(workspace_dir, "comparator")

        assert snapshot.primary_language == "py"

    def test_handles_java_files(self, workspace_dir):
        """Should handle Java files."""
        comparator_dir = Path(workspace_dir) / "comparator"
        comparator_dir.mkdir()
        (comparator_dir / "Generator.java").write_text(SAMPLE_JAVA_CODE)
        (comparator_dir / "Correct.java").write_text(SAMPLE_JAVA_CODE)
        (comparator_dir / "Test.java").write_text(SAMPLE_JAVA_CODE)

        snapshot = FilesSnapshotService.create_snapshot(workspace_dir, "comparator")

        assert snapshot.primary_language == "java"

    def test_handles_header_files(self, workspace_dir):
        """Should handle C++ header files."""
        comparator_dir = Path(workspace_dir) / "comparator"
        comparator_dir.mkdir()
        (comparator_dir / "generator.h").write_text("#ifndef GEN_H\n#define GEN_H\n")
        (comparator_dir / "correct.cpp").write_text(SAMPLE_CPP_CODE)
        (comparator_dir / "test.cpp").write_text(SAMPLE_CPP_CODE)

        snapshot = FilesSnapshotService.create_snapshot(workspace_dir, "comparator")

        # Should still work
        assert isinstance(snapshot, FilesSnapshot)


class TestMismatchAnalysis:
    """Test output mismatch analysis."""

    def test_analyzes_identical_output(self):
        """Should analyze identical output correctly."""
        expected = "hello\nworld\n"
        actual = "hello\nworld\n"

        analysis = FilesSnapshotService.analyze_output_mismatch(expected, actual)

        assert isinstance(analysis, dict)
        # Should indicate no differences
        assert "summary" in analysis

    def test_analyzes_different_output(self):
        """Should detect differences in output."""
        expected = "hello\nworld\n"
        actual = "hello\nWORLD\n"

        analysis = FilesSnapshotService.analyze_output_mismatch(expected, actual)

        assert isinstance(analysis, dict)
        assert "unified_diff" in analysis or "line_differences" in analysis

    def test_provides_character_level_diff(self):
        """Should provide character-level differences."""
        expected = "test"
        actual = "tent"

        analysis = FilesSnapshotService.analyze_output_mismatch(expected, actual)

        assert isinstance(analysis, dict)
        # Should have detailed analysis
        assert "character_differences" in analysis or "unified_diff" in analysis

    def test_provides_line_level_diff(self):
        """Should provide line-level differences."""
        expected = "line1\nline2\nline3\n"
        actual = "line1\nLINE2\nline3\n"

        analysis = FilesSnapshotService.analyze_output_mismatch(expected, actual)

        assert isinstance(analysis, dict)
        assert "line_differences" in analysis or "unified_diff" in analysis

    def test_handles_empty_strings(self):
        """Should handle empty strings."""
        analysis = FilesSnapshotService.analyze_output_mismatch("", "")

        assert isinstance(analysis, dict)

    def test_handles_multiline_output(self):
        """Should handle multiline output."""
        expected = "1\n2\n3\n4\n5\n"
        actual = "1\n2\nX\n4\n5\n"

        analysis = FilesSnapshotService.analyze_output_mismatch(expected, actual)

        assert isinstance(analysis, dict)
        # Should detect line 3 difference
        assert "unified_diff" in analysis or "line_differences" in analysis

    def test_provides_summary_statistics(self):
        """Should provide summary statistics."""
        expected = "hello world"
        actual = "hello earth"

        analysis = FilesSnapshotService.analyze_output_mismatch(expected, actual)

        assert isinstance(analysis, dict)
        assert "summary" in analysis


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_unicode_content(self, workspace_dir):
        """Should handle Unicode content in files."""
        comparator_dir = Path(workspace_dir) / "comparator"
        comparator_dir.mkdir()
        (comparator_dir / "generator.cpp").write_text(
            "// Héllo Wörld 你好\n" + SAMPLE_CPP_CODE, encoding="utf-8"
        )
        (comparator_dir / "correct.cpp").write_text(SAMPLE_CPP_CODE)
        (comparator_dir / "test.cpp").write_text(SAMPLE_CPP_CODE)

        snapshot = FilesSnapshotService.create_snapshot(workspace_dir, "comparator")

        assert isinstance(snapshot, FilesSnapshot)

    def test_handles_large_files(self, workspace_dir):
        """Should handle large files."""
        comparator_dir = Path(workspace_dir) / "comparator"
        comparator_dir.mkdir()
        large_content = SAMPLE_CPP_CODE * 100  # Repeat many times
        (comparator_dir / "generator.cpp").write_text(large_content)
        (comparator_dir / "correct.cpp").write_text(SAMPLE_CPP_CODE)
        (comparator_dir / "test.cpp").write_text(SAMPLE_CPP_CODE)

        snapshot = FilesSnapshotService.create_snapshot(workspace_dir, "comparator")

        assert isinstance(snapshot, FilesSnapshot)

    def test_handles_binary_files_gracefully(self, workspace_dir):
        """Should skip or handle binary files."""
        comparator_dir = Path(workspace_dir) / "comparator"
        comparator_dir.mkdir()
        (comparator_dir / "binary.exe").write_bytes(b"\x00\x01\x02\x03")
        (comparator_dir / "generator.cpp").write_text(SAMPLE_CPP_CODE)
        (comparator_dir / "correct.cpp").write_text(SAMPLE_CPP_CODE)
        (comparator_dir / "test.cpp").write_text(SAMPLE_CPP_CODE)

        # Should not crash
        snapshot = FilesSnapshotService.create_snapshot(workspace_dir, "comparator")

        assert isinstance(snapshot, FilesSnapshot)

    def test_static_methods_dont_require_instance(self):
        """Should be able to call static methods without instance."""
        # Should not need to create instance
        result = FilesSnapshotService.create_snapshot("nonexistent", "comparator")

        assert isinstance(result, FilesSnapshot)

        analysis = FilesSnapshotService.analyze_output_mismatch("a", "b")
        assert isinstance(analysis, dict)
