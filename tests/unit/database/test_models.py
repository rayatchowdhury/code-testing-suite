"""
Unit tests for database models.

Tests model serialization, validation, and JSON conversion.
Tests both new format and backward compatibility with old format.
"""

import pytest
import json
from src.app.persistence.database.models import (
    FilesSnapshot,
    TestResult,
    Session,
    ProjectData,
)


class TestFilesSnapshotSerialization:
    """Test FilesSnapshot serialization and deserialization."""

    def test_to_json_serializes_correctly(self):
        """Should serialize FilesSnapshot to JSON."""
        snapshot = FilesSnapshot(
            files={
                "generator.py": {
                    "content": "import random\nprint(random.randint(1, 100))",
                    "language": "py",
                    "role": "generator",
                },
                "test.cpp": {
                    "content": "#include <iostream>\nint main() { return 0; }",
                    "language": "cpp",
                    "role": "test",
                },
            },
            test_type="comparison",
            primary_language="py",
        )

        json_str = snapshot.to_json()

        # Should be valid JSON
        data = json.loads(json_str)
        assert "files" in data
        assert "test_type" in data
        assert "primary_language" in data
        assert data["test_type"] == "comparison"
        assert data["primary_language"] == "py"
        assert len(data["files"]) == 2

    def test_from_json_deserializes_new_format(self):
        """Should deserialize new format FilesSnapshot from JSON."""
        json_str = json.dumps(
            {
                "files": {
                    "generator.cpp": {
                        "content": "int main() { return 0; }",
                        "language": "cpp",
                        "role": "generator",
                    }
                },
                "test_type": "benchmark",
                "primary_language": "cpp",
            }
        )

        snapshot = FilesSnapshot.from_json(json_str)

        assert len(snapshot.files) == 1
        assert "generator.cpp" in snapshot.files
        assert snapshot.files["generator.cpp"]["content"] == "int main() { return 0; }"
        assert snapshot.files["generator.cpp"]["language"] == "cpp"
        assert snapshot.files["generator.cpp"]["role"] == "generator"
        assert snapshot.test_type == "benchmark"
        assert snapshot.primary_language == "cpp"

    def test_from_json_handles_empty_string(self):
        """Should handle empty JSON string gracefully."""
        snapshot = FilesSnapshot.from_json("")

        assert snapshot is not None
        assert len(snapshot.files) == 0
        assert snapshot.test_type == ""
        assert snapshot.primary_language == "cpp"

    def test_from_json_handles_invalid_json(self):
        """Should handle invalid JSON gracefully."""
        snapshot = FilesSnapshot.from_json("not valid json {{{")

        assert snapshot is not None
        assert len(snapshot.files) == 0


class TestFilesSnapshotBackwardCompatibility:
    """Test backward compatibility with old FilesSnapshot format."""

    def test_migrates_old_format_cpp(self):
        """Should migrate old format with C++ files."""
        old_json = json.dumps(
            {
                "generator_code": "#include <iostream>\nint main() { return 0; }",
                "correct_code": "#include <iostream>\nint main() { std::cout << 42; }",
                "test_code": "#include <iostream>\nint main() { std::cout << 0; }",
            }
        )

        snapshot = FilesSnapshot.from_json(old_json)

        # Should have migrated to new format
        assert len(snapshot.files) == 3
        assert "generator.cpp" in snapshot.files
        assert "correct.cpp" in snapshot.files
        assert "test.cpp" in snapshot.files

        # Should preserve content
        assert "#include <iostream>" in snapshot.files["generator.cpp"]["content"]

        # Should detect language
        assert snapshot.files["generator.cpp"]["language"] == "cpp"
        assert snapshot.primary_language == "cpp"

    def test_migrates_old_format_python(self):
        """Should migrate old format with Python files."""
        old_json = json.dumps(
            {
                "generator_code": "import random\nprint(random.randint(1, 100))",
                "test_code": "def solve():\n    return 42",
                "validator_code": "def validate(input, output):\n    return True",
            }
        )

        snapshot = FilesSnapshot.from_json(old_json)

        # Should detect Python and use .py extension
        assert "generator.py" in snapshot.files
        assert "test.py" in snapshot.files
        assert "validator.py" in snapshot.files

        # Should detect Python language
        assert snapshot.files["generator.py"]["language"] == "py"
        assert snapshot.primary_language == "py"

    def test_migrates_old_format_java(self):
        """Should migrate old format with Java files and proper capitalization."""
        old_json = json.dumps(
            {
                "generator_code": "public class Main { public static void main(String[] args) {} }",
                "correct_code": "import java.util.*;\npublic class Solution {}",
            }
        )

        snapshot = FilesSnapshot.from_json(old_json)

        # Java files should be capitalized
        assert "Generator.java" in snapshot.files
        assert "Correct.java" in snapshot.files

        # Should detect Java language
        assert snapshot.files["Generator.java"]["language"] == "java"
        assert snapshot.primary_language == "java"

    def test_migrates_old_format_with_additional_files(self):
        """Should migrate old format including additional_files."""
        old_json = json.dumps(
            {
                "generator_code": "int main() { return 0; }",
                "additional_files": {
                    "helper.cpp": "#include <vector>\nvector<int> helpers;",
                    "utils.py": "def helper():\n    pass",
                },
            }
        )

        snapshot = FilesSnapshot.from_json(old_json)

        # Should include additional files
        assert "generator.cpp" in snapshot.files
        assert "helper.cpp" in snapshot.files
        assert "utils.py" in snapshot.files

        # Should detect languages from extensions
        assert snapshot.files["helper.cpp"]["language"] == "cpp"
        assert snapshot.files["utils.py"]["language"] == "py"


