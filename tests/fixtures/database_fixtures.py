"""
Database test fixtures and builders.

Provides reusable test data for database layer testing including:
- Sample TestResult objects
- Test data builders
- Mock file contents
- Database snapshots
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import asdict

from src.app.persistence.database.models import TestResult


class ResultBuilder:
    """Builder pattern for creating TestResult objects in tests (renamed to avoid pytest collection)."""
    
    def __init__(self):
        """Initialize with default values."""
        self._test_type = 'comparator'
        self._file_path = '/test/path/test.cpp'
        self._test_count = 10
        self._passed_tests = 8
        self._failed_tests = 2
        self._total_time = 1.234
        self._timestamp = datetime.now().isoformat()
        self._test_details = json.dumps([
            {'test_number': 1, 'passed': True, 'time': 0.1},
            {'test_number': 2, 'passed': False, 'time': 0.2},
        ])
        self._project_name = 'test_project'
        self._files_snapshot = ''
        self._mismatch_analysis = ''
    
    def with_test_type(self, test_type: str) -> 'ResultBuilder':
        """Set test type (comparator, validator, benchmarker)."""
        self._test_type = test_type
        return self
    
    def with_file_path(self, file_path: str) -> 'ResultBuilder':
        """Set file path."""
        self._file_path = file_path
        return self
    
    def with_test_count(self, count: int) -> 'ResultBuilder':
        """Set number of tests."""
        self._test_count = count
        return self
    
    def with_results(self, passed: int, failed: int) -> 'ResultBuilder':
        """Set test results."""
        self._passed_tests = passed
        self._failed_tests = failed
        self._test_count = passed + failed
        return self
    
    def with_total_time(self, time: float) -> 'ResultBuilder':
        """Set total execution time."""
        self._total_time = time
        return self
    
    def with_timestamp(self, timestamp: str) -> 'ResultBuilder':
        """Set timestamp."""
        self._timestamp = timestamp
        return self
    
    def with_test_details(self, details: List[Dict]) -> 'ResultBuilder':
        """Set test details."""
        self._test_details = json.dumps(details)
        return self
    
    def with_project_name(self, name: str) -> 'ResultBuilder':
        """Set project name."""
        self._project_name = name
        return self
    
    def with_files_snapshot(self, snapshot: str) -> 'ResultBuilder':
        """Set files snapshot."""
        self._files_snapshot = snapshot
        return self
    
    def with_mismatch_analysis(self, analysis: str) -> 'ResultBuilder':
        """Set mismatch analysis."""
        self._mismatch_analysis = analysis
        return self
    
    def build(self) -> TestResult:
        """Build the TestResult object."""
        return TestResult(
            id=None,  # Will be assigned by database
            test_type=self._test_type,
            file_path=self._file_path,
            test_count=self._test_count,
            passed_tests=self._passed_tests,
            failed_tests=self._failed_tests,
            total_time=self._total_time,
            timestamp=self._timestamp,
            test_details=self._test_details,
            project_name=self._project_name,
            files_snapshot=self._files_snapshot,
            mismatch_analysis=self._mismatch_analysis
        )


def create_sample_test_result(test_type: str = 'comparator', **kwargs) -> TestResult:
    """
    Create a sample TestResult with default or custom values.
    
    Args:
        test_type: Type of test (comparator, validator, benchmarker)
        **kwargs: Additional fields to override defaults
    
    Returns:
        TestResult object with sample data
    """
    builder = ResultBuilder().with_test_type(test_type)
    
    for key, value in kwargs.items():
        if key == 'passed_tests' or key == 'failed_tests':
            builder.with_results(
                kwargs.get('passed_tests', 8),
                kwargs.get('failed_tests', 2)
            )
        elif hasattr(builder, f'with_{key}'):
            getattr(builder, f'with_{key}')(value)
    
    return builder.build()


def create_test_result_series(count: int = 5, test_type: str = 'comparator') -> List[TestResult]:
    """
    Create a series of test results over time.
    
    Args:
        count: Number of test results to create
        test_type: Type of tests
    
    Returns:
        List of TestResult objects with incrementing timestamps
    """
    base_time = datetime.now()
    results = []
    
    for i in range(count):
        timestamp = (base_time - timedelta(hours=i)).isoformat()
        result = ResultBuilder() \
            .with_test_type(test_type) \
            .with_timestamp(timestamp) \
            .with_results(passed=10 - i, failed=i) \
            .with_project_name(f'project_{i % 3}') \
            .build()
        results.append(result)
    
    return results


def create_files_snapshot(files: Dict[str, str]) -> str:
    """
    Create a JSON snapshot of file contents.
    
    Args:
        files: Dictionary mapping file names to their contents
    
    Returns:
        JSON string of files snapshot
    """
    snapshot = {
        'files': files,
        'created_at': datetime.now().isoformat()
    }
    return json.dumps(snapshot)


# Sample file contents for testing
SAMPLE_CPP_CODE = """
#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    cout << n * 2 << endl;
    return 0;
}
""".strip()

SAMPLE_PYTHON_CODE = """
def main():
    n = int(input())
    print(n * 2)

