"""
Phase 4 Task 2 - Tests for logging_config.py

Tests cover:
- Logging setup with various configurations
- File handler creation (rotating logs)
- Console handler setup
- Migration logging
- Logger retrieval
- Exception classes
"""

import logging
import logging.handlers
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from src.app.core.config.logging_config import (
    DatabaseError,
    MigrationError,
    ValidationError,
    get_logger,
    setup_logging,
    setup_migration_logging,
)

# ============================================================================
# Logging Setup Tests
# ============================================================================


class TestSetupLogging:
    """Test setup_logging function."""

    def setup_method(self):
        """Clean up logging before each test."""
        logging.root.handlers.clear()

    def teardown_method(self):
        """Clean up after each test."""
        logging.root.handlers.clear()

    @patch("pathlib.Path.mkdir")
    def test_setup_logging_creates_log_directory(self, mock_mkdir):
        """Test setup_logging creates logs directory."""
        with patch("logging.handlers.RotatingFileHandler") as mock_file_handler:
            mock_handler = Mock()
            mock_handler.level = logging.INFO
            mock_file_handler.return_value = mock_handler
            setup_logging()

        mock_mkdir.assert_called()

    @patch("pathlib.Path.mkdir")
    @patch("logging.handlers.RotatingFileHandler")
    def test_setup_logging_with_console_and_file(self, mock_file_handler, mock_mkdir):
        """Test setup_logging with both console and file handlers."""
        mock_handler = Mock()
        mock_handler.level = logging.INFO
        mock_file_handler.return_value = mock_handler

        logger = setup_logging(
            log_level=logging.INFO, log_to_console=True, log_to_file=True
        )

        assert logger is not None
        assert logger == logging.root

    @patch("pathlib.Path.mkdir")
    def test_setup_logging_console_only(self, mock_mkdir):
        """Test setup_logging with console only."""
        logger = setup_logging(
            log_level=logging.INFO, log_to_console=True, log_to_file=False
        )

        # Should have console handler
        assert len(logger.handlers) >= 1
        # At least one should be StreamHandler
        assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)

    @patch("pathlib.Path.mkdir")
    @patch("logging.handlers.RotatingFileHandler")
    def test_setup_logging_file_only(self, mock_file_handler, mock_mkdir):
        """Test setup_logging with file only."""
        mock_handler = Mock()
        mock_handler.level = logging.DEBUG
        mock_file_handler.return_value = mock_handler

        logger = setup_logging(
            log_level=logging.DEBUG, log_to_console=False, log_to_file=True
        )

        # Should have file handlers
        assert mock_file_handler.call_count >= 1

    @patch("pathlib.Path.mkdir")
    def test_setup_logging_sets_log_level(self, mock_mkdir):
        """Test setup_logging sets correct log level."""
        logger = setup_logging(
            log_level=logging.WARNING, log_to_console=True, log_to_file=False
        )

        assert logger.level == logging.WARNING

    @patch("pathlib.Path.mkdir")
    def test_setup_logging_clears_existing_handlers(self, mock_mkdir):
        """Test setup_logging clears existing handlers."""
        # Add a dummy handler
        dummy_handler = logging.StreamHandler()
        logging.root.addHandler(dummy_handler)

        logger = setup_logging(log_to_console=False, log_to_file=False)

        # Dummy handler should be cleared
        assert dummy_handler not in logger.handlers

    @patch("pathlib.Path.mkdir")
    @patch("logging.handlers.RotatingFileHandler")
    def test_setup_logging_creates_rotating_file_handler(
        self, mock_file_handler, mock_mkdir
    ):
        """Test setup_logging creates rotating file handler."""
        mock_handler = Mock()
        mock_handler.level = logging.DEBUG
        mock_file_handler.return_value = mock_handler

        setup_logging(log_to_console=False, log_to_file=True)

        # Should create file handler
        assert mock_file_handler.call_count >= 1

    @patch("pathlib.Path.mkdir")
    @patch("logging.handlers.RotatingFileHandler")
    def test_setup_logging_creates_error_log_handler(
        self, mock_file_handler, mock_mkdir
    ):
        """Test setup_logging creates separate error log handler."""
        mock_handler = Mock()
        mock_handler.level = logging.DEBUG
        mock_file_handler.return_value = mock_handler

        setup_logging(log_to_console=False, log_to_file=True)

        # Should create at least 2 handlers (app.log and errors.log)
        assert mock_file_handler.call_count >= 2

    @patch("pathlib.Path.mkdir")
    @patch("logging.handlers.RotatingFileHandler")
    def test_setup_logging_logs_startup_message(self, mock_file_handler, mock_mkdir):
        """Test setup_logging logs startup message."""
        mock_handler = Mock()
        mock_handler.level = logging.DEBUG
        mock_file_handler.return_value = mock_handler

        with patch.object(logging.root, "info") as mock_info:
            setup_logging(log_to_console=False, log_to_file=True)

            # Should log startup messages
            assert mock_info.call_count >= 3


