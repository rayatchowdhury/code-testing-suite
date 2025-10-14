"""
Unit tests for database exceptions.

Tests exception hierarchy, error messages, and exception raising scenarios.
"""

import pytest

from src.app.persistence.database.exceptions import (
    ConnectionError,
    DatabaseError,
    RepositoryError,
    ValidationError,
)


class TestExceptionHierarchy:
    """Test exception inheritance hierarchy."""

    def test_database_error_is_base_exception(self):
        """DatabaseError should inherit from Exception."""
        exc = DatabaseError("test")
        assert isinstance(exc, Exception)

    def test_connection_error_inherits_from_database_error(self):
        """ConnectionError should inherit from DatabaseError."""
        exc = ConnectionError("test")
        assert isinstance(exc, DatabaseError)
        assert isinstance(exc, Exception)

    def test_repository_error_inherits_from_database_error(self):
        """RepositoryError should inherit from DatabaseError."""
        exc = RepositoryError("test")
        assert isinstance(exc, DatabaseError)
        assert isinstance(exc, Exception)

    def test_validation_error_inherits_from_database_error(self):
        """ValidationError should inherit from DatabaseError."""
        exc = ValidationError("test")
        assert isinstance(exc, DatabaseError)
        assert isinstance(exc, Exception)


class TestExceptionMessages:
    """Test exception message handling."""

    def test_database_error_stores_message(self):
        """DatabaseError should store error message."""
        msg = "Database operation failed"
        exc = DatabaseError(msg)
        assert str(exc) == msg

    def test_connection_error_stores_message(self):
        """ConnectionError should store error message."""
        msg = "Failed to connect to database"
        exc = ConnectionError(msg)
        assert str(exc) == msg

    def test_repository_error_stores_message(self):
        """RepositoryError should store error message."""
        msg = "Repository operation failed"
        exc = RepositoryError(msg)
        assert str(exc) == msg

    def test_validation_error_stores_message(self):
        """ValidationError should store error message."""
        msg = "Data validation failed"
        exc = ValidationError(msg)
        assert str(exc) == msg


class TestExceptionRaising:
    """Test exception raising scenarios."""

    def test_can_raise_database_error(self):
        """Should be able to raise DatabaseError."""
        with pytest.raises(DatabaseError) as exc_info:
            raise DatabaseError("test error")

        assert "test error" in str(exc_info.value)

    def test_can_raise_connection_error(self):
        """Should be able to raise ConnectionError."""
        with pytest.raises(ConnectionError) as exc_info:
            raise ConnectionError("connection failed")

        assert "connection failed" in str(exc_info.value)

    def test_can_raise_repository_error(self):
        """Should be able to raise RepositoryError."""
        with pytest.raises(RepositoryError) as exc_info:
            raise RepositoryError("repository error")

        assert "repository error" in str(exc_info.value)

    def test_can_raise_validation_error(self):
        """Should be able to raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("validation failed")

        assert "validation failed" in str(exc_info.value)


class TestExceptionCatching:
    """Test exception catching with inheritance."""

    def test_catch_connection_error_as_database_error(self):
        """Should be able to catch ConnectionError as DatabaseError."""
        with pytest.raises(DatabaseError):
            raise ConnectionError("test")

    def test_catch_repository_error_as_database_error(self):
        """Should be able to catch RepositoryError as DatabaseError."""
        with pytest.raises(DatabaseError):
            raise RepositoryError("test")

    def test_catch_validation_error_as_database_error(self):
        """Should be able to catch ValidationError as DatabaseError."""
        with pytest.raises(DatabaseError):
            raise ValidationError("test")

    def test_specific_exception_not_caught_by_wrong_type(self):
        """ConnectionError should not be caught as RepositoryError."""
        with pytest.raises(ConnectionError):
            try:
                raise ConnectionError("test")
            except RepositoryError:
                pytest.fail("Should not catch ConnectionError as RepositoryError")
            except ConnectionError:
                raise


class TestExceptionChaining:
    """Test exception chaining with 'from' clause."""

    def test_database_error_chains_original_exception(self):
        """Should chain original exception with 'from' clause."""
        original = ValueError("original error")

        with pytest.raises(DatabaseError) as exc_info:
            try:
                raise original
            except ValueError as e:
                raise DatabaseError("wrapped error") from e

        assert exc_info.value.__cause__ is original

    def test_connection_error_chains_original_exception(self):
        """Should chain original exception for ConnectionError."""
        original = OSError("network error")

        with pytest.raises(ConnectionError) as exc_info:
            try:
                raise original
            except OSError as e:
                raise ConnectionError("connection failed") from e

        assert exc_info.value.__cause__ is original
        assert isinstance(exc_info.value.__cause__, OSError)


class TestExceptionWithContext:
    """Test exceptions with additional context."""

    def test_exception_with_formatted_message(self):
        """Should support formatted error messages."""
        db_path = "/path/to/db.sqlite"
        error = "File not found"

        exc = ConnectionError(f"Failed to connect to {db_path}: {error}")

        assert db_path in str(exc)
        assert error in str(exc)

    def test_exception_with_multiple_values(self):
        """Should support multiple values in message."""
        table = "test_results"
        operation = "INSERT"
        reason = "constraint violation"

        exc = RepositoryError(f"Failed to {operation} into {table}: {reason}")

        assert table in str(exc)
        assert operation in str(exc)
        assert reason in str(exc)
