from PySide6.QtCore import QObject, Signal, QThread
import subprocess
import os

class CompilerWorker(QObject):
    finished = Signal()
    output = Signal(str)
    error = Signal(str)

    def compile(self, filepath):
        try:
            compile_process = subprocess.run(
                ['g++', filepath, '-o', os.path.splitext(filepath)[0]],
                capture_output=True, text=True
            )
            
            if compile_process.returncode == 0:
                self.output.emit("Compilation successful!")
                return True
            else:
                self.error.emit(f"Compilation Error:\n{compile_process.stderr}")
                return False
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")
            return False

    def run(self, filepath):
        exe_path = os.path.splitext(filepath)[0]
        try:
            run_process = subprocess.run(
                [exe_path],
                capture_output=True, 
                text=True
            )
            
            self.output.emit("Program Output:")
            self.output.emit(run_process.stdout)
            
            if run_process.returncode != 0:
                self.error.emit(f"Runtime Error:\n{run_process.stderr}")
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")
        finally:
            self.finished.emit()

class CompilerRunner(QObject):
    finished = Signal()  # Add this signal

    def __init__(self, console_output):
        super().__init__()
        self.console = console_output
        self.worker = None
        self.thread = None

    def _cleanup_thread(self):
        if self.thread:
            self.thread.quit()
            self.thread.wait()
            self.thread = None
        self.worker = None

    def _setup_thread(self):
        self._cleanup_thread()
            
        self.worker = CompilerWorker()
        self.thread = QThread()
        
        self.worker.moveToThread(self.thread)
        self.worker.output.connect(self.console.displayOutput)
        self.worker.error.connect(self.console.displayOutput)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.finished)  # Forward the finished signal
        self.thread.finished.connect(self._cleanup_thread)
        
        return True

    def compile_code(self, filepath):
        if not filepath:
            self.console.displayOutput("Error: No file to compile")
            return False

        self._setup_thread()
        self.thread.started.connect(lambda: self.worker.compile(filepath))
        self.thread.start()

    def run_code(self, filepath):
        if not filepath:
            self.console.displayOutput("Error: No file to run")
            return

        exe_path = os.path.splitext(filepath)[0]
        if not os.path.exists(exe_path):
            self.console.displayOutput("Error: Executable not found. Compile first.")
            return

        self._setup_thread()
        self.thread.started.connect(lambda: self.worker.run(filepath))
        self.thread.start()
