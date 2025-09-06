
from src.app.tools.compiler_runner import CompilerRunner
from PySide6.QtCore import QObject, Signal
import logging

logger = logging.getLogger(__name__)

class TLECompilerRunner(CompilerRunner):
    """Specialized compiler runner for TLE testing"""
    
    # Additional signals specific to TLE testing
    compilationStarted = Signal()
    compilationFinished = Signal(bool)  # True if successful
    outputAvailable = Signal(str, str)  # message, type

    def __init__(self, console_output):
        # Initialize the base compiler runner (which already handles threading)
        super().__init__(console_output)
        
        # Connect additional signals for TLE-specific behavior
        if self.worker:
            self.worker.output.connect(self._handle_output_for_tle)
            self.worker.error.connect(self._handle_error_for_tle)
        
        logger.debug("TLECompilerRunner initialized")

    def _handle_output_for_tle(self, output_data):
        """Handle output with TLE-specific signals"""
        if isinstance(output_data, tuple) and len(output_data) == 2:
            text, format_type = output_data
        else:
            text, format_type = str(output_data), 'default'
            
        # Emit TLE-specific signal
        self.outputAvailable.emit(text, format_type)

    def _handle_error_for_tle(self, error_data):
        """Handle error with TLE-specific signals"""
        if isinstance(error_data, tuple) and len(error_data) == 2:
            text, format_type = error_data
        else:
            text, format_type = str(error_data), 'error'
            
        # Emit TLE-specific signal
        self.outputAvailable.emit(text, format_type)

    def compile_and_run_code(self, filepath):
        """Compile and run code for TLE testing"""
        logger.debug(f"Starting TLE test compilation for {filepath}")
        
        # Emit TLE-specific signal
        self.compilationStarted.emit()
        
        # Connect to finished signal to emit compilation result
        def on_finished():
            # Assume success if we get here without errors
            self.compilationFinished.emit(True)
            self.finished.disconnect(on_finished)
        
        self.finished.connect(on_finished)
        
        # Use base class method
        super().compile_and_run_code(filepath)

    def stop(self):
        """Stop any running process (alias for compatibility)"""
        self.stop_execution()