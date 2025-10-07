"""
Test suite for create_files_snapshot() with test type filtering.

Tests that the function:
- Only saves files relevant to the test type
- Stores full filenames with extensions
- Detects languages correctly per file
- Handles mixed-language projects
- Includes additional helper files
"""

import pytest
import os
import tempfile
import shutil
from src.app.persistence.database.database_manager import DatabaseManager, FilesSnapshot


class TestCreateFilesSnapshotFiltering:
    """Test create_files_snapshot() filters files by test type"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace with nested structure"""
        workspace = tempfile.mkdtemp()
        
        # Create comparator directory
        comparator_dir = os.path.join(workspace, 'comparator')
        os.makedirs(comparator_dir)
        os.makedirs(os.path.join(comparator_dir, 'inputs'))
        os.makedirs(os.path.join(comparator_dir, 'outputs'))
        
        # Create validator directory
        validator_dir = os.path.join(workspace, 'validator')
        os.makedirs(validator_dir)
        os.makedirs(os.path.join(validator_dir, 'inputs'))
        os.makedirs(os.path.join(validator_dir, 'outputs'))
        
        # Create benchmarker directory
        benchmarker_dir = os.path.join(workspace, 'benchmarker')
        os.makedirs(benchmarker_dir)
        os.makedirs(os.path.join(benchmarker_dir, 'inputs'))
        os.makedirs(os.path.join(benchmarker_dir, 'outputs'))
        
        yield workspace
        
        # Cleanup
        shutil.rmtree(workspace)
    
    def test_comparator_saves_3_files_cpp(self, temp_workspace):
        """Test comparator saves only generator, correct, test (C++)"""
        comparator_dir = os.path.join(temp_workspace, 'comparator')
        
        # Create files
        with open(os.path.join(comparator_dir, 'generator.cpp'), 'w') as f:
            f.write('#include <iostream>\nint main() { return 0; }')
        
        with open(os.path.join(comparator_dir, 'correct.cpp'), 'w') as f:
            f.write('#include <iostream>\nint solve() { return 42; }')
        
        with open(os.path.join(comparator_dir, 'test.cpp'), 'w') as f:
            f.write('#include <iostream>\nvoid test() {}')
        
        # Create extra file that shouldn't be saved
        with open(os.path.join(comparator_dir, 'validator.cpp'), 'w') as f:
            f.write('// Validator not needed for comparator')
        
        # Create snapshot
        snapshot = DatabaseManager.create_files_snapshot(temp_workspace, 'comparison')
        
        # Should have exactly 3 files
        assert len(snapshot.files) == 3
        assert 'generator.cpp' in snapshot.files
        assert 'correct.cpp' in snapshot.files
        assert 'test.cpp' in snapshot.files
        assert 'validator.cpp' not in snapshot.files  # Should be filtered out
        
        # Verify metadata
        assert snapshot.test_type == 'comparison'
        assert snapshot.primary_language == 'cpp'
        assert snapshot.files['generator.cpp']['language'] == 'cpp'
        assert snapshot.files['generator.cpp']['role'] == 'generator'
    
    def test_validator_saves_3_files_python(self, temp_workspace):
        """Test validator saves only generator, validator, test (Python)"""
        validator_dir = os.path.join(temp_workspace, 'validator')
        
        # Create files
        with open(os.path.join(validator_dir, 'generator.py'), 'w') as f:
            f.write('import random\ndef generate(): pass')
        
        with open(os.path.join(validator_dir, 'validator.py'), 'w') as f:
            f.write('def validate(): pass')
        
        with open(os.path.join(validator_dir, 'test.py'), 'w') as f:
            f.write('def test(): pass')
        
        # Create extra file that shouldn't be saved
        with open(os.path.join(validator_dir, 'correct.py'), 'w') as f:
            f.write('# Correct not needed for validator')
        
        # Create snapshot
        snapshot = DatabaseManager.create_files_snapshot(temp_workspace, 'validation')
        
        # Should have exactly 3 files
        assert len(snapshot.files) == 3
        assert 'generator.py' in snapshot.files
        assert 'validator.py' in snapshot.files
        assert 'test.py' in snapshot.files
        assert 'correct.py' not in snapshot.files  # Should be filtered out
        
        # Verify metadata
        assert snapshot.test_type == 'validation'
        assert snapshot.primary_language == 'py'
        assert snapshot.files['validator.py']['role'] == 'validator'
    
    def test_benchmarker_saves_2_files_java(self, temp_workspace):
        """Test benchmarker saves only generator, test (Java)"""
        benchmarker_dir = os.path.join(temp_workspace, 'benchmarker')
        
        # Create files
        with open(os.path.join(benchmarker_dir, 'Generator.java'), 'w') as f:
            f.write('public class Generator {}')
        
        with open(os.path.join(benchmarker_dir, 'Test.java'), 'w') as f:
            f.write('public class Test {}')
        
        # Create extra files that shouldn't be saved
        with open(os.path.join(benchmarker_dir, 'Correct.java'), 'w') as f:
            f.write('// Correct not needed for benchmarker')
        
        with open(os.path.join(benchmarker_dir, 'Validator.java'), 'w') as f:
            f.write('// Validator not needed for benchmarker')
        
        # Create snapshot
        snapshot = DatabaseManager.create_files_snapshot(temp_workspace, 'benchmark')
        
        # Should have exactly 2 files
        assert len(snapshot.files) == 2
        assert 'Generator.java' in snapshot.files
        assert 'Test.java' in snapshot.files
        assert 'Correct.java' not in snapshot.files  # Should be filtered out
        assert 'Validator.java' not in snapshot.files  # Should be filtered out
        
        # Verify metadata
        assert snapshot.test_type == 'benchmark'
        assert snapshot.primary_language == 'java'
        assert snapshot.files['Generator.java']['role'] == 'generator'
        assert snapshot.files['Test.java']['role'] == 'test'
    
    def test_mixed_language_support(self, temp_workspace):
        """Test snapshot with mixed languages (generator.py, correct.cpp, test.java)"""
        comparator_dir = os.path.join(temp_workspace, 'comparator')
        
        # Create files with different languages
        with open(os.path.join(comparator_dir, 'generator.py'), 'w') as f:
            f.write('import random\nprint("Python generator")')
        
        with open(os.path.join(comparator_dir, 'correct.cpp'), 'w') as f:
            f.write('#include <iostream>\nint main() {}')
        
        with open(os.path.join(comparator_dir, 'Test.java'), 'w') as f:
            f.write('public class Test {}')
        
        # Create snapshot
        snapshot = DatabaseManager.create_files_snapshot(temp_workspace, 'comparison')
        
        # Should have all 3 files
        assert len(snapshot.files) == 3
        
        # Verify each file has correct language
        assert snapshot.files['generator.py']['language'] == 'py'
        assert snapshot.files['correct.cpp']['language'] == 'cpp'
        assert snapshot.files['Test.java']['language'] == 'java'
        
        # Primary language should be most common (all 1 each, defaults to cpp)
        assert snapshot.primary_language in ['cpp', 'py', 'java']
    
    def test_additional_files_excluded(self, temp_workspace):
        """Test that only required files are included, not additional workspace files"""
        comparator_dir = os.path.join(temp_workspace, 'comparator')
        
        # Create main files
        with open(os.path.join(comparator_dir, 'generator.cpp'), 'w') as f:
            f.write('int main() {}')
        
        with open(os.path.join(comparator_dir, 'correct.cpp'), 'w') as f:
            f.write('int solve() {}')
        
        with open(os.path.join(comparator_dir, 'test.cpp'), 'w') as f:
            f.write('void test() {}')
        
        # Create additional files that should be excluded
        with open(os.path.join(comparator_dir, 'helper.cpp'), 'w') as f:
            f.write('// Helper functions')
        
        with open(os.path.join(comparator_dir, 'utils.py'), 'w') as f:
            f.write('# Utility functions')
        
        # Create snapshot
        snapshot = DatabaseManager.create_files_snapshot(temp_workspace, 'comparison')
        
        # Should have only 3 required files (no additional files)
        assert len(snapshot.files) == 3
        assert 'generator.cpp' in snapshot.files
        assert 'correct.cpp' in snapshot.files
        assert 'test.cpp' in snapshot.files
        assert 'helper.cpp' not in snapshot.files
        assert 'utils.py' not in snapshot.files
    
    def test_duplicate_roles_only_one_per_role(self, temp_workspace):
        """Test that when multiple files match a role, only one is included per role"""
        validator_dir = os.path.join(temp_workspace, 'validator')
        
        # Create multiple files for each role (mixed languages)
        with open(os.path.join(validator_dir, 'generator.cpp'), 'w') as f:
            f.write('int main() {}')
        
        with open(os.path.join(validator_dir, 'Generator.java'), 'w') as f:
            f.write('public class Generator {}')
        
        with open(os.path.join(validator_dir, 'generator.py'), 'w') as f:
            f.write('print("hi")')
        
        with open(os.path.join(validator_dir, 'test.cpp'), 'w') as f:
            f.write('void test() {}')
        
        with open(os.path.join(validator_dir, 'test.py'), 'w') as f:
            f.write('def test(): pass')
        
        with open(os.path.join(validator_dir, 'TestCode.java'), 'w') as f:
            f.write('public class TestCode {}')
        
        with open(os.path.join(validator_dir, 'validator.cpp'), 'w') as f:
            f.write('bool validate() {}')
        
        with open(os.path.join(validator_dir, 'validator.py'), 'w') as f:
            f.write('def validate(): pass')
        
        with open(os.path.join(validator_dir, 'ValidatorCode.java'), 'w') as f:
            f.write('public class ValidatorCode {}')
        
        # Create snapshot
        snapshot = DatabaseManager.create_files_snapshot(temp_workspace, 'validation')
        
        # Should have exactly 3 files (one per role), not 9!
        assert len(snapshot.files) == 3
        
        # Count roles
        roles = [file_data['role'] for file_data in snapshot.files.values()]
        assert roles.count('generator') == 1
        assert roles.count('test') == 1
        assert roles.count('validator') == 1
        
        # Verify only one of each role is present
        generator_files = [f for f in snapshot.files.keys() if 'generator' in f.lower()]
        test_files = [f for f in snapshot.files.keys() if 'test' in f.lower()]
        validator_files = [f for f in snapshot.files.keys() if 'validator' in f.lower()]
        
        assert len(generator_files) == 1
        assert len(test_files) == 1
        assert len(validator_files) == 1
    
    def test_skips_directories(self, temp_workspace):
        """Test that inputs/outputs directories are skipped"""
        comparator_dir = os.path.join(temp_workspace, 'comparator')
        
        # Create main files
        with open(os.path.join(comparator_dir, 'generator.cpp'), 'w') as f:
            f.write('int main() {}')
        
        with open(os.path.join(comparator_dir, 'correct.cpp'), 'w') as f:
            f.write('int solve() {}')
        
        with open(os.path.join(comparator_dir, 'test.cpp'), 'w') as f:
            f.write('void test() {}')
        
        # Create files in subdirectories (should be ignored)
        inputs_dir = os.path.join(comparator_dir, 'inputs')
        with open(os.path.join(inputs_dir, '1.txt'), 'w') as f:
            f.write('input data')
        
        outputs_dir = os.path.join(comparator_dir, 'outputs')
        with open(os.path.join(outputs_dir, '1.txt'), 'w') as f:
            f.write('output data')
        
        # Create snapshot
        snapshot = DatabaseManager.create_files_snapshot(temp_workspace, 'comparison')
        
        # Should only have 3 main files, no inputs/outputs
        assert len(snapshot.files) == 3
        assert all('.txt' not in filename for filename in snapshot.files.keys())
    
    def test_test_type_aliases(self, temp_workspace):
        """Test that test type aliases work correctly"""
        comparator_dir = os.path.join(temp_workspace, 'comparator')
        
        with open(os.path.join(comparator_dir, 'generator.cpp'), 'w') as f:
            f.write('int main() {}')
        with open(os.path.join(comparator_dir, 'correct.cpp'), 'w') as f:
            f.write('int solve() {}')
        with open(os.path.join(comparator_dir, 'test.cpp'), 'w') as f:
            f.write('void test() {}')
        
        # Test different aliases for same test type
        snapshot1 = DatabaseManager.create_files_snapshot(temp_workspace, 'comparison')
        snapshot2 = DatabaseManager.create_files_snapshot(temp_workspace, 'comparator')
        snapshot3 = DatabaseManager.create_files_snapshot(temp_workspace, 'stress')  # Legacy
        
        # All should produce same result
        assert snapshot1.test_type == snapshot2.test_type == snapshot3.test_type == 'comparison'
        assert len(snapshot1.files) == len(snapshot2.files) == len(snapshot3.files) == 3
    
    def test_empty_directory(self, temp_workspace):
        """Test handling of empty test type directory"""
        # Create snapshot for comparator with no files
        snapshot = DatabaseManager.create_files_snapshot(temp_workspace, 'comparison')
        
        # Should return empty snapshot
        assert len(snapshot.files) == 0
        assert snapshot.test_type == 'comparison'
    
    def test_nonexistent_directory(self):
        """Test handling of nonexistent workspace"""
        snapshot = DatabaseManager.create_files_snapshot('/nonexistent/path', 'comparison')
        
        # Should return empty snapshot without crashing
        assert len(snapshot.files) == 0
    
    def test_primary_language_detection(self, temp_workspace):
        """Test that primary language is correctly detected as most common"""
        comparator_dir = os.path.join(temp_workspace, 'comparator')
        
        # Create 2 Python files, 1 C++ file
        with open(os.path.join(comparator_dir, 'generator.py'), 'w') as f:
            f.write('def gen(): pass')
        
        with open(os.path.join(comparator_dir, 'correct.py'), 'w') as f:
            f.write('def solve(): pass')
        
        with open(os.path.join(comparator_dir, 'test.cpp'), 'w') as f:
            f.write('void test() {}')
        
        snapshot = DatabaseManager.create_files_snapshot(temp_workspace, 'comparison')
        
        # Primary language should be Python (2 files vs 1 C++)
        assert snapshot.primary_language == 'py'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
