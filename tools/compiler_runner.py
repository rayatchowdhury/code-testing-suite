from PySide6.QtCore import QObject, Signal, QProcess
import os
import sys

class CompilerWorker(QObject):
    finished = Signal()
    output = Signal(tuple)  # Change to emit tuple
    error = Signal(tuple)   # Change to emit tuple
    input_requested = Signal()

    def __init__(self):
        super().__init__()
        self.process = None

    def compile_and_run(self, filepath):
        try:
            self.output.emit(("Compiling...\n", 'info'))
            compile_process = QProcess()
            compile_process.setProgram('g++')
            compile_process.setArguments([filepath, '-o', os.path.splitext(filepath)[0]])
            compile_process.start()
            compile_process.waitForFinished()

            if compile_process.exitCode() != 0:
                error_output = compile_process.readAllStandardError().data().decode()
                self.error.emit((f"Compilation Error:\n{error_output}", 'error'))
                self.finished.emit()
                return

            self.output.emit(("Compilation successful!\n", 'success'))
            self.output.emit(("Running program...\n\n", 'info'))
            
            exe_path = os.path.splitext(filepath)[0] + ('.exe' if os.name == 'nt' else '')
            self.process = QProcess()
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyReadStandardOutput.connect(self.handle_output)
            self.process.readyReadStandardError.connect(self.handle_error)
            self.process.finished.connect(self.process_finished)
            self.process.start(exe_path)
        except Exception as e:
            self.error.emit((f"Error: {str(e)}", 'error'))
            self.finished.emit()

    def handle_output(self):
        while self.process and self.process.canReadLine():
            output = self.process.readLine().data().decode()
            self.output.emit((output, 'default'))  # Always emit tuple
            if output.strip() == '':
                self.input_requested.emit()

    def handle_error(self):
        if self.process:
            error = self.process.readAllStandardError().data().decode()
            if error:
                self.error.emit((error, 'error'))  # Always emit tuple

    def handle_input(self, text):
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.process.write((text + '\n').encode())

    def stop_execution(self):
        """Stop the running process safely"""
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.process.finished.disconnect()  # Disconnect to prevent callback
            self.process.kill()
            self.process.waitForFinished()  # Wait for process to actually terminate
        self.process = None

    def process_finished(self):
        """Handle process completion"""
        if self.process:  # Check if process still exists
            self.output.emit(("\nProgram finished.\n", 'success'))  # Emit as tuple
            self.process = None
        self.finished.emit()

class CompilerRunner(QObject):
    finished = Signal()

    def __init__(self, console_output):
        super().__init__()
        self.console = console_output
        self.worker = CompilerWorker()
        self._setup_connections()

    def _setup_connections(self):
        """Setup signal connections"""
        self.console.inputSubmitted.connect(self.worker.handle_input)
        self.worker.output.connect(self.handle_output)
        self.worker.error.connect(self.handle_error)
        self.worker.input_requested.connect(self.handle_input_request)
        self.worker.finished.connect(self._cleanup)

    def handle_output(self, output_data):
        """Handle output safely"""
        if isinstance(output_data, tuple) and len(output_data) == 2:
            text, format_type = output_data
        else:
            text, format_type = str(output_data), 'default'  # Fallback
        
        if self.console:
            self.console.displayOutput(text, format_type)

    def handle_error(self, error_data):
        """Handle error safely"""
        if isinstance(error_data, tuple) and len(error_data) == 2:
            text, format_type = error_data
        else:
            text, format_type = str(error_data), 'error'  # Fallback
            
        if self.console:
            self.console.displayOutput(text, format_type)

    def handle_input_request(self):
        """Handle input request safely"""
        if self.console:
            self.console.requestInput()

    def stop_execution(self):
        """Stop execution safely"""
        if self.worker:
            self.worker.stop_execution()
        self._cleanup()

    def _cleanup(self):
        """Clean up resources safely"""
        try:
            if self.console and not self.console.isDestroyed():
                self.console.setInputEnabled(False)
        except (RuntimeError, AttributeError):
            pass  # Handle case where console is already destroyed
        self.finished.emit()

    def compile_and_run_code(self, filepath):
        """Start compilation and execution"""
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
        self.worker.compile_and_run(filepath)