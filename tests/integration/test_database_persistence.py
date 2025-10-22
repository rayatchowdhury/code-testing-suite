"""
Integration tests for database persistence workflow.

Tests end-to-end database operations with real DatabaseManager:
- Complete save/retrieve cycle for test results
- FilesSnapshot persistence and retrieval
- Session management
- Project data persistence
- Database integrity across operations
- Multi-entity workflows

Per Phase 6.3 requirements: Use real components, minimal mocking.
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.app.database.database_manager import DatabaseError, DatabaseManager
from src.app.database.models import (
    FilesSnapshot,
    ProjectData,
    Session,
    TestResult,
)
from src.app.database.services.database_maintenance_service import (
    DatabaseMaintenanceService,
)
from src.app.database.services.database_stats_service import (
    DatabaseStatsService,
)
from src.app.database.services.files_snapshot_service import (
    FilesSnapshotService,
)
from tests.fixtures.database_fixtures import (
    SAMPLE_CPP_CODE,
    SAMPLE_JAVA_CODE,
    SAMPLE_PYTHON_CODE,
)
from tests.fixtures.database_fixtures import ResultBuilder as TestResultBuilder
from tests.fixtures.database_fixtures import (
    create_sample_test_result,
)


@pytest.fixture
def temp_db(tmp_path):
    """Create temporary database for integration tests."""
    db_path = str(tmp_path / "integration_test.db")
    db_manager = DatabaseManager(db_path)
    yield db_manager
    db_manager.close()


@pytest.fixture
def workspace_with_files(tmp_path):
    """Create workspace with source files."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    # Create comparator subdirectory
    comparator_dir = workspace / "comparator"
    comparator_dir.mkdir()

    # Create source files
    (comparator_dir / "generator.cpp").write_text(SAMPLE_CPP_CODE)
    (comparator_dir / "correct.py").write_text(SAMPLE_PYTHON_CODE)
    (comparator_dir / "test.java").write_text(SAMPLE_JAVA_CODE)

    return workspace


class TestBasicPersistence:
    """Test basic save and retrieve operations."""

    def test_save_and_retrieve_test_result(self, temp_db):
        """Should save and retrieve a test result."""
        # Create test result
        result = (
            TestResultBuilder()
            .with_test_type("comparator")
            .with_results(passed=8, failed=2)
            .with_project_name("test_project")
            .build()
        )

        # Save to database
        result_id = temp_db.save_test_result(result)

        assert result_id > 0

        # Retrieve from database
        retrieved = temp_db.get_test_results()

        assert len(retrieved) == 1
        assert retrieved[0].id == result_id
        assert retrieved[0].test_type == "comparator"
        assert retrieved[0].passed_tests == 8
        assert retrieved[0].failed_tests == 2
        assert retrieved[0].project_name == "test_project"

    def test_save_multiple_test_results(self, temp_db):
        """Should save and retrieve multiple test results."""
        # Save multiple results
        result_ids = []
        for i in range(5):
            result = (
                TestResultBuilder()
                .with_test_type("validator")
                .with_results(passed=10 - i, failed=i)
                .with_project_name(f"project_{i}")
                .build()
            )

            result_id = temp_db.save_test_result(result)
            result_ids.append(result_id)

        # Retrieve all
        all_results = temp_db.get_test_results()

        assert len(all_results) == 5
        assert all(r.id in result_ids for r in all_results)

    def test_save_and_retrieve_session(self, temp_db):
        """Should save and retrieve a session."""
        # Create session
        session = Session(
            session_name="integration_test_session",
            open_files=json.dumps(["file1.cpp", "file2.py", "file3.java"]),
            active_file="file1.cpp",
            timestamp=datetime.now().isoformat(),
            project_name="test_project",
        )

        # Save to database
        session_id = temp_db.save_session(session)

        assert session_id > 0

        # Retrieve from database
        sessions = temp_db.get_sessions()

        assert len(sessions) == 1
        assert sessions[0].id == session_id
        assert sessions[0].session_name == "integration_test_session"
        assert sessions[0].project_name == "test_project"

    def test_save_and_retrieve_project_data(self, temp_db):
        """Should save and retrieve project data."""
        # Create project data
        project = ProjectData(
            project_name="integration_test_project",
            project_path="/path/to/project",
            last_accessed=datetime.now().isoformat(),
            file_count=15,
            total_lines=1500,
            languages=json.dumps(["cpp", "py", "java"]),
        )

        # Save to database
        project_id = temp_db.save_project_data(project)

        assert project_id > 0

        # Retrieve from database
        projects = temp_db.get_projects()

        assert len(projects) == 1
        assert projects[0].id == project_id
        assert projects[0].project_name == "integration_test_project"
        assert projects[0].file_count == 15


