
from PySide6.QtCore import QObject, Signal, QProcess, QThread

class TLECompilerRunner(QObject):
    compilationStarted = Signal()
    compilationFinished = Signal(bool)  # True if successful
    outputAvailable = Signal(str, str)  # message, type
    finished = Signal()

    def __init__(self, console):
        super().__init__()
        self.console = console
        self.process = None

    def compile_and_run_code(self, file_path):
        """Compile and run a single cpp file"""
        self.compilationStarted.emit()
        self.console.clear()
        self.console.append("Compiling...\n", "info")
        
        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        
        # Connect signals
        self.process.finished.connect(self._handle_compilation_finished)
        self.process.readyReadStandardOutput.connect(
            lambda: self._handle_output(self.process.readAllStandardOutput().data().decode())
        )
        self.process.readyReadStandardError.connect(
            lambda: self._handle_output(self.process.readAllStandardError().data().decode(), "error")
        )
        
        # Start compilation
        output_path = file_path.replace('.cpp', '.exe')
        self.process.start('g++', [file_path, '-o', output_path])

    def _handle_compilation_finished(self, exit_code, exit_status):
        """Handle compilation completion"""
        success = exit_code == 0
        self.compilationFinished.emit(success)
        
        if success:
            self.console.append("Compilation successful!\n", "success")
        else:
            self.console.append("Compilation failed!\n", "error")
        
        self.finished.emit()

    def _handle_output(self, output, output_type="info"):
        """Handle process output"""
        if output:
            self.outputAvailable.emit(output, output_type)
            self.console.append(output, output_type)

    def stop(self):
        """Stop any running process"""
        if self.process and self.process.state() == QProcess.Running:
            self.process.kill()
            self.process.waitForFinished()