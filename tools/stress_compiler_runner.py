from tools.compiler_runner import CompilerRunner, CompilerWorker
from PySide6.QtCore import QThread, Signal, QObject

class StressCompilerWorker(CompilerWorker):
    def __init__(self):
        super().__init__()
        # Additional setup for stress testing if needed
        pass

class StressCompilerRunner(CompilerRunner):
    def __init__(self, console_output):
        super().__init__(console_output)
        
        # Create thread
        self.thread = QThread()
        
        # Move worker to thread
        self.worker.moveToThread(self.thread)
        
        # Connect thread signals
        self.thread.started.connect(self._on_thread_start)
        self.worker.finished.connect(self.thread.quit)
        self.thread.finished.connect(self._cleanup)

    def compile_and_run_code(self, filepath):
        """Start compilation and execution in separate thread"""
        if not filepath:
            if self.console:
                self.console.displayOutput("Error: No file to compile\n", 'error')
            return
        
        self.stop_execution()
        if self.console:
            try:
                self.console.clear()
                self.console.setInputEnabled(True)
            except AttributeError as e:
                print(f"Warning: Console operation failed - {str(e)}")
        
        # Store filepath for thread
        self.pending_filepath = filepath
        # Start thread
        self.thread.start()

    def _on_thread_start(self):
        """Called when thread starts"""
        self.worker.compile_and_run(self.pending_filepath)

    def stop_execution(self):
        """Stop execution and thread safely"""
        super().stop_execution()
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

    def _cleanup(self):
        """Clean up resources safely"""
        super()._cleanup()
        # Additional thread cleanup if needed
