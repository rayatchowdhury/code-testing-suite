from src.app.core.tools.compiler_runner import CompilerRunner
from PySide6.QtCore import QObject, Signal
import logging

logger = logging.getLogger(__name__)

class ValidatorCompilerRunner(CompilerRunner):
    """Specialized compiler runner for validator testing"""
    
    def __init__(self, console_output):
        # Initialize the base compiler runner (which already handles threading)
        super().__init__(console_output)
        logger.debug("ValidatorCompilerRunner initialized")

    def compile_and_run_code(self, filepath):
        """Compile and run code for validator testing"""
        logger.debug(f"Starting validator test compilation for {filepath}")
        super().compile_and_run_code(filepath)