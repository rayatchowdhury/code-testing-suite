
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

class TLETestWorker(QObject):
    testStarted = Signal(str, int, int)  # test name, current test, total tests
    testCompleted = Signal(str, int, bool, float, float, bool)  # test name, test number, passed, execution time, memory used, memory passed
    allTestsCompleted = Signal(bool)  # True if all passed

    def __init__(self, workspace_dir, executables, time_limit, memory_limit, test_count=1):
        super().__init__()
        self.workspace_dir = workspace_dir
        self.executables = executables
        self.time_limit = time_limit / 1000.0  # Convert ms to seconds
        self.memory_limit = memory_limit  # MB
        self.test_count = test_count
        self.is_running = True
        self.test_results = []  # Store detailed test results

    def run_tests(self):
        """Run multiple TLE tests with memory monitoring"""
        all_passed = True
        
        for test_num in range(1, self.test_count + 1):
            if not self.is_running:
                break
                
            try:
                # Run generator first
                self.testStarted.emit(f"Test {test_num} - Generator", test_num, self.test_count)
                start_time = time.time()
                max_memory = 0
                
                # Generate unique input file for each test
                input_file_path = os.path.join(self.workspace_dir, f"input_{test_num}.txt")
                output_file_path = os.path.join(self.workspace_dir, f"output_{test_num}.txt")
                
                with open(input_file_path, "w") as input_file:
                    generator_process = subprocess.Popen(
                        [self.executables['generator']],
                        stdout=input_file,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    # Monitor memory usage
                    try:
                        psutil_process = psutil.Process(generator_process.pid)
                        while generator_process.poll() is None:
                            try:
                                memory_info = psutil_process.memory_info()
                                current_memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
                                max_memory = max(max_memory, current_memory_mb)
                                time.sleep(0.01)  # Check every 10ms
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                    
                    try:
                        generator_process.wait(timeout=self.time_limit)
                        gen_time = time.time() - start_time
                        time_passed = gen_time <= self.time_limit
                        memory_passed = max_memory <= self.memory_limit
                        gen_passed = time_passed and memory_passed
                        
                        if not gen_passed:
                            all_passed = False
                        
                        self.testCompleted.emit(f"Test {test_num} - Generator", test_num, gen_passed, gen_time, max_memory, memory_passed)
                        
                        # If generator failed, skip test solution
                        if not gen_passed:
                            continue
                            
                    except subprocess.TimeoutExpired:
                        generator_process.kill()
                        gen_time = self.time_limit
                        all_passed = False
                        self.testCompleted.emit(f"Test {test_num} - Generator", test_num, False, gen_time, max_memory, max_memory <= self.memory_limit)
                        continue
                
                # Run test solution with generated input
                self.testStarted.emit(f"Test {test_num} - Solution", test_num, self.test_count)
                start_time = time.time()
                max_memory = 0
                
                with open(input_file_path, "r") as input_file:
                    with open(output_file_path, "w") as output_file:
                        test_process = subprocess.Popen(
                            [self.executables['test']],
                            stdin=input_file,
                            stdout=output_file,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        
                        # Monitor memory usage
                        try:
                            psutil_process = psutil.Process(test_process.pid)
                            while test_process.poll() is None:
                                try:
                                    memory_info = psutil_process.memory_info()
                                    current_memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
                                    max_memory = max(max_memory, current_memory_mb)
                                    time.sleep(0.01)  # Check every 10ms
                                except (psutil.NoSuchProcess, psutil.AccessDenied):
                                    break
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                        
                        try:
                            test_process.wait(timeout=self.time_limit)
                            execution_time = time.time() - start_time
                            time_passed = execution_time <= self.time_limit
                            memory_passed = max_memory <= self.memory_limit
                            test_passed = time_passed and memory_passed
                            
                            if not test_passed:
                                all_passed = False
                                
                        except subprocess.TimeoutExpired:
                            test_process.kill()
                            execution_time = self.time_limit
                            test_passed = False
                            memory_passed = max_memory <= self.memory_limit
                            time_passed = False
                            all_passed = False
                        
                        # Store test result with detailed information
                        test_result = {
                            'test_name': f'Test {test_num} - Solution',
                            'test_number': test_num,
                            'passed': test_passed,
                            'time_passed': time_passed if 'time_passed' in locals() else False,
                            'memory_passed': memory_passed,
                            'execution_time': execution_time,
                            'memory_used': max_memory,
                            'time_limit': self.time_limit,
                            'memory_limit': self.memory_limit,
                            'timestamp': datetime.now().isoformat(),
                            'timed_out': execution_time >= self.time_limit,
                            'memory_exceeded': max_memory > self.memory_limit,
                            'performance_ratio': execution_time / self.time_limit if self.time_limit > 0 else 0,
                            'memory_ratio': max_memory / self.memory_limit if self.memory_limit > 0 else 0
                        }
                        
                        # Read input and output files for analysis
                        try:
                            if os.path.exists(input_file_path):
                                with open(input_file_path, 'r') as f:
                                    test_result['input'] = f.read()
                            
                            if os.path.exists(output_file_path):
                                with open(output_file_path, 'r') as f:
                                    test_result['output'] = f.read()
                        except Exception as e:
                            test_result['file_read_error'] = str(e)
                        
                        self.test_results.append(test_result)
                        self.testCompleted.emit(f"Test {test_num} - Solution", test_num, test_passed, execution_time, max_memory, memory_passed)

            except Exception as e:
                print(f"Error during TLE testing on test {test_num}: {str(e)}")
                all_passed = False

        self.allTestsCompleted.emit(all_passed)

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

    def run_tle_test(self, time_limit, memory_limit=256, test_count=1):
        """Start TLE testing using QThread and worker"""
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

        # Create worker and thread
        self.worker = TLETestWorker(self.workspace_dir, self.executables, time_limit, memory_limit, test_count)
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