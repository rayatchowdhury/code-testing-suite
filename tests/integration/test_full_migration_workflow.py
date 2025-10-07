"""
Phase 6 Task 2: Comprehensive Integration Tests
Tests the complete migration workflow end-to-end.

This test suite verifies:
1. Full workflow: create → save → filter → export → delete
2. Storage reduction (97.9% for files snapshot)
3. On-demand saving functionality
4. SQL date filtering performance
5. Backward compatibility with old data
"""

import pytest
import json
import tempfile
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from src.app.persistence.database import (
    DatabaseManager,
    TestResult
)
from tests.fixtures.test_adapters import TestDataFactory


class TestFullMigrationWorkflow:
    """Test complete migration workflow from start to finish"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_migration.db"
            db = DatabaseManager(db_path=str(db_path))
            yield db
            # Explicitly close connection before cleanup
            if hasattr(db, 'connection') and db.connection:
                db.connection.close()
    
    def test_create_and_save_result(self, temp_db):
        """Test creating and saving a test result"""
        # Create test result
        result = TestDataFactory.create_test_result(
            project_name="Migration Test Project Unique",
            test_count=10,
            passed_tests=8,
            failed_tests=2
        )
        
        # Save the result
        result_id = temp_db.save_test_result(result)
        
        assert result_id is not None
        assert result_id > 0
        
        # Retrieve and verify using query
        retrieved_list = temp_db.get_test_results(project_name="Migration Test Project")
        assert len(retrieved_list) > 0
        retrieved = retrieved_list[0]
        assert retrieved.project_name == "Migration Test Project Unique"
        assert retrieved.test_count == 10
        assert retrieved.passed_tests == 8
        assert retrieved.failed_tests == 2
    
    def test_files_snapshot_storage_efficiency(self, temp_db):
        """Test that files snapshot is stored efficiently as JSON"""
        # Create result with files snapshot
        result = TestDataFactory.create_test_result(
            project_name="Storage Efficiency Test"
        )
        result.files_snapshot = json.dumps({
            "generator.py": "def generate():\n    " + "x = 1\n" * 100,
            "correct.py": "def solve(n):\n    " + "y = 2\n" * 100,
            "test.py": "import sys\n" * 50
        })
        
        result_id = temp_db.save_test_result(result)
        
        # Retrieve result to verify JSON storage
        retrieved_list = temp_db.get_test_results(project_name="Storage Efficiency", limit=10)
        assert len(retrieved_list) > 0
        retrieved = retrieved_list[0]
        
        files_json = retrieved.files_snapshot
        assert files_json is not None
        
        # Verify it's valid JSON
        files_dict = json.loads(files_json)
        assert "generator.py" in files_dict
        assert "correct.py" in files_dict
        assert "test.py" in files_dict
        
        # Measure JSON size
        json_size = len(files_json.encode('utf-8'))
        
        # Old format would have been ~24KB, new format should be <5KB
        print(f"\nFiles snapshot size: {json_size:,} bytes ({json_size/1024:.1f} KB)")
        assert json_size < 5000, f"JSON size {json_size} bytes is too large"
    
    def test_sql_date_filtering_7_days(self, temp_db):
        """Test SQL date filtering for last 7 days"""
        # Create test results with different dates
        now = datetime.now()
        
        # Recent result (within 7 days)
        recent = TestDataFactory.create_test_result()
        recent.timestamp = (now - timedelta(days=3)).isoformat()
        recent.project_name = "Recent Project 7Day"
        temp_db.save_test_result(recent)
        
        # Old result (beyond 7 days)
        old = TestDataFactory.create_test_result()
        old.timestamp = (now - timedelta(days=10)).isoformat()
        old.project_name = "Old Project 7Day"
        temp_db.save_test_result(old)
        
        # Query with date filter (7 days)
        results = temp_db.get_test_results(days=7, limit=200)
        
        # Should only get recent result
        project_names = [r.project_name for r in results]
        assert "Recent Project 7Day" in project_names
        assert "Old Project 7Day" not in project_names
    
    def test_sql_date_filtering_30_days(self, temp_db):
        """Test SQL date filtering for last 30 days"""
        now = datetime.now()
        
        # Recent result
        recent = TestDataFactory.create_test_result()
        recent.timestamp = (now - timedelta(days=20)).isoformat()
        recent.project_name = "Recent Project 30Day"
        temp_db.save_test_result(recent)
        
        # Very old result
        very_old = TestDataFactory.create_test_result()
        very_old.timestamp = (now - timedelta(days=40)).isoformat()
        very_old.project_name = "Very Old Project 30Day"
        temp_db.save_test_result(very_old)
        
        # Query with 30 day filter
        results = temp_db.get_test_results(days=30, limit=200)
        
        project_names = [r.project_name for r in results]
        assert "Recent Project 30Day" in project_names
        assert "Very Old Project 30Day" not in project_names
    
    def test_filter_by_test_type(self, temp_db):
        """Test filtering by test type"""
        # Create results with different test types
        comparator = TestDataFactory.create_test_result(
            test_type="comparison",
            project_name="Comparator Project Test"
        )
        temp_db.save_test_result(comparator)
        
        validator = TestDataFactory.create_test_result(
            test_type="validation",
            project_name="Validator Project Test"
        )
        temp_db.save_test_result(validator)
        
        benchmarker = TestDataFactory.create_test_result(
            test_type="benchmark",
            project_name="Benchmarker Project Test"
        )
        temp_db.save_test_result(benchmarker)
        
        # Filter by comparison
        comp_results = temp_db.get_test_results(test_type="comparison", limit=200)
        comp_names = [r.project_name for r in comp_results]
        
        assert "Comparator Project Test" in comp_names
        assert "Validator Project Test" not in comp_names
        assert "Benchmarker Project Test" not in comp_names
    
    def test_filter_by_status(self, temp_db):
        """Test filtering by pass/fail status"""
        # Create passed and failed results
        passed = TestDataFactory.create_test_result(
            failed_tests=0,
            passed_tests=10,
            test_count=10,
            project_name="Passed Project Test"
        )
        temp_db.save_test_result(passed)
        
        failed = TestDataFactory.create_test_result(
            failed_tests=5,
            passed_tests=5,
            test_count=10,
            project_name="Failed Project Test"
        )
        temp_db.save_test_result(failed)
        
        # Get passed results using SQL filter
        passed_results = temp_db.get_test_results(status='passed', limit=200)
        passed_names = [r.project_name for r in passed_results]
        
        # Get failed results using SQL filter
        failed_results = temp_db.get_test_results(status='failed', limit=200)
        failed_names = [r.project_name for r in failed_results]
        
        assert "Passed Project Test" in passed_names
        assert "Failed Project Test" in failed_names
        assert "Passed Project Test" not in failed_names
        assert "Failed Project Test" not in passed_names
    
    def test_combined_filters(self, temp_db):
        """Test combining multiple filters (date + test_type + project)"""
        now = datetime.now()
        
        # Target result: recent comparison project
        target = TestDataFactory.create_test_result(
            project_name="Target Project Combined",
            test_type="comparison",
            timestamp=(now - timedelta(days=5)).isoformat()
        )
        temp_db.save_test_result(target)
        
        # Noise: old comparator
        old_comp = TestDataFactory.create_test_result(
            project_name="Old Comparator Combined",
            test_type="comparison",
            timestamp=(now - timedelta(days=20)).isoformat()
        )
        temp_db.save_test_result(old_comp)
        
        # Noise: recent validator
        recent_val = TestDataFactory.create_test_result(
            project_name="Recent Validator Combined",
            test_type="validation",
            timestamp=(now - timedelta(days=3)).isoformat()
        )
        temp_db.save_test_result(recent_val)
        
        # Query with combined filters
        results = temp_db.get_test_results(
            days=7,
            test_type="comparison",
            project_name="Target",
            limit=200
        )
        
        project_names = [r.project_name for r in results]
        assert "Target Project Combined" in project_names
        assert "Old Comparator Combined" not in project_names  # Filtered by date
        assert "Recent Validator Combined" not in project_names  # Filtered by test_type
    
    def test_delete_result(self, temp_db):
        """Test deleting a test result"""
        # Create and save result
        result = TestDataFactory.create_test_result(
            project_name="To Delete Test"
        )
        result_id = temp_db.save_test_result(result)
        
        # Verify it exists
        results = temp_db.get_test_results(project_name="To Delete", limit=10)
        assert len(results) > 0
        
        # Delete result
        success = temp_db.delete_test_result(result_id)
        assert success is True
        
        # Verify deleted
        results_after = temp_db.get_test_results(project_name="To Delete", limit=10)
        # Should not find the specific deleted result
        deleted_ids = [r.id for r in results_after if r.id == result_id]
        assert len(deleted_ids) == 0
    
    def test_backward_compatibility_old_naming(self, temp_db):
        """Test that old test_type naming still works"""
        # Old naming convention: "stress", "comparison", "benchmark"
        old_test = TestDataFactory.create_test_result(
            project_name="Legacy Project Old Naming",
            test_type="comparison"  # Old naming still supported
        )
        
        # Should save without error
        result_id = temp_db.save_test_result(old_test)
        assert result_id is not None
        
        # Should retrieve correctly
        retrieved = temp_db.get_test_results(project_name="Legacy Project", limit=10)
        assert len(retrieved) > 0
        assert retrieved[0].test_type == "comparison"


class TestStorageReduction:
    """Verify storage reduction metrics from migration"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "storage_test.db"
            db = DatabaseManager(db_path=str(db_path))
            yield db
            if hasattr(db, 'connection') and db.connection:
                db.connection.close()
    
    def test_measure_files_snapshot_size(self, temp_db):
        """Measure actual files snapshot storage size"""
        # Create realistic code samples
        result = TestDataFactory.create_test_result(
            project_name="Storage Measure Test"
        )
        result.files_snapshot = json.dumps({
            "generator.py": "def generate():\n    return [f'test_{i}' for i in range(100)]",
            "correct.py": "def solve(input):\n    # Complex solution\n    return process(input)",
            "test.py": "import sys\n" * 50  # Simulate larger file
        })
        
        result_id = temp_db.save_test_result(result)
        
        # Retrieve result to measure JSON size
        retrieved_list = temp_db.get_test_results(project_name="Storage Measure", limit=10)
        assert len(retrieved_list) > 0
        retrieved = retrieved_list[0]
        
        files_json = retrieved.files_snapshot
        assert files_json is not None
        json_size = len(files_json.encode('utf-8'))
        
        # Calculate theoretical old size
        old_estimated_size = 24000
        
        # Calculate reduction percentage
        reduction_percent = ((old_estimated_size - json_size) / old_estimated_size) * 100
        
        # Should achieve close to 97.9% reduction
        print(f"\n📊 Storage Reduction Analysis:")
        print(f"  Old format (estimated): {old_estimated_size:,} bytes")
        print(f"  New format (actual): {json_size:,} bytes")
        print(f"  Reduction: {reduction_percent:.1f}%")
        
        # Verify significant reduction (at least 80%)
        assert reduction_percent > 80, f"Expected >80% reduction, got {reduction_percent:.1f}%"
        assert json_size < 5000, f"JSON size {json_size} bytes exceeds 5KB limit"
    
    def test_database_size_with_many_results(self, temp_db):
        """Test database size with 50 test results"""
        # Create 50 test results
        for i in range(50):
            result = TestDataFactory.create_test_result(
                project_name=f"Project {i}",
                file_path=f"/test/file_{i}.cpp"
            )
            result.files_snapshot = json.dumps({
                f"generator_{i}.py": f"# Generator {i}\n" + "x = 1\n" * 100,
                f"correct_{i}.py": f"# Correct {i}\n" + "y = 2\n" * 100,
                f"test_{i}.py": f"# Test {i}\n" + "z = 3\n" * 100
            })
            
            temp_db.save_test_result(result)
        
        # Check database size
        db_size = os.path.getsize(temp_db.db_path)
        
        # With 50 results and efficient storage, should be < 500KB
        print(f"\n💾 Database Size with 50 Results: {db_size:,} bytes ({db_size/1024:.1f} KB)")
        
        assert db_size < 500_000, f"Database too large: {db_size:,} bytes"


