"""Configuration-related exception classes."""


class ConfigError(Exception):
    """Base exception for configuration-related errors."""

    pass


class ConfigPermissionError(ConfigError):
    """Raised when there are permission issues with config files."""

    def __init__(self, operation, file_path):
        super().__init__(f"Permission denied {operation} config file: {file_path}")
        self.operation = operation
        self.file_path = file_path


class ConfigFormatError(ConfigError):
    """Raised when config file has invalid JSON format."""

    def __init__(self, message, line_number=None):
        if line_number:
            super().__init__(f"Config format error at line {line_number}: {message}")
        else:
            super().__init__(f"Config format error: {message}")
        self.line_number = line_number


class ConfigValidationError(ConfigError):
    """Raised when config structure validation fails."""

    def __init__(self, field, message, details=None):
        super().__init__(f"Config validation error in {field}: {message}")
        self.field = field
        self.details = details


class ConfigLoadError(ConfigError):
    """Raised when config cannot be loaded."""

    def __init__(self, message):
        super().__init__(f"Failed to load config: {message}")


class ConfigSaveError(ConfigError):
    """Raised when config cannot be saved."""

    def __init__(self, message):
        super().__init__(f"Failed to save config: {message}")


class ConfigMissingError(ConfigError):
    """Raised when required configuration keys are missing."""

    def __init__(self, message):
        super().__init__(f"Missing configuration: {message}")
