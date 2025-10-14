"""Logging configuration for Code Testing Suite"""

import logging
import logging.handlers
from datetime import datetime
from pathlib import Path


def setup_logging(log_level=logging.DEBUG, log_to_console=True, log_to_file=True):
    """
    Configure application logging with rotating file handler and console output.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_console: If True, outputs logs to console
        log_to_file: If True, outputs logs to rotating file

    Returns:
        Configured root logger
    """
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    simple_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
    )

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # File handler (rotating) - detailed format
    if log_to_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(detailed_formatter)
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)

        # Separate error log file
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / "errors.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding="utf-8",
        )
        error_handler.setFormatter(detailed_formatter)
        error_handler.setLevel(logging.ERROR)
        root_logger.addHandler(error_handler)

    # Console handler - simple format
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(simple_formatter)
        console_handler.setLevel(logging.INFO)
        root_logger.addHandler(console_handler)

    # Log startup message
    root_logger.info("=" * 60)
    root_logger.info(
        f"Logging initialized at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    root_logger.info(f"Log level: {logging.getLevelName(log_level)}")
    root_logger.info(f"Log directory: {log_dir.absolute()}")
    root_logger.info("=" * 60)

    return root_logger


def get_logger(name):
    """
    Get a logger with the specified name.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def setup_migration_logging():
    """
    Special logging configuration for migration process.
    Creates a separate migration log file for tracking migration progress.
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create migration-specific logger
    migration_logger = logging.getLogger("migration")
    migration_logger.setLevel(logging.DEBUG)

    # Clear existing handlers
    migration_logger.handlers.clear()

    # Detailed formatter for migration
    migration_formatter = logging.Formatter(
        "%(asctime)s - MIGRATION - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Migration log file
    migration_handler = logging.handlers.RotatingFileHandler(
        log_dir / "migration.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    migration_handler.setFormatter(migration_formatter)
    migration_logger.addHandler(migration_handler)

    # Console handler for migration
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(migration_formatter)
    console_handler.setLevel(logging.INFO)
    migration_logger.addHandler(console_handler)

    migration_logger.info("=" * 80)
    migration_logger.info("MIGRATION LOGGING STARTED")
    migration_logger.info(f"Timestamp: {datetime.now().isoformat()}")
    migration_logger.info("=" * 80)

    return migration_logger


class DatabaseError(Exception):
    """Custom exception for database operations"""

    pass


class MigrationError(Exception):
    """Custom exception for migration operations"""

    pass


class ValidationError(Exception):
    """Custom exception for validation failures"""

    pass


if __name__ == "__main__":
    # Test logging configuration
    print("Testing logging configuration...")

    # Setup logging
    logger = setup_logging()

    # Test different log levels
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")

    # Test module-specific logger
    module_logger = get_logger(__name__)
    module_logger.info("This is a module-specific log message")

    # Test migration logging
    print("\nTesting migration logging...")
    migration_logger = setup_migration_logging()
    migration_logger.info("Migration test message")
    migration_logger.warning("Migration warning test")

    print("\n✓ Logging configuration test complete!")
    print(f"✓ Check logs/ directory for log files")
