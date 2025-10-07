"""Service for database maintenance operations."""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict

from ..connection import DatabaseConnection
from ..constants import DEFAULT_CLEANUP_DAYS

logger = logging.getLogger(__name__)


class DatabaseMaintenanceService:
    """Service for database cleanup and optimization."""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def cleanup_old_data(self, days: int = DEFAULT_CLEANUP_DAYS) -> Dict[str, int]:
        """
        Clean up data older than specified days.
        
        Args:
            days: Number of days to keep (default from constants)
            
        Returns:
            Dict containing:
                - test_rows_deleted: Number of test results deleted
                - session_rows_deleted: Number of sessions deleted
                - vacuumed: Whether database was vacuumed
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Delete old data within a transaction
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Clean old test results
            cursor.execute(
                'DELETE FROM test_results WHERE timestamp < ?',
                (cutoff_date,)
            )
            test_rows_deleted = cursor.rowcount
            
            # Clean old sessions
            cursor.execute(
                'DELETE FROM sessions WHERE timestamp < ?',
                (cutoff_date,)
            )
            session_rows_deleted = cursor.rowcount
        
        # VACUUM outside transaction (required by SQLite)
        vacuumed = False
        if test_rows_deleted > 0 or session_rows_deleted > 0:
            with self.db.get_connection() as conn:
                conn.isolation_level = None  # Autocommit mode for VACUUM
                cursor = conn.cursor()
                cursor.execute("VACUUM")
                conn.isolation_level = ""  # Restore default
                vacuumed = True
        
        logger.info(
            f"Cleaned up old data (days={days}, "
            f"test_results={test_rows_deleted}, "
            f"sessions={session_rows_deleted}, "
            f"vacuumed={vacuumed})"
        )
        
        return {
            'test_rows_deleted': test_rows_deleted,
            'session_rows_deleted': session_rows_deleted,
            'vacuumed': vacuumed
        }
    
    def optimize_database(self) -> Dict[str, float]:
        """
        Optimize database by reclaiming unused space (VACUUM).
        
        This should be called after deleting large amounts of data.
        VACUUM rebuilds the database file, reclaiming space from deleted records.
        
        Returns:
            Dict containing:
                - size_before_bytes: Database size before optimization (bytes)
                - size_after_bytes: Database size after optimization (bytes)
                - space_saved_bytes: Space saved (bytes)
                - size_before_mb: Database size before optimization (MB)
                - size_after_mb: Database size after optimization (MB)
                - space_saved_mb: Space saved (MB)
        """
        # Get size before
        size_before = 0
        if os.path.exists(self.db.db_path):
            size_before = os.path.getsize(self.db.db_path)
        
        # VACUUM must run outside a transaction
        with self.db.get_connection() as conn:
            conn.isolation_level = None  # Autocommit mode for VACUUM
            cursor = conn.cursor()
            cursor.execute("VACUUM")
            conn.isolation_level = ""  # Restore default
        
        # Get size after
        size_after = 0
        if os.path.exists(self.db.db_path):
            size_after = os.path.getsize(self.db.db_path)
        
        space_saved = size_before - size_after
        space_saved_mb = space_saved / (1024 * 1024)
        
        logger.info(
            f"Database optimized: "
            f"{size_before/1024/1024:.2f} MB → {size_after/1024/1024:.2f} MB "
            f"(saved {space_saved_mb:.2f} MB)"
        )
        
        return {
            'size_before_bytes': size_before,
            'size_after_bytes': size_after,
            'space_saved_bytes': space_saved,
            'size_before_mb': round(size_before / (1024 * 1024), 2),
            'size_after_mb': round(size_after / (1024 * 1024), 2),
            'space_saved_mb': round(space_saved_mb, 2)
        }
