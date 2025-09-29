"""
Validation Worker - Async validation test worker.
"""

import asyncio
from typing import Dict, AsyncIterator
from pathlib import Path
from .base_worker import BaseWorker
from ...results.result_models import TestResult


class ValidationWorker(BaseWorker):
    """Async validation test worker with custom validators."""
    
    async def run_tests_async(self, test_count: int, executables: Dict[str, Path]) -> AsyncIterator[TestResult]:
        """Run validation tests with custom validator."""
        pass
    
    async def _run_single_validation_async(self, test_num: int, executables: Dict[str, Path], 
                                         semaphore: asyncio.Semaphore, session) -> TestResult:
        """Run single validation test."""
        pass
    
    async def _validate_output_async(self, validator_path: Path, input_data: str, 
                                   output_data: str, session) -> Dict:
        """Validate output using custom validator."""
        pass