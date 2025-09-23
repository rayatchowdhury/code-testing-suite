import os
from PySide6.QtCore import QObject, Signal, QProcess, QThread
from src.app.presentation.views.comparator.compilation_status_window import CompilationStatusWindow
from src.app.presentation.views.validator.validator_status_window import ValidatorStatusWindow
import subprocess
import threading
from PySide6.QtCore import QObject, Signal, Slot
from src.app.persistence.database import DatabaseManager, TestResult
import time
from datetime import datetime
import json

class ValidatorTestWorker(QObject):
    # Signals to communicate with the UI thread
    testStarted = Signal(int, int)  # current test, total tests
    testCompleted = Signal(int, bool, str, str, str, str, int)  # test number, passed, input, test_output, validation_message, error_details, validator_exit_code
    allTestsCompleted = Signal(bool)  # True if all passed

    def __init__(self, workspace_dir, executables, test_count):
        super().__init__()
        self.workspace_dir = workspace_dir
        self.executables = executables
        self.test_count = test_count
        self.is_running = True  # Flag to control the worker loop
        self.test_results = []  # Store detailed test results for database

    @Slot()
    def run_tests(self):
        """Run validation tests without blocking the main thread"""
        all_passed = True
        for i in range(1, self.test_count + 1):
            if not self.is_running:
                break  # Stop if the flag is set to False
            self.testStarted.emit(i, self.test_count)
            
            try:
                # Stage 1: Run generator
                input_file_path = os.path.join(self.workspace_dir, f"input_{i}.txt")
                generator_start = time.time()
                
                with open(input_file_path, "w") as input_file:
                    generator_result = subprocess.run(
                        [self.executables['generator']],
                        stdout=input_file,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        timeout=10  # 10 second timeout for generator
                    )
                
                generator_time = time.time() - generator_start
                
                if generator_result.returncode != 0:
                    error_msg = f"Generator failed: {generator_result.stderr.decode()}"
                    self.testCompleted.emit(i, False, "", "", "Generator Error", error_msg, -1)
                    self._record_test_result(i, False, "", "", "Generator failed", error_msg, -1, generator_time, 0, 0)
                    all_passed = False
                    continue
                
                # Stage 2: Run test solution
                output_file_path = os.path.join(self.workspace_dir, f"output_{i}.txt")
                test_start = time.time()
                
                with open(input_file_path, "r") as input_file:
                    with open(output_file_path, "w") as output_file:
                        test_result = subprocess.run(
                            [self.executables['test']],
                            stdin=input_file,
                            stdout=output_file,
                            stderr=subprocess.PIPE,
                            creationflags=subprocess.CREATE_NO_WINDOW,
                            timeout=30  # 30 second timeout for test solution
                        )
                
                test_time = time.time() - test_start
                
                if test_result.returncode != 0:
                    error_msg = f"Test solution failed: {test_result.stderr.decode()}"
                    self.testCompleted.emit(i, False, "", "", "Test Solution Error", error_msg, -1)
                    self._record_test_result(i, False, "", "", "Test solution failed", error_msg, -1, generator_time, test_time, 0)
                    all_passed = False
                    continue
                
                # Stage 3: Run validator
                validator_start = time.time()
                
                validator_result = subprocess.run(
                    [self.executables['validator'], input_file_path, output_file_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    timeout=10  # 10 second timeout for validator
                )
                
                validator_time = time.time() - validator_start
                validator_exit_code = validator_result.returncode
                
                # Read input and output for reporting
                with open(input_file_path, "r") as f:
                    input_text = f.read()
                with open(output_file_path, "r") as f:
                    test_output = f.read()
                
                # Interpret validator exit code
                if validator_exit_code == 0:
                    validation_message = "Invalid output"
                    test_passed = False
                    all_passed = False
                elif validator_exit_code == 1:
                    validation_message = "Valid output"
                    test_passed = True
                else:
                    validation_message = f"Validator error (exit code {validator_exit_code})"
                    test_passed = False
                    all_passed = False
                
                # Get validator output/error for debugging
                validator_output = validator_result.stdout.decode().strip()
                validator_error = validator_result.stderr.decode().strip()
                error_details = validator_error if validator_error else validator_output
                
                self.testCompleted.emit(i, test_passed, input_text, test_output, validation_message, error_details, validator_exit_code)
                self._record_test_result(i, test_passed, input_text, test_output, validation_message, error_details, validator_exit_code, generator_time, test_time, validator_time)

            except subprocess.TimeoutExpired as e:
                timeout_msg = f"Timeout in {e.cmd[0] if e.cmd else 'unknown stage'}"
                self.testCompleted.emit(i, False, "", "", "Timeout Error", timeout_msg, -2)
                self._record_test_result(i, False, "", "", "Timeout", timeout_msg, -2, 0, 0, 0)
                all_passed = False
                
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                self.testCompleted.emit(i, False, "", "", "System Error", error_msg, -3)
                self._record_test_result(i, False, "", "", "System error", error_msg, -3, 0, 0, 0)
                all_passed = False

        self.allTestsCompleted.emit(all_passed)

    def _record_test_result(self, test_number, passed, input_text, test_output, validation_message, error_details, validator_exit_code, generator_time, test_time, validator_time):
        """Record detailed test result for database storage"""
        test_result = {
            'test_number': test_number,
            'passed': passed,
            'input': input_text,
            'test_output': test_output,
            'validation_message': validation_message,
            'error_details': error_details,
            'validator_exit_code': validator_exit_code,
            'execution_times': {
                'generator': generator_time,
                'test': test_time,
                'validator': validator_time
            },
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(test_result)

    def stop(self):
        """Stop the worker loop"""
        self.is_running = False

class ValidatorRunner(QObject):
    compilationFinished = Signal(bool)  # True if successful, False if failed
    compilationOutput = Signal(str, str)  # (message, type)
    testStarted = Signal(int, int)  # current test, total tests
    testCompleted = Signal(int, bool, str, str, str, str, int)  # test number, passed, input, test_output, validation_message, error_details, validator_exit_code
    allTestsCompleted = Signal(bool)  # True if all passed

    def __init__(self, workspace_dir):
        super().__init__()
        self.workspace_dir = workspace_dir
        self.files = {
            'generator': os.path.join(workspace_dir, 'generator.cpp'),
            'test': os.path.join(workspace_dir, 'test.cpp'),
            'validator': os.path.join(workspace_dir, 'validator.cpp')
        }
        self.executables = {
            'generator': os.path.join(workspace_dir, 'generator.exe'),
            'test': os.path.join(workspace_dir, 'test.exe'),
            'validator': os.path.join(workspace_dir, 'validator.exe')
        }
        self.current_process = None
        self.db_manager = DatabaseManager()  # Add database manager

    def compile_all(self):
        """Compile all three cpp files"""
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
            'test': 'validator',
            'validator': None
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
            self.status_window.update_status('validator', True, final_msg)
            self.compilationFinished.emit(True)

    def stop(self):
        """Stop any running compilation process"""
        if self.current_process and self.current_process.state() == QProcess.Running:
            self.current_process.kill()
            self.current_process.waitForFinished()
        if hasattr(self, 'status_window'):
            self.status_window.close()

    def run_validation_test(self, test_count):
        """Start validation tests using QThread and worker"""
        self.test_count = test_count  # Store for database saving
        self.test_start_time = datetime.now()  # Track start time
        
        # Use the new validator status window
        self.status_window = ValidatorStatusWindow()
        self.status_window.show()

        # Create the worker and thread
        self.worker = ValidatorTestWorker(self.workspace_dir, self.executables, test_count)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        # Connect signals from worker to status window
        self.worker.testStarted.connect(self.status_window.show_test_running)
        self.worker.testCompleted.connect(self.status_window.show_test_complete)
        self.worker.allTestsCompleted.connect(self.status_window.show_all_passed)
        
        # Forward signals to external listeners
        self.worker.testStarted.connect(self.testStarted)
        self.worker.testCompleted.connect(self.testCompleted)
        self.worker.allTestsCompleted.connect(self.allTestsCompleted)
        
        # Connect to our database saving method
        self.worker.allTestsCompleted.connect(self._save_validation_results)

        # Start the worker when the thread starts
        self.thread.started.connect(self.worker.run_tests)
        # Clean up when the worker is done
        self.worker.allTestsCompleted.connect(self.thread.quit)
        self.worker.allTestsCompleted.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start the thread
        self.thread.start()
    
    def _save_validation_results(self, all_passed):
        """Save validation results to database"""
        if not hasattr(self, 'worker') or not hasattr(self.worker, 'test_results'):
            return
        
        # Calculate statistics
        total_time = (datetime.now() - self.test_start_time).total_seconds()
        passed_tests = sum(1 for result in self.worker.test_results if result.get('passed', False))
        failed_tests = len(self.worker.test_results) - passed_tests
        
        # Get the test file path (we'll use the test.cpp file)
        test_file_path = self.files.get('test', '')
        
        # Create files snapshot
        files_snapshot = DatabaseManager.create_files_snapshot(self.workspace_dir)
        
        # Compile validation analysis
        validation_analysis = {
            'test_count': self.test_count,
            'validation_summary': {
                'valid_outputs': sum(1 for r in self.worker.test_results if r.get('validator_exit_code') == 1),
                'invalid_outputs': sum(1 for r in self.worker.test_results if r.get('validator_exit_code') == 0),
                'validator_errors': sum(1 for r in self.worker.test_results if r.get('validator_exit_code', 0) > 1),
                'timeouts': sum(1 for r in self.worker.test_results if r.get('validator_exit_code') == -2),
                'system_errors': sum(1 for r in self.worker.test_results if r.get('validator_exit_code') == -3)
            },
            'execution_times': {
                'avg_generator': sum(r.get('execution_times', {}).get('generator', 0) for r in self.worker.test_results) / len(self.worker.test_results) if self.worker.test_results else 0,
                'avg_test': sum(r.get('execution_times', {}).get('test', 0) for r in self.worker.test_results) / len(self.worker.test_results) if self.worker.test_results else 0,
                'avg_validator': sum(r.get('execution_times', {}).get('validator', 0) for r in self.worker.test_results) / len(self.worker.test_results) if self.worker.test_results else 0
            },
            'failed_tests': [r for r in self.worker.test_results if not r.get('passed', True)]
        }
        
        # Create test result object
        result = TestResult(
            test_type="validator",
            file_path=test_file_path,
            test_count=self.test_count,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_time=total_time,
            timestamp=datetime.now().isoformat(),
            test_details=json.dumps(self.worker.test_results),
            project_name=os.path.basename(self.workspace_dir),
            files_snapshot=json.dumps(files_snapshot.__dict__),
            mismatch_analysis=json.dumps(validation_analysis)
        )
        
        # Save to database
        try:
            result_id = self.db_manager.save_test_result(result)
            if result_id > 0:
                print(f"Validation results saved to database with ID: {result_id}")
            else:
                print("Failed to save validation results to database")
        except Exception as e:
            print(f"Error saving validation results: {e}")