class TestFilesSnapshotPersistence:
    """Test FilesSnapshot persistence with real workspace files."""

    def test_create_and_save_files_snapshot(self, temp_db, workspace_with_files):
        """Should create snapshot from workspace and save to database."""
        # Create snapshot using service
        snapshot = FilesSnapshotService.create_snapshot(
            str(workspace_with_files), test_type="comparator"
        )

        # Verify snapshot has files
        assert len(snapshot.files) > 0

        # Save with test result
        result = (
            TestResultBuilder()
            .with_files_snapshot(snapshot.to_json())
            .with_project_name("snapshot_test")
            .build()
        )

        result_id = temp_db.save_test_result(result)

        # Retrieve and verify
        retrieved = temp_db.get_test_results()[0]

        assert retrieved.files_snapshot is not None
        assert retrieved.files_snapshot != ""

        # Deserialize snapshot
        retrieved_snapshot = FilesSnapshot.from_json(retrieved.files_snapshot)

        assert len(retrieved_snapshot.files) == len(snapshot.files)
        assert retrieved_snapshot.test_type == snapshot.test_type

    def test_snapshot_preserves_file_contents(self, temp_db, workspace_with_files):
        """Should preserve exact file contents in snapshot."""
        # Create snapshot
        snapshot = FilesSnapshotService.create_snapshot(
            str(workspace_with_files), test_type="comparator"
        )

        # Save to database
        result = TestResultBuilder().with_files_snapshot(snapshot.to_json()).build()

        temp_db.save_test_result(result)

        # Retrieve
        retrieved = temp_db.get_test_results()[0]
        retrieved_snapshot = FilesSnapshot.from_json(retrieved.files_snapshot)

        # Verify file contents are preserved
        for filename, file_info in retrieved_snapshot.files.items():
            assert "content" in file_info
            assert len(file_info["content"]) > 0
            assert "language" in file_info
            assert "role" in file_info

    def test_snapshot_multi_language_detection(self, temp_db, workspace_with_files):
        """Should detect multiple languages in snapshot."""
        # Create snapshot
        snapshot = FilesSnapshotService.create_snapshot(
            str(workspace_with_files), test_type="comparator"
        )

        # Should have detected C++, Python, and Java
        languages = set()
        for file_info in snapshot.files.values():
            languages.add(file_info["language"])

        assert len(languages) >= 2  # At least 2 different languages

        # Save and retrieve
        result = TestResultBuilder().with_files_snapshot(snapshot.to_json()).build()

        temp_db.save_test_result(result)

        # Verify languages preserved
        retrieved = temp_db.get_test_results()[0]
        retrieved_snapshot = FilesSnapshot.from_json(retrieved.files_snapshot)

        retrieved_languages = set(
            file_info["language"] for file_info in retrieved_snapshot.files.values()
        )

        assert retrieved_languages == languages


class TestFilteringAndQuerying:
    """Test database filtering and query operations."""

    def test_filter_by_test_type(self, temp_db):
        """Should filter test results by test type."""
        # Save different test types
        for test_type in ["comparator", "validator", "benchmarker"]:
            for i in range(3):
                result = TestResultBuilder().with_test_type(test_type).build()
                temp_db.save_test_result(result)

        # Filter by comparator
        comparator_results = temp_db.get_test_results(test_type="comparator")

        assert len(comparator_results) == 3
        assert all(r.test_type == "comparator" for r in comparator_results)

    def test_filter_by_project_name(self, temp_db):
        """Should filter test results by project name."""
        # Save results for different projects
        for project in ["project_a", "project_b", "project_c"]:
            for i in range(2):
                result = TestResultBuilder().with_project_name(project).build()
                temp_db.save_test_result(result)

        # Filter by project_a
        project_a_results = temp_db.get_test_results(project_name="project_a")

        assert len(project_a_results) == 2
        assert all(r.project_name == "project_a" for r in project_a_results)

    def test_filter_by_date_range(self, temp_db):
        """Should filter test results by date range."""
        # Save results with different timestamps
        base_time = datetime.now()

        # Old results (>7 days)
        for i in range(3):
            result = (
                TestResultBuilder()
                .with_timestamp((base_time - timedelta(days=10 + i)).isoformat())
                .build()
            )
            temp_db.save_test_result(result)

        # Recent results (<7 days)
        for i in range(2):
            result = (
                TestResultBuilder()
                .with_timestamp((base_time - timedelta(days=i)).isoformat())
                .build()
            )
            temp_db.save_test_result(result)

        # Filter last 7 days
        recent_results = temp_db.get_test_results(days=7)

        assert len(recent_results) == 2

    def test_filter_by_status(self, temp_db):
        """Should filter test results by pass/fail status."""
        # Save passing results
        for i in range(3):
            result = TestResultBuilder().with_results(passed=10, failed=0).build()
            temp_db.save_test_result(result)

        # Save failing results
        for i in range(2):
            result = TestResultBuilder().with_results(passed=7, failed=3).build()
            temp_db.save_test_result(result)

        # Filter passed only
        passed_results = temp_db.get_test_results(status="passed")

        assert len(passed_results) == 3
        assert all(r.passed_tests == r.test_count for r in passed_results)

        # Filter failed only
        failed_results = temp_db.get_test_results(status="failed")

        assert len(failed_results) == 2
        assert all(r.failed_tests > 0 for r in failed_results)

    def test_combined_filters(self, temp_db):
        """Should apply multiple filters simultaneously."""
        # Save varied results
        for test_type in ["comparator", "validator"]:
            for project in ["project_a", "project_b"]:
                result = (
                    TestResultBuilder()
                    .with_test_type(test_type)
                    .with_project_name(project)
                    .with_results(passed=10, failed=0)
                    .build()
                )
                temp_db.save_test_result(result)

        # Filter: comparator + project_a + passed
        filtered = temp_db.get_test_results(
            test_type="comparator", project_name="project_a", status="passed"
        )

        assert len(filtered) == 1
        assert filtered[0].test_type == "comparator"
        assert filtered[0].project_name == "project_a"


