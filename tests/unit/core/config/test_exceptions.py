"""
Unit tests for core/config/core/exceptions.py module.

Tests the configuration exception hierarchy and error handling.

Test Coverage:
- ConfigError: Base exception class
- ConfigPermissionError: Permission-related errors
- ConfigFormatError: JSON format errors
- ConfigValidationError: Structure validation errors
- ConfigLoadError: Loading failures
- ConfigSaveError: Saving failures
- ConfigMissingError: Missing required keys
"""

import pytest

from src.app.core.config.core.exceptions import (
    ConfigError,
    ConfigPermissionError,
    ConfigFormatError,
    ConfigValidationError,
    ConfigLoadError,
    ConfigSaveError,
    ConfigMissingError,
)


class TestConfigError:
    """Tests for ConfigError base exception."""

    def test_is_exception(self):
        """Test that ConfigError inherits from Exception."""
        assert issubclass(ConfigError, Exception)

    def test_can_be_raised(self):
        """Test that ConfigError can be raised."""
        with pytest.raises(ConfigError):
            raise ConfigError("Test error")

    def test_has_message(self):
        """Test that ConfigError stores message."""
        error = ConfigError("Test message")
        assert "Test message" in str(error)

    def test_can_be_caught_as_exception(self):
        """Test that ConfigError can be caught as Exception."""
        with pytest.raises(Exception):
            raise ConfigError("Test error")


class TestConfigPermissionError:
    """Tests for ConfigPermissionError exception."""

    def test_inherits_from_config_error(self):
        """Test that ConfigPermissionError inherits from ConfigError."""
        assert issubclass(ConfigPermissionError, ConfigError)

    def test_formats_message_correctly(self):
        """Test error message formatting."""
        error = ConfigPermissionError("reading", "/path/to/config.json")
        message = str(error)
        assert "Permission denied" in message
        assert "reading" in message
        assert "/path/to/config.json" in message

    def test_stores_operation(self):
        """Test that operation is stored as attribute."""
        error = ConfigPermissionError("writing", "/path/to/config.json")
        assert error.operation == "writing"

    def test_stores_file_path(self):
        """Test that file_path is stored as attribute."""
        error = ConfigPermissionError("reading", "/path/to/config.json")
        assert error.file_path == "/path/to/config.json"

    def test_reading_operation(self):
        """Test permission error for reading operation."""
        error = ConfigPermissionError("reading", "config.json")
        assert "reading" in str(error)

    def test_writing_operation(self):
        """Test permission error for writing operation."""
        error = ConfigPermissionError("writing", "config.json")
        assert "writing" in str(error)

    def test_can_be_raised(self):
        """Test that exception can be raised and caught."""
        with pytest.raises(ConfigPermissionError) as exc_info:
            raise ConfigPermissionError("reading", "test.json")

        assert exc_info.value.operation == "reading"
        assert exc_info.value.file_path == "test.json"


class TestConfigFormatError:
    """Tests for ConfigFormatError exception."""

    def test_inherits_from_config_error(self):
        """Test that ConfigFormatError inherits from ConfigError."""
        assert issubclass(ConfigFormatError, ConfigError)

    def test_formats_message_with_line_number(self):
        """Test error message with line number."""
        error = ConfigFormatError("Invalid JSON syntax", 42)
        message = str(error)
        assert "format error" in message.lower()
        assert "line 42" in message
        assert "Invalid JSON syntax" in message

    def test_formats_message_without_line_number(self):
        """Test error message without line number."""
        error = ConfigFormatError("Invalid JSON syntax")
        message = str(error)
        assert "format error" in message.lower()
        assert "Invalid JSON syntax" in message
        assert "line" not in message

    def test_stores_line_number(self):
        """Test that line_number is stored as attribute."""
        error = ConfigFormatError("Test error", 10)
        assert error.line_number == 10

    def test_line_number_none_when_not_provided(self):
        """Test that line_number is None when not provided."""
        error = ConfigFormatError("Test error")
        assert error.line_number is None

    def test_can_be_raised(self):
        """Test that exception can be raised and caught."""
        with pytest.raises(ConfigFormatError) as exc_info:
            raise ConfigFormatError("Invalid JSON", 5)

        assert exc_info.value.line_number == 5


class TestConfigValidationError:
    """Tests for ConfigValidationError exception."""

    def test_inherits_from_config_error(self):
        """Test that ConfigValidationError inherits from ConfigError."""
        assert issubclass(ConfigValidationError, ConfigError)

    def test_formats_message_correctly(self):
        """Test error message formatting."""
        error = ConfigValidationError("gemini_settings", "Missing API key")
        message = str(error)
        assert "validation error" in message.lower()
        assert "gemini_settings" in message
        assert "Missing API key" in message

    def test_stores_field(self):
        """Test that field is stored as attribute."""
        error = ConfigValidationError("test_field", "Test message")
        assert error.field == "test_field"

    def test_stores_details(self):
        """Test that details are stored as attribute."""
        details = "Additional validation info"
        error = ConfigValidationError("field", "message", details)
        assert error.details == details

    def test_details_none_when_not_provided(self):
        """Test that details is None when not provided."""
        error = ConfigValidationError("field", "message")
        assert error.details is None

    def test_can_be_raised_with_details(self):
        """Test raising exception with details."""
        with pytest.raises(ConfigValidationError) as exc_info:
            raise ConfigValidationError("config", "Invalid", "Details here")

        assert exc_info.value.field == "config"
        assert exc_info.value.details == "Details here"


