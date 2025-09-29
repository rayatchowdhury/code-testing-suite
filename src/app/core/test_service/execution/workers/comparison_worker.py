"""
Comparison Worker - Async comparison test worker.
"""

import asyncio
from typing import Dict, AsyncIterator
from pathlib import Path
from .base_worker import BaseWorker
from ...results.result_models import TestResult


class ComparisonWorker(BaseWorker):
    """Async comparison test worker with proper resource management."""
    
    async def run_tests_async(self, test_count: int, executables: Dict[str, Path]) -> AsyncIterator[TestResult]:
        """Run comparison tests with async streaming results."""
        pass
    
    async def _run_single_test_async(self, test_num: int, executables: Dict[str, Path], 
                                   semaphore: asyncio.Semaphore, session) -> TestResult:
        """Run single comparison test with resource management."""
        pass
    
    async def _generate_input_async(self, generator_path: Path, session) -> str:
        """Generate test input asynchronously."""
        pass
    
    async def _execute_solution_async(self, executable_path: Path, input_data: str, session) -> dict:
        """Execute solution with input data asynchronously."""
        pass
    
    def _compare_outputs(self, output1: str, output2: str) -> bool:
        """Compare two outputs for correctness."""
        pass