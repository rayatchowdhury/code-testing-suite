"""
Integration tests for BaseRunner._create_files_snapshot() with new format.

Tests that runners properly create FilesSnapshot with:
- Correct file counts per test type (comparator=3, validator=3, benchmarker=2)
- File extensions preserved
- Per-file language detection
- Mixed language support
"""

import pytest
import os
import tempfile
import shutil
from src.app.core.tools.base.base_runner import BaseRunner
from src.app.persistence.database import FilesSnapshot


@pytest.fixture
def temp_workspace():
    """Create temporary workspace with test files."""
    workspace = tempfile.mkdtemp()
    yield workspace
    shutil.rmtree(workspace, ignore_errors=True)


def create_test_files(workspace_dir, test_type, language='cpp'):
    """Helper to create test files in workspace."""
    test_subdir = {
        'comparison': 'comparator',
        'validator': 'validator', 
        'benchmark': 'benchmarker'
    }[test_type]
    
    test_dir = os.path.join(workspace_dir, test_subdir)
    os.makedirs(test_dir, exist_ok=True)
    
    ext = {'cpp': '.cpp', 'py': '.py', 'java': '.java'}[language]
    
    # Generator (all test types)
    gen_name = 'Generator.java' if language == 'java' else f'generator{ext}'
    gen_path = os.path.join(test_dir, gen_name)
    with open(gen_path, 'w') as f:
        if language == 'cpp':
            f.write('#include <iostream>\nint main() { return 0; }')
        elif language == 'py':
            f.write('def generate():\n    pass')
        else:
            f.write('public class Generator {\n    public static void main(String[] args) {}\n}')
    
    # Correct/Validator
    if test_type == 'comparison':
        correct_name = 'Correct.java' if language == 'java' else f'correct{ext}'
        correct_path = os.path.join(test_dir, correct_name)
        with open(correct_path, 'w') as f:
            if language == 'cpp':
                f.write('#include <iostream>\nint main() { return 0; }')
            elif language == 'py':
                f.write('def correct():\n    pass')
            else:
                f.write('public class Correct {\n    public static void main(String[] args) {}\n}')
    elif test_type == 'validator':
        val_name = 'Validator.java' if language == 'java' else f'validator{ext}'
        val_path = os.path.join(test_dir, val_name)
        with open(val_path, 'w') as f:
            if language == 'cpp':
                f.write('#include <iostream>\nint main() { return 0; }')
            elif language == 'py':
                f.write('def validate():\n    pass')
            else:
                f.write('public class Validator {\n    public static void main(String[] args) {}\n}')
    
    # Test (all test types)
    test_name = 'Test.java' if language == 'java' else f'test{ext}'
    test_path = os.path.join(test_dir, test_name)
    with open(test_path, 'w') as f:
        if language == 'cpp':
            f.write('#include <iostream>\nint main() { return 0; }')
        elif language == 'py':
            f.write('def test():\n    pass')
        else:
            f.write('public class Test {\n    public static void main(String[] args) {}\n}')


