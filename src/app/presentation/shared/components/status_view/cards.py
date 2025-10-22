"""
Domain-Specific Test Cards

Type-specific cards that store additional data for detail views.
These are thin wrappers around BaseTestCard.
"""

from .widgets import BaseTestCard
from .models import TestResult

class ComparatorTestCard(BaseTestCard):
    """Card for comparator tests"""
    
    def __init__(self, result: TestResult, parent=None):
        super().__init__(
            test_number=result.test_number,
            passed=result.passed,
            time=result.time,
            memory=result.memory,
            parent=parent
        )
        self.result = result

class ValidatorTestCard(BaseTestCard):
    """Card for validator tests"""
    
    def __init__(self, result: TestResult, parent=None):
        super().__init__(
            test_number=result.test_number,
            passed=result.passed,
            time=result.time,
            memory=result.memory,
            parent=parent
        )
        self.result = result

class BenchmarkerTestCard(BaseTestCard):
    """Card for benchmarker tests"""
    
    def __init__(self, result: TestResult, parent=None):
        super().__init__(
            test_number=result.test_number,
            passed=result.passed,
            time=result.time,
            memory=result.memory,
            parent=parent
        )
        self.result = result