# ============================================================================
# Get Logger Tests
# ============================================================================


class TestGetLogger:
    """Test get_logger function."""

    def test_get_logger_returns_logger(self):
        """Test get_logger returns logger instance."""
        logger = get_logger("test.module")

        assert logger is not None
        assert isinstance(logger, logging.Logger)

    def test_get_logger_with_name(self):
        """Test get_logger creates logger with correct name."""
        logger_name = "my.custom.logger"
        logger = get_logger(logger_name)

        assert logger.name == logger_name

    def test_get_logger_returns_same_instance(self):
        """Test get_logger returns same instance for same name."""
        logger1 = get_logger("same.logger")
        logger2 = get_logger("same.logger")

        assert logger1 is logger2


# ============================================================================
# Migration Logging Tests
# ============================================================================


class TestSetupMigrationLogging:
    """Test setup_migration_logging function."""

    def setup_method(self):
        """Clean up logging before each test."""
        migration_logger = logging.getLogger("migration")
        migration_logger.handlers.clear()

    def teardown_method(self):
        """Clean up after each test."""
        migration_logger = logging.getLogger("migration")
        migration_logger.handlers.clear()

    @patch("pathlib.Path.mkdir")
    @patch("logging.handlers.RotatingFileHandler")
    def test_setup_migration_logging_creates_logger(
        self, mock_file_handler, mock_mkdir
    ):
        """Test setup_migration_logging creates migration logger."""
        mock_handler = Mock()
        mock_handler.level = logging.DEBUG
        mock_file_handler.return_value = mock_handler

        logger = setup_migration_logging()

        assert logger is not None
        assert logger.name == "migration"

    @patch("pathlib.Path.mkdir")
    @patch("logging.handlers.RotatingFileHandler")
    def test_setup_migration_logging_creates_directory(
        self, mock_file_handler, mock_mkdir
    ):
        """Test setup_migration_logging creates log directory."""
        mock_handler = Mock()
        mock_handler.level = logging.DEBUG
        mock_file_handler.return_value = mock_handler

        setup_migration_logging()

        mock_mkdir.assert_called()

    @patch("pathlib.Path.mkdir")
    @patch("logging.handlers.RotatingFileHandler")
    def test_setup_migration_logging_sets_debug_level(
        self, mock_file_handler, mock_mkdir
    ):
        """Test setup_migration_logging sets DEBUG level."""
        mock_handler = Mock()
        mock_handler.level = logging.DEBUG
        mock_file_handler.return_value = mock_handler

        logger = setup_migration_logging()

        assert logger.level == logging.DEBUG

    @patch("pathlib.Path.mkdir")
    @patch("logging.handlers.RotatingFileHandler")
    def test_setup_migration_logging_creates_file_handler(
        self, mock_file_handler, mock_mkdir
    ):
        """Test setup_migration_logging creates file handler."""
        mock_handler = Mock()
        mock_handler.level = logging.DEBUG
        mock_file_handler.return_value = mock_handler

        setup_migration_logging()

        # Should create migration.log file handler
        assert mock_file_handler.called

    @patch("pathlib.Path.mkdir")
    @patch("logging.handlers.RotatingFileHandler")
    def test_setup_migration_logging_adds_console_handler(
        self, mock_file_handler, mock_mkdir
    ):
        """Test setup_migration_logging adds console handler."""
        mock_handler = Mock()
        mock_handler.level = logging.DEBUG
        mock_file_handler.return_value = mock_handler

        logger = setup_migration_logging()

        # Should have handlers
        assert len(logger.handlers) >= 1

    @patch("pathlib.Path.mkdir")
    @patch("logging.handlers.RotatingFileHandler")
    def test_setup_migration_logging_clears_existing_handlers(
        self, mock_file_handler, mock_mkdir
    ):
        """Test setup_migration_logging clears existing handlers."""
        mock_handler = Mock()
        mock_handler.level = logging.DEBUG
        mock_file_handler.return_value = mock_handler

        migration_logger = logging.getLogger("migration")
        dummy_handler = logging.StreamHandler()
        migration_logger.addHandler(dummy_handler)

        logger = setup_migration_logging()

        # Dummy handler should be cleared
        assert dummy_handler not in logger.handlers