class TestFilesSnapshotLanguageDetection:
    """Test language detection logic."""

    def test_detects_python_from_content(self):
        """Should detect Python from content patterns."""
        snapshot = FilesSnapshot()

        # Test various Python patterns
        assert snapshot._detect_language_from_content("def main():\n    pass") == "py"
        assert (
            snapshot._detect_language_from_content("import sys\nprint('hello')") == "py"
        )
        assert snapshot._detect_language_from_content("x = 5\nprint(x)") == "py"

    def test_detects_java_from_content(self):
        """Should detect Java from content patterns."""
        snapshot = FilesSnapshot()

        # Test various Java patterns
        assert snapshot._detect_language_from_content("public class Main {}") == "java"
        assert snapshot._detect_language_from_content("import java.util.*;") == "java"
        assert snapshot._detect_language_from_content("System.out.println();") == "java"

    def test_detects_cpp_as_default(self):
        """Should detect C++ as default for non-specific code."""
        snapshot = FilesSnapshot()

        # Test C++ patterns and fallback
        assert snapshot._detect_language_from_content("#include <iostream>") == "cpp"
        assert (
            snapshot._detect_language_from_content("int main() { return 0; }") == "cpp"
        )

    def test_detects_language_from_extension(self):
        """Should detect language from file extension."""
        snapshot = FilesSnapshot()

        assert snapshot._detect_language_from_extension("test.py") == "py"
        assert snapshot._detect_language_from_extension("Test.java") == "java"
        assert snapshot._detect_language_from_extension("main.cpp") == "cpp"
        assert snapshot._detect_language_from_extension("main.h") == "cpp"  # Default


class TestFilesSnapshotFilenameGeneration:
    """Test filename generation with proper capitalization."""

    def test_generates_cpp_filenames(self):
        """Should generate C++ filenames correctly."""
        snapshot = FilesSnapshot()

        assert snapshot._generate_filename("generator", "cpp") == "generator.cpp"
        assert snapshot._generate_filename("test", "cpp") == "test.cpp"
        assert snapshot._generate_filename("correct", "cpp") == "correct.cpp"

    def test_generates_python_filenames(self):
        """Should generate Python filenames correctly."""
        snapshot = FilesSnapshot()

        assert snapshot._generate_filename("generator", "py") == "generator.py"
        assert snapshot._generate_filename("validator", "py") == "validator.py"

    def test_generates_java_filenames_with_capitalization(self):
        """Should generate Java filenames with proper capitalization."""
        snapshot = FilesSnapshot()

        assert snapshot._generate_filename("generator", "java") == "Generator.java"
        assert snapshot._generate_filename("correct", "java") == "Correct.java"
        assert snapshot._generate_filename("test", "java") == "Test.java"
        assert snapshot._generate_filename("validator", "java") == "Validator.java"


class TestTestResultModel:
    """Test TestResult dataclass."""

    def test_creates_with_defaults(self):
        """Should create TestResult with default values."""
        result = TestResult()

        assert result.id is None
        assert result.test_type == ""
        assert result.file_path == ""
        assert result.test_count == 0
        assert result.passed_tests == 0
        assert result.failed_tests == 0
        assert result.total_time == 0.0
        assert result.timestamp == ""

    def test_creates_with_values(self):
        """Should create TestResult with provided values."""
        result = TestResult(
            id=1,
            test_type="comparison",
            file_path="/path/to/test.cpp",
            test_count=10,
            passed_tests=8,
            failed_tests=2,
            total_time=5.5,
            timestamp="2024-01-01 12:00:00",
            test_details='{"test1": "passed"}',
            project_name="MyProject",
            files_snapshot='{"files": {}}',
            mismatch_analysis='{"analysis": "data"}',
        )

        assert result.id == 1
        assert result.test_type == "comparison"
        assert result.test_count == 10
        assert result.passed_tests == 8
        assert result.failed_tests == 2


class TestSessionModel:
    """Test Session dataclass."""

    def test_creates_with_defaults(self):
        """Should create Session with default values."""
        session = Session()

        assert session.id is None
        assert session.session_name == ""
        assert session.open_files == ""
        assert session.active_file == ""
        assert session.timestamp == ""
        assert session.project_name == ""

    def test_creates_with_values(self):
        """Should create Session with provided values."""
        session = Session(
            id=1,
            session_name="Test Session",
            open_files='["file1.cpp", "file2.cpp"]',
            active_file="file1.cpp",
            timestamp="2024-01-01 12:00:00",
            project_name="MyProject",
        )

        assert session.id == 1
        assert session.session_name == "Test Session"
        assert "file1.cpp" in session.open_files


class TestProjectDataModel:
    """Test ProjectData dataclass."""

    def test_creates_with_defaults(self):
        """Should create ProjectData with default values."""
        project = ProjectData()

        assert project.id is None
        assert project.project_name == ""
        assert project.project_path == ""
        assert project.last_accessed == ""
        assert project.file_count == 0
        assert project.total_lines == 0
        assert project.languages == ""

    def test_creates_with_values(self):
        """Should create ProjectData with provided values."""
        project = ProjectData(
            id=1,
            project_name="MyProject",
            project_path="/path/to/project",
            last_accessed="2024-01-01",
            file_count=5,
            total_lines=1000,
            languages='["cpp", "py"]',
        )

        assert project.id == 1
        assert project.project_name == "MyProject"
        assert project.file_count == 5
        assert project.total_lines == 1000
