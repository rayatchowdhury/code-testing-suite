"""
Migration 002: Add Database Constraints and Indexes

Changes:
- Add CHECK constraint for test_type (must be 'validator', 'comparison', or 'benchmark')
- Add CHECK constraint for test_count >= 0
- Add CHECK constraint for passed_tests >= 0
- Add CHECK constraint for failed_tests >= 0
- Add CHECK constraint for total_time >= 0
- Add CHECK constraint for passed_tests + failed_tests <= test_count
- Make project_name NOT NULL
- Add performance indexes on test_type, timestamp, project_name

This fixes the lack of data validation that allows invalid data into the database.
"""
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("migration")


def add_constraints_and_indexes(db_path: str = None) -> bool:
    """
    Add database constraints and performance indexes.
    
    Creates a new table with constraints, copies data, drops old table, renames new table.
    
    Args:
        db_path: Path to database file. If None, uses default location.
        
    Returns:
        True if migration successful, False otherwise
    """
    if db_path is None:
        db_path = Path.home() / ".code_testing_suite" / "code_testing_suite.db"
    
    logger.info("=" * 80)
    logger.info("MIGRATION 002: Add Database Constraints and Indexes")
    logger.info(f"Database: {db_path}")
    logger.info(f"Started: {datetime.now().isoformat()}")
    logger.info("=" * 80)
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_results'")
        if not cursor.fetchone():
            logger.warning("test_results table does not exist - creating fresh table with constraints")
            _create_fresh_table(conn)
            conn.close()
            return True
        
        # Count records before migration
        cursor.execute("SELECT COUNT(*) FROM test_results")
        record_count = cursor.fetchone()[0]
        logger.info(f"Records to migrate: {record_count}")
        
        # Check if constraints already exist (by trying to insert invalid data)
        try:
            cursor.execute("""
                INSERT INTO test_results (test_type, file_path, test_count, passed_tests, failed_tests, total_time, timestamp, project_name)
                VALUES ('invalid', 'test.cpp', -1, 0, 0, 0, '2025-01-01', 'Test')
            """)
            # If this succeeds, constraints don't exist yet
            cursor.execute("DELETE FROM test_results WHERE test_type = 'invalid'")
            logger.info("No constraints detected - proceeding with migration")
            has_constraints = False
        except sqlite3.IntegrityError:
            logger.info("Constraints already exist - skipping migration")
            conn.close()
            return True
        
        # Create new table with constraints
        logger.info("Creating new table with constraints...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_results_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_type TEXT NOT NULL CHECK(test_type IN ('validator', 'comparison', 'benchmark')),
                file_path TEXT NOT NULL,
                test_count INTEGER NOT NULL CHECK(test_count >= 0),
                passed_tests INTEGER NOT NULL CHECK(passed_tests >= 0),
                failed_tests INTEGER NOT NULL CHECK(failed_tests >= 0),
                total_time REAL NOT NULL CHECK(total_time >= 0),
                timestamp TEXT NOT NULL,
                test_details TEXT,
                project_name TEXT NOT NULL,
                files_snapshot TEXT,
                mismatch_analysis TEXT,
                CHECK(passed_tests + failed_tests <= test_count)
            )
        """)
        logger.info("✓ New table created with constraints")
        
        # Copy valid data from old table
        logger.info("Copying data to new table...")
        
        # First, validate existing data
        cursor.execute("""
            SELECT COUNT(*) FROM test_results 
            WHERE test_type NOT IN ('validator', 'comparison', 'benchmark', 'stress', 'tle')
        """)
        invalid_types = cursor.fetchone()[0]
        
        if invalid_types > 0:
            logger.warning(f"Found {invalid_types} records with invalid test types")
            logger.warning("These records will be skipped")
        
        # Copy data (filtering out invalid records)
        # Only copy the 12 columns we need
        cursor.execute("""
            INSERT INTO test_results_new 
            (id, test_type, file_path, test_count, passed_tests, failed_tests, 
             total_time, timestamp, test_details, project_name, files_snapshot, mismatch_analysis)
            SELECT id, test_type, file_path, test_count, passed_tests, failed_tests,
                   total_time, timestamp, test_details, project_name, files_snapshot, mismatch_analysis
            FROM test_results
            WHERE test_type IN ('validator', 'comparison', 'benchmark')
            AND test_count >= 0
            AND passed_tests >= 0
            AND failed_tests >= 0
            AND total_time >= 0
            AND passed_tests + failed_tests <= test_count
            AND project_name IS NOT NULL
        """)
        copied_count = cursor.rowcount
        logger.info(f"✓ Copied {copied_count}/{record_count} valid records")
        
        if copied_count < record_count:
            skipped = record_count - copied_count
            logger.warning(f"Skipped {skipped} invalid records")
        
        # Drop old table
        logger.info("Dropping old table...")
        cursor.execute("DROP TABLE test_results")
        logger.info("✓ Old table dropped")
        
        # Rename new table
        logger.info("Renaming new table...")
        cursor.execute("ALTER TABLE test_results_new RENAME TO test_results")
        logger.info("✓ Table renamed")
        
        # Create indexes
        logger.info("Creating performance indexes...")
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_type ON test_results(test_type)")
        logger.info("✓ Created index on test_type")
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON test_results(timestamp DESC)")
        logger.info("✓ Created index on timestamp")
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_project_name ON test_results(project_name)")
        logger.info("✓ Created index on project_name")
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_type_timestamp ON test_results(test_type, timestamp DESC)")
        logger.info("✓ Created compound index on test_type + timestamp")
        
        # Commit all changes
        conn.commit()
        logger.info("✓ All changes committed")
        
        # Verify constraints
        logger.info("Verifying constraints...")
        
        # Try to insert invalid data - should fail
        constraint_tests = [
            ("Invalid test type", "INSERT INTO test_results (test_type, file_path, test_count, passed_tests, failed_tests, total_time, timestamp, project_name) VALUES ('invalid', 'test.cpp', 1, 0, 0, 1.0, '2025-01-01', 'Test')"),
            ("Negative test count", "INSERT INTO test_results (test_type, file_path, test_count, passed_tests, failed_tests, total_time, timestamp, project_name) VALUES ('validator', 'test.cpp', -1, 0, 0, 1.0, '2025-01-01', 'Test')"),
            ("Negative time", "INSERT INTO test_results (test_type, file_path, test_count, passed_tests, failed_tests, total_time, timestamp, project_name) VALUES ('validator', 'test.cpp', 1, 0, 0, -1.0, '2025-01-01', 'Test')"),
            ("Passed + failed > total", "INSERT INTO test_results (test_type, file_path, test_count, passed_tests, failed_tests, total_time, timestamp, project_name) VALUES ('validator', 'test.cpp', 10, 8, 5, 1.0, '2025-01-01', 'Test')"),
        ]
        
        constraints_working = True
        for test_name, query in constraint_tests:
            try:
                cursor.execute(query)
                logger.error(f"✗ Constraint failed: {test_name} was accepted!")
                constraints_working = False
            except sqlite3.IntegrityError:
                logger.info(f"✓ Constraint working: {test_name} rejected")
        
        conn.close()
        
        if not constraints_working:
            logger.error("Some constraints are not working properly!")
            return False
        
        logger.info("=" * 80)
        logger.info("MIGRATION 002: COMPLETED SUCCESSFULLY")
        logger.info(f"Records migrated: {copied_count}")
        logger.info(f"Indexes created: 4")
        logger.info(f"Constraints verified: ✓")
        logger.info(f"Finished: {datetime.now().isoformat()}")
        logger.info("=" * 80)
        
        return True
        
    except sqlite3.Error as e:
        logger.error(f"Migration failed with database error: {e}", exc_info=True)
        return False
        
    except Exception as e:
        logger.error(f"Migration failed with unexpected error: {e}", exc_info=True)
        return False


def _create_fresh_table(conn):
    """Create fresh table with constraints (for new installations)"""
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_type TEXT NOT NULL CHECK(test_type IN ('validator', 'comparison', 'benchmark')),
            file_path TEXT NOT NULL,
            test_count INTEGER NOT NULL CHECK(test_count >= 0),
            passed_tests INTEGER NOT NULL CHECK(passed_tests >= 0),
            failed_tests INTEGER NOT NULL CHECK(failed_tests >= 0),
            total_time REAL NOT NULL CHECK(total_time >= 0),
            timestamp TEXT NOT NULL,
            test_details TEXT,
            project_name TEXT NOT NULL,
            files_snapshot TEXT,
            mismatch_analysis TEXT,
            CHECK(passed_tests + failed_tests <= test_count)
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_type ON test_results(test_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON test_results(timestamp DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_project_name ON test_results(project_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_type_timestamp ON test_results(test_type, timestamp DESC)")
    
    conn.commit()
    logger.info("✓ Fresh table created with constraints and indexes")


def verify_constraints(db_path: str = None) -> dict:
    """
    Verify that constraints are properly enforced.
    
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
        
        # Check if indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='test_results'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        has_indexes = all(idx in indexes for idx in [
            'idx_test_type', 'idx_timestamp', 'idx_project_name', 'idx_test_type_timestamp'
        ])
        
        # Try to insert invalid data
        constraints_work = False
        try:
            cursor.execute("""
                INSERT INTO test_results (test_type, file_path, test_count, passed_tests, failed_tests, total_time, timestamp, project_name)
                VALUES ('invalid_type', 'test.cpp', 1, 0, 0, 1.0, '2025-01-01', 'Test')
            """)
        except sqlite3.IntegrityError:
            constraints_work = True
        
        conn.close()
        
        return {
            'success': has_indexes and constraints_work,
            'has_indexes': has_indexes,
            'indexes': indexes,
            'constraints_work': constraints_work
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
    print("Running Migration 002: Add Database Constraints and Indexes")
    print("=" * 80 + "\n")
    
    # Use default database path
    db_path = Path.home() / ".code_testing_suite" / "code_testing_suite.db"
    
    if not db_path.exists():
        print(f"⚠️  Database not found at: {db_path}")
        print("Migration will create a fresh table with constraints.")
    
    # Run migration
    print("\n🔄 Running migration...")
    success = add_constraints_and_indexes(str(db_path))
    
    if success:
        print("\n✅ Migration completed successfully!")
        
        # Verify
        print("\n📊 Verifying constraints and indexes...")
        verify_result = verify_constraints(str(db_path))
        print(f"  Has indexes: {verify_result.get('has_indexes', False)}")
        print(f"  Indexes: {verify_result.get('indexes', [])}")
        print(f"  Constraints working: {verify_result.get('constraints_work', False)}")
        
        if verify_result['success']:
            print("\n✨ Verification: PASSED")
        else:
            print("\n⚠️  Verification: FAILED")
    else:
        print("\n❌ Migration failed! Check logs for details.")
    
    print("\n" + "=" * 80)
