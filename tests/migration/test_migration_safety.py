"""Test suite to ensure migration safety"""
import pytest
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

from src.app.persistence.database.database_manager import (
    DatabaseManager, TestResult, FilesSnapshot
)


@pytest.fixture
def sample_test_results_old_naming():
    """Create sample test results with OLD naming (stress, tle)"""
    return [
        TestResult(
            test_type="stress",  # Old naming
            file_path="comparator/test.cpp",
            test_count=10,
            passed_tests=8,
            failed_tests=2,
            total_time=5.0,
            timestamp="2025-10-01T10:00:00",
            test_details='[{"test_number": 1, "passed": true}]',
            project_name="TestProject",
            files_snapshot='{"generator_code": "code1", "correct_code": "code2", "test_code": "code3"}',
            mismatch_analysis='{"summary": "test"}'
        ),
        TestResult(
            test_type="tle",  # Old naming
            file_path="benchmarker/test.java",
            test_count=5,
            passed_tests=5,
            failed_tests=0,
            total_time=3.5,
            timestamp="2025-10-02T14:30:00",
            test_details='[{"test_number": 1, "passed": true}]',
            project_name="BenchmarkProject",
            files_snapshot='{"generator_code": "code1", "test_code": "code2"}',
            mismatch_analysis='{"summary": "benchmark"}'
        ),
        TestResult(
            test_type="validator",  # Already correct
            file_path="validator/test.py",
            test_count=15,
            passed_tests=14,
            failed_tests=1,
            total_time=2.0,
            timestamp="2025-10-03T09:15:00",
            test_details='[{"test_number": 1, "passed": true}]',
            project_name="ValidatorProject",
            files_snapshot='{"generator_code": "code1", "test_code": "code2", "validator_code": "code3"}',
            mismatch_analysis='{"summary": "validation"}'
        ),
    ]


@pytest.fixture
def sample_test_results_new_naming():
    """Create sample test results with NEW naming (comparison, benchmark, validator)"""
    return [
        TestResult(
            test_type="comparison",  # New naming
            file_path="comparator/test.cpp",
            test_count=10,
            passed_tests=8,
            failed_tests=2,
            total_time=5.0,
            timestamp="2025-10-01T10:00:00",
            test_details='[{"test_number": 1, "passed": true}]',
            project_name="TestProject",
            files_snapshot='{"generator_code": "code1"}',
            mismatch_analysis='{"summary": "test"}'
        ),
        TestResult(
            test_type="benchmark",  # New naming
            file_path="benchmarker/test.java",
            test_count=5,
            passed_tests=5,
            failed_tests=0,
            total_time=3.5,
            timestamp="2025-10-02T14:30:00",
            test_details='[{"test_number": 1, "passed": true}]',
            project_name="BenchmarkProject",
            files_snapshot='{"generator_code": "code1"}',
            mismatch_analysis='{"summary": "benchmark"}'
        ),
    ]


