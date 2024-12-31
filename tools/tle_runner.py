
import os
from PySide6.QtCore import QObject, Signal, QProcess, QThread
from views.stress_tester.compilation_status_window import CompilationStatusWindow
from views.tle_tester.tle_test_status_window import TLETestStatusWindow
import subprocess
import threading
import time

class TLETestWorker(QObject):
    testStarted = Signal(str)  # test name
    testCompleted = Signal(str, bool, float)  # test name, passed (under time limit), execution time
    allTestsCompleted = Signal(bool)  # True if all passed

    def __init__(self, workspace_dir, executables, time_limit):
        super().__init__()
        self.workspace_dir = workspace_dir
        self.executables = executables
        self.time_limit = time_limit
        self.is_running = True

    def run_tests(self):
        """Run TLE tests"""
        all_passed = True
        
        try:
            # Run generator first
            self.testStarted.emit("Generator")
            start_time = time.time()
            generator_process = subprocess.Popen(
                [self.executables['generator']],
                stdout=open(os.path.join(self.workspace_dir, "input.txt"), "w"),
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            generator_process.wait(timeout=self.time_limit)
            gen_time = time.time() - start_time
            self.testCompleted.emit("Generator", True, gen_time)
            
            # Run test solution with input
            self.testStarted.emit("Test Solution")
            start_time = time.time()
            with open(os.path.join(self.workspace_dir, "input.txt"), "r") as input_file:
                test_process = subprocess.Popen(
                    [self.executables['test']],
                    stdin=input_file,
                    stdout=open(os.path.join(self.workspace_dir, "output.txt"), "w"),
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                try:
                    test_process.wait(timeout=self.time_limit)
                    execution_time = time.time() - start_time
                    passed = True
                except subprocess.TimeoutExpired:
                    test_process.kill()
                    execution_time = self.time_limit
                    passed = False
                    all_passed = False
                
                self.testCompleted.emit("Test Solution", passed, execution_time)

        except Exception as e:
            print(f"Error during TLE testing: {str(e)}")
            all_passed = False

        self.allTestsCompleted.emit(all_passed)

    def stop(self):
        """Stop the worker"""
        self.is_running = False

class TLERunner(QObject):
    compilationFinished = Signal(bool)
    compilationOutput = Signal(str, str)
    testStarted = Signal(str)
    testCompleted = Signal(str, bool, float)
    allTestsCompleted = Signal(bool)

    def __init__(self, workspace_dir):
        super().__init__()
        self.workspace_dir = workspace_dir
        self.files = {
            'generator': os.path.join(workspace_dir, 'generator.cpp'),
            'test': os.path.join(workspace_dir, 'test.cpp')
        }
        self.executables = {
            'generator': os.path.join(workspace_dir, 'generator.exe'),
            'test': os.path.join(workspace_dir, 'test.exe')
        }
        self.current_process = None

    def compile_all(self):
        """Compile all files"""
        self.compilation_failed = False
        self.status_window = CompilationStatusWindow()
        self.status_window.show()
        self._compile_next('generator')

    def _compile_next(self, current_file):
        """Compile the specified file and chain to the next one"""
        if self.compilation_failed:
            return

        if current_file not in self.files:
            self.compilationFinished.emit(True)
            return

        self.compilationOutput.emit(f"\nCompiling {current_file}.cpp...\n", 'info')
        
        process = QProcess()
        self.current_process = process
        
        process.finished.connect(
            lambda code, status: self._handle_compilation_finished(
                code, current_file, process.readAllStandardError().data().decode()
            )
        )

        process.start('g++', [
            self.files[current_file],
            '-o',
            self.executables[current_file]
        ])

    def _handle_compilation_finished(self, exit_code, current_file, error_output):
        """Handle compilation completion and chain to next file"""
        next_file_map = {
            'generator': 'test',
            'test': None
        }

        if exit_code != 0:
            self.compilation_failed = True
            error_msg = f"Compilation Error in {current_file}.cpp:\n{error_output}\n"
            self.compilationOutput.emit(error_msg, 'error')
            self.status_window.update_status(current_file, False, error_output)
            self.compilationFinished.emit(False)
            return

        success_msg = f"Successfully compiled {current_file}.cpp\n"
        self.compilationOutput.emit(success_msg, 'success')
        self.status_window.update_status(current_file, True, success_msg)

        next_file = next_file_map[current_file]
        if next_file:
            self._compile_next(next_file)
        else:
            final_msg = "\nAll files compiled successfully!\n"
            self.compilationOutput.emit(final_msg, 'success')
            self.status_window.update_status('all', True, final_msg)
            self.compilationFinished.emit(True)

    def run_tle_test(self, time_limit):
        """Start TLE testing using QThread and worker"""
        self.status_window = TLETestStatusWindow()
        self.status_window.show()

        # Create worker and thread
        self.worker = TLETestWorker(self.workspace_dir, self.executables, time_limit)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.worker.testStarted.connect(self.status_window.show_test_running)
        self.worker.testCompleted.connect(self.status_window.show_test_complete)
        self.worker.allTestsCompleted.connect(self.status_window.show_all_passed)

        # Start worker when thread starts
        self.thread.started.connect(self.worker.run_tests)
        self.worker.allTestsCompleted.connect(self.thread.quit)
        self.worker.allTestsCompleted.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start the thread
        self.thread.start()

    def stop(self):
        """Stop any running processes"""
        if self.current_process and self.current_process.state() == QProcess.Running:
            self.current_process.kill()
            self.current_process.waitForFinished()
        if hasattr(self, 'worker'):
            self.worker.stop()
        if hasattr(self, 'status_window'):
            self.status_window.close()