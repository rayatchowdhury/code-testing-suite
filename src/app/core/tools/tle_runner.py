
import os
import psutil
from PySide6.QtCore import QObject, Signal, QProcess, QThread
from src.app.presentation.views.comparator.compilation_status_window import CompilationStatusWindow
from src.app.presentation.views.benchmarker.benchmark_status_window import BenchmarkStatusWindow
import subprocess
import threading
import time
from src.app.persistence.database import DatabaseManager, TestResult
from datetime import datetime
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
import tempfile

class TLETestWorker(QObject):
    testStarted = Signal(str, int, int)  # test name, current test, total tests
    testCompleted = Signal(str, int, bool, float, float, bool)  # test name, test number, passed, execution time, memory used, memory passed
    allTestsCompleted = Signal(bool)  # True if all passed

    def __init__(self, workspace_dir, executables, time_limit, memory_limit, test_count=1, max_workers=None):
        super().__init__()
        self.workspace_dir = workspace_dir
        self.executables = executables
        self.time_limit = time_limit / 1000.0  # Convert ms to seconds
        self.memory_limit = memory_limit  # MB
        self.test_count = test_count
        self.is_running = True
        self.test_results = []  # Store detailed test results
        # Use reasonable default for TLE testing (less workers due to memory monitoring overhead)
        self.max_workers = max_workers or min(4, max(1, multiprocessing.cpu_count() - 1))
        self._results_lock = threading.Lock()  # Thread-safe results access

    def run_tests(self):
        """Run TLE tests in parallel with memory and time monitoring"""
        all_passed = True
        completed_tests = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all test jobs
            future_to_test = {
                executor.submit(self._run_single_tle_test, i): i 
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
                        self.testStarted.emit(f"Test {completed_tests}", completed_tests, self.test_count)
                        self.testCompleted.emit(
                            test_result['test_name'],
                            test_result['test_number'],
                            test_result['passed'],
                            test_result['execution_time'],
                            test_result['memory_used'],
                            test_result['memory_passed']
                        )
                        
                        if not test_result['passed']:
                            all_passed = False
                            
                except Exception as e:
                    # Handle any unexpected errors
                    error_result = self._create_tle_error_result(test_number, f"Execution error: {str(e)}")
                    with self._results_lock:
                        self.test_results.append(error_result)
                    self.testCompleted.emit(
                        f"Test {test_number} - Error",
                        test_number,
                        False,
                        0.0,
                        0.0,
                        False
                    )
                    all_passed = False

        self.allTestsCompleted.emit(all_passed)

    def _run_single_tle_test(self, test_number):
        """Run a single TLE test with optimized I/O and memory monitoring"""
        if not self.is_running:
            return None
            
        try:
            # Stage 1: Run generator with memory monitoring
            generator_start = time.time()
            max_generator_memory = 0
            
            generator_process = subprocess.Popen(
                [self.executables['generator']],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
                text=True
            )
            
            # Monitor generator memory usage
            try:
                psutil_process = psutil.Process(generator_process.pid)
                while generator_process.poll() is None:
                    try:
                        memory_info = psutil_process.memory_info()
                        current_memory_mb = memory_info.rss / (1024 * 1024)
                        max_generator_memory = max(max_generator_memory, current_memory_mb)
                        time.sleep(0.005)  # Check every 5ms for better precision
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            
            try:
                stdout, stderr = generator_process.communicate(timeout=self.time_limit)
                generator_time = time.time() - generator_start
                
                if generator_process.returncode != 0:
                    return self._create_tle_error_result(
                        test_number, f"Generator failed: {stderr}", 
                        execution_time=generator_time, memory_used=max_generator_memory
                    )
                
                input_text = stdout
                
            except subprocess.TimeoutExpired:
                generator_process.kill()
                generator_time = self.time_limit
                return self._create_tle_error_result(
                    test_number, "Generator timeout", 
                    execution_time=generator_time, memory_used=max_generator_memory
                )
            
            # Stage 2: Run test solution with memory monitoring
            test_start = time.time()
            max_test_memory = 0
            
            test_process = subprocess.Popen(
                [self.executables['test']],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
                text=True
            )
            
            # Monitor test solution memory usage
            try:
                psutil_process = psutil.Process(test_process.pid)
                # Start the process with input
                test_process.stdin.write(input_text)
                test_process.stdin.close()
                
                while test_process.poll() is None:
                    try:
                        memory_info = psutil_process.memory_info()
                        current_memory_mb = memory_info.rss / (1024 * 1024)
                        max_test_memory = max(max_test_memory, current_memory_mb)
                        time.sleep(0.005)  # Check every 5ms
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            
            try:
                stdout, stderr = test_process.communicate(timeout=self.time_limit)
                execution_time = time.time() - test_start
                
                if test_process.returncode != 0:
                    return self._create_tle_error_result(
                        test_number, f"Test solution failed: {stderr}",
                        execution_time=execution_time, memory_used=max_test_memory
                    )
                
                test_output = stdout
                
            except subprocess.TimeoutExpired:
                test_process.kill()
                execution_time = self.time_limit
                test_output = ""
            
            # Evaluate performance
            time_passed = execution_time <= self.time_limit
            memory_passed = max_test_memory <= self.memory_limit
            test_passed = time_passed and memory_passed
            
            return {
                'test_name': f'Test {test_number} - Solution',
                'test_number': test_number,
                'passed': test_passed,
                'time_passed': time_passed,
                'memory_passed': memory_passed,
                'execution_time': execution_time,
                'memory_used': max_test_memory,
                'time_limit': self.time_limit,
                'memory_limit': self.memory_limit,
                'timestamp': datetime.now().isoformat(),
                'timed_out': execution_time >= self.time_limit,
                'memory_exceeded': max_test_memory > self.memory_limit,
                'performance_ratio': execution_time / self.time_limit if self.time_limit > 0 else 0,
                'memory_ratio': max_test_memory / self.memory_limit if self.memory_limit > 0 else 0,
                'input': input_text,
                'output': test_output,
                'generator_time': generator_time,
                'generator_memory': max_generator_memory
            }

        except Exception as e:
            return self._create_tle_error_result(test_number, f"Unexpected error: {str(e)}")

    def _create_tle_error_result(self, test_number, error_msg, execution_time=0.0, memory_used=0.0):
        """Create a standardized TLE error result"""
        return {
            'test_name': f'Test {test_number} - Error',
            'test_number': test_number,
            'passed': False,
            'time_passed': False,
            'memory_passed': memory_used <= self.memory_limit,
            'execution_time': execution_time,
            'memory_used': memory_used,
            'time_limit': self.time_limit,
            'memory_limit': self.memory_limit,
            'timestamp': datetime.now().isoformat(),
            'timed_out': execution_time >= self.time_limit,
            'memory_exceeded': memory_used > self.memory_limit,
            'performance_ratio': execution_time / self.time_limit if self.time_limit > 0 else 0,
            'memory_ratio': memory_used / self.memory_limit if self.memory_limit > 0 else 0,
            'input': "",
            'output': "",
            'error_details': error_msg,
            'generator_time': 0.0,
            'generator_memory': 0.0
        }

    def stop(self):
        """Stop the worker"""
        self.is_running = False

class TLERunner(QObject):
    compilationFinished = Signal(bool)
    compilationOutput = Signal(str, str)
    testStarted = Signal(str, int, int)  # test name, current test, total tests
    testCompleted = Signal(str, int, bool, float, float, bool)  # test name, test number, passed, execution time, memory used, memory passed
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
        self.db_manager = DatabaseManager()  # Add database manager

    def compile_all(self):
        """Compile all files in parallel with optimizations and caching"""
        self.compilation_failed = False
        self.status_window = CompilationStatusWindow()
        self.status_window.show()
        
        # Start parallel compilation in a separate thread to avoid blocking UI
        compile_thread = threading.Thread(target=self._parallel_compile_all)
        compile_thread.daemon = True
        compile_thread.start()

    def _parallel_compile_all(self):
        """Compile all files in parallel with smart caching and optimization"""
        files_to_compile = ['generator', 'test']
        max_workers = min(2, multiprocessing.cpu_count())  # Use both files or available cores
        
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
        
        # Optimized compiler flags for TLE testing (balance between compile time and runtime performance)
        compiler_flags = [
            '-O2',           # Level 2 optimization for good performance/compile time balance
            '-march=native', # Optimize for current CPU architecture
            '-mtune=native', # Tune for current CPU
            '-pipe',         # Use pipes instead of temporary files
            '-std=c++17',    # Use modern C++ standard
            '-DNDEBUG',      # Disable debug assertions for better performance
        ]
        
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

    def run_tle_test(self, time_limit, memory_limit=256, test_count=1, max_workers=None):
        """Start TLE testing using QThread and parallel worker"""
        self.time_limit = time_limit  # Store for database saving (in ms)
        self.memory_limit = memory_limit  # Store for database saving (in MB)
        self.test_count = test_count  # Store for database saving
        self.test_start_time = datetime.now()  # Track start time
        
        self.status_window = BenchmarkStatusWindow()
        self.status_window.workspace_dir = self.workspace_dir  # Pass workspace directory for file access
        self.status_window.time_limit = time_limit / 1000.0  # Pass time limit for comparison (convert to seconds)
        self.status_window.memory_limit = memory_limit  # Pass memory limit for comparison
        self.status_window.test_count = test_count  # Pass test count
        self.status_window.show()

        # Create worker and thread with parallel processing
        self.worker = TLETestWorker(self.workspace_dir, self.executables, time_limit, memory_limit, test_count, max_workers)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.worker.testStarted.connect(self.status_window.show_test_running)
        self.worker.testCompleted.connect(self.status_window.show_test_complete)
        self.worker.allTestsCompleted.connect(self.status_window.show_all_passed)
        
        # Forward signals to external listeners
        self.worker.testStarted.connect(self.testStarted)
        self.worker.testCompleted.connect(self.testCompleted)
        self.worker.allTestsCompleted.connect(self.allTestsCompleted)
        
        # Connect to our database saving method
        self.worker.allTestsCompleted.connect(self._save_test_results)

        # Start worker when thread starts
        self.thread.started.connect(self.worker.run_tests)
        self.worker.allTestsCompleted.connect(self.thread.quit)
        self.worker.allTestsCompleted.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start the thread
        self.thread.start()
    
    def _save_test_results(self, all_passed):
        """Save TLE test results to database"""
        if not hasattr(self, 'worker') or not hasattr(self.worker, 'test_results'):
            return
        
        # Calculate statistics
        total_time = (datetime.now() - self.test_start_time).total_seconds()
        passed_tests = sum(1 for result in self.worker.test_results if result.get('passed', False))
        failed_tests = len(self.worker.test_results) - passed_tests
        
        # Get the test file path
        test_file_path = self.files.get('test', '')
        
        # Create files snapshot
        files_snapshot = DatabaseManager.create_files_snapshot(self.workspace_dir)
        
        # Compile analysis for TLE tests
        tle_analysis = {
            'time_limit': getattr(self, 'time_limit', 0),
            'memory_limit': getattr(self, 'memory_limit', 256),
            'test_count': getattr(self, 'test_count', 1),
            'test_details': [],
            'performance_summary': {
                'fastest_test': None,
                'slowest_test': None,
                'average_time': 0,
                'max_memory_used': None,
                'min_memory_used': None,
                'average_memory': 0
            }
        }
        
        execution_times = []
        memory_usages = []
        for result in self.worker.test_results:
            if 'execution_time' in result:
                execution_times.append(result['execution_time'])
            if 'memory_used' in result:
                memory_usages.append(result['memory_used'])
        
        if execution_times:
            tle_analysis['performance_summary']['average_time'] = sum(execution_times) / len(execution_times)
            tle_analysis['performance_summary']['fastest_test'] = min(execution_times)
            tle_analysis['performance_summary']['slowest_test'] = max(execution_times)
        
        if memory_usages:
            tle_analysis['performance_summary']['average_memory'] = sum(memory_usages) / len(memory_usages)
            tle_analysis['performance_summary']['max_memory_used'] = max(memory_usages)
            tle_analysis['performance_summary']['min_memory_used'] = min(memory_usages)
        
        # Create test result object
        result = TestResult(
            test_type="tle",
            file_path=test_file_path,
            test_count=getattr(self, 'test_count', len(self.worker.test_results)),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_time=total_time,
            timestamp=datetime.now().isoformat(),
            test_details=json.dumps(self.worker.test_results),
            project_name=os.path.basename(self.workspace_dir),
            files_snapshot=json.dumps(files_snapshot.__dict__),
            mismatch_analysis=json.dumps(tle_analysis)
        )
        
        # Save to database
        try:
            result_id = self.db_manager.save_test_result(result)
            if result_id > 0:
                print(f"TLE test results saved to database with ID: {result_id}")
            else:
                print("Failed to save TLE test results to database")
        except Exception as e:
            print(f"Error saving TLE test results: {e}")

    def stop(self):
        """Stop any running processes"""
        if self.current_process and self.current_process.state() == QProcess.Running:
            self.current_process.kill()
            self.current_process.waitForFinished()
        if hasattr(self, 'worker'):
            self.worker.stop()
        if hasattr(self, 'status_window'):
            self.status_window.close()