"""
Migration 001: Fix Test Type Naming Inconsistency

Changes:
- 'stress' → 'comparison'
- 'tle' → 'benchmark'
- 'validator' → 'validator' (no change)

This fixes the critical naming inconsistency where test types were initialized
with one name but saved to database with different names.
"""
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("migration")


def migrate_test_types(db_path: str = None) -> bool:
    """
    Migrate test types from old to new naming convention.
    
    Args:
        db_path: Path to database file. If None, uses default location.
        
    Returns:
        True if migration successful, False otherwise
    """
    if db_path is None:
        db_path = Path.home() / ".code_testing_suite" / "code_testing_suite.db"
    
    logger.info("=" * 80)
    logger.info("MIGRATION 001: Fix Test Type Naming")
    logger.info(f"Database: {db_path}")
    logger.info(f"Started: {datetime.now().isoformat()}")
    logger.info("=" * 80)
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_results'")
        if not cursor.fetchone():
            logger.warning("test_results table does not exist - nothing to migrate")
            conn.close()
            return True
        
        # Check counts before migration
        cursor.execute("SELECT test_type, COUNT(*) FROM test_results GROUP BY test_type")
        before_counts = dict(cursor.fetchall())
        logger.info(f"Before migration: {before_counts}")
        
        total_records = sum(before_counts.values())
        logger.info(f"Total records: {total_records}")
        
        # Update 'stress' → 'comparison'
        cursor.execute("UPDATE test_results SET test_type = 'comparison' WHERE test_type = 'stress'")
        stress_updated = cursor.rowcount
        logger.info(f"Updated {stress_updated} records: 'stress' → 'comparison'")
        
        # Update 'tle' → 'benchmark'
        cursor.execute("UPDATE test_results SET test_type = 'tle' WHERE test_type = 'benchmark'")
        tle_updated = cursor.rowcount
        logger.info(f"Updated {tle_updated} records: 'tle' → 'benchmark'")
        
        # Commit changes
        conn.commit()
        logger.info("Changes committed to database")
        
        # Verify after migration
        cursor.execute("SELECT test_type, COUNT(*) FROM test_results GROUP BY test_type")
        after_counts = dict(cursor.fetchall())
        logger.info(f"After migration: {after_counts}")
        
        # Verify total count unchanged
        total_after = sum(after_counts.values())
        if total_after != total_records:
            logger.error(f"Record count mismatch! Before: {total_records}, After: {total_after}")
            conn.close()
            return False
        
        # Verify no old naming remains
        old_types = [t for t in after_counts.keys() if t in ['stress', 'tle']]
        if old_types:
            logger.warning(f"Old test types still exist: {old_types}")
        
        # Verify new naming present
        new_types = [t for t in after_counts.keys() if t in ['comparison', 'benchmark', 'validator']]
        logger.info(f"New test types present: {new_types}")
        
        conn.close()
        
        logger.info("=" * 80)
        logger.info("MIGRATION 001: COMPLETED SUCCESSFULLY")
        logger.info(f"Finished: {datetime.now().isoformat()}")
        logger.info("=" * 80)
        
        return True
        
    except sqlite3.Error as e:
        logger.error(f"Migration failed with database error: {e}", exc_info=True)
        return False
        
    except Exception as e:
        logger.error(f"Migration failed with unexpected error: {e}", exc_info=True)
        return False


