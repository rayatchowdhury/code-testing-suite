"""
Base Worker - Abstract base class for async workers.
"""

from abc import ABC, abstractmethod
import asyncio
from typing import Dict, AsyncIterator
from pathlib import Path
from ...config.config_service import ConfigService
from ...resources.resource_manager import ResourceManager, ResourceSession
from ...results.result_models import TestResult


class BaseWorker(ABC):
    """Abstract base class for async test workers."""
    
    def __init__(self, config_service: ConfigService, resource_manager: ResourceManager):
        """Initialize base worker."""
        self.config_service = config_service
        self.resource_manager = resource_manager
    
    @abstractmethod
    async def run_tests_async(self, test_count: int, executables: Dict[str, Path]) -> AsyncIterator[TestResult]:
        """Run tests asynchronously with streaming results."""
        pass
    
    async def _stream_test_results(self, tasks: list) -> AsyncIterator[TestResult]:
        """Stream test results as they complete."""
        pass
    
    def _validate_executables(self, executables: Dict[str, Path]) -> bool:
        """Validate that all required executables exist."""
        pass