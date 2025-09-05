import os
from PySide6.QtCore import QObject, Signal, QProcess, QThread
from ..views.stress_tester.compilation_status_window import CompilationStatusWindow
from ..views.stress_tester.stress_test_status_window import StressTestStatusWindow
import subprocess
import threading
from PySide6.QtCore import QObject, Signal, Slot
from ..database import DatabaseManager, TestResult
import time
from datetime import datetime
import json

class StressTestWorker(QObject):
    # Signals to communicate with the UI thread
    testStarted = Signal(int, int)  # current test, total tests
    testCompleted = Signal(int, bool, str, str, str)  # test number, passed, input, correct output, test output
    allTestsCompleted = Signal(bool)  # True if all passed

    def __init__(self, workspace_dir, executables, test_count):
        super().__init__()
        self.workspace_dir = workspace_dir
        self.executables = executables  # Add this line
        self.test_count = test_count
        self.is_running = True  # Flag to control the worker loop
        self.test_results = []  # Store detailed test results for database

    @Slot()
    def run_tests(self):
        """Run stress tests without blocking the main thread"""
        all_passed = True
        for i in range(1, self.test_count + 1):
            if not self.is_running:
                break  # Stop if the flag is set to False
            self.testStarted.emit(i, self.test_count)
            try:
                # Run generator
                subprocess.run([self.executables['generator']],
                               stdout=open(os.path.join(self.workspace_dir, "input.txt"), "w"),
                               creationflags=subprocess.CREATE_NO_WINDOW)
                
                # Run correct solution
                subprocess.run([self.executables['correct']],
                               stdin=open(os.path.join(self.workspace_dir, "input.txt"), "r"),
                               stdout=open(os.path.join(self.workspace_dir, "correct.txt"), "w"),
                               creationflags=subprocess.CREATE_NO_WINDOW)
                
                # Run test solution
                subprocess.run([self.executables['test']],
                               stdin=open(os.path.join(self.workspace_dir, "input.txt"), "r"),
                               stdout=open(os.path.join(self.workspace_dir, "test.txt"), "w"),
                               creationflags=subprocess.CREATE_NO_WINDOW)
                
                # Read results
                with open(os.path.join(self.workspace_dir, "input.txt"), "r") as f:
                    input_text = f.read()
                with open(os.path.join(self.workspace_dir, "correct.txt"), "r") as f:
                    correct_output = f.read()
                with open(os.path.join(self.workspace_dir, "test.txt"), "r") as f:
                    test_output = f.read()
                
                # Measure execution time for this test
                test_start = time.time()
                
                # Compare outputs
                passed = (correct_output == test_output)
                test_time = time.time() - test_start
                
                self.testCompleted.emit(i, passed, input_text, correct_output, test_output)
                
                # Store detailed result for database with mismatch analysis
                test_result = {
                    'test_number': i,
                    'passed': passed,
                    'input': input_text,
                    'correct_output': correct_output,
                    'test_output': test_output,
                    'execution_time': test_time,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Add mismatch analysis if test failed
                if not passed:
                    mismatch_analysis = DatabaseManager.analyze_output_mismatch(correct_output, test_output)
                    test_result['mismatch_analysis'] = mismatch_analysis
                
                self.test_results.append(test_result)

                if not passed:
                    all_passed = False
                    break

            except Exception as e:
                self.testCompleted.emit(i, False, str(e), "", "")
                self.test_results.append({
                    'test_number': i,
                    'passed': False,
                    'error': str(e),
                    'execution_time': 0.0,
                    'timestamp': datetime.now().isoformat()
                })
                all_passed = False
                break

        self.allTestsCompleted.emit(all_passed)
        # Ensure that `show_all_passed` is called after `show_test_complete` in case of failure

    def stop(self):
        """Stop the worker loop"""
        self.is_running = False

class Stresser(QObject):
    compilationFinished = Signal(bool)  # True if successful, False if failed
    compilationOutput = Signal(str, str)  # (message, type)
    testStarted = Signal(int, int)  # current test, total tests
    testCompleted = Signal(int, bool, str, str, str)  # test number, passed, input, correct output, test output
    allTestsCompleted = Signal(bool)  # True if all passed

    def __init__(self, workspace_dir):
        super().__init__()
        self.workspace_dir = workspace_dir
        self.files = {
            'generator': os.path.join(workspace_dir, 'generator.cpp'),
            'correct': os.path.join(workspace_dir, 'correct.cpp'),
            'test': os.path.join(workspace_dir, 'test.cpp')
        }
        self.executables = {
            'generator': os.path.join(workspace_dir, 'generator.exe'),
            'correct': os.path.join(workspace_dir, 'correct.exe'),
            'test': os.path.join(workspace_dir, 'test.exe')
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
            'generator': 'correct',
            'correct': 'test',
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
            self.status_window.update_status('test', True, final_msg)
            self.compilationFinished.emit(True)

    def stop(self):
        """Stop any running compilation process"""
        if self.current_process and self.current_process.state() == QProcess.Running:
            self.current_process.kill()
            self.current_process.waitForFinished()
        if hasattr(self, 'status_window'):
            self.status_window.close()

    def run_stress_test(self, test_count):
        """Start stress tests using QThread and worker"""
        self.test_count = test_count  # Store for database saving
        self.test_start_time = datetime.now()  # Track start time
        
        self.status_window = StressTestStatusWindow()
        self.status_window.show()

        # Create the worker and thread
        self.worker = StressTestWorker(self.workspace_dir, self.executables, test_count)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        # Connect signals from worker to status window
        self.worker.testStarted.connect(self.status_window.show_test_running)
        self.worker.testCompleted.connect(self.status_window.show_test_complete)
        self.worker.allTestsCompleted.connect(self.status_window.show_all_passed)
        
        # Connect to our database saving method
        self.worker.allTestsCompleted.connect(self._save_test_results)

        # Start the worker when the thread starts
        self.thread.started.connect(self.worker.run_tests)
        # Clean up when the worker is done
        self.worker.allTestsCompleted.connect(self.thread.quit)
        self.worker.allTestsCompleted.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start the thread
        self.thread.start()
    
    def _save_test_results(self, all_passed):
        """Save test results to database"""
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
        
        # Compile mismatch analysis from all failed tests
        mismatch_summary = {
            'failed_tests': [],
            'total_failures': failed_tests,
            'common_patterns': []
        }
        
        for result in self.worker.test_results:
            if not result.get('passed', True) and 'mismatch_analysis' in result:
                mismatch_summary['failed_tests'].append({
                    'test_number': result['test_number'],
                    'analysis': result['mismatch_analysis']
                })
        
        # Create test result object
        result = TestResult(
            test_type="stress",
            file_path=test_file_path,
            test_count=self.test_count,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_time=total_time,
            timestamp=datetime.now().isoformat(),
            test_details=json.dumps(self.worker.test_results),
            project_name=os.path.basename(self.workspace_dir),
            files_snapshot=json.dumps(files_snapshot.__dict__),
            mismatch_analysis=json.dumps(mismatch_summary)
        )
        
        # Save to database
        try:
            result_id = self.db_manager.save_test_result(result)
            if result_id > 0:
                print(f"Test results saved to database with ID: {result_id}")
            else:
                print("Failed to save test results to database")
        except Exception as e:
            print(f"Error saving test results: {e}")
