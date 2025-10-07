"""
Integration tests for FilesSnapshot migration and backward compatibility.

Tests that:
- Old format results are automatically migrated
- Migration utility works correctly
- Mixed old/new results coexist
- No data loss during migration
- Dry run mode works correctly
"""

import pytest
import os
import tempfile
import shutil
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


class TestMigrationAndBackwardCompatibility:
    """Test migration utility and backward compatibility."""
    
    def test_save_and_load_old_format_result(self, temp_db):
        """Test saving result with old format and loading it (auto-migration)."""
        # Create old format snapshot
        old_snapshot = {
            'generator_code': '#include <iostream>\nint main() { return 0; }',
            'correct_code': '#include <iostream>\nint main() { return 0; }',
            'test_code': '#include <iostream>\nint main() { return 0; }',
            'language': 'cpp'
        }
        
        result = TestResult(
            project_name='Old Format Test',
            test_type='comparison',
            timestamp='2024-01-01 12:00:00',
            test_count=10,
            passed_tests=10,
            files_snapshot=json.dumps(old_snapshot)
        )
        
        # Save to database
        result_id = temp_db.save_test_result(result)
        assert result_id is not None
        
        # Load back (should auto-migrate on read)
        loaded_results = temp_db.get_test_results()
        assert len(loaded_results) == 1
        
        loaded_result = loaded_results[0]
        assert loaded_result.project_name == 'Old Format Test'
        
        # Parse snapshot with auto-migration
        snapshot = FilesSnapshot.from_json(loaded_result.files_snapshot)
        
        # Verify migration worked
        assert len(snapshot.files) == 3
        assert 'generator.cpp' in snapshot.files
        assert 'correct.cpp' in snapshot.files
        assert 'test.cpp' in snapshot.files
        assert snapshot.primary_language == 'cpp'
    
    def test_migrate_old_results_dry_run(self, temp_db):
        """Test migration dry run mode (no actual changes)."""
        # Create multiple old format results
        for i in range(3):
            old_snapshot = {
                'generator_code': f'// Generator {i}',
                'test_code': f'// Test {i}',
                'language': 'cpp'
            }
            
            result = TestResult(
                project_name=f'Project {i}',
                test_type='benchmark',
                timestamp='2024-01-01 12:00:00',
                test_count=1,
                passed_tests=1,
                files_snapshot=json.dumps(old_snapshot)
            )
            temp_db.save_test_result(result)
        
        # Run dry run migration
        stats = temp_db.migrate_old_results_to_new_format(dry_run=True)
        
        # Check stats
        assert stats['total_results'] == 3
        assert stats['old_format_count'] == 3
        assert stats['migrated_count'] == 3  # Would be migrated
        assert stats['failed_count'] == 0
        assert stats['skipped_count'] == 0
        
        # Verify database NOT changed (still old format)
        results = temp_db.get_test_results()
        for result in results:
            snapshot_data = json.loads(result.files_snapshot)
            assert 'generator_code' in snapshot_data  # Still old format
            assert 'files' not in snapshot_data  # Not migrated yet
    
    def test_migrate_old_results_actual(self, temp_db):
        """Test actual migration (updates database)."""
        # Create old format results
        for i in range(3):
            old_snapshot = {
                'generator_code': f'# Generator {i}\ndef generate():\n    pass',
                'correct_code': f'# Correct {i}\ndef correct():\n    pass',
                'test_code': f'# Test {i}\ndef test():\n    pass',
                'language': 'py'
            }
            
            result = TestResult(
                project_name=f'Python Project {i}',
                test_type='comparison',
                timestamp='2024-01-01 12:00:00',
                test_count=5,
                passed_tests=5,
                files_snapshot=json.dumps(old_snapshot)
            )
            temp_db.save_test_result(result)
        
        # Run actual migration
        stats = temp_db.migrate_old_results_to_new_format(dry_run=False)
        
        # Check stats
        assert stats['total_results'] == 3
        assert stats['old_format_count'] == 3
        assert stats['migrated_count'] == 3
        assert stats['failed_count'] == 0
        assert stats['skipped_count'] == 0
        
        # Verify database WAS changed (now new format)
        results = temp_db.get_test_results()
        for result in results:
            snapshot_data = json.loads(result.files_snapshot)
            assert 'files' in snapshot_data  # New format
            assert 'generator_code' not in snapshot_data  # Old format gone
            
            # Verify proper migration
            assert 'generator.py' in snapshot_data['files']
            assert 'correct.py' in snapshot_data['files']
            assert 'test.py' in snapshot_data['files']
            assert snapshot_data['primary_language'] == 'py'
    
    def test_mixed_old_and_new_results(self, temp_db):
        """Test database with mixed old and new format results."""
        # Add old format result
        old_snapshot = {
            'generator_code': '// Old generator',
            'test_code': '// Old test',
            'language': 'cpp'
        }
        
        old_result = TestResult(
            project_name='Old Format',
            test_type='benchmark',
            timestamp='2024-01-01 12:00:00',
            test_count=1,
            passed_tests=1,
            files_snapshot=json.dumps(old_snapshot)
        )
        temp_db.save_test_result(old_result)
        
        # Add new format result
        new_snapshot = FilesSnapshot(test_type='benchmark', primary_language='cpp')
        new_snapshot.files = {
            'generator.cpp': {
                'content': '// New generator',
                'language': 'cpp',
                'role': 'generator'
            },
            'test.cpp': {
                'content': '// New test',
                'language': 'cpp',
                'role': 'test'
            }
        }
        
        new_result = TestResult(
            project_name='New Format',
            test_type='benchmark',
            timestamp='2024-01-01 13:00:00',
            test_count=1,
            passed_tests=1,
            files_snapshot=new_snapshot.to_json()
        )
        temp_db.save_test_result(new_result)
        
        # Run migration
        stats = temp_db.migrate_old_results_to_new_format(dry_run=False)
        
        # Should migrate 1 old, skip 1 new
        assert stats['total_results'] == 2
        assert stats['old_format_count'] == 1
        assert stats['migrated_count'] == 1
        assert stats['skipped_count'] == 1
        assert stats['failed_count'] == 0
        
        # Verify both are now in new format
        results = temp_db.get_test_results()
        for result in results:
            snapshot = FilesSnapshot.from_json(result.files_snapshot)
            assert len(snapshot.files) == 2
            assert 'generator.cpp' in snapshot.files
            assert 'test.cpp' in snapshot.files
    
    def test_migration_preserves_content(self, temp_db):
        """Test that migration preserves all code content."""
        original_content = {
            'generator': '#include <iostream>\nint main() { std::cout << "Hello"; return 0; }',
            'correct': '#include <iostream>\nint main() { std::cout << "World"; return 0; }',
            'test': '#include <iostream>\nint main() { return 0; }'
        }
        
        old_snapshot = {
            'generator_code': original_content['generator'],
            'correct_code': original_content['correct'],
            'test_code': original_content['test'],
            'language': 'cpp'
        }
        
        result = TestResult(
            project_name='Content Test',
            test_type='comparison',
            timestamp='2024-01-01 12:00:00',
            test_count=10,
            passed_tests=10,
            files_snapshot=json.dumps(old_snapshot)
        )
        temp_db.save_test_result(result)
        
        # Migrate
        temp_db.migrate_old_results_to_new_format(dry_run=False)
        
        # Load and verify content
        results = temp_db.get_test_results()
        snapshot = FilesSnapshot.from_json(results[0].files_snapshot)
        
        assert snapshot.files['generator.cpp']['content'] == original_content['generator']
        assert snapshot.files['correct.cpp']['content'] == original_content['correct']
        assert snapshot.files['test.cpp']['content'] == original_content['test']
    
    def test_migration_with_validator_files(self, temp_db):
        """Test migration of validator-specific files."""
        old_snapshot = {
            'generator_code': 'def generate(): pass',
            'validator_code': 'def validate(): pass',
            'test_code': 'def test(): pass',
            'language': 'py'
        }
        
        result = TestResult(
            project_name='Validator Test',
            test_type='validation',
            timestamp='2024-01-01 12:00:00',
            test_count=5,
            passed_tests=5,
            files_snapshot=json.dumps(old_snapshot)
        )
        temp_db.save_test_result(result)
        
        # Migrate
        temp_db.migrate_old_results_to_new_format(dry_run=False)
        
        # Verify validator file migrated
        results = temp_db.get_test_results()
        snapshot = FilesSnapshot.from_json(results[0].files_snapshot)
        
        assert 'generator.py' in snapshot.files
        assert 'validator.py' in snapshot.files
        assert 'test.py' in snapshot.files
        assert snapshot.files['validator.py']['role'] == 'validator'
    
    def test_migration_with_additional_files(self, temp_db):
        """Test migration preserves additional files."""
        old_snapshot = {
            'generator_code': '// Generator',
            'test_code': '// Test',
            'language': 'cpp',
            'additional_files': {
                'helper.cpp': '// Helper functions',
                'utils.h': '// Utility headers'
            }
        }
        
        result = TestResult(
            project_name='Additional Files Test',
            test_type='benchmark',
            timestamp='2024-01-01 12:00:00',
            test_count=1,
            passed_tests=1,
            files_snapshot=json.dumps(old_snapshot)
        )
        temp_db.save_test_result(result)
        
        # Migrate
        temp_db.migrate_old_results_to_new_format(dry_run=False)
        
        # Verify additional files preserved
        results = temp_db.get_test_results()
        snapshot = FilesSnapshot.from_json(results[0].files_snapshot)
        
        assert 'helper.cpp' in snapshot.files
        assert 'utils.h' in snapshot.files
        assert snapshot.files['helper.cpp']['role'] == 'additional'
        assert snapshot.files['utils.h']['role'] == 'additional'
    
    def test_migration_handles_invalid_json(self, temp_db):
        """Test migration handles corrupted JSON gracefully."""
        # Create result with invalid JSON
        result = TestResult(
            project_name='Invalid JSON Test',
            test_type='comparison',
            timestamp='2024-01-01 12:00:00',
            test_count=0,
            passed_tests=0,
            files_snapshot='{"invalid": json syntax}'
        )
        temp_db.save_test_result(result)
        
        # Migrate should not crash
        stats = temp_db.migrate_old_results_to_new_format(dry_run=False)
        
        assert stats['total_results'] == 1
        assert stats['failed_count'] == 1
        assert len(stats['failures']) == 1
        assert 'Invalid JSON' in stats['failures'][0][1]
    
    def test_migration_idempotent(self, temp_db):
        """Test that running migration multiple times is safe."""
        old_snapshot = {
            'generator_code': '// Code',
            'test_code': '// Test',
            'language': 'cpp'
        }
        
        result = TestResult(
            project_name='Idempotent Test',
            test_type='benchmark',
            timestamp='2024-01-01 12:00:00',
            test_count=1,
            passed_tests=1,
            files_snapshot=json.dumps(old_snapshot)
        )
        temp_db.save_test_result(result)
        
        # First migration
        stats1 = temp_db.migrate_old_results_to_new_format(dry_run=False)
        assert stats1['migrated_count'] == 1
        
        # Second migration (should skip, already migrated)
        stats2 = temp_db.migrate_old_results_to_new_format(dry_run=False)
        assert stats2['migrated_count'] == 0
        assert stats2['skipped_count'] == 1
        
        # Verify still correct format
        results = temp_db.get_test_results()
        snapshot = FilesSnapshot.from_json(results[0].files_snapshot)
        assert 'generator.cpp' in snapshot.files


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
