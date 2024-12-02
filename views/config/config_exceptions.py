class ConfigError(Exception):
    """Base exception for configuration errors"""
    def __init__(self, message, details=None):
        super().__init__(message)
        self.message = message
        self.details = details

class ConfigLoadError(ConfigError):
    """Error loading configuration file"""
    def __init__(self, message, details=None):
        super().__init__(f"Failed to load configuration: {message}", details)

class ConfigSaveError(ConfigError):
    """Error saving configuration file"""
    def __init__(self, message, details=None):
        super().__init__(f"Failed to save configuration: {message}", details)

class ConfigValidationError(ConfigError):
    """Error validating configuration values"""
    def __init__(self, field_name, message, details=None):
        super().__init__(f"Invalid {field_name}: {message}", details)

class ConfigPermissionError(ConfigError):
    """Error accessing configuration file due to permissions"""
    def __init__(self, operation, path, details=None):
        super().__init__(
            f"Permission denied while {operation} config file: {path}", 
            details
        )

class ConfigFormatError(ConfigError):
    """Error in configuration file format"""
    def __init__(self, message, line_number=None, details=None):
        msg = f"Invalid configuration format: {message}"
        if line_number:
            msg += f" (line {line_number})"
        super().__init__(msg, details)

class ConfigMissingError(ConfigError):
    """Error when required configuration is missing"""
    def __init__(self, missing_item, details=None):
        super().__init__(
            f"Missing required configuration: {missing_item}", 
            details
        )