def rollback_test_types(db_path: str = None) -> bool:
    """
    Rollback test type naming to old convention.
    
    WARNING: This should only be used if you need to revert the migration.
    
    Args:
        db_path: Path to database file. If None, uses default location.
        
    Returns:
        True if rollback successful, False otherwise
    """
    if db_path is None:
        db_path = Path.home() / ".code_testing_suite" / "code_testing_suite.db"
    
    logger.warning("=" * 80)
    logger.warning("MIGRATION 001: ROLLBACK - Reverting to old naming")
    logger.warning(f"Database: {db_path}")
    logger.warning(f"Started: {datetime.now().isoformat()}")
    logger.warning("=" * 80)
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check counts before rollback
        cursor.execute("SELECT test_type, COUNT(*) FROM test_results GROUP BY test_type")
        before_counts = dict(cursor.fetchall())
        logger.warning(f"Before rollback: {before_counts}")
        
        # Rollback: 'comparison' → 'stress'
        cursor.execute("UPDATE test_results SET test_type = 'stress' WHERE test_type = 'comparison'")
        comparison_rolled = cursor.rowcount
        logger.warning(f"Rolled back {comparison_rolled} records: 'comparison' → 'stress'")
        
        # Rollback: 'benchmark' → 'tle'
        cursor.execute("UPDATE test_results SET test_type = 'tle' WHERE test_type = 'benchmark'")
        benchmark_rolled = cursor.rowcount
        logger.warning(f"Rolled back {benchmark_rolled} records: 'benchmark' → 'tle'")
        
        conn.commit()
        logger.warning("Rollback committed to database")
        
        # Verify after rollback
        cursor.execute("SELECT test_type, COUNT(*) FROM test_results GROUP BY test_type")
        after_counts = dict(cursor.fetchall())
        logger.warning(f"After rollback: {after_counts}")
        
        conn.close()
        
        logger.warning("=" * 80)
        logger.warning("MIGRATION 001: ROLLBACK COMPLETED")
        logger.warning(f"Finished: {datetime.now().isoformat()}")
        logger.warning("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"Rollback failed: {e}", exc_info=True)
        return False


def verify_migration(db_path: str = None) -> dict:
    """
    Verify migration was successful.
    
    Args:
        db_path: Path to database file. If None, uses default location.
        
    Returns:
        Dict with verification results
    """
    if db_path is None:
        db_path = Path.home() / ".code_testing_suite" / "code_testing_suite.db"
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all test types
        cursor.execute("SELECT DISTINCT test_type FROM test_results")
        test_types = [row[0] for row in cursor.fetchall()]
        
        # Check for old naming
        has_old_naming = any(t in ['stress', 'tle'] for t in test_types)
        
        # Check for new naming
        has_new_naming = any(t in ['comparison', 'benchmark'] for t in test_types)
        
        # Get counts
        cursor.execute("SELECT test_type, COUNT(*) FROM test_results GROUP BY test_type")
        counts = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'success': not has_old_naming and (has_new_naming or 'validator' in test_types),
            'test_types': test_types,
            'has_old_naming': has_old_naming,
            'has_new_naming': has_new_naming,
            'counts': counts
        }
        
    except Exception as e:
        logger.error(f"Verification failed: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == "__main__":
    # Setup logging for standalone execution
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
    
    from src.app.core.config.logging_config import setup_migration_logging
    
    logger = setup_migration_logging()
    
    # Run migration
    print("\n" + "=" * 80)
    print("Running Migration 001: Fix Test Type Naming")
    print("=" * 80 + "\n")
    
    # Check if database exists
    db_path = Path.home() / ".code_testing_suite" / "code_testing_suite.db"
    
    if not db_path.exists():
        print(f"⚠️  Database not found at: {db_path}")
        print("Creating test database for demonstration...")
        
        # Create test database
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)
        
        # Initialize database
        from src.app.persistence.database.database_manager import DatabaseManager
        db = DatabaseManager(str(db_path))
        
        # Add sample old data
        from tests.fixtures.generate_test_data import generate_old_format_results
        old_results = generate_old_format_results(10)
        for result in old_results:
            db.save_test_result(result)
        
        print(f"✓ Test database created with sample data")
    
    # Show before state
    print("\n📊 Before Migration:")
    before_verify = verify_migration(str(db_path))
    print(f"  Test types: {before_verify['test_types']}")
    print(f"  Counts: {before_verify['counts']}")
    
    # Run migration
    print("\n🔄 Running migration...")
    success = migrate_test_types(str(db_path))
    
    if success:
        print("\n✅ Migration completed successfully!")
        
        # Show after state
        print("\n📊 After Migration:")
        after_verify = verify_migration(str(db_path))
        print(f"  Test types: {after_verify['test_types']}")
        print(f"  Counts: {after_verify['counts']}")
        print(f"  Has old naming: {after_verify['has_old_naming']}")
        print(f"  Has new naming: {after_verify['has_new_naming']}")
        
        if after_verify['success']:
            print("\n✨ Verification: PASSED")
        else:
            print("\n⚠️  Verification: FAILED")
    else:
        print("\n❌ Migration failed! Check logs for details.")
    
    print("\n" + "=" * 80)
