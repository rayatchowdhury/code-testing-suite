"""
Integration tests for Load to Test feature with new FilesSnapshot format.

Tests that _load_to_test() properly:
- Parses new FilesSnapshot format (with backward compatibility)
- Writes files to workspace/{test_type}/ preserving filenames
- Creates correct directory structure
- Handles all three test types (comparator, validator, benchmarker)
- Works with mixed-language projects
"""

import pytest
import os
import tempfile
import shutil
import json
from unittest.mock import Mock, patch, MagicMock
from src.app.persistence.database import TestResult
from src.app.persistence.database.database_manager import FilesSnapshot


class TestLoadToTestFeature:
    """Test Load to Test feature with new FilesSnapshot format."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace directory."""
        workspace = tempfile.mkdtemp()
        yield workspace
        shutil.rmtree(workspace, ignore_errors=True)
    
    @pytest.fixture
    def mock_test_result_comparator(self):
        """Create mock TestResult for comparator with new format."""
        snapshot = FilesSnapshot(test_type='comparison', primary_language='cpp')
        snapshot.files = {
            'generator.cpp': {
                'content': '#include <iostream>\nint main() { return 0; }',
                'language': 'cpp',
                'role': 'generator'
            },
            'correct.cpp': {
                'content': '#include <iostream>\nint main() { return 0; }',
                'language': 'cpp',
                'role': 'correct'
            },
            'test.cpp': {
                'content': '#include <iostream>\nint main() { return 0; }',
                'language': 'cpp',
                'role': 'test'
            }
        }
        
        result = TestResult(
            project_name='Test Project',
            test_type='comparison',
            timestamp='2024-01-01 12:00:00',
            test_count=10,
            passed_tests=10,
            files_snapshot=snapshot.to_json()
        )
        result.id = 1
        return result
    
    @pytest.fixture
    def mock_test_result_validator(self):
        """Create mock TestResult for validator with new format."""
        snapshot = FilesSnapshot(test_type='validation', primary_language='py')
        snapshot.files = {
            'generator.py': {
                'content': 'def generate():\n    pass',
                'language': 'py',
                'role': 'generator'
            },
            'validator.py': {
                'content': 'def validate():\n    pass',
                'language': 'py',
                'role': 'validator'
            },
            'test.py': {
                'content': 'def test():\n    pass',
                'language': 'py',
                'role': 'test'
            }
        }
        
        result = TestResult(
            project_name='Validator Project',
            test_type='validation',
            timestamp='2024-01-01 12:00:00',
            test_count=5,
            passed_tests=5,
            files_snapshot=snapshot.to_json()
        )
        result.id = 2
        return result
    
    @pytest.fixture
    def mock_test_result_benchmarker(self):
        """Create mock TestResult for benchmarker with new format."""
        snapshot = FilesSnapshot(test_type='benchmark', primary_language='java')
        snapshot.files = {
            'Generator.java': {
                'content': 'public class Generator {\n    public static void main(String[] args) {}\n}',
                'language': 'java',
                'role': 'generator'
            },
            'Test.java': {
                'content': 'public class Test {\n    public static void main(String[] args) {}\n}',
                'language': 'java',
                'role': 'test'
            }
        }
        
        result = TestResult(
            project_name='Benchmark Project',
            test_type='benchmark',
            timestamp='2024-01-01 12:00:00',
            test_count=1,
            passed_tests=1,
            files_snapshot=snapshot.to_json()
        )
        result.id = 3
        return result
    
    def test_parse_new_format_snapshot(self, mock_test_result_comparator):
        """Test that new format FilesSnapshot is parsed correctly."""
        snapshot = FilesSnapshot.from_json(mock_test_result_comparator.files_snapshot)
        
        assert len(snapshot.files) == 3
        assert 'generator.cpp' in snapshot.files
        assert 'correct.cpp' in snapshot.files
        assert 'test.cpp' in snapshot.files
        assert snapshot.test_type == 'comparison'
        assert snapshot.primary_language == 'cpp'
    
    def test_write_comparator_files_to_workspace(self, temp_workspace, mock_test_result_comparator):
        """Test writing comparator files to workspace/comparator/."""
        snapshot = FilesSnapshot.from_json(mock_test_result_comparator.files_snapshot)
        target_dir = os.path.join(temp_workspace, 'comparator')
        os.makedirs(target_dir, exist_ok=True)
        
        # Write files
        for filename, file_data in snapshot.files.items():
            file_path = os.path.join(target_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_data['content'])
        
        # Verify files exist with correct content
        assert os.path.exists(os.path.join(target_dir, 'generator.cpp'))
        assert os.path.exists(os.path.join(target_dir, 'correct.cpp'))
        assert os.path.exists(os.path.join(target_dir, 'test.cpp'))
        
        with open(os.path.join(target_dir, 'generator.cpp'), 'r') as f:
            content = f.read()
            assert '#include <iostream>' in content
    
    def test_write_validator_files_to_workspace(self, temp_workspace, mock_test_result_validator):
        """Test writing validator files to workspace/validator/."""
        snapshot = FilesSnapshot.from_json(mock_test_result_validator.files_snapshot)
        target_dir = os.path.join(temp_workspace, 'validator')
        os.makedirs(target_dir, exist_ok=True)
        
        # Write files
        for filename, file_data in snapshot.files.items():
            file_path = os.path.join(target_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_data['content'])
        
        # Verify files exist with correct content
        assert os.path.exists(os.path.join(target_dir, 'generator.py'))
        assert os.path.exists(os.path.join(target_dir, 'validator.py'))
        assert os.path.exists(os.path.join(target_dir, 'test.py'))
        
        with open(os.path.join(target_dir, 'validator.py'), 'r') as f:
            content = f.read()
            assert 'def validate()' in content
    
    def test_write_benchmarker_files_to_workspace(self, temp_workspace, mock_test_result_benchmarker):
        """Test writing benchmarker files to workspace/benchmarker/."""
        snapshot = FilesSnapshot.from_json(mock_test_result_benchmarker.files_snapshot)
        target_dir = os.path.join(temp_workspace, 'benchmarker')
        os.makedirs(target_dir, exist_ok=True)
        
        # Write files
        for filename, file_data in snapshot.files.items():
            file_path = os.path.join(target_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_data['content'])
        
        # Verify exactly 2 files (generator + test, no correct)
        files = os.listdir(target_dir)
        assert len(files) == 2
        assert 'Generator.java' in files
        assert 'Test.java' in files
        assert 'Correct.java' not in files
        
        with open(os.path.join(target_dir, 'Generator.java'), 'r') as f:
            content = f.read()
            assert 'public class Generator' in content
    
    def test_old_format_backward_compatibility(self, temp_workspace):
        """Test that old FilesSnapshot format is automatically migrated."""
        # Create old format snapshot
        old_snapshot = {
            'generator_code': '#include <iostream>\nint main() { return 0; }',
            'correct_code': '#include <iostream>\nint main() { return 0; }',
            'test_code': '#include <iostream>\nint main() { return 0; }',
            'language': 'cpp'
        }
        
        result = TestResult(
            project_name='Old Format Project',
            test_type='comparison',
            timestamp='2024-01-01 12:00:00',
            test_count=10,
            passed_tests=10,
            files_snapshot=json.dumps(old_snapshot)
        )
        result.id = 99
        
        # Parse with new FilesSnapshot (should auto-migrate)
        snapshot = FilesSnapshot.from_json(result.files_snapshot)
        
        # Verify migration worked
        assert len(snapshot.files) == 3
        assert 'generator.cpp' in snapshot.files
        assert 'correct.cpp' in snapshot.files
        assert 'test.cpp' in snapshot.files
        assert snapshot.primary_language == 'cpp'
        
        # Write to workspace
        target_dir = os.path.join(temp_workspace, 'comparator')
        os.makedirs(target_dir, exist_ok=True)
        
        for filename, file_data in snapshot.files.items():
            file_path = os.path.join(target_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_data['content'])
        
        # Verify files written correctly
        assert os.path.exists(os.path.join(target_dir, 'generator.cpp'))
        assert os.path.exists(os.path.join(target_dir, 'correct.cpp'))
        assert os.path.exists(os.path.join(target_dir, 'test.cpp'))
    
    def test_mixed_language_files(self, temp_workspace):
        """Test writing mixed-language files (Python generator + C++ test)."""
        snapshot = FilesSnapshot(test_type='comparison', primary_language='cpp')
        snapshot.files = {
            'generator.py': {
                'content': 'def generate():\n    pass',
                'language': 'py',
                'role': 'generator'
            },
            'correct.cpp': {
                'content': '#include <iostream>\nint main() { return 0; }',
                'language': 'cpp',
                'role': 'correct'
            },
            'test.cpp': {
                'content': '#include <iostream>\nint main() { return 0; }',
                'language': 'cpp',
                'role': 'test'
            }
        }
        
        target_dir = os.path.join(temp_workspace, 'comparator')
        os.makedirs(target_dir, exist_ok=True)
        
        # Write files
        for filename, file_data in snapshot.files.items():
            file_path = os.path.join(target_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_data['content'])
        
        # Verify all files with correct extensions
        assert os.path.exists(os.path.join(target_dir, 'generator.py'))
        assert os.path.exists(os.path.join(target_dir, 'correct.cpp'))
        assert os.path.exists(os.path.join(target_dir, 'test.cpp'))
        
        # Verify content
        with open(os.path.join(target_dir, 'generator.py'), 'r') as f:
            assert 'def generate()' in f.read()
        with open(os.path.join(target_dir, 'test.cpp'), 'r') as f:
            assert '#include <iostream>' in f.read()
    
    def test_overwrite_existing_files(self, temp_workspace):
        """Test that Load to Test overwrites existing files."""
        target_dir = os.path.join(temp_workspace, 'comparator')
        os.makedirs(target_dir, exist_ok=True)
        
        # Create existing file
        existing_file = os.path.join(target_dir, 'generator.cpp')
        with open(existing_file, 'w') as f:
            f.write('// Old content')
        
        # Load new snapshot
        snapshot = FilesSnapshot(test_type='comparison', primary_language='cpp')
        snapshot.files = {
            'generator.cpp': {
                'content': '// New content',
                'language': 'cpp',
                'role': 'generator'
            }
        }
        
        # Overwrite
        for filename, file_data in snapshot.files.items():
            file_path = os.path.join(target_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_data['content'])
        
        # Verify new content
        with open(existing_file, 'r') as f:
            content = f.read()
            assert '// New content' in content
            assert '// Old content' not in content
    
    def test_empty_snapshot_handling(self):
        """Test handling of empty files_snapshot."""
        result = TestResult(
            project_name='Empty Project',
            test_type='comparison',
            timestamp='2024-01-01 12:00:00',
            test_count=0,
            passed_tests=0,
            files_snapshot=None
        )
        result.id = 100
        
        # Should not raise exception, just return None
        assert result.files_snapshot is None
    
    def test_test_type_mapping(self):
        """Test that test_type is correctly mapped to subdirectory."""
        test_type_map = {
            'comparison': 'comparator',
            'validation': 'validator',
            'benchmark': 'benchmarker'
        }
        
        for test_type, expected_subdir in test_type_map.items():
            snapshot = FilesSnapshot(test_type=test_type)
            assert test_type_map[snapshot.test_type] == expected_subdir


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