class TestConfigLoadError:
    """Tests for ConfigLoadError exception."""

    def test_inherits_from_config_error(self):
        """Test that ConfigLoadError inherits from ConfigError."""
        assert issubclass(ConfigLoadError, ConfigError)

    def test_formats_message_correctly(self):
        """Test error message formatting."""
        error = ConfigLoadError("File not found")
        message = str(error)
        assert "Failed to load config" in message
        assert "File not found" in message

    def test_stores_custom_message(self):
        """Test that custom message is preserved."""
        custom_msg = "Custom error description"
        error = ConfigLoadError(custom_msg)
        assert custom_msg in str(error)

    def test_can_be_raised(self):
        """Test that exception can be raised and caught."""
        with pytest.raises(ConfigLoadError):
            raise ConfigLoadError("Test load error")


class TestConfigSaveError:
    """Tests for ConfigSaveError exception."""

    def test_inherits_from_config_error(self):
        """Test that ConfigSaveError inherits from ConfigError."""
        assert issubclass(ConfigSaveError, ConfigError)

    def test_formats_message_correctly(self):
        """Test error message formatting."""
        error = ConfigSaveError("Disk full")
        message = str(error)
        assert "Failed to save config" in message
        assert "Disk full" in message

    def test_stores_custom_message(self):
        """Test that custom message is preserved."""
        custom_msg = "Custom save error"
        error = ConfigSaveError(custom_msg)
        assert custom_msg in str(error)

    def test_can_be_raised(self):
        """Test that exception can be raised and caught."""
        with pytest.raises(ConfigSaveError):
            raise ConfigSaveError("Test save error")


class TestConfigMissingError:
    """Tests for ConfigMissingError exception."""

    def test_inherits_from_config_error(self):
        """Test that ConfigMissingError inherits from ConfigError."""
        assert issubclass(ConfigMissingError, ConfigError)

    def test_formats_message_correctly(self):
        """Test error message formatting."""
        error = ConfigMissingError("Required keys: api_key, model")
        message = str(error)
        assert "Missing configuration" in message
        assert "Required keys" in message

    def test_stores_custom_message(self):
        """Test that custom message is preserved."""
        custom_msg = "api_key field is missing"
        error = ConfigMissingError(custom_msg)
        assert custom_msg in str(error)

    def test_can_be_raised(self):
        """Test that exception can be raised and caught."""
        with pytest.raises(ConfigMissingError):
            raise ConfigMissingError("Test missing error")


class TestExceptionHierarchy:
    """Tests for exception class hierarchy."""

    def test_all_inherit_from_config_error(self):
        """Test that all config exceptions inherit from ConfigError."""
        exceptions = [
            ConfigPermissionError,
            ConfigFormatError,
            ConfigValidationError,
            ConfigLoadError,
            ConfigSaveError,
            ConfigMissingError,
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, ConfigError)

    def test_all_inherit_from_exception(self):
        """Test that all config exceptions inherit from Exception."""
        exceptions = [
            ConfigError,
            ConfigPermissionError,
            ConfigFormatError,
            ConfigValidationError,
            ConfigLoadError,
            ConfigSaveError,
            ConfigMissingError,
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, Exception)

    def test_can_catch_all_with_config_error(self):
        """Test that all specific exceptions can be caught as ConfigError."""
        exceptions_to_test = [
            ConfigPermissionError("reading", "test.json"),
            ConfigFormatError("Invalid JSON", 1),
            ConfigValidationError("field", "message"),
            ConfigLoadError("Load failed"),
            ConfigSaveError("Save failed"),
            ConfigMissingError("Missing key"),
        ]

        for exc in exceptions_to_test:
            with pytest.raises(ConfigError):
                raise exc

    def test_specific_exceptions_are_distinct(self):
        """Test that specific exceptions are distinct types."""
        exceptions = [
            ConfigPermissionError,
            ConfigFormatError,
            ConfigValidationError,
            ConfigLoadError,
            ConfigSaveError,
            ConfigMissingError,
        ]

        # Each exception type should be distinct
        for i, exc1 in enumerate(exceptions):
            for j, exc2 in enumerate(exceptions):
                if i != j:
                    assert exc1 is not exc2


class TestExceptionUsage:
    """Integration tests for exception usage patterns."""

    def test_catching_specific_exception(self):
        """Test catching specific exception type."""
        with pytest.raises(ConfigPermissionError) as exc_info:
            raise ConfigPermissionError("reading", "config.json")

        assert isinstance(exc_info.value, ConfigPermissionError)
        assert isinstance(exc_info.value, ConfigError)
        assert isinstance(exc_info.value, Exception)

    def test_catching_base_exception(self):
        """Test catching base ConfigError."""
        with pytest.raises(ConfigError):
            raise ConfigValidationError("field", "Invalid")

    def test_exception_chaining(self):
        """Test exception chaining for debugging."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise ConfigLoadError("Failed to load") from e
        except ConfigLoadError as e:
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, ValueError)

    def test_multiple_exception_types_in_try_except(self):
        """Test handling multiple exception types."""

        def test_function(exception_type):
            if exception_type == "permission":
                raise ConfigPermissionError("reading", "file.json")
            elif exception_type == "format":
                raise ConfigFormatError("Invalid JSON", 1)
            elif exception_type == "validation":
                raise ConfigValidationError("field", "Invalid")

        # Test permission error
        with pytest.raises(ConfigError):
            test_function("permission")

        # Test format error
        with pytest.raises(ConfigError):
            test_function("format")

        # Test validation error
        with pytest.raises(ConfigError):
            test_function("validation")

    def test_exception_attributes_accessible(self):
        """Test that exception attributes are accessible after raising."""
        try:
            raise ConfigPermissionError("writing", "/path/to/file.json")
        except ConfigPermissionError as e:
            assert e.operation == "writing"
            assert e.file_path == "/path/to/file.json"
            assert "Permission denied" in str(e)