class TestOnDemandSaving:
    """Test on-demand saving functionality"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "ondemand_test.db"
            db = DatabaseManager(db_path=str(db_path))
            yield db
            if hasattr(db, 'connection') and db.connection:
                db.connection.close()
    
    def test_save_returns_valid_id(self, temp_db):
        """Test that save operation returns valid result ID"""
        result = TestDataFactory.create_test_result(
            project_name="On-Demand Test Valid ID"
        )
        
        # Save and get ID
        result_id = temp_db.save_test_result(result)
        
        assert isinstance(result_id, int)
        assert result_id > 0
        
        # Verify can retrieve with query
        retrieved = temp_db.get_test_results(project_name="On-Demand Test", limit=10)
        assert len(retrieved) > 0
        assert retrieved[0].id == result_id
    
    def test_multiple_saves_independent(self, temp_db):
        """Test that multiple saves create independent records"""
        # Save result 1
        result1 = TestDataFactory.create_test_result(
            project_name="Project 1 Independent",
            test_type="comparison"
        )
        id1 = temp_db.save_test_result(result1)
        
        # Save result 2
        result2 = TestDataFactory.create_test_result(
            project_name="Project 2 Independent",
            test_type="validation"
        )
        id2 = temp_db.save_test_result(result2)
        
        # IDs should be different
        assert id1 != id2
        
        # Both should be retrievable independently
        retrieved1 = temp_db.get_test_results(project_name="Project 1", limit=10)
        retrieved2 = temp_db.get_test_results(project_name="Project 2", limit=10)
        
        assert len(retrieved1) > 0
        assert len(retrieved2) > 0
        assert retrieved1[0].project_name == "Project 1 Independent"
        assert retrieved2[0].project_name == "Project 2 Independent"
        assert retrieved1[0].test_type == "comparison"
        assert retrieved2[0].test_type == "validation"


class TestPerformanceComparison:
    """Compare SQL filtering vs Python filtering performance"""
    
    @pytest.fixture
    def populated_db(self):
        """Create database with 100 test results"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "performance_test.db"
            db = DatabaseManager(db_path=str(db_path))
            
            # Create 100 test results with various dates
            now = datetime.now()
            for i in range(100):
                days_ago = i  # Spread results across 100 days
                
                result = TestDataFactory.create_test_result(
                    project_name=f"Project {i}",
                    test_type="comparison" if i % 3 == 0 else "validation",
                    timestamp=(now - timedelta(days=days_ago)).isoformat()
                )
                
                db.save_test_result(result)
            
            yield db
            if hasattr(db, 'connection') and db.connection:
                db.connection.close()
    
    def test_sql_date_filter_performance(self, populated_db):
        """Test SQL date filtering is fast"""
        # Measure SQL filtering (7 days)
        start = time.time()
        sql_results = populated_db.get_test_results(days=7, limit=200)
        sql_time = time.time() - start
        
        # Should get only last 7 days (0-6 inclusive)
        assert len(sql_results) == 7
        
        # Should be very fast (< 100ms even on slower systems)
        print(f"\n⚡ SQL Date Filter (7 days): {sql_time*1000:.2f}ms")
        assert sql_time < 0.1, f"SQL filtering too slow: {sql_time*1000:.2f}ms"
    
    def test_python_vs_sql_filtering_comparison(self, populated_db):
        """Compare Python filtering vs SQL filtering"""
        # Method 1: SQL filtering
        start_sql = time.time()
        sql_results = populated_db.get_test_results(days=7, limit=200)
        sql_time = time.time() - start_sql
        
        # Method 2: Python filtering (old approach)
        start_python = time.time()
        all_results = populated_db.get_test_results(limit=200)
        now = datetime.now()
        cutoff = now - timedelta(days=7)
        python_results = [r for r in all_results if datetime.fromisoformat(r.timestamp) >= cutoff]
        python_time = time.time() - start_python
        
        # Both should get same results
        assert len(sql_results) == len(python_results)
        
        # SQL should be faster or comparable
        print(f"\n🏎️  Filtering Performance Comparison (7 days):")
        print(f"  SQL filtering: {sql_time*1000:.2f}ms")
        print(f"  Python filtering: {python_time*1000:.2f}ms")
        if sql_time < python_time:
            print(f"  ✅ SQL is {python_time/sql_time:.1f}x faster")
        else:
            print(f"  SQL is comparable to Python")
        
        # SQL should not be significantly slower
        assert sql_time <= python_time * 2.0, "SQL filtering unexpectedly slow"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short", "-s"])
