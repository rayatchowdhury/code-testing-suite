"""Test database constants.

This module tests that all constants are properly defined and have expected values.
Phase 3: Extract Constants & Utilities
"""
import pytest
from src.app.persistence.database.constants import (
    # Query Limits
    DEFAULT_RESULTS_LIMIT,
    DEFAULT_SESSIONS_LIMIT,
    DEFAULT_PROJECTS_LIMIT,
    EXPORT_RESULTS_LIMIT,
    MAX_SEARCH_RESULTS,
    # Cleanup & Retention
    DEFAULT_CLEANUP_DAYS,
    OLD_DATA_CLEANUP_DAYS,
    MAX_DATABASE_SIZE_MB,
    VACUUM_THRESHOLD_MB,
    # Test Types
    TEST_TYPE_COMPARISON,
    TEST_TYPE_VALIDATOR,
    TEST_TYPE_BENCHMARK,
    VALID_TEST_TYPES,
    LEGACY_TEST_TYPE_MAP,
    # File Roles
    FILE_ROLE_GENERATOR,
    FILE_ROLE_CORRECT,
    FILE_ROLE_TEST,
    FILE_ROLE_VALIDATOR,
    FILE_ROLE_CHECKER,
    VALID_FILE_ROLES,
    # Languages
    LANGUAGE_CPP,
    LANGUAGE_PYTHON,
    LANGUAGE_JAVA,
    LANGUAGE_C,
    LANGUAGE_JAVASCRIPT,
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    EXTENSION_MAP,
    # Status
    STATUS_PASSED,
    STATUS_FAILED,
    STATUS_ERROR,
    STATUS_SKIPPED,
    VALID_STATUS_VALUES,
    # Performance
    SUCCESS_RATE_PERCENTAGE_MULTIPLIER,
    MAX_EXECUTION_TIME_SECONDS,
    DEFAULT_TIMEOUT_SECONDS,
    # Database Schema
    TABLE_TEST_RESULTS,
    TABLE_SESSIONS,
    TABLE_PROJECTS,
    # Export
    EXPORT_FORMAT_CSV,
    EXPORT_FORMAT_JSON,
    EXPORT_FORMAT_HTML,
    VALID_EXPORT_FORMATS,
)


class TestQueryLimits:
    """Test query limit constants."""
    
    def test_default_results_limit(self):
        """Test default results limit is 100."""
        assert DEFAULT_RESULTS_LIMIT == 100
        assert isinstance(DEFAULT_RESULTS_LIMIT, int)
    
    def test_default_sessions_limit(self):
        """Test default sessions limit is 10."""
        assert DEFAULT_SESSIONS_LIMIT == 10
        assert isinstance(DEFAULT_SESSIONS_LIMIT, int)
    
    def test_default_projects_limit(self):
        """Test default projects limit is 50."""
        assert DEFAULT_PROJECTS_LIMIT == 50
        assert isinstance(DEFAULT_PROJECTS_LIMIT, int)
    
    def test_export_results_limit(self):
        """Test export results limit is 1000."""
        assert EXPORT_RESULTS_LIMIT == 1000
        assert isinstance(EXPORT_RESULTS_LIMIT, int)
    
    def test_max_search_results(self):
        """Test max search results is 500."""
        assert MAX_SEARCH_RESULTS == 500
        assert isinstance(MAX_SEARCH_RESULTS, int)
    
    def test_limits_are_positive(self):
        """Test all limits are positive numbers."""
        assert DEFAULT_RESULTS_LIMIT > 0
        assert DEFAULT_SESSIONS_LIMIT > 0
        assert DEFAULT_PROJECTS_LIMIT > 0
        assert EXPORT_RESULTS_LIMIT > 0
        assert MAX_SEARCH_RESULTS > 0


class TestCleanupConstants:
    """Test cleanup and retention constants."""
    
    def test_default_cleanup_days(self):
        """Test default cleanup days is 7."""
        assert DEFAULT_CLEANUP_DAYS == 7
        assert isinstance(DEFAULT_CLEANUP_DAYS, int)
    
    def test_old_data_cleanup_days(self):
        """Test old data cleanup days is 30."""
        assert OLD_DATA_CLEANUP_DAYS == 30
        assert isinstance(OLD_DATA_CLEANUP_DAYS, int)
    
    def test_max_database_size_mb(self):
        """Test max database size is 500 MB."""
        assert MAX_DATABASE_SIZE_MB == 500
        assert isinstance(MAX_DATABASE_SIZE_MB, int)
    
    def test_vacuum_threshold_mb(self):
        """Test vacuum threshold is 100 MB."""
        assert VACUUM_THRESHOLD_MB == 100
        assert isinstance(VACUUM_THRESHOLD_MB, int)
    
    def test_cleanup_days_ordering(self):
        """Test cleanup days have logical ordering."""
        assert DEFAULT_CLEANUP_DAYS < OLD_DATA_CLEANUP_DAYS
    
    def test_size_thresholds_ordering(self):
        """Test size thresholds have logical ordering."""
        assert VACUUM_THRESHOLD_MB < MAX_DATABASE_SIZE_MB