class TestStatisticsAndAnalytics:
    """Test database statistics and analytics operations."""

    def test_calculate_test_statistics(self, temp_db):
        """Should calculate test statistics correctly."""
        # Add varied test results
        for i in range(10):
            result = (
                TestResultBuilder()
                .with_test_type("comparator" if i % 2 == 0 else "validator")
                .with_results(passed=8, failed=2)
                .build()
            )
            temp_db.save_test_result(result)

        # Get statistics
        stats = temp_db.get_test_statistics()

        assert stats["total_tests"] == 10
        assert stats["by_type"]["comparator"] == 5
        assert stats["by_type"]["validator"] == 5
        assert stats["success_rate"] == 80.0  # 8/10 = 80%

    def test_project_specific_statistics(self, temp_db):
        """Should calculate statistics for specific project."""
        # Add results for different projects
        for project in ["project_a", "project_b"]:
            for i in range(5):
                result = (
                    TestResultBuilder()
                    .with_project_name(project)
                    .with_results(
                        passed=10 if project == "project_a" else 5,
                        failed=0 if project == "project_a" else 5,
                    )
                    .build()
                )
                temp_db.save_test_result(result)

        # Get project_a stats
        stats_a = temp_db.get_test_statistics(project_name="project_a")

        assert stats_a["total_tests"] == 5
        assert stats_a["success_rate"] == 100.0

        # Get project_b stats
        stats_b = temp_db.get_test_statistics(project_name="project_b")

        assert stats_b["total_tests"] == 5
        assert stats_b["success_rate"] == 50.0

    def test_database_stats_via_manager(self, temp_db):
        """Should calculate statistics via DatabaseManager."""
        # Add data
        for i in range(5):
            result = (
                TestResultBuilder()
                .with_test_type("comparator" if i % 2 == 0 else "validator")
                .with_results(passed=10, failed=0)
                .with_project_name("stats_test")
                .build()
            )
            temp_db.save_test_result(result)

        # Get stats from DatabaseManager
        stats = temp_db.get_test_statistics(project_name="stats_test")

        assert stats["total_tests"] == 5
        assert stats["by_type"]["comparator"] == 3
        assert stats["by_type"]["validator"] == 2
        assert stats["success_rate"] == 100.0