class TestRunnerFilesSnapshot:
    """Test BaseRunner._create_files_snapshot() with new format."""
    
    def test_comparator_creates_3_files_cpp(self, temp_workspace):
        """Test comparator runner creates snapshot with exactly 3 C++ files."""
        create_test_files(temp_workspace, 'comparison', 'cpp')
        
        runner = BaseRunner(
            workspace_dir=temp_workspace,
            files_dict={},  # Not used by new implementation
            test_type='comparison'
        )
        
        snapshot_dict = runner._create_files_snapshot()
        assert 'files' in snapshot_dict
        assert len(snapshot_dict['files']) == 3
        assert 'generator.cpp' in snapshot_dict['files']
        assert 'correct.cpp' in snapshot_dict['files']
        assert 'test.cpp' in snapshot_dict['files']
        
        # Check file metadata
        gen = snapshot_dict['files']['generator.cpp']
        assert gen['language'] == 'cpp'
        assert gen['role'] == 'generator'
        assert '#include <iostream>' in gen['content']
        
        assert snapshot_dict['test_type'] == 'comparison'
        assert snapshot_dict['primary_language'] == 'cpp'
    
    def test_validator_creates_3_files_python(self, temp_workspace):
        """Test validator runner creates snapshot with exactly 3 Python files."""
        create_test_files(temp_workspace, 'validator', 'py')
        
        runner = BaseRunner(
            workspace_dir=temp_workspace,
            files_dict={},
            test_type='validator'
        )
        
        snapshot_dict = runner._create_files_snapshot()
        assert 'files' in snapshot_dict
        assert len(snapshot_dict['files']) == 3
        assert 'generator.py' in snapshot_dict['files']
        assert 'validator.py' in snapshot_dict['files']
        assert 'test.py' in snapshot_dict['files']
        
        # Check file metadata
        val = snapshot_dict['files']['validator.py']
        assert val['language'] == 'py'
        assert val['role'] == 'validator'
        assert 'def validate()' in val['content']
        
        assert snapshot_dict['test_type'] == 'validation'  # Normalized to 'validation' by create_files_snapshot
        assert snapshot_dict['primary_language'] == 'py'
    
    def test_benchmarker_creates_2_files_java(self, temp_workspace):
        """Test benchmarker runner creates snapshot with exactly 2 Java files."""
        create_test_files(temp_workspace, 'benchmark', 'java')
        
        runner = BaseRunner(
            workspace_dir=temp_workspace,
            files_dict={},
            test_type='benchmark'
        )
        
        snapshot_dict = runner._create_files_snapshot()
        assert 'files' in snapshot_dict
        assert len(snapshot_dict['files']) == 2
        assert 'Generator.java' in snapshot_dict['files']
        assert 'Test.java' in snapshot_dict['files']
        assert 'Correct.java' not in snapshot_dict['files']  # Benchmarker doesn't need correct
        assert 'Validator.java' not in snapshot_dict['files']
        
        # Check file metadata
        gen = snapshot_dict['files']['Generator.java']
        assert gen['language'] == 'java'
        assert gen['role'] == 'generator'
        assert 'public class Generator' in gen['content']
        
        assert snapshot_dict['test_type'] == 'benchmark'
        assert snapshot_dict['primary_language'] == 'java'
    
    def test_mixed_language_comparator(self, temp_workspace):
        """Test comparator with mixed Python generator + C++ test."""
        test_dir = os.path.join(temp_workspace, 'comparator')
        os.makedirs(test_dir, exist_ok=True)
        
        # Python generator
        with open(os.path.join(test_dir, 'generator.py'), 'w') as f:
            f.write('def generate():\n    pass')
        
        # C++ correct
        with open(os.path.join(test_dir, 'correct.cpp'), 'w') as f:
            f.write('#include <iostream>\nint main() { return 0; }')
        
        # C++ test
        with open(os.path.join(test_dir, 'test.cpp'), 'w') as f:
            f.write('#include <iostream>\nint main() { return 0; }')
        
        runner = BaseRunner(
            workspace_dir=temp_workspace,
            files_dict={},
            test_type='comparison'
        )
        
        snapshot_dict = runner._create_files_snapshot()
        assert len(snapshot_dict['files']) == 3
        
        # Check per-file languages
        assert snapshot_dict['files']['generator.py']['language'] == 'py'
        assert snapshot_dict['files']['correct.cpp']['language'] == 'cpp'
        assert snapshot_dict['files']['test.cpp']['language'] == 'cpp'
        
        # Primary language should be cpp (2 cpp files vs 1 py)
        assert snapshot_dict['primary_language'] == 'cpp'
    
    def test_snapshot_can_be_deserialized(self, temp_workspace):
        """Test that runner snapshot can be deserialized back to FilesSnapshot object."""
        create_test_files(temp_workspace, 'comparison', 'cpp')
        
        runner = BaseRunner(
            workspace_dir=temp_workspace,
            files_dict={},
            test_type='comparison'
        )
        
        snapshot_dict = runner._create_files_snapshot()
        
        # Convert back to FilesSnapshot object
        import json
        snapshot_obj = FilesSnapshot.from_json(json.dumps(snapshot_dict))
        
        assert len(snapshot_obj.files) == 3
        assert 'generator.cpp' in snapshot_obj.files
        assert snapshot_obj.test_type == 'comparison'
        assert snapshot_obj.primary_language == 'cpp'
    
    def test_empty_workspace_returns_empty_snapshot(self, temp_workspace):
        """Test that empty workspace returns empty but valid snapshot."""
        runner = BaseRunner(
            workspace_dir=temp_workspace,
            files_dict={},
            test_type='comparison'
        )
        
        snapshot_dict = runner._create_files_snapshot()
        assert 'files' in snapshot_dict
        assert len(snapshot_dict['files']) == 0
        assert snapshot_dict['test_type'] == 'comparison'
    
    def test_additional_files_excluded(self, temp_workspace):
        """Test that only required files are included (no additional helper files)."""
        test_dir = os.path.join(temp_workspace, 'comparator')
        os.makedirs(test_dir, exist_ok=True)
        
        # Main files
        with open(os.path.join(test_dir, 'generator.cpp'), 'w') as f:
            f.write('#include <iostream>\nint main() { return 0; }')
        with open(os.path.join(test_dir, 'correct.cpp'), 'w') as f:
            f.write('#include <iostream>\nint main() { return 0; }')
        with open(os.path.join(test_dir, 'test.cpp'), 'w') as f:
            f.write('#include <iostream>\nint main() { return 0; }')
        
        # Additional helper file that should be excluded
        with open(os.path.join(test_dir, 'helper.cpp'), 'w') as f:
            f.write('// Helper functions\nvoid helper() {}')
        
        runner = BaseRunner(
            workspace_dir=temp_workspace,
            files_dict={},
            test_type='comparison'
        )
        
        snapshot_dict = runner._create_files_snapshot()
        
        # Should have only 3 main files (no helper)
        assert len(snapshot_dict['files']) == 3
        assert 'helper.cpp' not in snapshot_dict['files']
        assert 'generator.cpp' in snapshot_dict['files']
        assert 'correct.cpp' in snapshot_dict['files']
        assert 'test.cpp' in snapshot_dict['files']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