class TestTestTypes:
    """Test test type constants."""
    
    def test_test_type_comparison(self):
        """Test comparison test type."""
        assert TEST_TYPE_COMPARISON == "comparison"
        assert isinstance(TEST_TYPE_COMPARISON, str)
    
    def test_test_type_validator(self):
        """Test validator test type."""
        assert TEST_TYPE_VALIDATOR == "validator"
        assert isinstance(TEST_TYPE_VALIDATOR, str)
    
    def test_test_type_benchmark(self):
        """Test benchmark test type."""
        assert TEST_TYPE_BENCHMARK == "benchmark"
        assert isinstance(TEST_TYPE_BENCHMARK, str)
    
    def test_valid_test_types_list(self):
        """Test valid test types list contains all types."""
        assert TEST_TYPE_COMPARISON in VALID_TEST_TYPES
        assert TEST_TYPE_VALIDATOR in VALID_TEST_TYPES
        assert TEST_TYPE_BENCHMARK in VALID_TEST_TYPES
        assert len(VALID_TEST_TYPES) == 3
    
    def test_legacy_test_type_map(self):
        """Test legacy test type mapping."""
        assert LEGACY_TEST_TYPE_MAP['stress'] == TEST_TYPE_COMPARISON
        assert LEGACY_TEST_TYPE_MAP['tle'] == TEST_TYPE_BENCHMARK
        assert LEGACY_TEST_TYPE_MAP['stress_test'] == TEST_TYPE_COMPARISON
        assert LEGACY_TEST_TYPE_MAP['time_limit'] == TEST_TYPE_BENCHMARK
    
    def test_legacy_map_values_are_valid(self):
        """Test all legacy map values are valid test types."""
        for legacy_type, current_type in LEGACY_TEST_TYPE_MAP.items():
            assert current_type in VALID_TEST_TYPES, f"{current_type} not in valid types"


class TestFileRoles:
    """Test file role constants."""
    
    def test_file_role_generator(self):
        """Test generator role."""
        assert FILE_ROLE_GENERATOR == "generator"
    
    def test_file_role_correct(self):
        """Test correct role."""
        assert FILE_ROLE_CORRECT == "correct"
    
    def test_file_role_test(self):
        """Test test role."""
        assert FILE_ROLE_TEST == "test"
    
    def test_file_role_validator(self):
        """Test validator role."""
        assert FILE_ROLE_VALIDATOR == "validator"
    
    def test_file_role_checker(self):
        """Test checker role."""
        assert FILE_ROLE_CHECKER == "checker"
    
    def test_valid_file_roles_list(self):
        """Test valid file roles list."""
        assert FILE_ROLE_GENERATOR in VALID_FILE_ROLES
        assert FILE_ROLE_CORRECT in VALID_FILE_ROLES
        assert FILE_ROLE_TEST in VALID_FILE_ROLES
        assert FILE_ROLE_VALIDATOR in VALID_FILE_ROLES
        assert FILE_ROLE_CHECKER in VALID_FILE_ROLES
        assert len(VALID_FILE_ROLES) == 5


class TestLanguageConstants:
    """Test language constants."""
    
    def test_language_constants(self):
        """Test language identifier constants."""
        assert LANGUAGE_CPP == "cpp"
        assert LANGUAGE_PYTHON == "py"
        assert LANGUAGE_JAVA == "java"
        assert LANGUAGE_C == "c"
        assert LANGUAGE_JAVASCRIPT == "js"
    
    def test_default_language(self):
        """Test default language is C++."""
        assert DEFAULT_LANGUAGE == LANGUAGE_CPP
        assert DEFAULT_LANGUAGE in SUPPORTED_LANGUAGES
    
    def test_supported_languages_list(self):
        """Test supported languages list."""
        assert LANGUAGE_CPP in SUPPORTED_LANGUAGES
        assert LANGUAGE_PYTHON in SUPPORTED_LANGUAGES
        assert LANGUAGE_JAVA in SUPPORTED_LANGUAGES
        assert LANGUAGE_C in SUPPORTED_LANGUAGES
        assert LANGUAGE_JAVASCRIPT in SUPPORTED_LANGUAGES
        assert len(SUPPORTED_LANGUAGES) == 5
    
    def test_extension_map_completeness(self):
        """Test extension map has all supported languages."""
        for lang in SUPPORTED_LANGUAGES:
            assert lang in EXTENSION_MAP, f"Language {lang} missing from EXTENSION_MAP"
            assert isinstance(EXTENSION_MAP[lang], list)
            assert len(EXTENSION_MAP[lang]) > 0
    
    def test_extension_map_extensions_format(self):
        """Test all extensions start with a dot."""
        for lang, extensions in EXTENSION_MAP.items():
            for ext in extensions:
                assert ext.startswith('.'), f"Extension {ext} for {lang} should start with '.'"