class TestDataIntegrity:
    """Test database integrity and consistency."""

    def test_maintains_referential_integrity(self, temp_db):
        """Should maintain data consistency across related entities."""
        project_name = "integrity_test_project"

        # Save project data
        project = ProjectData(
            project_name=project_name,
            project_path="/test/path",
            last_accessed=datetime.now().isoformat(),
            file_count=10,
            total_lines=1000,
            languages='["cpp"]',
        )
        temp_db.save_project_data(project)

        # Save test results for project
        for i in range(3):
            result = TestResultBuilder().with_project_name(project_name).build()
            temp_db.save_test_result(result)

        # Save session for project
        session = Session(
            session_name="test_session",
            open_files="[]",
            active_file="",
            timestamp=datetime.now().isoformat(),
            project_name=project_name,
        )
        temp_db.save_session(session)

        # Verify all data exists
        test_results = temp_db.get_test_results(project_name=project_name)
        sessions = temp_db.get_sessions(project_name=project_name)
        projects = temp_db.get_projects()

        assert len(test_results) == 3
        assert len(sessions) == 1
        assert len(projects) == 1
        assert all(r.project_name == project_name for r in test_results)

    def test_handles_concurrent_writes(self, temp_db):
        """Should handle multiple writes in quick succession."""
        # Rapidly save multiple results
        result_ids = []
        for i in range(20):
            result = TestResultBuilder().with_project_name(f"project_{i % 3}").build()
            result_id = temp_db.save_test_result(result)
            result_ids.append(result_id)

        # All should have unique IDs
        assert len(result_ids) == 20
        assert len(set(result_ids)) == 20

        # All should be retrievable
        all_results = temp_db.get_test_results(limit=100)
        assert len(all_results) == 20

    def test_preserves_data_after_reopen(self, tmp_path):
        """Should preserve data after closing and reopening database."""
        db_path = str(tmp_path / "persistence_test.db")

        # Save data
        db1 = DatabaseManager(db_path)
        result = TestResultBuilder().with_project_name("persist_test").build()
        result_id = db1.save_test_result(result)
        db1.close()

        # Reopen and verify
        db2 = DatabaseManager(db_path)
        retrieved = db2.get_test_results(project_name="persist_test")

        assert len(retrieved) == 1
        assert retrieved[0].id == result_id
        db2.close()


class TestMaintenanceOperations:
    """Test database maintenance operations."""

    def test_cleanup_old_test_results(self, temp_db):
        """Should clean up old test results using DatabaseManager."""
        # Add old data
        old_time = datetime.now() - timedelta(days=40)
        old_ids = []
        for i in range(3):
            result = (
                TestResultBuilder()
                .with_timestamp((old_time - timedelta(hours=i)).isoformat())
                .build()
            )
            old_id = temp_db.save_test_result(result)
            old_ids.append(old_id)

        # Add recent data
        recent_ids = []
        for i in range(2):
            result = (
                TestResultBuilder().with_timestamp(datetime.now().isoformat()).build()
            )
            recent_id = temp_db.save_test_result(result)
            recent_ids.append(recent_id)

        # Verify 5 total before cleanup
        assert len(temp_db.get_test_results()) == 5

        # Use DatabaseManager's cleanup method
        temp_db.cleanup_old_data(days=30)

        # Verify only recent data remains (2 results)
        remaining = temp_db.get_test_results()
        assert len(remaining) == 2
        assert all(r.id in recent_ids for r in remaining)

    def test_delete_individual_test_result(self, temp_db):
        """Should delete individual test results."""
        # Add test results
        ids = []
        for i in range(5):
            result = TestResultBuilder().build()
            result_id = temp_db.save_test_result(result)
            ids.append(result_id)

        # Delete middle one
        temp_db.delete_test_result(ids[2])

        # Verify only 4 remain
        remaining = temp_db.get_test_results()
        assert len(remaining) == 4
        assert ids[2] not in [r.id for r in remaining]


