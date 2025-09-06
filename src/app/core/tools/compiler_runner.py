from PySide6.QtCore import QObject, Signal, QProcess, QThread, QMutex, QMetaObject, Qt, Q_ARG, Slot
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CompilerWorker(QObject):
    finished = Signal()
    output = Signal(tuple)  # Change to emit tuple
    error = Signal(tuple)   # Change to emit tuple
    input_requested = Signal()

    def __init__(self):
        super().__init__()
        self.process = None
        self.mutex = QMutex()
        self.current_file = None
        self.current_program = None
        self._error_emitted = False
        self.language_handlers = {
            'cpp': self._handle_cpp,
            'h': self._handle_cpp,
            'hpp': self._handle_cpp,
            'py': self._handle_python,
            'java': self._handle_java
        }

    @Slot(str)
    def compile_and_run(self, filepath):
        """Main entry point for compilation and execution"""
        self.mutex.lock()
        try:
            logger.debug(f"Starting compilation for {filepath}")
            ext = filepath.lower().split('.')[-1]
            handler = self.language_handlers.get(ext)
            
            if handler:
                handler(filepath)
            else:
                self.error.emit(("Unsupported file type\n", 'error'))
                self.finished.emit()
        except Exception as e:
            logger.error(f"Compilation error: {str(e)}")
            self.error.emit((f"Error: {str(e)}\n", 'error'))
            self.finished.emit()
        finally:
            self.mutex.unlock()

    def _emit_status(self, message, format_type='info', newlines=1):
        """Helper method to emit formatted status messages"""
        self.output.emit((message + '\n' * newlines, format_type))

    def _handle_cpp(self, filepath):
        """Handle C++ compilation and execution"""
        basename = os.path.basename(filepath)
        exe_name = os.path.splitext(filepath)[0] + ('.exe' if os.name == 'nt' else '')
        exe_basename = os.path.basename(exe_name)

        self._emit_status(f"Compiling {basename}...")
        
        # Create compile process in the current thread
        compile_process = QProcess()
        compile_process.setProgram('g++')
        compile_process.setArguments([filepath, '-o', exe_name])
        compile_process.start()
        compile_process.waitForFinished(10000)  # 10 second timeout
        compile_process.waitForFinished(10000)  # 10 second timeout

        if compile_process.exitCode() != 0:
            error_output = compile_process.readAllStandardError().data().decode()
            self.error.emit((f"Compilation Error in {basename}:\n{error_output}\n", 'error'))
            self.finished.emit()
            return

        self._emit_status("Compilation successful!", 'success')
        self._emit_status(f"Running program {exe_basename}...", 'info', 2)
        self._emit_status(f"----------------------------", 'info', 2)
        self._run_executable(exe_name)

    def _handle_python(self, filepath):
        """Handle Python script execution"""
        basename = os.path.basename(filepath)
        self._emit_status(f"Running Python script {basename}...", 'info', 2)
        self._emit_status(f"---------------------------------", 'info', 2)
        self._run_process('python', [filepath])

    def _check_java_class_name(self, filepath, classname):
        """Validate Java class name matches file name"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                valid_names = [classname, classname.capitalize()]
                if not any(f'class {name}' in content for name in valid_names):
                    self.error.emit((
                        f"Error: Java class name must match the file name '{classname}'\n",
                        'error'
                    ))
                    return False
            return True
        except Exception as e:
            self.error.emit((f"Error reading file: {str(e)}\n", 'error'))
            return False

    def _handle_java(self, filepath):
        """Handle Java compilation and execution"""
        basename = os.path.basename(filepath)
        classname = os.path.splitext(basename)[0]
        directory = os.path.dirname(filepath) or '.'

        if not self._check_java_class_name(filepath, classname):
            self.finished.emit()
            return

        self._emit_status(f"Running Java program {basename}...", 'info', 2)
        self._emit_status(f"---------------------------------------", 'info', 2)
        
        original_dir = os.getcwd()
        try:
            os.chdir(directory)
            self._run_process('java', [filepath])
        finally:
            os.chdir(original_dir)

    def _handle_error(self, error_type, basename, details=""):
        """Helper method for error handling"""
        self.error.emit(("\n", 'error'))
        self.error.emit((f"Runtime Error in {basename}: {error_type}\n", 'error'))
        if details:
            self.error.emit((f"{details}\n", 'error'))
        self._error_emitted = True

    def handle_error(self):
        """Handle process errors safely"""
        if not self.process:
            return
            
        self._error_emitted = False
        error = self.process.readAllStandardError().data().decode()
        output = self.process.readAllStandardOutput().data().decode()
        basename = os.path.basename(self.current_file) if self.current_file else "unknown"
        full_output = (error + output).lower()
        
        # Check for specific runtime errors
        if any(err in full_output for err in ['floating point', 'divide by zero']):
            self._handle_error("Division by zero detected", basename)
        elif 'segmentation fault' in full_output:
            self._handle_error("Memory access violation", basename, "Segmentation Fault")
        elif 'abort' in full_output:
            self._handle_error("Program terminated abnormally", basename)
        elif error:
            self._handle_error("", basename, error)

    def _run_executable(self, exe_path):
        """Run an executable safely"""
        self._setup_process()
        self.current_file = exe_path
        if self.process:
            self.process.start(exe_path)

    def _run_process(self, program, arguments):
        """Run a process with arguments safely"""
        self._setup_process()
        self.current_program = program
        self.current_file = arguments[0] if arguments else None
        if self.process:
            self.process.start(program, arguments)

    def _setup_process(self):
        """Common process setup logic - always creates process in current thread"""
        # Clean up any existing process
        if self.process:
            self.stop_execution()
        
        try:
            # Create new process in current thread
            self.process = QProcess()
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            
            # Connect signals
            self.process.readyReadStandardOutput.connect(self.handle_output)
            self.process.readyReadStandardError.connect(self.handle_error)
            self.process.finished.connect(self._handle_process_exit)
            
            logger.debug(f"Process created in thread: {QThread.currentThread()}")
            
        except Exception as e:
            logger.error(f"Failed to setup process: {e}")
            self.error.emit((f"Failed to setup process: {e}\n", 'error'))
            self.finished.emit()

    def handle_output(self):
        """Handle process output safely"""
        if not self.process:
            return
            
        try:
            while self.process.canReadLine():
                output = self.process.readLine().data().decode()
                if 'Exception' in output:  # Check for Java exceptions
                    self.error.emit((output, 'error'))
                else:
                    self.output.emit((output, 'default'))
                if output.strip() == '':
                    self.input_requested.emit()
        except Exception as e:
            logger.error(f"Error handling output: {e}")
    def handle_input(self, text):
        """Handle input to running process safely"""
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            try:
                self.process.write((text + '\n').encode())
            except Exception as e:
                logger.error(f"Error writing to process: {e}")

    @Slot()
    def stop_execution(self):
        """Stop the running process safely"""
        self.mutex.lock()
        try:
            if self.process and self.process.state() == QProcess.ProcessState.Running:
                # Disconnect signals to prevent callbacks during cleanup
                try:
                    self.process.finished.disconnect()
                    self.process.readyReadStandardOutput.disconnect()
                    self.process.readyReadStandardError.disconnect()
                except:
                    pass  # Ignore if already disconnected
                
                self.process.kill()
                self.process.waitForFinished(3000)  # Wait up to 3 seconds
                
            if self.process:
                self.process.deleteLater()
                self.process = None
                
            logger.debug("Process stopped and cleaned up")
        finally:
            self.mutex.unlock()

    def _handle_process_exit(self, exit_code=None, exit_status=None):
        """Handle process exit safely"""
        if not self.process:
            return
            
        try:
            # Get exit info from process if not provided (normal operation)
            if exit_code is None:
                exit_code = self.process.exitCode()
            if exit_status is None:
                exit_status = self.process.exitStatus()
            
            basename = os.path.basename(self.current_file) if self.current_file else "unknown"
            
            if exit_code != 0 or exit_status == QProcess.CrashExit:
                if not hasattr(self, '_error_emitted') or not self._error_emitted:
                    self._handle_error(f"Program terminated with error code {exit_code}", basename)
            else:
                self._emit_status("\nProgram finished successfully.", 'success')
            
        except Exception as e:
            logger.error(f"Error in process exit handler: {e}")
        finally:
            self.process = None
            self.finished.emit()

class CompilerRunner(QObject):
    finished = Signal()

    def __init__(self, console_output):
        super().__init__()
        self.console = console_output
        self.worker = None
        self.thread = None
        self._setup_worker()

    def _setup_worker(self):
        """Setup worker in a separate thread"""
        # Clean up existing worker/thread
        self._cleanup_worker()
        
        # Create new thread and worker
        self.thread = QThread()
        self.worker = CompilerWorker()
        
        # Move worker to thread
        self.worker.moveToThread(self.thread)
        
        # Connect thread signals
        self.thread.started.connect(self._on_thread_started)
        self.thread.finished.connect(self._on_thread_finished)
        
        # Connect worker signals - these are thread-safe
        self.worker.output.connect(self.handle_output)
        self.worker.error.connect(self.handle_error)
        self.worker.input_requested.connect(self.handle_input_request)
        self.worker.finished.connect(self._on_worker_finished)
        
        # Connect input from console if available
        if self.console and hasattr(self.console, 'inputSubmitted'):
            self.console.inputSubmitted.connect(self.worker.handle_input)

    def _cleanup_worker(self):
        """Clean up worker and thread safely"""
        if self.worker:
            self.worker.stop_execution()
            
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            if not self.thread.wait(5000):  # Wait up to 5 seconds
                logger.warning("Thread did not terminate gracefully, forcing termination")
                self.thread.terminate()
                self.thread.wait(1000)  # Wait 1 more second after terminate
            
        if self.thread:
            self.thread.deleteLater()
            self.thread = None
            
        if self.worker:
            self.worker.deleteLater()
            self.worker = None

    def __del__(self):
        """Destructor to ensure proper cleanup"""
        self._cleanup_worker()

    def _on_thread_started(self):
        """Called when thread starts"""
        logger.debug("Worker thread started")

    def _on_thread_finished(self):
        """Called when thread finishes"""
        logger.debug("Worker thread finished")

    def _on_worker_finished(self):
        """Called when worker finishes"""
        if self.thread:
            self.thread.quit()
        self.finished.emit()

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
            # Use QThread.invokeMethod for thread-safe call
            QMetaObject.invokeMethod(self.worker, "stop_execution", Qt.QueuedConnection)
        self._cleanup()

    def _cleanup(self):
        """Clean up resources safely"""
        try:
            if self.console and hasattr(self.console, 'setInputEnabled'):
                self.console.setInputEnabled(False)
        except (RuntimeError, AttributeError):
            pass  # Handle case where console is already destroyed

    def compile_and_run_code(self, filepath):
        """Start compilation and execution"""
        if not filepath:
            if self.console:
                self.console.displayOutput("Error: No file to compile\n", 'error')
            return
        
        # Stop any existing execution
        self.stop_execution()
        
        # Setup console
        if self.console:
            try:
                self.console.clear()
                self.console.setInputEnabled(True)
            except AttributeError as e:
                logger.warning(f"Console operation failed - {str(e)}")
        
        # Start thread if not running
        if not self.thread.isRunning():
            self.thread.start()
        
        # Start compilation in worker thread
        QMetaObject.invokeMethod(
            self.worker, 
            "compile_and_run", 
            Qt.QueuedConnection,
            Q_ARG(str, filepath)
        )