class TestStatusConstants:
    """Test status constants."""
    
    def test_status_constants(self):
        """Test status constant values."""
        assert STATUS_PASSED == "passed"
        assert STATUS_FAILED == "failed"
        assert STATUS_ERROR == "error"
        assert STATUS_SKIPPED == "skipped"
    
    def test_valid_status_values_list(self):
        """Test valid status values list."""
        assert STATUS_PASSED in VALID_STATUS_VALUES
        assert STATUS_FAILED in VALID_STATUS_VALUES
        assert STATUS_ERROR in VALID_STATUS_VALUES
        assert STATUS_SKIPPED in VALID_STATUS_VALUES
        assert len(VALID_STATUS_VALUES) == 4


class TestPerformanceConstants:
    """Test performance constants."""
    
    def test_success_rate_multiplier(self):
        """Test success rate percentage multiplier."""
        assert SUCCESS_RATE_PERCENTAGE_MULTIPLIER == 100
        # Test conversion: 0.75 * 100 = 75%
        assert 0.75 * SUCCESS_RATE_PERCENTAGE_MULTIPLIER == 75.0
    
    def test_max_execution_time(self):
        """Test max execution time."""
        assert MAX_EXECUTION_TIME_SECONDS == 60
        assert isinstance(MAX_EXECUTION_TIME_SECONDS, int)
    
    def test_default_timeout(self):
        """Test default timeout."""
        assert DEFAULT_TIMEOUT_SECONDS == 30
        assert isinstance(DEFAULT_TIMEOUT_SECONDS, int)
    
    def test_timeout_ordering(self):
        """Test timeout has logical ordering."""
        assert DEFAULT_TIMEOUT_SECONDS <= MAX_EXECUTION_TIME_SECONDS


class TestDatabaseSchemaConstants:
    """Test database schema constants."""
    
    def test_table_names(self):
        """Test table name constants."""
        assert TABLE_TEST_RESULTS == "test_results"
        assert TABLE_SESSIONS == "sessions"
        assert TABLE_PROJECTS == "projects"
    
    def test_table_names_are_strings(self):
        """Test all table names are strings."""
        assert isinstance(TABLE_TEST_RESULTS, str)
        assert isinstance(TABLE_SESSIONS, str)
        assert isinstance(TABLE_PROJECTS, str)


class TestExportConstants:
    """Test export constants."""
    
    def test_export_format_constants(self):
        """Test export format constant values."""
        assert EXPORT_FORMAT_CSV == "csv"
        assert EXPORT_FORMAT_JSON == "json"
        assert EXPORT_FORMAT_HTML == "html"
    
    def test_valid_export_formats_list(self):
        """Test valid export formats list."""
        assert EXPORT_FORMAT_CSV in VALID_EXPORT_FORMATS
        assert EXPORT_FORMAT_JSON in VALID_EXPORT_FORMATS
        assert EXPORT_FORMAT_HTML in VALID_EXPORT_FORMATS
        assert len(VALID_EXPORT_FORMATS) == 3


class TestConstantImmutability:
    """Test that constants are properly typed."""
    
    def test_string_constants_are_strings(self):
        """Test all string constants are actually strings."""
        string_constants = [
            TEST_TYPE_COMPARISON, TEST_TYPE_VALIDATOR, TEST_TYPE_BENCHMARK,
            FILE_ROLE_GENERATOR, FILE_ROLE_CORRECT, FILE_ROLE_TEST,
            LANGUAGE_CPP, LANGUAGE_PYTHON, LANGUAGE_JAVA,
            STATUS_PASSED, STATUS_FAILED, STATUS_ERROR,
            TABLE_TEST_RESULTS, TABLE_SESSIONS,
            EXPORT_FORMAT_CSV, EXPORT_FORMAT_JSON,
        ]
        for const in string_constants:
            assert isinstance(const, str), f"Constant {const} should be a string"
    
    def test_integer_constants_are_integers(self):
        """Test all integer constants are actually integers."""
        int_constants = [
            DEFAULT_RESULTS_LIMIT, DEFAULT_SESSIONS_LIMIT, DEFAULT_PROJECTS_LIMIT,
            DEFAULT_CLEANUP_DAYS, OLD_DATA_CLEANUP_DAYS,
            MAX_DATABASE_SIZE_MB, VACUUM_THRESHOLD_MB,
            SUCCESS_RATE_PERCENTAGE_MULTIPLIER,
            MAX_EXECUTION_TIME_SECONDS, DEFAULT_TIMEOUT_SECONDS,
        ]
        for const in int_constants:
            assert isinstance(const, int), f"Constant {const} should be an integer"
    
    def test_list_constants_are_lists(self):
        """Test all list constants are actually lists."""
        list_constants = [
            VALID_TEST_TYPES, VALID_FILE_ROLES, SUPPORTED_LANGUAGES,
            VALID_STATUS_VALUES, VALID_EXPORT_FORMATS,
        ]
        for const in list_constants:
            assert isinstance(const, list), f"Constant {const} should be a list"
    
    def test_dict_constants_are_dicts(self):
        """Test all dict constants are actually dicts."""
        dict_constants = [LEGACY_TEST_TYPE_MAP, EXTENSION_MAP]
        for const in dict_constants:
            assert isinstance(const, dict), f"Constant {const} should be a dict"
