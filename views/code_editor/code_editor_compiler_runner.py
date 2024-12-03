from PySide6.QtCore import QObject, Signal, QThread
import subprocess
import os

class CompilerWorker(QObject):
    finished = Signal()
    output = Signal(str)
    error = Signal(str)

    def compile_and_run(self, filepath):
        try:
            # First compile
            self.output.emit("Compiling...")
            compile_process = subprocess.run(
                ['g++', filepath, '-o', os.path.splitext(filepath)[0]],
                capture_output=True, text=True
            )
            
            if compile_process.returncode != 0:
                self.error.emit(f"Compilation Error:\n{compile_process.stderr}")
                self.finished.emit()
                return
                
            self.output.emit("Compilation successful!")
            
            # Then run
            self.output.emit("\nRunning program...")
            exe_path = os.path.splitext(filepath)[0]
            run_process = subprocess.run(
                [exe_path],
                capture_output=True, 
                text=True
            )
            
            if run_process.stdout:
                self.output.emit("\nProgram Output:")
                self.output.emit(run_process.stdout)
            
            if run_process.returncode != 0:
                self.error.emit(f"\nRuntime Error:\n{run_process.stderr}")
            elif not run_process.stdout:
                self.output.emit("\nProgram completed with no output.")
                
        except FileNotFoundError:
            self.error.emit("Error: G++ compiler not found. Please install a C++ compiler.")
        except PermissionError:
            self.error.emit("Error: Permission denied. Cannot create or run executable.")
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")
        finally:
            self.finished.emit()

class CompilerRunner(QObject):
    finished = Signal()

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

    def compile_and_run_code(self, filepath):
        if not filepath:
            self.console.displayOutput("Error: No file to compile")
            return

        self._cleanup_thread()
        self.worker = CompilerWorker()
        self.thread = QThread()
        
        self.worker.moveToThread(self.thread)
        self.worker.output.connect(self.console.displayOutput)
        self.worker.error.connect(self.console.displayOutput)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.finished)
        self.thread.finished.connect(self._cleanup_thread)
        
        self.thread.started.connect(lambda: self.worker.compile_and_run(filepath))
        self.thread.start()

# Remove compile_code and run_code methods as they're no longer needed