if __name__ == '__main__':
    main()
""".strip()

SAMPLE_JAVA_CODE = """
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        System.out.println(n * 2);
    }
}
""".strip()

SAMPLE_GENERATOR_CODE = """
#include <iostream>
#include <random>
using namespace std;

int main() {
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<> dis(1, 100);
    cout << dis(gen) << endl;
    return 0;
}
""".strip()

SAMPLE_VALIDATOR_CODE = """
#include <iostream>
using namespace std;

int main() {
    int answer, output;
    cin >> answer >> output;
    if (answer == output) return 0;  // Accepted
    if (abs(answer - output) <= 1) return 2;  // Presentation Error
    return 1;  // Wrong Answer
}
""".strip()


# Sample test details
def create_test_details(count: int = 10, pass_rate: float = 0.8) -> str:
    """
    Create sample test details JSON.
    
    Args:
        count: Number of tests
        pass_rate: Percentage of tests that should pass (0.0 to 1.0)
    
    Returns:
        JSON string of test details
    """
    details = []
    for i in range(1, count + 1):
        passed = i <= int(count * pass_rate)
        details.append({
            'test_number': i,
            'passed': passed,
            'total_time': round(0.1 + (i * 0.01), 3),
            'memory': round(10.0 + (i * 0.5), 2),
            'status': 'PASS' if passed else 'FAIL',
            'expected_output': f'output_{i}',
            'actual_output': f'output_{i}' if passed else f'wrong_{i}'
        })
    return json.dumps(details)


# Sample mismatch analysis
SAMPLE_MISMATCH_ANALYSIS = """
Test #1: PASSED
  Expected: 42
  Got: 42
  
Test #2: FAILED
  Expected: 100
  Got: 99
  Difference: Output is off by 1
  
Test #3: PASSED
  Expected: hello world
  Got: hello world
""".strip()


# Database query filters
class TestResultFilters:
    """Common filter configurations for test result queries."""
    
    @staticmethod
    def by_test_type(test_type: str) -> Dict:
        """Filter by test type."""
        return {'test_type': test_type}
    
    @staticmethod
    def by_date_range(start_date: str, end_date: str) -> Dict:
        """Filter by date range."""
        return {
            'start_date': start_date,
            'end_date': end_date
        }
    
    @staticmethod
    def by_project(project_name: str) -> Dict:
        """Filter by project name."""
        return {'project_name': project_name}
    
    @staticmethod
    def passing_tests_only() -> Dict:
        """Filter for tests with 100% pass rate."""
        return {'min_pass_rate': 1.0}
    
    @staticmethod
    def failing_tests_only() -> Dict:
        """Filter for tests with failures."""
        return {'has_failures': True}
