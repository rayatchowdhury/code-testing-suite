"""
Validation Runner - Handles custom validation testing.
"""

import asyncio
from typing import Dict, AsyncIterator
from pathlib import Path
from .base_runner import BaseRunner
from ...results.result_models import TestResult


class ValidationRunner(BaseRunner):
    """Validation test runner with custom validators."""
    
    async def run_tests_async(self, test_count: int, executables: Dict[str, Path]) -> AsyncIterator[TestResult]:
        """Run validation tests with custom validator."""
        pass
    
    async def _run_single_validation_test(self, test_num: int, executables: Dict[str, Path]) -> TestResult:
        """Run single validation test."""
        pass
    
    async def _validate_output(self, validator_path: Path, input_data: str, output_data: str) -> Dict:
        """Validate output using custom validator."""
        pass