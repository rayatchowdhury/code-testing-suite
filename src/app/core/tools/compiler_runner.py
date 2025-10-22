import logging
import os

from PySide6.QtCore import (
    Q_ARG,
    QMetaObject,
    QMutex,
    QObject,
    QProcess,
    Qt,
    QThread,
    Signal,
    Slot,
)

from src.app.core.config.core import ConfigManager
from src.app.core.tools.base.language_compilers import LanguageCompilerFactory
from src.app.core.tools.base.language_detector import Language, LanguageDetector

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CompilerWorker(QObject):
    finished = Signal()
    output = Signal(tuple)  # Change to emit tuple
    error = Signal(tuple)  # Change to emit tuple
    input_requested = Signal()

    def __init__(self):
        super().__init__()
        self.process = None
        self.mutex = QMutex()
        self.current_file = None
        self.current_program = None
        self._error_emitted = False
        
        # Initialize config-driven compilation
        self.config_manager = ConfigManager.instance()
        self.language_detector = LanguageDetector()
        self.language_compilers = {}  # Cache of language -> compiler instances
        
        logger.info("CompilerWorker initialized with config-driven compilation")

    @Slot(str)
    def compile_and_run(self, filepath):
        """Main entry point for compilation and execution using config-driven approach"""
        self.mutex.lock()
        try:
            logger.debug(f"Starting compilation for {filepath}")
            
            # Detect language from file
            language = self.language_detector.detect_from_extension(filepath)
            
            if language == Language.UNKNOWN:
                self.error.emit(("Unsupported file type\n", "error"))
                self.finished.emit()
                return
            
            # Get or create language-specific compiler with current config
            if language not in self.language_compilers:
                config = self.config_manager.load_config()
                lang_config = self._get_language_config(config, language)
                self.language_compilers[language] = LanguageCompilerFactory.create_compiler(
                    language, lang_config
                )
            
            compiler = self.language_compilers[language]
            
            # Handle compilation based on language
            if compiler.needs_compilation():
                success, message = self._compile_file(filepath, compiler, language)
                if not success:
                    self.error.emit((message, "error"))
                    self.finished.emit()
                    return
            else:
                # Interpreted language - just validate syntax if needed
                self._emit_status(f"✓ {os.path.basename(filepath)} ready to run", "success")
            
            # Execute the program
            self._execute_file(filepath, compiler, language)
            
        except Exception as e:
            logger.error(f"Compilation error: {str(e)}")
            self.error.emit((f"Error: {str(e)}\n", "error"))
            self.finished.emit()
        finally:
            self.mutex.unlock()
    
    def _get_language_config(self, config, language):
        """Extract language-specific config from main config"""
        languages_config = config.get("languages", {})
        return languages_config.get(language.value, {})

    def _emit_status(self, message, format_type="info", newlines=1):
        """Helper method to emit formatted status messages"""
        self.output.emit((message + "\n" * newlines, format_type))
    
    def _compile_file(self, filepath, compiler, language):
        """
        Compile a file using config-driven compiler settings.
        
        Args:
            filepath: Source file path
            compiler: Language-specific compiler instance
            language: Language enum
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        basename = os.path.basename(filepath)
        executable_path = compiler.get_executable_path(filepath)
        exe_basename = os.path.basename(executable_path)
        
        # Check if recompilation is needed
        if self._is_executable_up_to_date(filepath, executable_path):
            self._emit_status(f"✅ {exe_basename} is up-to-date, skipping compilation", "success")
            return True, "Up to date"
        
        # Compile using language-specific compiler with config-driven settings
        self._emit_status(f"🔨 Compiling {basename}...")
        
        success, output = compiler.compile(
            source_file=filepath,
            output_file=executable_path,
            timeout=30
        )
        
        if success:
            self._emit_status("✅ Compilation successful!", "success")
            return True, output
        else:
            return False, f"Compilation Error in {basename}:\n{output}\n"
    
    def _execute_file(self, filepath, compiler, language):
        """Execute a compiled/interpreted file"""
        basename = os.path.basename(filepath)
        executable_path = compiler.get_executable_path(filepath)
        exe_basename = os.path.basename(executable_path)
        
        self._emit_status(f"🚀 Running {exe_basename}...", "info", 2)
        self._emit_status("----------------------------", "info", 2)
        
        # Get execution command from compiler
        if language == Language.JAVA:
            # Extract class name for Java
            classname = os.path.splitext(basename)[0]
            command = compiler.get_executable_command(executable_path, class_name=classname)
        else:
            command = compiler.get_executable_command(executable_path)
        
        # Execute the command
        if len(command) > 1:
            # Command with arguments (e.g., python script.py, java -cp . ClassName)
            self._run_process(command[0], command[1:])
        else:
            # Direct execution (e.g., ./program.exe)
            self._run_executable(command[0])

    def _is_executable_up_to_date(self, source_file, executable_file):
        """Check if executable is newer than source file"""
        # If executable doesn't exist, need to compile
        if not os.path.exists(executable_file):
            return False

        # If source doesn't exist, can't compile
        if not os.path.exists(source_file):
            return False

        # Compare timestamps
        try:
            source_mtime = os.path.getmtime(source_file)
            exe_mtime = os.path.getmtime(executable_file)
            return exe_mtime > source_mtime  # Executable is newer than source
        except OSError:
            return False  # If we can't check timestamps, be safe and recompile

    @Slot()
    def reload_config(self):
        """Reload configuration and recreate language compilers"""
        logger.info("Reloading compiler configuration")
        self.language_compilers.clear()
        # Compilers will be recreated on next compile_and_run call with fresh config

    def _handle_error(self, error_type, basename, details=""):
        """Helper method for error handling"""
        self.error.emit(("\n", "error"))
        self.error.emit((f"Runtime Error in {basename}: {error_type}\n", "error"))
        if details:
            self.error.emit((f"{details}\n", "error"))
        self._error_emitted = True

    def handle_error(self):
        """Handle process errors safely"""
        if not self.process:
            return

        self._error_emitted = False
        error = self.process.readAllStandardError().data().decode()
        output = self.process.readAllStandardOutput().data().decode()
        basename = (
            os.path.basename(self.current_file) if self.current_file else "unknown"
        )
        full_output = (error + output).lower()

        # Check for specific runtime errors
        if any(err in full_output for err in ["floating point", "divide by zero"]):
            self._handle_error("Division by zero detected", basename)
        elif "segmentation fault" in full_output:
            self._handle_error(
                "Memory access violation", basename, "Segmentation Fault"
            )
        elif "abort" in full_output:
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
            self.error.emit((f"Failed to setup process: {e}\n", "error"))
            self.finished.emit()

    def handle_output(self):
        """Handle process output safely"""
        if not self.process:
            return

        try:
            while self.process.canReadLine():
                output = self.process.readLine().data().decode()
                if "Exception" in output:  # Check for Java exceptions
                    self.error.emit((output, "error"))
                else:
                    self.output.emit((output, "default"))
                if output.strip() == "":
                    self.input_requested.emit()
        except Exception as e:
            logger.error(f"Error handling output: {e}")

    def handle_input(self, text):
        """Handle input to running process safely"""
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            try:
                self.process.write((text + "\n").encode())
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
                except Exception:
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

            basename = (
                os.path.basename(self.current_file) if self.current_file else "unknown"
            )

            if exit_code != 0 or exit_status == QProcess.CrashExit:
                if not hasattr(self, "_error_emitted") or not self._error_emitted:
                    self._handle_error(
                        f"Program terminated with error code {exit_code}", basename
                    )
            else:
                self._emit_status("\nProgram finished successfully.", "success")

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
        if self.console and hasattr(self.console, "inputSubmitted"):
            self.console.inputSubmitted.connect(self.worker.handle_input)

    def _cleanup_worker(self):
        """Clean up worker and thread safely"""
        # CRITICAL FIX (P0 Issue #1): Kill QProcess BEFORE terminating thread
        # to prevent zombie processes
        if self.worker:
            # Step 1: Stop the worker's process synchronously
            try:
                if hasattr(self.worker, 'process') and self.worker.process:
                    if self.worker.process.state() == QProcess.ProcessState.Running:
                        logger.debug("Killing worker process before thread cleanup")
                        self.worker.process.kill()
                        self.worker.process.waitForFinished(1000)
            except (RuntimeError, AttributeError) as e:
                # Worker or process might be deleted already
                logger.debug(f"Process already cleaned up: {e}")
            
            # Step 2: Signal worker to stop
            self.worker.stop_execution()

        # Step 3: Now safely cleanup the thread
        try:
            if (
                self.thread
                and hasattr(self.thread, "isRunning")
                and self.thread.isRunning()
            ):
                self.thread.quit()
                if not self.thread.wait(5000):  # Wait up to 5 seconds
                    logger.warning(
                        "Thread did not terminate gracefully, forcing termination"
                    )
                    # Thread terminate is now safe - process already killed
                    self.thread.terminate()
                    self.thread.wait(1000)  # Wait 1 more second after terminate

            if self.thread:
                self.thread.deleteLater()
                self.thread = None

            if self.worker:
                self.worker.deleteLater()
                self.worker = None
        except RuntimeError:
            # Handle case where Qt objects are already deleted
            self.thread = None
            self.worker = None

    def __del__(self):
        """Destructor to ensure proper cleanup"""
        try:
            self._cleanup_worker()
        except RuntimeError:
            # Skip cleanup if Qt objects are already deleted
            pass

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
            text, format_type = str(output_data), "default"  # Fallback

        if self.console:
            self.console.displayOutput(text, format_type)

    def handle_error(self, error_data):
        """Handle error safely"""
        if isinstance(error_data, tuple) and len(error_data) == 2:
            text, format_type = error_data
        else:
            text, format_type = str(error_data), "error"  # Fallback

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
            if self.console and hasattr(self.console, "setInputEnabled"):
                self.console.setInputEnabled(False)
        except (RuntimeError, AttributeError):
            pass  # Handle case where console is already destroyed

    def compile_and_run_code(self, filepath):
        """Start compilation and execution"""
        if not filepath:
            if self.console:
                self.console.displayOutput("Error: No file to compile\n", "error")
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
            self.worker, "compile_and_run", Qt.QueuedConnection, Q_ARG(str, filepath)
        )
    
    def reload_config(self):
        """Reload configuration for the worker"""
        if self.worker:
            # Use QueuedConnection to avoid blocking the main thread
            # Worker will clear compilers on next compile_and_run call
            QMetaObject.invokeMethod(
                self.worker, "reload_config", Qt.QueuedConnection
            )
            logger.info("CompilerRunner config reload queued")