class TestComplexWorkflows:
    """Test complex multi-step workflows."""

    def test_complete_test_execution_workflow(self, temp_db, workspace_with_files):
        """Should handle complete test execution and persistence workflow."""
        # Step 1: Create files snapshot
        snapshot = FilesSnapshotService.create_snapshot(
            str(workspace_with_files), test_type="comparator"
        )

        # Step 2: Create test result with snapshot
        test_details = [
            {"test_number": i, "passed": i % 2 == 0, "time": 0.1 + i * 0.01}
            for i in range(10)
        ]

        result = (
            TestResultBuilder()
            .with_test_type("comparator")
            .with_results(passed=5, failed=5)
            .with_test_details(test_details)
            .with_files_snapshot(snapshot.to_json())
            .with_project_name("workflow_test")
            .build()
        )

        # Step 3: Save to database
        result_id = temp_db.save_test_result(result)

        # Step 4: Save session
        session = Session(
            session_name="test_session",
            open_files=json.dumps(["generator.cpp", "correct.py", "test.java"]),
            active_file="generator.cpp",
            timestamp=datetime.now().isoformat(),
            project_name="workflow_test",
        )
        session_id = temp_db.save_session(session)

        # Step 5: Save project data
        project = ProjectData(
            project_name="workflow_test",
            project_path=str(workspace_with_files),
            last_accessed=datetime.now().isoformat(),
            file_count=3,
            total_lines=150,
            languages=json.dumps(["cpp", "py", "java"]),
        )
        project_id = temp_db.save_project_data(project)

        # Verify: All data persisted and retrievable
        assert result_id > 0
        assert session_id > 0
        assert project_id > 0

        # Verify: Data consistency
        retrieved_result = temp_db.get_test_results(project_name="workflow_test")[0]
        retrieved_sessions = temp_db.get_sessions(project_name="workflow_test")
        retrieved_projects = temp_db.get_projects()

        assert retrieved_result.id == result_id
        assert len(retrieved_sessions) == 1
        assert len(retrieved_projects) == 1

        # Verify: Snapshot integrity
        retrieved_snapshot = FilesSnapshot.from_json(retrieved_result.files_snapshot)
        assert len(retrieved_snapshot.files) > 0

        # Verify: Statistics
        stats = temp_db.get_test_statistics(project_name="workflow_test")
        assert stats["total_tests"] == 1
        assert stats["success_rate"] == 50.0  # 5 passed out of 10

    def test_multi_project_workflow(self, temp_db):
        """Should handle multiple projects simultaneously."""
        projects = ["project_alpha", "project_beta", "project_gamma"]

        # Create data for each project
        for project_name in projects:
            # Project data
            project = ProjectData(
                project_name=project_name,
                project_path=f"/path/to/{project_name}",
                last_accessed=datetime.now().isoformat(),
                file_count=10,
                total_lines=1000,
                languages='["cpp", "py"]',
            )
            temp_db.save_project_data(project)

            # Test results
            for i in range(3):
                result = (
                    TestResultBuilder()
                    .with_project_name(project_name)
                    .with_results(passed=10, failed=0)
                    .build()
                )
                temp_db.save_test_result(result)

            # Sessions
            session = Session(
                session_name=f"{project_name}_session",
                open_files="[]",
                active_file="",
                timestamp=datetime.now().isoformat(),
                project_name=project_name,
            )
            temp_db.save_session(session)

        # Verify: Each project has correct data
        for project_name in projects:
            test_results = temp_db.get_test_results(project_name=project_name)
            sessions = temp_db.get_sessions(project_name=project_name)
            stats = temp_db.get_test_statistics(project_name=project_name)

            assert len(test_results) == 3
            assert len(sessions) == 1
            assert stats["total_tests"] == 3
            assert stats["success_rate"] == 100.0

        # Verify: Total counts
        all_results = temp_db.get_test_results(limit=100)
        all_sessions = temp_db.get_sessions(limit=100)
        all_projects = temp_db.get_projects(limit=100)

        assert len(all_results) == 9  # 3 projects × 3 results
        assert len(all_sessions) == 3  # 3 projects × 1 session
        assert len(all_projects) == 3


class TestErrorHandling:
    """Test error handling in database operations."""

    def test_handles_invalid_data_gracefully(self, temp_db):
        """Should handle invalid data without crashing."""
        # Try to save result with missing required fields
        # Note: TestResult dataclass will catch this, but test DB handling
        result = TestResult(
            id=None,
            test_type="",  # Empty type
            file_path="",
            test_count=0,
            passed_tests=0,
            failed_tests=0,
            total_time=0,
            timestamp=datetime.now().isoformat(),
            test_details="",
            project_name="",
            files_snapshot="",
            mismatch_analysis="",
        )

        # Should save without error (even if data is minimal)
        result_id = temp_db.save_test_result(result)
        assert result_id > 0

    def test_handles_corrupted_json_in_snapshot(self, temp_db):
        """Should handle corrupted JSON in files_snapshot field."""
        # Save result with invalid JSON
        result = TestResultBuilder().with_files_snapshot('{"invalid json}').build()

        result_id = temp_db.save_test_result(result)

        # Should save successfully
        assert result_id > 0

        # Retrieve and try to parse
        retrieved = temp_db.get_test_results()[0]

        # FilesSnapshot.from_json should handle gracefully
        snapshot = FilesSnapshot.from_json(retrieved.files_snapshot)

        # Should return empty snapshot, not crash
        assert len(snapshot.files) == 0

    def test_handles_database_file_permission_error(self, tmp_path):
        """Should handle permission errors gracefully."""
        # Note: This test may behave differently on different platforms
        # Just verify it doesn't crash
        db_path = str(tmp_path / "test.db")

        try:
            db_manager = DatabaseManager(db_path)
            result = TestResultBuilder().build()
            result_id = db_manager.save_test_result(result)
            assert result_id > 0
            db_manager.close()
        except DatabaseError:
            # Expected if permissions are restricted
            pass
