"""
Base Runner - Abstract base class for test runners.
"""

from abc import ABC, abstractmethod
import asyncio
from typing import Dict, AsyncIterator
from pathlib import Path
from ...config.config_service import ConfigService
from ...resources.resource_manager import ResourceManager
from ...results.result_models import TestResult


class BaseRunner(ABC):
    """Abstract base class for all test runners."""
    
    def __init__(self, config_service: ConfigService, resource_manager: ResourceManager):
        """Initialize base runner."""
        self.config_service = config_service
        self.resource_manager = resource_manager
    
    @abstractmethod
    async def run_tests_async(self, test_count: int, executables: Dict[str, Path]) -> AsyncIterator[TestResult]:
        """Run tests asynchronously."""
        pass
    
    def _validate_executables(self, executables: Dict[str, Path]) -> bool:
        """Validate that all required executables exist."""
        pass
    
    def _get_execution_config(self) -> Dict:
        """Get execution configuration."""
        pass