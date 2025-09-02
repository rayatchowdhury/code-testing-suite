from PySide6.QtCore import QObject, Signal, QProcess
import os
import sys

class CompilerWorker(QObject):
    finished = Signal()
    output = Signal(tuple)  # Change to emit tuple
    error = Signal(tuple)   # Change to emit tuple
    input_requested = Signal()

    def __init__(self):
        super().__init__()
        self.process = None
        self.language_handlers = {
            'cpp': self._handle_cpp,
            'h': self._handle_cpp,
            'hpp': self._handle_cpp,
            'py': self._handle_python,
            'java': self._handle_java
        }

    def compile_and_run(self, filepath):
        try:
            ext = filepath.lower().split('.')[-1]
            handler = self.language_handlers.get(ext)
            
            if handler:
                handler(filepath)
            else:
                self.error.emit(("Unsupported file type\n", 'error'))
                self.finished.emit()
        except Exception as e:
            self.error.emit((f"Error: {str(e)}\n", 'error'))
            self.finished.emit()

    def _emit_status(self, message, format_type='info', newlines=1):
        """Helper method to emit formatted status messages"""
        self.output.emit((message + '\n' * newlines, format_type))

    def _handle_cpp(self, filepath):
        basename = os.path.basename(filepath)
        exe_name = os.path.splitext(filepath)[0] + ('.exe' if os.name == 'nt' else '')
        exe_basename = os.path.basename(exe_name)

        self._emit_status(f"Compiling {basename}...")
        
        compile_process = QProcess()
        compile_process.setProgram('g++')
        compile_process.setArguments([filepath, '-o', exe_name])
        compile_process.start()
        compile_process.waitForFinished()

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
        if not self.process:
            return
            
        self._error_emitted = False
        error = self.process.readAllStandardError().data().decode()
        output = self.process.readAllStandardOutput().data().decode()
        basename = os.path.basename(self.current_file)
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
        self._setup_process()
        self.current_file = exe_path
        self.process.start(exe_path)

    def _run_process(self, program, arguments):
        self._setup_process()
        self.current_program = program
        self.current_file = arguments[0]
        self.process.start(program, arguments)

    def _setup_process(self):
        """Common process setup logic"""
        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.readyReadStandardError.connect(self.handle_error)
        self.process.finished.connect(self._handle_process_exit)

    def handle_output(self):
        while self.process and self.process.canReadLine():
            output = self.process.readLine().data().decode()
            if 'Exception' in output:  # Check for Java exceptions
                self.error.emit((output, 'error'))
            else:
                self.output.emit((output, 'default'))
            if output.strip() == '':
                self.input_requested.emit()

    def handle_input(self, text):
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.process.write((text + '\n').encode())

    def stop_execution(self):
        """Stop the running process safely"""
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.process.finished.disconnect()  # Disconnect to prevent callback
            self.process.kill()
            self.process.waitForFinished()  # Wait for process to actually terminate
        self.process = None

    def _handle_process_exit(self, exit_code=None, exit_status=None):
        if not self.process:
            return
            
        # Get exit info from process if not provided (normal operation)
        if exit_code is None:
            exit_code = self.process.exitCode()
        if exit_status is None:
            exit_status = self.process.exitStatus()
        
        basename = os.path.basename(self.current_file)
        
        if exit_code != 0 or exit_status == QProcess.CrashExit:
            if not hasattr(self, '_error_emitted') or not self._error_emitted:
                self._handle_error(f"Program terminated with error code {exit_code}", basename)
        else:
            self._emit_status("\nProgram finished successfully.", 'success')
        
        self.process = None
        self.finished.emit()

class CompilerRunner(QObject):
    finished = Signal()

    def __init__(self, console_output):
        super().__init__()
        self.console = console_output
        self.worker = CompilerWorker()
        self._setup_connections()

    def _setup_connections(self):
        """Setup signal connections"""
        self.console.inputSubmitted.connect(self.worker.handle_input)
        self.worker.output.connect(self.handle_output)
        self.worker.error.connect(self.handle_error)
        self.worker.input_requested.connect(self.handle_input_request)
        self.worker.finished.connect(self._cleanup)

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
            self.worker.stop_execution()
        self._cleanup()

    def _cleanup(self):
        """Clean up resources safely"""
        try:
            if self.console and not self.console.isDestroyed():
                self.console.setInputEnabled(False)
        except (RuntimeError, AttributeError):
            pass  # Handle case where console is already destroyed
        self.finished.emit()

    def compile_and_run_code(self, filepath):
        """Start compilation and execution"""
        if not filepath:
            if self.console:
                self.console.displayOutput("Error: No file to compile\n", 'error')
            return
        
        self.stop_execution()
        if self.console:
            try:
                self.console.clear()
                self.console.setInputEnabled(True)
            except AttributeError as e:
                print(f"Warning: Console operation failed - {str(e)}")
        self.worker.compile_and_run(filepath)