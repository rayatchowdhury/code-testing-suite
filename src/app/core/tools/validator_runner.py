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
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
import tempfile

class ValidatorTestWorker(QObject):
    # Signals to communicate with the UI thread
    testStarted = Signal(int, int)  # current test, total tests
    testCompleted = Signal(int, bool, str, str, str, str, int)  # test number, passed, input, test_output, validation_message, error_details, validator_exit_code
    allTestsCompleted = Signal(bool)  # True if all passed

    def __init__(self, workspace_dir, executables, test_count, max_workers=None):
        super().__init__()
        self.workspace_dir = workspace_dir
        self.executables = executables
        self.test_count = test_count
        self.is_running = True  # Flag to control the worker loop
        self.test_results = []  # Store detailed test results for database
        # Use reasonable default: CPU cores - 1, min 1, max 8 (to avoid overwhelming system)
        self.max_workers = max_workers or min(8, max(1, multiprocessing.cpu_count() - 1))
        self._results_lock = threading.Lock()  # Thread-safe results access

    @Slot()
    def run_tests(self):
        """Run validation tests in parallel without blocking the main thread"""
        all_passed = True
        completed_tests = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all test jobs
            future_to_test = {
                executor.submit(self._run_single_test, i): i 
                for i in range(1, self.test_count + 1)
            }
            
            # Process completed tests as they finish
            for future in as_completed(future_to_test):
                if not self.is_running:
                    # Cancel remaining futures if stopped
                    for f in future_to_test:
                        f.cancel()
                    break
                
                test_number = future_to_test[future]
                completed_tests += 1
                
                try:
                    test_result = future.result()
                    if test_result:  # Check if test wasn't cancelled
                        # Thread-safe result storage
                        with self._results_lock:
                            self.test_results.append(test_result)
                        
                        # Emit signals for UI updates
                        self.testStarted.emit(completed_tests, self.test_count)
                        self.testCompleted.emit(
                            test_result['test_number'],
                            test_result['passed'],
                            test_result['input'],
                            test_result['test_output'],
                            test_result['validation_message'],
                            test_result['error_details'],
                            test_result['validator_exit_code']
                        )
                        
                        if not test_result['passed']:
                            all_passed = False
                            
                except Exception as e:
                    # Handle any unexpected errors
                    error_result = self._create_error_result(test_number, f"Execution error: {str(e)}")
                    with self._results_lock:
                        self.test_results.append(error_result)
                    self.testCompleted.emit(
                        error_result['test_number'],
                        False,
                        "",
                        "",
                        "Execution Error",
                        str(e),
                        -3
                    )
                    all_passed = False

        self.allTestsCompleted.emit(all_passed)

    def _run_single_test(self, test_number):
        """Run a single validation test (executed in parallel) - optimized with in-memory pipes"""
        if not self.is_running:
            return None
            
        try:
            # Stage 1: Run generator - capture output in memory
            generator_start = time.time()
            
            generator_result = subprocess.run(
                [self.executables['generator']],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=10,
                text=True  # Decode to string directly
            )
            
            generator_time = time.time() - generator_start
            
            if generator_result.returncode != 0:
                error_msg = f"Generator failed: {generator_result.stderr}"
                return self._create_error_result(test_number, error_msg, "Generator failed", -1, generator_time, 0, 0)
            
            # Get generated input data
            input_text = generator_result.stdout
            
            # Stage 2: Run test solution - pipe input directly, capture output in memory
            test_start = time.time()
            
            test_result = subprocess.run(
                [self.executables['test']],
                input=input_text,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=30,
                text=True  # Decode to string directly
            )
            
            test_time = time.time() - test_start
            
            if test_result.returncode != 0:
                error_msg = f"Test solution failed: {test_result.stderr}"
                return self._create_error_result(test_number, error_msg, "Test solution failed", -1, generator_time, test_time, 0)
            
            # Get test output
            test_output = test_result.stdout
            
            # Stage 3: Run validator - ultra-fast RAM-based temporary files
            validator_start = time.time()
            
            # Use memory-based temporary files with minimal overhead
            # Create files in RAM disk if available, otherwise use system temp with optimizations
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False, 
                                           dir=None, prefix='vld_in_') as input_temp:
                input_temp.write(input_text)
                input_temp.flush()
                os.fsync(input_temp.fileno())  # Force write to storage
                input_temp_path = input_temp.name
            
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False,
                                           dir=None, prefix='vld_out_') as output_temp:
                output_temp.write(test_output)
                output_temp.flush()
                os.fsync(output_temp.fileno())  # Force write to storage
                output_temp_path = output_temp.name
            
            try:
                validator_result = subprocess.run(
                    [self.executables['validator'], input_temp_path, output_temp_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    timeout=10,
                    text=True
                )
                
                validator_time = time.time() - validator_start
                validator_exit_code = validator_result.returncode
                
                # Interpret validator exit code
                if validator_exit_code == 0:
                    validation_message = "Invalid output"
                    test_passed = False
                elif validator_exit_code == 1:
                    validation_message = "Valid output"
                    test_passed = True
                else:
                    validation_message = f"Validator error (exit code {validator_exit_code})"
                    test_passed = False
                
                # Get validator output/error for debugging
                validator_output = validator_result.stdout.strip()
                validator_error = validator_result.stderr.strip()
                error_details = validator_error if validator_error else validator_output
                
                return {
                    'test_number': test_number,
                    'passed': test_passed,
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
                
            finally:
                # Clean up temporary files immediately
                try:
                    os.unlink(input_temp_path)
                    os.unlink(output_temp_path)
                except OSError:
                    pass  # Ignore cleanup errors

        except subprocess.TimeoutExpired as e:
            timeout_msg = f"Timeout in {e.cmd[0] if e.cmd else 'unknown stage'}"
            return self._create_error_result(test_number, timeout_msg, "Timeout", -2)
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            return self._create_error_result(test_number, error_msg, "System error", -3)

    def _create_error_result(self, test_number, error_msg, validation_message="Error", validator_exit_code=-3, generator_time=0, test_time=0, validator_time=0):
        """Create a standardized error result"""
        return {
            'test_number': test_number,
            'passed': False,
            'input': "",
            'test_output': "",
            'validation_message': validation_message,
            'error_details': error_msg,
            'validator_exit_code': validator_exit_code,
            'execution_times': {
                'generator': generator_time,
                'test': test_time,
                'validator': validator_time
            },
            'timestamp': datetime.now().isoformat()
        }

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
        """Compile all three cpp files in parallel with optimizations and caching"""
        self.compilation_failed = False
        self.status_window = CompilationStatusWindow()
        self.status_window.show()
        
        # Start parallel compilation in a separate thread to avoid blocking UI
        compile_thread = threading.Thread(target=self._parallel_compile_all)
        compile_thread.daemon = True
        compile_thread.start()

    def _parallel_compile_all(self):
        """Compile all files in parallel with smart caching and optimization"""
        files_to_compile = ['generator', 'test', 'validator']
        max_workers = min(3, multiprocessing.cpu_count())  # Use all 3 files or available cores
        
        self.compilationOutput.emit("🚀 Starting optimized parallel compilation...\n", 'info')
        
        # Check which files need recompilation
        files_needing_compilation = []
        for file_key in files_to_compile:
            if self._needs_recompilation(file_key):
                files_needing_compilation.append(file_key)
            else:
                self.compilationOutput.emit(f"✅ {file_key}.exe is up-to-date, skipping compilation\n", 'success')
                self.status_window.update_status(file_key, True, f"{file_key}.exe up-to-date")
        
        if not files_needing_compilation:
            self.compilationOutput.emit("\n🎉 All files are up-to-date! No compilation needed.\n", 'success')
            self.compilationFinished.emit(True)
            return
        
        compilation_results = {}
        all_success = True
        
        # Compile files in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit compilation jobs
            future_to_file = {
                executor.submit(self._compile_single_file, file_key): file_key 
                for file_key in files_needing_compilation
            }
            
            # Process results as they complete
            for future in as_completed(future_to_file):
                file_key = future_to_file[future]
                try:
                    success, output = future.result()
                    compilation_results[file_key] = (success, output)
                    
                    if success:
                        self.compilationOutput.emit(f"✅ Successfully compiled {file_key}.cpp\n", 'success')
                        self.status_window.update_status(file_key, True, f"Compiled {file_key}.cpp")
                    else:
                        all_success = False
                        self.compilationOutput.emit(f"❌ Failed to compile {file_key}.cpp:\n{output}\n", 'error')
                        self.status_window.update_status(file_key, False, output)
                        
                except Exception as e:
                    all_success = False
                    error_msg = f"Compilation error for {file_key}: {str(e)}"
                    self.compilationOutput.emit(f"❌ {error_msg}\n", 'error')
                    self.status_window.update_status(file_key, False, error_msg)
        
        # Final result
        if all_success:
            self.compilationOutput.emit("\n🎉 All files compiled successfully with optimizations!\n", 'success')
            self.compilationFinished.emit(True)
        else:
            self.compilationOutput.emit("\n❌ Some files failed to compile.\n", 'error')
            self.compilationFinished.emit(False)

    def _needs_recompilation(self, file_key):
        """Check if file needs recompilation based on timestamps"""
        source_file = self.files[file_key]
        executable_file = self.executables[file_key]
        
        # If executable doesn't exist, need to compile
        if not os.path.exists(executable_file):
            return True
        
        # If source doesn't exist, can't compile
        if not os.path.exists(source_file):
            return True
        
        # Compare timestamps
        try:
            source_mtime = os.path.getmtime(source_file)
            exe_mtime = os.path.getmtime(executable_file)
            return source_mtime > exe_mtime  # Source is newer than executable
        except OSError:
            return True  # If we can't check timestamps, be safe and recompile

    def _compile_single_file(self, file_key):
        """Compile a single file with optimization flags"""
        source_file = self.files[file_key]
        executable_file = self.executables[file_key]
        
        # Optimized compiler flags for faster compilation and better runtime performance
        compiler_flags = [
            '-O2',           # Level 2 optimization for good performance/compile time balance
            '-march=native', # Optimize for current CPU architecture
            '-mtune=native', # Tune for current CPU
            '-pipe',         # Use pipes instead of temporary files
            '-std=c++17',    # Use modern C++ standard
            '-Wall',         # Enable common warnings
        ]
        
        # Add link-time optimization for release builds (optional, can slow compilation)
        # compiler_flags.append('-flto')  # Uncomment for maximum runtime performance
        
        try:
            compile_command = ['g++'] + compiler_flags + [source_file, '-o', executable_file]
            
            result = subprocess.run(
                compile_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30  # 30 second timeout per file
            )
            
            if result.returncode == 0:
                return True, f"Compiled {file_key}.cpp with optimizations"
            else:
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            return False, f"Compilation timeout for {file_key}.cpp"
        except Exception as e:
            return False, f"Compilation error: {str(e)}"

    def _compile_next(self, current_file):
        """Legacy method - kept for compatibility but not used in parallel compilation"""
        pass

    def _handle_compilation_finished(self, exit_code, current_file, error_output):
        """Legacy method - kept for compatibility but not used in parallel compilation"""
        pass

    def stop(self):
        """Stop any running compilation process"""
        if self.current_process and self.current_process.state() == QProcess.Running:
            self.current_process.kill()
            self.current_process.waitForFinished()
        if hasattr(self, 'status_window'):
            self.status_window.close()

    def run_validation_test(self, test_count, max_workers=None):
        """Start validation tests using QThread and parallel worker"""
        self.test_count = test_count  # Store for database saving
        self.test_start_time = datetime.now()  # Track start time
        
        # Use the new validator status window
        self.status_window = ValidatorStatusWindow()
        self.status_window.show()

        # Create the worker and thread with parallel processing
        self.worker = ValidatorTestWorker(self.workspace_dir, self.executables, test_count, max_workers)
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