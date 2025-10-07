"""Database constants and magic numbers.

This module centralizes all magic numbers, string literals, and configuration
values used throughout the database layer. This improves maintainability and
makes the codebase more testable.

Phase 3: Extract Constants & Utilities
"""

# ============================================================================
# Query Limits
# ============================================================================

DEFAULT_RESULTS_LIMIT = 100
"""Default limit for test results queries"""

DEFAULT_SESSIONS_LIMIT = 10
"""Default limit for session queries"""

DEFAULT_PROJECTS_LIMIT = 50
"""Default limit for project queries"""

EXPORT_RESULTS_LIMIT = 1000
"""Maximum results to export at once"""

MAX_SEARCH_RESULTS = 500
"""Maximum search results to return"""


# ============================================================================
# Cleanup & Retention
# ============================================================================

DEFAULT_CLEANUP_DAYS = 7
"""Default number of days to keep recent data"""

OLD_DATA_CLEANUP_DAYS = 30
"""Number of days after which data is considered old and can be cleaned up"""

MAX_DATABASE_SIZE_MB = 500
"""Maximum database size in megabytes before cleanup is recommended"""

VACUUM_THRESHOLD_MB = 100
"""Database size threshold to trigger VACUUM operation"""


# ============================================================================
# Test Types
# ============================================================================

TEST_TYPE_COMPARISON = "comparison"
"""Comparison test type - compares output of two solutions"""

TEST_TYPE_VALIDATOR = "validator"
"""Validator test type - validates solution output against rules"""

TEST_TYPE_BENCHMARK = "benchmark"
"""Benchmark test type - measures performance and execution time"""

VALID_TEST_TYPES = [
    TEST_TYPE_COMPARISON,
    TEST_TYPE_VALIDATOR,
    TEST_TYPE_BENCHMARK
]
"""List of all valid test types"""


# Legacy test type mappings for backward compatibility
LEGACY_TEST_TYPE_MAP = {
    'stress': TEST_TYPE_COMPARISON,
    'tle': TEST_TYPE_BENCHMARK,
    'stress_test': TEST_TYPE_COMPARISON,
    'time_limit': TEST_TYPE_BENCHMARK,
}
"""Maps old test type names to current standard names"""


# ============================================================================
# File Roles
# ============================================================================

FILE_ROLE_GENERATOR = "generator"
"""File role for input generators"""

FILE_ROLE_CORRECT = "correct"
"""File role for correct/reference solutions"""

FILE_ROLE_TEST = "test"
"""File role for solutions being tested"""

FILE_ROLE_VALIDATOR = "validator"
"""File role for output validators"""

FILE_ROLE_CHECKER = "checker"
"""File role for custom checkers"""

VALID_FILE_ROLES = [
    FILE_ROLE_GENERATOR,
    FILE_ROLE_CORRECT,
    FILE_ROLE_TEST,
    FILE_ROLE_VALIDATOR,
    FILE_ROLE_CHECKER
]
"""List of all valid file roles"""


# ============================================================================
# Language Constants
# ============================================================================

LANGUAGE_CPP = "cpp"
"""C++ language identifier"""

LANGUAGE_PYTHON = "py"
"""Python language identifier"""

LANGUAGE_JAVA = "java"
"""Java language identifier"""

LANGUAGE_C = "c"
"""C language identifier"""

LANGUAGE_JAVASCRIPT = "js"
"""JavaScript language identifier"""

DEFAULT_LANGUAGE = LANGUAGE_CPP
"""Default language when none is specified"""

SUPPORTED_LANGUAGES = [
    LANGUAGE_CPP,
    LANGUAGE_PYTHON,
    LANGUAGE_JAVA,
    LANGUAGE_C,
    LANGUAGE_JAVASCRIPT
]
"""List of all supported programming languages"""


# ============================================================================
# File Extensions
# ============================================================================

EXTENSION_MAP = {
    LANGUAGE_CPP: ['.cpp', '.cc', '.cxx', '.h', '.hpp'],
    LANGUAGE_PYTHON: ['.py'],
    LANGUAGE_JAVA: ['.java'],
    LANGUAGE_C: ['.c', '.h'],
    LANGUAGE_JAVASCRIPT: ['.js'],
}
"""Maps languages to their file extensions"""


# ============================================================================
# Status Constants
# ============================================================================

STATUS_PASSED = "passed"
"""Test status: All tests passed"""

STATUS_FAILED = "failed"
"""Test status: Some tests failed"""

STATUS_ERROR = "error"
"""Test status: Error during execution"""

STATUS_SKIPPED = "skipped"
"""Test status: Test was skipped"""

VALID_STATUS_VALUES = [
    STATUS_PASSED,
    STATUS_FAILED,
    STATUS_ERROR,
    STATUS_SKIPPED
]
"""List of all valid test status values"""


# ============================================================================
# Performance Constants
# ============================================================================

SUCCESS_RATE_PERCENTAGE_MULTIPLIER = 100
"""Multiplier to convert success rate to percentage (0.75 -> 75%)"""

MAX_EXECUTION_TIME_SECONDS = 60
"""Maximum execution time for a single test in seconds"""

DEFAULT_TIMEOUT_SECONDS = 30
"""Default timeout for test execution"""


# ============================================================================
# Database Schema Constants
# ============================================================================

TABLE_TEST_RESULTS = "test_results"
"""Name of the test results table"""

TABLE_SESSIONS = "sessions"
"""Name of the sessions table"""

TABLE_PROJECTS = "projects"
"""Name of the projects table (if exists)"""


# ============================================================================
# Export Constants
# ============================================================================

EXPORT_FORMAT_CSV = "csv"
"""Export format: CSV"""

EXPORT_FORMAT_JSON = "json"
"""Export format: JSON"""

EXPORT_FORMAT_HTML = "html"
"""Export format: HTML"""

VALID_EXPORT_FORMATS = [
    EXPORT_FORMAT_CSV,
    EXPORT_FORMAT_JSON,
    EXPORT_FORMAT_HTML
]
"""List of all valid export formats"""