class TestDatabaseMigrationSafety:
    """Test suite for migration safety checks"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        yield db_path
        
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
    
    def test_old_data_readable(self, temp_db, sample_test_results_old_naming):
        """Ensure old data can be read before migration"""
        db = DatabaseManager(temp_db)
        
        # Save old-format data
        for result in sample_test_results_old_naming:
            result_id = db.save_test_result(result)
            assert result_id > 0, "Failed to save old-format test result"
        
        # Retrieve and verify
        results = db.get_test_results()
        assert len(results) == 3
        
        # Check old naming is preserved
        types = [r.test_type for r in results]
        assert "stress" in types
        assert "tle" in types
        assert "validator" in types
    
    def test_database_backup_works(self, temp_db, sample_test_results_old_naming):
        """Verify database can be backed up and restored"""
        db = DatabaseManager(temp_db)
        
        # Add test data
        for result in sample_test_results_old_naming:
            db.save_test_result(result)
        
        original_count = len(db.get_test_results())
        
        # Simulate backup by copying database file
        backup_path = temp_db + ".backup"
        Path(temp_db).replace(backup_path)
        Path(backup_path).replace(temp_db)
        
        # Verify data still intact
        db2 = DatabaseManager(temp_db)
        restored_count = len(db2.get_test_results())
        
        assert original_count == restored_count
    
    def test_mixed_old_and_new_naming_coexist(self, temp_db, sample_test_results_old_naming, sample_test_results_new_naming):
        """Verify old and new naming can coexist temporarily during migration"""
        db = DatabaseManager(temp_db)
        
        # Save old format
        for result in sample_test_results_old_naming:
            db.save_test_result(result)
        
        # Save new format
        for result in sample_test_results_new_naming:
            db.save_test_result(result)
        
        # Both should be retrievable
        all_results = db.get_test_results()
        assert len(all_results) == 5
        
        types = [r.test_type for r in all_results]
        # Old naming
        assert "stress" in types
        assert "tle" in types
        # New naming
        assert "comparison" in types
        assert "benchmark" in types
        assert "validator" in types
    
    def test_database_schema_exists(self, temp_db):
        """Verify current database schema is properly initialized"""
        db = DatabaseManager(temp_db)
        connection = db.connect()
        cursor = connection.cursor()
        
        # Check test_results table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_results'")
        assert cursor.fetchone() is not None
        
        # Check columns exist
        cursor.execute("PRAGMA table_info(test_results)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = [
            'id', 'test_type', 'file_path', 'test_count', 
            'passed_tests', 'failed_tests', 'total_time', 
            'timestamp', 'test_details', 'project_name',
            'files_snapshot', 'mismatch_analysis'
        ]
        
        for col in required_columns:
            assert col in columns, f"Column {col} missing from database"
        
        db.close()
    
    def test_invalid_test_type_currently_accepted(self, temp_db):
        """Verify that invalid test types are currently accepted (will change after migration)"""
        db = DatabaseManager(temp_db)
        
        # This should currently work (no constraints yet)
        invalid_result = TestResult(
            test_type="invalid_type",  # Invalid
            file_path="test.cpp",
            test_count=1,
            passed_tests=1,
            failed_tests=0,
            total_time=1.0,
            timestamp=datetime.now().isoformat(),
            test_details='[]',
            project_name="Test",
            files_snapshot='{}',
            mismatch_analysis='{}'
        )
        
        # Should save without error (no constraints yet)
        result_id = db.save_test_result(invalid_result)
        # In current system, this works (which is the problem we're fixing!)
        # After Phase 1, this test should be updated to expect failure
    
    def test_files_snapshot_structure(self, temp_db):
        """Test that files snapshot can be saved and retrieved"""
        db = DatabaseManager(temp_db)
        
        result = TestResult(
            test_type="comparison",
            file_path="test.cpp",
            test_count=1,
            passed_tests=1,
            failed_tests=0,
            total_time=1.0,
            timestamp=datetime.now().isoformat(),
            test_details='[]',
            project_name="Test",
            files_snapshot='{"generator_code": "int main(){}", "test_code": "test"}',
            mismatch_analysis='{}'
        )
        
        result_id = db.save_test_result(result)
        assert result_id > 0
        
        # Retrieve and verify
        retrieved = db.get_test_results()[0]
        assert retrieved.files_snapshot is not None
        assert "generator_code" in retrieved.files_snapshot


class TestMigrationPreChecks:
    """Pre-migration validation tests"""
    
    def test_python_version(self):
        """Verify Python version is compatible"""
        import sys
        assert sys.version_info >= (3, 8), "Python 3.8+ required"
    
    def test_required_modules_available(self):
        """Verify all required modules are importable"""
        try:
            import sqlite3
            import json
            from datetime import datetime
            from pathlib import Path
            from dataclasses import dataclass
        except ImportError as e:
            pytest.fail(f"Required module not available: {e}")
    
    def test_database_module_imports(self):
        """Verify database module imports work"""
        try:
            from src.app.persistence.database.database_manager import (
                DatabaseManager, TestResult, FilesSnapshot
            )
        except ImportError as e:
            pytest.fail(f"Database module import failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
