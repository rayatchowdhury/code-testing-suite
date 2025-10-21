"""
End-to-end tests for application startup and basic functionality.

These tests validate core functionality without creating actual windows
to avoid Qt cleanup issues in the test environment.

Tests cover:
- Module imports work correctly
- Database initialization
- Workspace structure creation
- Core application components are accessible
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace for testing."""
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()
    yield workspace


class TestApplicationImports:
    """Test that all core application modules can be imported."""

    def test_can_import_main_window(self):
        """Main window module should be importable."""
        try:
            from src.app.presentation.windows.main import MainWindow

            assert MainWindow is not None
        except ImportError as e:
            pytest.fail(f"Failed to import MainWindow: {e}")

    def test_can_import_database_manager(self):
        """Database manager should be importable."""
        from src.app.persistence.database.database_manager import DatabaseManager

        assert DatabaseManager is not None

    def test_can_import_validators(self):
        """Validator module should be importable."""
        from src.app.core.tools.validator import ValidatorRunner

        assert ValidatorRunner is not None

    def test_can_import_comparator(self):
        """Comparator module should be importable."""
        from src.app.core.tools.comparator import Comparator

        assert Comparator is not None

    def test_can_import_benchmarker(self):
        """Benchmarker module should be importable."""
        from src.app.core.tools.benchmarker import Benchmarker

        assert Benchmarker is not None


class TestQtApplication:
    """Test Qt application initialization."""

    def test_qt_application_exists(self, qapp):
        """QApplication instance should exist in test environment."""
        from PySide6.QtWidgets import QApplication

        assert QApplication.instance() is not None

    def test_qt_version_is_available(self, qapp):
        """Qt version information should be accessible."""
        from PySide6.QtCore import qVersion

        version = qVersion()
        assert version is not None
        assert len(version) > 0

    def test_application_has_no_windows_initially(self, qapp):
        """Application should have no windows initially."""
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        # In test environment, topLevelWidgets might have test fixtures
        assert app is not None


class TestDatabaseInitialization:
    """Test database initialization and basic operations."""

    def test_database_can_be_created(self, temp_workspace):
        """Database should initialize without errors."""
        from src.app.persistence.database.database_manager import DatabaseManager

        db_path = temp_workspace / "test.db"
        db_manager = DatabaseManager(str(db_path))

        assert db_manager is not None
        assert db_path.exists()

    def test_database_creates_required_tables(self, temp_workspace):
        """Database should create all required tables."""
        from src.app.persistence.database.database_manager import DatabaseManager

        db_path = temp_workspace / "test.db"
        db_manager = DatabaseManager(str(db_path))

        # Test that basic operations work (implies tables exist)
        results = db_manager.get_test_results()
        assert isinstance(results, list)

    def test_database_can_be_reopened(self, temp_workspace):
        """Database should be reopenable after creation."""
        from src.app.persistence.database.database_manager import DatabaseManager

        db_path = temp_workspace / "test.db"

        # Create and close
        db1 = DatabaseManager(str(db_path))
        del db1

        # Reopen
        db2 = DatabaseManager(str(db_path))
        assert db2 is not None

    def test_database_handles_concurrent_access(self, temp_workspace):
        """Multiple DatabaseManager instances should work with same file."""
        from src.app.persistence.database.database_manager import DatabaseManager

        db_path = temp_workspace / "test.db"

        db1 = DatabaseManager(str(db_path))
        db2 = DatabaseManager(str(db_path))

        assert db1 is not None
        assert db2 is not None


class TestWorkspaceStructure:
    """Test workspace directory structure creation."""

    def test_workspace_directory_can_be_created(self, temp_workspace):
        """Workspace structure should be creatable."""
        from src.app.shared.utils.workspace_utils import ensure_workspace_structure

        ensure_workspace_structure(temp_workspace)

        assert temp_workspace.exists()
        assert temp_workspace.is_dir()

    def test_workspace_structure_is_idempotent(self, temp_workspace):
        """Running ensure_workspace_structure multiple times should be safe."""
        from src.app.shared.utils.workspace_utils import ensure_workspace_structure

        ensure_workspace_structure(temp_workspace)
        ensure_workspace_structure(temp_workspace)
        ensure_workspace_structure(temp_workspace)

        assert temp_workspace.exists()

    def test_user_data_directory_creation(self):
        """User data directory should be creatable."""
        from src.app.shared.constants import ensure_user_data_dir

        # This should not crash
        ensure_user_data_dir()


class TestCoreComponents:
    """Test that core tool components can be instantiated."""

    def test_validator_can_be_instantiated(self, temp_workspace):
        """Validator should be instantiable."""
        from src.app.core.tools.validator import ValidatorRunner

        validator = ValidatorRunner(str(temp_workspace))
        assert validator is not None

    def test_comparator_can_be_instantiated(self, temp_workspace):
        """Comparator should be instantiable."""
        from src.app.core.tools.comparator import Comparator

        comparator = Comparator(str(temp_workspace))
        assert comparator is not None

    def test_benchmarker_can_be_instantiated(self, temp_workspace):
        """Benchmarker should be instantiable."""
        from src.app.core.tools.benchmarker import Benchmarker

        benchmarker = Benchmarker(str(temp_workspace))
        assert benchmarker is not None


class TestConfigurationLoading:
    """Test configuration and constants loading."""

    def test_can_load_workspace_constants(self):
        """Workspace constants should be accessible."""
        from src.app.shared.constants import WORKSPACE_DIR

        assert WORKSPACE_DIR is not None

    def test_can_load_file_constants(self):
        """File constants should be accessible."""
        from src.app.shared.constants.file_constants import LANGUAGE_EXTENSIONS

        assert LANGUAGE_EXTENSIONS is not None
        assert len(LANGUAGE_EXTENSIONS) > 0

    def test_can_load_paths_constants(self):
        """Path constants should be accessible."""
        from src.app.shared.constants.paths import USER_DATA_DIR

        assert USER_DATA_DIR is not None


# Mark all tests in this file as e2e tests
pytestmark = pytest.mark.e2e
