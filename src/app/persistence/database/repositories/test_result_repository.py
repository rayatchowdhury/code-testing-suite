"""TestResult repository - CRUD operations for test results.

This repository handles all database operations for test results,
providing a clean abstraction layer with filtering capabilities.

Phase 5: Migrate TestResult Operations
"""

from typing import List, Optional
from datetime import datetime, timedelta
import logging

from .base_repository import BaseRepository
from ..models import TestResult
from ..constants import DEFAULT_RESULTS_LIMIT, STATUS_PASSED, STATUS_FAILED
from ..exceptions import RepositoryError

logger = logging.getLogger(__name__)


class TestResultRepository(BaseRepository[TestResult]):
    """
    Repository for TestResult CRUD operations.
    
    Provides:
    - Save test results with automatic timestamp
    - Retrieve by ID
    - Advanced filtering (type, project, days, file name, status)
    - Delete operations with logging
    - Bulk delete with confirmation
    
    Example:
        repo = TestResultRepository()
        
        # Save
        result = TestResult(test_type="comparison", file_path="/test.cpp", ...)
        result_id = repo.save(result)
        
        # Get with filters
        recent_results = repo.get_all(days=7, status="passed")
        
        # Delete
        repo.delete(result_id)
    """
    
    def save(self, result: TestResult) -> int:
        """
        Save test result to database.
        
        If result.timestamp is None, automatically sets to current timestamp.
        
        Args:
            result: TestResult to save
            
        Returns:
            Inserted row ID
            
        Raises:
            RepositoryError: If save fails
            
        Example:
            result = TestResult(
                test_type="comparison",
                file_path="/test/solution.cpp",
                test_count=10,
                passed_tests=8,
                failed_tests=2,
                total_time=5.5,
                project_name="MyProject"
            )
            result_id = repo.save(result)
        """
        query = '''
            INSERT INTO test_results 
            (test_type, file_path, test_count, passed_tests, failed_tests, 
             total_time, timestamp, test_details, project_name, files_snapshot, mismatch_analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        cursor = self._execute_query(query, (
            result.test_type,
            result.file_path,
            result.test_count,
            result.passed_tests,
            result.failed_tests,
            result.total_time,
            result.timestamp or datetime.now().isoformat(),
            result.test_details or "",
            result.project_name or "",
            result.files_snapshot or "",
            result.mismatch_analysis or ""
        ))
        
        result_id = cursor.lastrowid
        logger.info(
            f"Saved test result #{result_id} "
            f"(type={result.test_type}, project={result.project_name}, "
            f"passed={result.passed_tests}/{result.test_count})"
        )
        return result_id
    
    def get_by_id(self, id: int) -> Optional[TestResult]:
        """
        Get test result by ID.
        
        Args:
            id: Test result ID
            
        Returns:
            TestResult if found, None otherwise
            
        Raises:
            RepositoryError: If query fails
        """
        query = 'SELECT * FROM test_results WHERE id = ?'
        row = self._execute_query(query, (id,), fetch_one=True)
        
        if row:
            logger.debug(f"Retrieved test result #{id}")
            return self._row_to_entity(row)
        
        logger.debug(f"Test result #{id} not found")
        return None
    
    def get_all(self, 
                test_type: str = None,
                project_name: str = None,
                days: int = None,
                file_name: str = None,
                status: str = None,
                limit: int = DEFAULT_RESULTS_LIMIT) -> List[TestResult]:
        """
        Get test results with advanced filtering.
        
        All filters are optional and can be combined.
        Results are ordered by timestamp (newest first).
        
        Args:
            test_type: Filter by test type (exact match)
            project_name: Filter by project name (LIKE - partial match)
            days: Filter results from last N days
            file_name: Filter by file name (LIKE - partial match)
            status: Filter by status ('passed' or 'failed')
            limit: Maximum number of results to return
            
        Returns:
            List of TestResult objects (may be empty)
            
        Raises:
            RepositoryError: If query fails
            
        Example:
            # Get all comparison tests from last 7 days that passed
            results = repo.get_all(
                test_type="comparison",
                days=7,
                status="passed",
                limit=50
            )
            
            # Get all tests for a specific project
            results = repo.get_all(project_name="MyProject")
        """
        query = "SELECT * FROM test_results"
        params = []
        conditions = []
        
        # Build WHERE conditions
        if test_type:
            conditions.append("test_type = ?")
            params.append(test_type)
        
        if project_name:
            conditions.append("project_name LIKE ?")
            params.append(f"%{project_name}%")
        
        if days:
            # Add 1 second to ensure we include results from exactly 'days' ago
            cutoff = (datetime.now() - timedelta(days=days, seconds=1)).isoformat()
            conditions.append("timestamp >= ?")
            params.append(cutoff)
        
        if file_name:
            conditions.append("file_path LIKE ?")
            params.append(f"%{file_name}%")
        
        if status == STATUS_PASSED:
            # Passed = all tests passed
            conditions.append("passed_tests = test_count")
        elif status == STATUS_FAILED:
            # Failed = at least one test failed
            conditions.append("failed_tests > 0")
        
        # Combine conditions
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        # Order by newest first and apply limit
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        # Execute query
        cursor = self._execute_query(query, tuple(params))
        results = [self._row_to_entity(row) for row in cursor.fetchall()]
        
        logger.info(
            f"Retrieved {len(results)} test results "
            f"(filters: type={test_type}, project={project_name}, "
            f"days={days}, file={file_name}, status={status})"
        )
        return results
    
    def delete(self, id: int) -> bool:
        """
        Delete test result by ID.
        
        Args:
            id: Test result ID to delete
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            RepositoryError: If deletion fails
        """
        # Check if exists first
        if not self.exists("test_results", id):
            logger.warning(f"Test result ID {id} not found for deletion")
            return False
        
        # Delete
        self._execute_query('DELETE FROM test_results WHERE id = ?', (id,))
        logger.info(f"Deleted test result ID {id}")
        return True
    
    def delete_all(self, confirm: bool = False) -> bool:
        """
        Delete all test results from database.
        
        This is a destructive operation that requires explicit confirmation.
        Also resets the auto-increment counter.
        
        Args:
            confirm: Must be True to proceed with deletion
            
        Returns:
            True if deleted, False if not confirmed
            
        Raises:
            RepositoryError: If deletion fails
            
        Example:
            # Wrong - will not delete
            repo.delete_all()  # Returns False
            
            # Correct - explicitly confirm
            repo.delete_all(confirm=True)  # Deletes all
        """
        if not confirm:
            logger.warning("delete_all() called without confirm=True - no action taken")
            return False
        
        # Delete all records
        self._execute_query("DELETE FROM test_results")
        
        # Reset auto-increment counter
        self._execute_query("DELETE FROM sqlite_sequence WHERE name='test_results'")
        
        logger.warning("Deleted ALL test results from database")
        return True
    
    def get_by_project(self, project_name: str, limit: int = DEFAULT_RESULTS_LIMIT) -> List[TestResult]:
        """
        Get all test results for a specific project.
        
        Convenience method that calls get_all() with project filter.
        
        Args:
            project_name: Exact project name to filter by
            limit: Maximum results
            
        Returns:
            List of TestResult objects for the project
        """
        return self.get_all(project_name=project_name, limit=limit)
    
    def get_recent(self, days: int = 7, limit: int = DEFAULT_RESULTS_LIMIT) -> List[TestResult]:
        """
        Get recent test results from last N days.
        
        Convenience method that calls get_all() with days filter.
        
        Args:
            days: Number of days to look back
            limit: Maximum results
            
        Returns:
            List of recent TestResult objects
        """
        return self.get_all(days=days, limit=limit)
    
    def count_by_status(self, status: str) -> int:
        """
        Count test results by status.
        
        Args:
            status: 'passed' or 'failed'
            
        Returns:
            Count of test results with given status
        """
        if status == STATUS_PASSED:
            return self.count("test_results", "passed_tests = test_count")
        elif status == STATUS_FAILED:
            return self.count("test_results", "failed_tests > 0")
        else:
            return 0
    
    def _row_to_entity(self, row) -> TestResult:
        """
        Convert database row to TestResult object.
        
        Args:
            row: sqlite3.Row from query
            
        Returns:
            TestResult instance
        """
        # sqlite3.Row doesn't support .get(), so we check key existence
        row_keys = row.keys()
        
        return TestResult(
            id=row['id'],
            test_type=row['test_type'],
            file_path=row['file_path'],
            test_count=row['test_count'],
            passed_tests=row['passed_tests'],
            failed_tests=row['failed_tests'],
            total_time=row['total_time'],
            timestamp=row['timestamp'],
            test_details=row['test_details'],
            project_name=row['project_name'],
            files_snapshot=row['files_snapshot'] if 'files_snapshot' in row_keys else '',
            mismatch_analysis=row['mismatch_analysis'] if 'mismatch_analysis' in row_keys else ''
        )
