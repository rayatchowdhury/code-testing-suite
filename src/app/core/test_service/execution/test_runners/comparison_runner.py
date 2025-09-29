"""
Comparison Runner - Handles comparison/stress testing.
"""

import asyncio
from typing import Dict, AsyncIterator
from pathlib import Path
from .base_runner import BaseRunner
from ...results.result_models import TestResult


class ComparisonRunner(BaseRunner):
    """Comparison test runner with parallel execution."""
    
    async def run_tests_async(self, test_count: int, executables: Dict[str, Path]) -> AsyncIterator[TestResult]:
        """Run comparison tests with generator, test, and correct solutions."""
        pass
    
    async def _run_single_comparison_test(self, test_num: int, executables: Dict[str, Path]) -> TestResult:
        """Run single comparison test."""
        pass
    
    async def _generate_input(self, generator_path: Path) -> str:
        """Generate test input using generator."""
        pass
    
    async def _execute_solution(self, executable_path: Path, input_data: str) -> str:
        """Execute solution with input data."""
        pass
    
    def _compare_outputs(self, output1: str, output2: str) -> bool:
        """Compare two outputs for correctness."""
        pass