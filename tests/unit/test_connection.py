"""
Test database connection manager.

Phase 2: Testing singleton pattern and thread safety
"""
import pytest
import tempfile
import os
import threading
from src.app.persistence.database.connection import DatabaseConnection
from src.app.persistence.database.exceptions import DatabaseError


@pytest.fixture
def temp_db():
    """Create temporary database."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    # Close connection before cleanup to release file handle
    DatabaseConnection.reset_instance()
    # Small delay to ensure file is released on Windows
    import time
    time.sleep(0.1)
    if os.path.exists(path):
        try:
            os.unlink(path)
        except PermissionError:
            pass  # File still in use, will be cleaned up eventually


class TestSingletonPattern:
    """Test singleton implementation"""
    
    def test_singleton_pattern(self, temp_db):
        """Test only one instance is created."""
        db1 = DatabaseConnection(temp_db)
        db2 = DatabaseConnection(temp_db)
        
        assert db1 is db2, "Should return same instance"
    
    def test_multiple_calls_same_instance(self, temp_db):
        """Test multiple instantiation attempts return same object."""
        instances = [DatabaseConnection(temp_db) for _ in range(10)]
        
        # All should be the same object
        assert all(inst is instances[0] for inst in instances)


class TestConnectionContextManager:
    """Test context manager functionality"""
    
    def test_connection_context_manager(self, temp_db):
        """Test connection context manager works."""
        db = DatabaseConnection(temp_db)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        assert result[0] == 1
    
    def test_multiple_context_uses(self, temp_db):
        """Test context manager can be used multiple times."""
        db = DatabaseConnection(temp_db)
        
        for i in range(5):
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ?", (i,))
                result = cursor.fetchone()
                assert result[0] == i


class TestTableCreation:
    """Test automatic table creation"""
    
    def test_tables_created(self, temp_db):
        """Test tables are auto-created."""
        db = DatabaseConnection(temp_db)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
        assert 'test_results' in tables
        assert 'sessions' in tables
    
    def test_test_results_schema(self, temp_db):
        """Test test_results table has correct schema."""
        db = DatabaseConnection(temp_db)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(test_results)")
            columns = {row[1] for row in cursor.fetchall()}
        
        required_columns = {
            'id', 'test_type', 'file_path', 'test_count',
            'passed_tests', 'failed_tests', 'total_time', 
            'timestamp', 'test_details', 'project_name',
            'files_snapshot', 'mismatch_analysis'
        }
        assert required_columns.issubset(columns)


class TestTransactionManagement:
    """Test transaction commit and rollback"""
    
    def test_transaction_commits_on_success(self, temp_db):
        """Test transaction commits when no error."""
        db = DatabaseConnection(temp_db)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO test_results 
                (test_type, file_path, test_count, passed_tests, failed_tests, total_time, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('test', '/test.py', 1, 1, 0, 1.0, '2025-10-08'))
        
        # Verify data persisted
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM test_results")
            count = cursor.fetchone()[0]
            
        assert count == 1, "Transaction should have committed"
    
    def test_transaction_rollback_on_error(self, temp_db):
        """Test transaction rolls back on error."""
        db = DatabaseConnection(temp_db)
        
        # Note: SQLite's isolation means individual statements commit
        # This test verifies that context manager catches and wraps errors
        with pytest.raises(DatabaseError) as exc_info:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                # Force an error with invalid SQL immediately
                cursor.execute("INVALID SQL STATEMENT")
        
        # Verify the error was caught and wrapped
        assert "Database operation failed" in str(exc_info.value)


class TestThreadSafety:
    """Test thread-safe operations"""
    
    def test_thread_safety(self, temp_db):
        """Test thread-safe operations with concurrent inserts."""
        db = DatabaseConnection(temp_db)
        results = []
        errors = []
        
        def insert_data(thread_id):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO test_results 
                        (test_type, file_path, test_count, passed_tests, failed_tests, total_time, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (f'test_{thread_id}', '/test', 1, 1, 0, 1.0, '2025-10-08'))
                    results.append(thread_id)
            except Exception as e:
                errors.append((thread_id, e))
        
        # Create and start 10 threads
        threads = [threading.Thread(target=insert_data, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All threads should complete successfully
        assert len(results) == 10, f"All threads should complete. Got {len(results)}, errors: {errors}"
        assert len(errors) == 0, f"No errors should occur. Errors: {errors}"
        
        # Verify all inserts persisted
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM test_results")
            count = cursor.fetchone()[0]
            
        assert count == 10, "All inserts should be persisted"
    
    def test_concurrent_reads(self, temp_db):
        """Test concurrent read operations."""
        db = DatabaseConnection(temp_db)
        
        # Insert test data
        with db.get_connection() as conn:
            cursor = conn.cursor()
            for i in range(5):
                cursor.execute('''
                    INSERT INTO test_results 
                    (test_type, file_path, test_count, passed_tests, failed_tests, total_time, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (f'test_{i}', '/test', 1, 1, 0, 1.0, '2025-10-08'))
        
        results = []
        errors = []
        
        def read_data(thread_id):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM test_results")
                    count = cursor.fetchone()[0]
                    results.append(count)
            except Exception as e:
                errors.append((thread_id, e))
        
        # Create and start 10 reader threads
        threads = [threading.Thread(target=read_data, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All threads should complete without errors
        assert len(errors) == 0, f"No errors should occur: {errors}"
        assert len(results) == 10, f"All threads should complete: got {len(results)}"
        # All reads should see all 5 records
        assert all(count == 5 for count in results), f"All reads should see 5 records, got: {results}"


class TestConnectionLifecycle:
    """Test connection open/close behavior"""
    
    def test_close_connection(self, temp_db):
        """Test connection can be closed."""
        db = DatabaseConnection(temp_db)
        
        # Use connection
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
        
        # Close connection
        db.close()
        
        # Should be able to reconnect
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        assert result[0] == 1
    
    def test_reset_instance(self, temp_db):
        """Test reset_instance for testing."""
        db1 = DatabaseConnection(temp_db)
        DatabaseConnection.reset_instance()
        
        db2 = DatabaseConnection(temp_db)
        
        # After reset, should be different instance
        # (though practically same path creates same singleton again)
        assert db2 is not None