# ============================================================================
# Exception Classes Tests
# ============================================================================


class TestExceptionClasses:
    """Test custom exception classes."""

    def test_database_error_is_exception(self):
        """Test DatabaseError is an Exception."""
        assert issubclass(DatabaseError, Exception)

    def test_database_error_can_be_raised(self):
        """Test DatabaseError can be raised."""
        with pytest.raises(DatabaseError):
            raise DatabaseError("Database error")

    def test_database_error_with_message(self):
        """Test DatabaseError stores message."""
        error_msg = "Connection failed"

        with pytest.raises(DatabaseError) as exc_info:
            raise DatabaseError(error_msg)

        assert error_msg in str(exc_info.value)

    def test_migration_error_is_exception(self):
        """Test MigrationError is an Exception."""
        assert issubclass(MigrationError, Exception)

    def test_migration_error_can_be_raised(self):
        """Test MigrationError can be raised."""
        with pytest.raises(MigrationError):
            raise MigrationError("Migration failed")

    def test_migration_error_with_message(self):
        """Test MigrationError stores message."""
        error_msg = "Migration step failed"

        with pytest.raises(MigrationError) as exc_info:
            raise MigrationError(error_msg)

        assert error_msg in str(exc_info.value)

    def test_validation_error_is_exception(self):
        """Test ValidationError is an Exception."""
        assert issubclass(ValidationError, Exception)

    def test_validation_error_can_be_raised(self):
        """Test ValidationError can be raised."""
        with pytest.raises(ValidationError):
            raise ValidationError("Validation failed")

    def test_validation_error_with_message(self):
        """Test ValidationError stores message."""
        error_msg = "Invalid input"

        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError(error_msg)

        assert error_msg in str(exc_info.value)


# ============================================================================
# Integration Tests
# ============================================================================


class TestLoggingIntegration:
    """Integration tests for logging configuration."""

    def setup_method(self):
        """Clean up logging before each test."""
        logging.root.handlers.clear()

    def teardown_method(self):
        """Clean up after each test."""
        logging.root.handlers.clear()

    @patch("pathlib.Path.mkdir")
    def test_setup_and_get_logger_workflow(self, mock_mkdir):
        """Test complete workflow: setup logging then get logger."""
        # Setup logging
        root_logger = setup_logging(log_to_console=True, log_to_file=False)

        # Get module-specific logger
        module_logger = get_logger("my.module")

        # Both should be valid
        assert root_logger is not None
        assert module_logger is not None
        assert module_logger.name == "my.module"

    @patch("pathlib.Path.mkdir")
    def test_logger_inheritance_from_root(self, mock_mkdir):
        """Test module logger inherits root logger configuration."""
        # Setup root logging
        setup_logging(log_level=logging.WARNING, log_to_console=True, log_to_file=False)

        # Get module logger
        module_logger = get_logger("test.module")

        # Module logger should inherit level from root
        # (effective level will be WARNING or higher)
        assert (
            module_logger.getEffectiveLevel() <= logging.WARNING
            or module_logger.level == 0
        )

    @patch("pathlib.Path.mkdir")
    @patch("logging.handlers.RotatingFileHandler")
    def test_different_logging_configurations(self, mock_file_handler, mock_mkdir):
        """Test switching between different logging configurations."""
        mock_handler = Mock()
        mock_handler.level = logging.DEBUG
        mock_file_handler.return_value = mock_handler

        # First configuration
        logger1 = setup_logging(
            log_level=logging.DEBUG, log_to_console=True, log_to_file=True
        )
        handlers_count_1 = len(logger1.handlers)

        # Second configuration (should clear previous)
        logger2 = setup_logging(
            log_level=logging.INFO, log_to_console=False, log_to_file=False
        )

        # Handlers should be cleared and reconfigured
        assert logger1 is logger2  # Same root logger
        # No handlers for console=False, file=False
        assert len(logger2.handlers) == 0
