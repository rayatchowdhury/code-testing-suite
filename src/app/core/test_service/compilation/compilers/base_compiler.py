"""
Base Compiler - Abstract base class for all language compilers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from ...config.config_models import LanguageConfig
from ...results.result_models import CompilationResult


class BaseCompiler(ABC):
    """Abstract base class for language-specific compilers."""
    
    def __init__(self, language: str):
        """Initialize base compiler."""
        self.language = language
    
    @abstractmethod
    async def compile_async(self, file_path: Path, config: LanguageConfig) -> CompilationResult:
        """Compile file asynchronously."""
        pass
    
    @abstractmethod
    def _build_command(self, file_path: Path, config: LanguageConfig) -> List[str]:
        """Build compilation command."""
        pass
    
    def _needs_recompilation(self, source_path: Path, output_path: Path) -> bool:
        """Check if recompilation is needed."""
        pass
    
    def _get_output_path(self, source_path: Path) -> Path:
        """Get output executable path."""
        pass