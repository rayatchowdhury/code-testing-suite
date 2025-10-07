"""
Test database models in isolation.

Phase 1: Testing models.py after extraction from database_manager.py
"""
import pytest
import json
from src.app.persistence.database.models import FilesSnapshot, TestResult, Session, ProjectData


class TestFilesSnapshot:
    """Test FilesSnapshot model"""
    
    def test_files_snapshot_new_format(self):
        """Test FilesSnapshot with new format."""
        snapshot = FilesSnapshot(
            files={
                "test.cpp": {
                    "content": "int main(){}",
                    "language": "cpp",
                    "role": "test"
                }
            },
            test_type="comparison",
            primary_language="cpp"
        )
        
        # Serialize and deserialize
        json_str = snapshot.to_json()
        restored = FilesSnapshot.from_json(json_str)
        
        assert restored.files == snapshot.files
        assert restored.test_type == snapshot.test_type
        assert restored.primary_language == snapshot.primary_language
    
    def test_files_snapshot_old_format_migration(self):
        """Test FilesSnapshot migrates old format."""
        old_format = json.dumps({
            "generator_code": "int main(){}",
            "test_code": "test code"
        })
        snapshot = FilesSnapshot.from_json(old_format)
        
        # Should migrate to new format with files dict
        assert len(snapshot.files) >= 1
        assert any('generator' in filename for filename in snapshot.files.keys())
        
        # Should be able to serialize back
        json_str = snapshot.to_json()
        assert 'files' in json_str
    
    def test_files_snapshot_empty_json(self):
        """Test FilesSnapshot handles empty JSON."""
        snapshot = FilesSnapshot.from_json("")
        assert snapshot.files == {}
        assert snapshot.test_type == ""
        assert snapshot.primary_language == "cpp"
    
    def test_files_snapshot_with_python_code(self):
        """Test FilesSnapshot detects Python language."""
        old_format = json.dumps({
            "generator_code": "def main():\n    print('hello')",
            "test_code": "import sys"
        })
        snapshot = FilesSnapshot.from_json(old_format)
        
        # Should detect Python and use .py extension
        assert any(filename.endswith('.py') for filename in snapshot.files.keys())
        assert any(f['language'] == 'py' for f in snapshot.files.values())
    
    def test_files_snapshot_with_java_code(self):
        """Test FilesSnapshot detects Java language."""
        old_format = json.dumps({
            "generator_code": "public class Generator { }",
            "test_code": "System.out.println();"
        })
        snapshot = FilesSnapshot.from_json(old_format)
        
        # Should detect Java and use .java extension with capitalization
        assert any(filename.endswith('.java') for filename in snapshot.files.keys())
        assert any(f['language'] == 'java' for f in snapshot.files.values())
        
        # Java files should be capitalized
        assert any(filename[0].isupper() for filename in snapshot.files.keys() if filename.endswith('.java'))


class TestTestResult:
    """Test TestResult model"""
    
    def test_test_result_creation(self):
        """Test TestResult can be created."""
        result = TestResult(
            test_type="comparison",
            file_path="/test/file.cpp",
            test_count=10,
            passed_tests=8,
            failed_tests=2
        )
        
        assert result.test_type == "comparison"
        assert result.passed_tests == 8
        assert result.failed_tests == 2
        assert result.test_count == 10
    
    def test_test_result_defaults(self):
        """Test TestResult default values."""
        result = TestResult()
        
        assert result.id is None
        assert result.test_type == ""
        assert result.test_count == 0
        assert result.passed_tests == 0
        assert result.total_time == 0.0
    
    def test_test_result_with_all_fields(self):
        """Test TestResult with all fields populated."""
        result = TestResult(
            id=1,
            test_type="benchmark",
            file_path="/path/to/test.py",
            test_count=100,
            passed_tests=95,
            failed_tests=5,
            total_time=12.5,
            timestamp="2025-10-08",
            test_details='{"details": "test"}',
            project_name="MyProject",
            files_snapshot='{"files": {}}',
            mismatch_analysis='{"analysis": "data"}'
        )
        
        assert result.id == 1
        assert result.test_type == "benchmark"
        assert result.test_count == 100
        assert result.project_name == "MyProject"


class TestSession:
    """Test Session model"""
    
    def test_session_creation(self):
        """Test Session can be created."""
        session = Session(
            session_name="Test Session",
            open_files='["file1.cpp", "file2.py"]',
            active_file="file1.cpp",
            timestamp="2025-10-08",
            project_name="TestProject"
        )
        
        assert session.session_name == "Test Session"
        assert session.active_file == "file1.cpp"
        assert session.project_name == "TestProject"
    
    def test_session_defaults(self):
        """Test Session default values."""
        session = Session()
        
        assert session.id is None
        assert session.session_name == ""
        assert session.open_files == ""


class TestProjectData:
    """Test ProjectData model"""
    
    def test_project_data_creation(self):
        """Test ProjectData can be created."""
        project = ProjectData(
            project_name="MyProject",
            project_path="/path/to/project",
            last_accessed="2025-10-08",
            file_count=25,
            total_lines=1500,
            languages='["cpp", "py"]'
        )
        
        assert project.project_name == "MyProject"
        assert project.file_count == 25
        assert project.total_lines == 1500
    
    def test_project_data_defaults(self):
        """Test ProjectData default values."""
        project = ProjectData()
        
        assert project.id is None
        assert project.project_name == ""
        assert project.file_count == 0
        assert project.total_lines == 0
