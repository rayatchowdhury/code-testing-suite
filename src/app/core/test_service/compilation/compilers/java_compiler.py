"""
Java Compiler - Handles Java compilation and execution setup.
"""

from pathlib import Path
from typing import List
from .base_compiler import BaseCompiler
from ...config.config_models import LanguageConfig
from ...results.result_models import CompilationResult


class JavaCompiler(BaseCompiler):
    """Java compiler with configurable versions."""
    
    def __init__(self):
        """Initialize Java compiler."""
        super().__init__('java')
    
    async def compile_async(self, file_path: Path, config: LanguageConfig) -> CompilationResult:
        """Compile Java file with javac."""
        pass
    
    def _build_command(self, file_path: Path, config: LanguageConfig) -> List[str]:
        """Build javac compilation command."""
        pass
    
    def _get_class_name(self, file_path: Path) -> str:
        """Extract class name from Java file."""
        pass
    
    def _build_run_command(self, class_name: str, config: LanguageConfig) -> List[str]:
        """Build java execution command."""
        pass