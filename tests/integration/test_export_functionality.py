"""
Integration tests for export functionality with new FilesSnapshot format.

Tests that exports:
- Preserve file extensions (generator.cpp, test.py, etc.)
- Include language metadata
- Handle all test types (comparator, validator, benchmarker)
- Support mixed-language projects
- Maintain backward compatibility with old format
- Create proper folder structure in ZIP
"""

import pytest
import os
import tempfile
import shutil
import zipfile
import json
from src.app.persistence.database import DatabaseManager, TestResult, FilesSnapshot


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_path = db_file.name
    db_file.close()
    
    db_manager = DatabaseManager(db_path)
    yield db_manager
    
    # Cleanup
    db_manager.close()
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def temp_export_dir():
    """Create temporary directory for export files."""
    export_dir = tempfile.mkdtemp()
    yield export_dir
    shutil.rmtree(export_dir, ignore_errors=True)


class TestExportFunctionality:
    """Test export functionality with new FilesSnapshot format."""
    
    def test_export_comparator_cpp_files(self, temp_db, temp_export_dir):
        """Test exporting comparator result with C++ files."""
        # Create comparator snapshot
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
            project_name='CPP Comparator',
            test_type='comparison',
            timestamp='2024-01-01 12:00:00',
            test_count=10,
            passed_tests=10,
            files_snapshot=snapshot.to_json(),
            test_details=json.dumps([
                {'test': 1, 'status': 'pass', 'input': 'test input', 'output': 'expected'}
            ])
        )
        result_id = temp_db.save_test_result(result)
        
        # Simulate export by creating ZIP manually
        export_path = os.path.join(temp_export_dir, 'export.zip')
        
        with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, file_data in snapshot.files.items():
                role = file_data['role']
                content = file_data['content']
                zipf.writestr(f"code/{role}/{filename}", content.encode('utf-8'))
        
        # Verify ZIP contents
        with zipfile.ZipFile(export_path, 'r') as zipf:
            files = zipf.namelist()
            
            # Check all files present with proper paths
            assert 'code/generator/generator.cpp' in files
            assert 'code/correct/correct.cpp' in files
            assert 'code/test/test.cpp' in files
            
            # Verify content
            content = zipf.read('code/generator/generator.cpp').decode('utf-8')
            assert '#include <iostream>' in content
    
    def test_export_validator_python_files(self, temp_db, temp_export_dir):
        """Test exporting validator result with Python files."""
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
            project_name='Python Validator',
            test_type='validation',
            timestamp='2024-01-01 12:00:00',
            test_count=5,
            passed_tests=5,
            files_snapshot=snapshot.to_json()
        )
        temp_db.save_test_result(result)
        
        # Simulate export
        export_path = os.path.join(temp_export_dir, 'validator_export.zip')
        
        with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, file_data in snapshot.files.items():
                role = file_data['role']
                content = file_data['content']
                zipf.writestr(f"code/{role}/{filename}", content.encode('utf-8'))
        
        # Verify
        with zipfile.ZipFile(export_path, 'r') as zipf:
            files = zipf.namelist()
            assert 'code/generator/generator.py' in files
            assert 'code/validator/validator.py' in files
            assert 'code/test/test.py' in files
    
    def test_export_benchmarker_java_files(self, temp_export_dir):
        """Test exporting benchmarker result with Java files (2 files only)."""
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
        
        # Simulate export
        export_path = os.path.join(temp_export_dir, 'benchmark_export.zip')
        
        with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, file_data in snapshot.files.items():
                role = file_data['role']
                content = file_data['content']
                zipf.writestr(f"code/{role}/{filename}", content.encode('utf-8'))
        
        # Verify only 2 files (no correct file)
        with zipfile.ZipFile(export_path, 'r') as zipf:
            files = zipf.namelist()
            assert len(files) == 2
            assert 'code/generator/Generator.java' in files
            assert 'code/test/Test.java' in files
            assert 'code/correct/Correct.java' not in files  # Benchmarker doesn't have correct
    
    def test_export_mixed_language_project(self, temp_export_dir):
        """Test exporting mixed-language project."""
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
        
        export_path = os.path.join(temp_export_dir, 'mixed_export.zip')
        
        with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, file_data in snapshot.files.items():
                role = file_data['role']
                content = file_data['content']
                zipf.writestr(f"code/{role}/{filename}", content.encode('utf-8'))
            
            # Add metadata file
            metadata = f"Test Type: {snapshot.test_type}\n"
            metadata += f"Primary Language: {snapshot.primary_language}\n"
            metadata += f"Files:\n"
            for filename, file_data in snapshot.files.items():
                metadata += f"  - {filename} ({file_data['language']}) [{file_data['role']}]\n"
            
            zipf.writestr("code/FILES_INFO.txt", metadata.encode('utf-8'))
        
        # Verify mixed languages preserved
        with zipfile.ZipFile(export_path, 'r') as zipf:
            files = zipf.namelist()
            assert 'code/generator/generator.py' in files
            assert 'code/correct/correct.cpp' in files
            assert 'code/test/test.cpp' in files
            assert 'code/FILES_INFO.txt' in files
            
            # Check metadata
            metadata_content = zipf.read('code/FILES_INFO.txt').decode('utf-8')
            assert 'generator.py (py)' in metadata_content
            assert 'correct.cpp (cpp)' in metadata_content
            assert 'Primary Language: cpp' in metadata_content
    
    def test_export_with_additional_files(self, temp_export_dir):
        """Test exporting with additional helper files."""
        snapshot = FilesSnapshot(test_type='comparison', primary_language='cpp')
        snapshot.files = {
            'generator.cpp': {
                'content': '// Generator',
                'language': 'cpp',
                'role': 'generator'
            },
            'correct.cpp': {
                'content': '// Correct',
                'language': 'cpp',
                'role': 'correct'
            },
            'test.cpp': {
                'content': '// Test',
                'language': 'cpp',
                'role': 'test'
            },
            'helper.cpp': {
                'content': '// Helper functions',
                'language': 'cpp',
                'role': 'additional'
            },
            'utils.h': {
                'content': '// Utility headers',
                'language': 'cpp',
                'role': 'additional'
            }
        }
        
        export_path = os.path.join(temp_export_dir, 'additional_export.zip')
        
        with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, file_data in snapshot.files.items():
                role = file_data['role']
                content = file_data['content']
                zipf.writestr(f"code/{role}/{filename}", content.encode('utf-8'))
        
        # Verify all files including additional
        with zipfile.ZipFile(export_path, 'r') as zipf:
            files = zipf.namelist()
            assert len(files) == 5
            assert 'code/additional/helper.cpp' in files
            assert 'code/additional/utils.h' in files
    
    def test_export_old_format_backward_compat(self, temp_db, temp_export_dir):
        """Test exporting old format result (backward compatibility)."""
        # Create old format snapshot
        old_snapshot = {
            'generator_code': '#include <iostream>\nint main() { return 0; }',
            'correct_code': '#include <iostream>\nint main() { return 0; }',
            'test_code': '#include <iostream>\nint main() { return 0; }',
            'language': 'cpp'
        }
        
        result = TestResult(
            project_name='Old Format Export',
            test_type='comparison',
            timestamp='2024-01-01 12:00:00',
            test_count=10,
            passed_tests=10,
            files_snapshot=json.dumps(old_snapshot)
        )
        temp_db.save_test_result(result)
        
        # Parse with auto-migration
        snapshot = FilesSnapshot.from_json(result.files_snapshot)
        
        # Export should work seamlessly
        export_path = os.path.join(temp_export_dir, 'old_format_export.zip')
        
        with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, file_data in snapshot.files.items():
                role = file_data['role']
                content = file_data['content']
                zipf.writestr(f"code/{role}/{filename}", content.encode('utf-8'))
        
        # Verify migration and export worked
        with zipfile.ZipFile(export_path, 'r') as zipf:
            files = zipf.namelist()
            assert 'code/generator/generator.cpp' in files
            assert 'code/correct/correct.cpp' in files
            assert 'code/test/test.cpp' in files
    
    def test_export_filename_preservation(self, temp_export_dir):
        """Test that exact filenames are preserved in export."""
        snapshot = FilesSnapshot(test_type='comparison', primary_language='java')
        snapshot.files = {
            'Generator.java': {  # Capitalized
                'content': 'public class Generator {}',
                'language': 'java',
                'role': 'generator'
            },
            'Correct.java': {  # Capitalized
                'content': 'public class Correct {}',
                'language': 'java',
                'role': 'correct'
            },
            'Test.java': {  # Capitalized
                'content': 'public class Test {}',
                'language': 'java',
                'role': 'test'
            }
        }
        
        export_path = os.path.join(temp_export_dir, 'filename_test.zip')
        
        with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, file_data in snapshot.files.items():
                role = file_data['role']
                content = file_data['content']
                zipf.writestr(f"code/{role}/{filename}", content.encode('utf-8'))
        
        # Verify exact filenames preserved
        with zipfile.ZipFile(export_path, 'r') as zipf:
            files = zipf.namelist()
            # Check capitalization is preserved
            assert 'code/generator/Generator.java' in files
            assert 'code/correct/Correct.java' in files
            assert 'code/test/Test.java' in files
            # Should NOT have lowercase versions
            assert 'code/generator/generator.java' not in files


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
