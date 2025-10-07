"""Generate realistic test data for migration testing"""
from datetime import datetime, timedelta
import random
from typing import List
from src.app.persistence.database import TestResult


def generate_old_format_results(count: int = 10) -> List[TestResult]:
    """
    Generate test results with OLD naming convention.
    
    Args:
        count: Number of test results to generate
        
    Returns:
        List of TestResult objects with old naming (stress, tle, validator)
    """
    results = []
    test_types_old = ["stress", "tle", "validator"]
    projects = ["AlgoProject", "DataStructures", "Optimization", "Testing"]
    
    for i in range(count):
        test_type = random.choice(test_types_old)
        
        # Determine file paths based on test type
        if test_type == "stress":
            file_path = f"comparator/test_{i}.cpp"
            files_snapshot = '{"generator_code": "// generator", "correct_code": "// correct", "test_code": "// test"}'
        elif test_type == "tle":
            file_path = f"benchmarker/test_{i}.java"
            files_snapshot = '{"generator_code": "// generator", "test_code": "// test"}'
        else:  # validator
            file_path = f"validator/test_{i}.py"
            files_snapshot = '{"generator_code": "# generator", "test_code": "# test", "validator_code": "# validator"}'
        
        test_count = random.randint(10, 100)
        passed_tests = random.randint(0, test_count)
        failed_tests = test_count - passed_tests
        
        result = TestResult(
            test_type=test_type,
            file_path=file_path,
            test_count=test_count,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_time=round(random.uniform(1.0, 30.0), 2),
            timestamp=(datetime.now() - timedelta(days=random.randint(0, 90))).isoformat(),
            test_details=f'[{{"test_number": 1, "passed": true}}]',
            project_name=random.choice(projects),
            files_snapshot=files_snapshot,
            mismatch_analysis='{"summary": "test analysis"}'
        )
        
        results.append(result)
    
    return results


def generate_new_format_results(count: int = 10) -> List[TestResult]:
    """
    Generate test results with NEW naming convention.
    
    Args:
        count: Number of test results to generate
        
    Returns:
        List of TestResult objects with new naming (comparison, benchmark, validator)
    """
    results = []
    test_types_new = ["comparison", "benchmark", "validator"]
    projects = ["AlgoProject", "DataStructures", "Optimization", "Testing"]
    
    for i in range(count):
        test_type = random.choice(test_types_new)
        
        # Determine file paths based on test type
        if test_type == "comparison":
            file_path = f"comparator/test_{i}.cpp"
            files_snapshot = '{"generator_code": "// generator", "correct_code": "// correct", "test_code": "// test"}'
        elif test_type == "benchmark":
            file_path = f"benchmarker/test_{i}.java"
            files_snapshot = '{"generator_code": "// generator", "test_code": "// test"}'
        else:  # validator
            file_path = f"validator/test_{i}.py"
            files_snapshot = '{"generator_code": "# generator", "test_code": "# test", "validator_code": "# validator"}'
        
        test_count = random.randint(10, 100)
        passed_tests = random.randint(0, test_count)
        failed_tests = test_count - passed_tests
        
        result = TestResult(
            test_type=test_type,
            file_path=file_path,
            test_count=test_count,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_time=round(random.uniform(1.0, 30.0), 2),
            timestamp=(datetime.now() - timedelta(days=random.randint(0, 90))).isoformat(),
            test_details=f'[{{"test_number": 1, "passed": true}}]',
            project_name=random.choice(projects),
            files_snapshot=files_snapshot,
            mismatch_analysis='{"summary": "test analysis"}'
        )
        
        results.append(result)
    
    return results


def generate_mixed_test_data(old_count: int = 50, new_count: int = 50) -> List[TestResult]:
    """
    Generate mixed test data with both old and new naming conventions.
    Useful for testing migration scenarios where data is partially migrated.
    
    Args:
        old_count: Number of old-format results
        new_count: Number of new-format results
        
    Returns:
        Combined list of old and new format test results
    """
    old_results = generate_old_format_results(old_count)
    new_results = generate_new_format_results(new_count)
    
    combined = old_results + new_results
    # Shuffle to mix them
    random.shuffle(combined)
    
    return combined


def generate_large_files_snapshot(include_all_languages: bool = True) -> str:
    """
    Generate a realistic files snapshot showing the bloat issue.
    
    Args:
        include_all_languages: If True, includes C++, Python, Java (bloat scenario)
                              If False, includes only one language (optimized)
    
    Returns:
        JSON string of files snapshot
    """
    if include_all_languages:
        # BLOAT: All languages even though only one was used
        return '''{
            "generator_code": "// C++ generator\\nint main() { return 0; }",
            "correct_code": "// C++ correct\\nint main() { return 0; }",
            "test_code": "// C++ test\\nint main() { return 0; }",
            "additional_files": {
                "generator.py": "# Python generator\\nprint('test')",
                "correct.py": "# Python correct\\nprint('test')",
                "test.py": "# Python test\\nprint('test')",
                "Generator.java": "// Java generator\\npublic class Generator {}",
                "Correct.java": "// Java correct\\npublic class Correct {}",
                "Test.java": "// Java test\\npublic class Test {}"
            }
        }'''
    else:
        # OPTIMIZED: Only the files actually used
        return '''{
            "generator_code": "// C++ generator\\nint main() { return 0; }",
            "correct_code": "// C++ correct\\nint main() { return 0; }",
            "test_code": "// C++ test\\nint main() { return 0; }"
        }'''


def populate_test_database(db_manager, count: int = 100, use_old_naming: bool = True):
    """
    Populate a database with test data for migration testing.
    
    Args:
        db_manager: DatabaseManager instance
        count: Number of test results to generate
        use_old_naming: If True, uses old naming; if False, uses new naming
    """
    if use_old_naming:
        results = generate_old_format_results(count)
    else:
        results = generate_new_format_results(count)
    
    saved_count = 0
    for result in results:
        result_id = db_manager.save_test_result(result)
        if result_id > 0:
            saved_count += 1
    
    return saved_count


if __name__ == "__main__":
    # Demo: Generate sample data
    print("Generating OLD format results (stress, tle, validator):")
    old_results = generate_old_format_results(5)
    for r in old_results:
        print(f"  - {r.test_type}: {r.file_path} ({r.passed_tests}/{r.test_count} passed)")
    
    print("\nGenerating NEW format results (comparison, benchmark, validator):")
    new_results = generate_new_format_results(5)
    for r in new_results:
        print(f"  - {r.test_type}: {r.file_path} ({r.passed_tests}/{r.test_count} passed)")
    
    print("\nGenerating MIXED format results:")
    mixed_results = generate_mixed_test_data(3, 3)
    for r in mixed_results:
        print(f"  - {r.test_type}: {r.file_path}")
    
    print("\n✓ Test data generator working correctly!")
