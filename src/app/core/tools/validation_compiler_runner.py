# -*- coding: utf-8 -*-
import subprocess
import os
import tempfile
import logging
from typing import Optional, List
from PySide6.QtCore import QObject, Signal, QThread
import threading

logger = logging.getLogger(__name__)

class ValidationCompilerRunner(QObject):
    """Compiler and runner for validation tasks"""
    
    compilationStarted = Signal()
    compilationFinished = Signal(bool, str)  # success, output
    executionStarted = Signal()
    executionFinished = Signal(str)  # output
    
    def __init__(self, console_output=None, parent=None):
        super().__init__(parent)
        self.console_output = console_output
        self.current_process = None
        self.temp_files = []
        
    def compile_and_run(self, source_file: str, input_data: Optional[str] = None):
        """Compile and run a source file with optional input data"""
        if not os.path.exists(source_file):
            self._emit_error(f"Source file not found: {source_file}")
            return
            
        # Run in separate thread to avoid blocking UI
        thread = threading.Thread(target=self._compile_and_run_worker, 
                                 args=(source_file, input_data))
        thread.daemon = True
        thread.start()
        
    def _compile_and_run_worker(self, source_file: str, input_data: Optional[str]):
        """Worker method for compilation and execution"""
        try:
            # Determine file type and compiler
            file_ext = os.path.splitext(source_file)[1].lower()
            
            if file_ext in ['.cpp', '.cxx', '.cc']:
                self._compile_and_run_cpp(source_file, input_data)
            elif file_ext == '.c':
                self._compile_and_run_c(source_file, input_data)
            elif file_ext == '.py':
                self._run_python(source_file, input_data)
            elif file_ext == '.java':
                self._compile_and_run_java(source_file, input_data)
            else:
                self._emit_error(f"Unsupported file type: {file_ext}")
                
        except Exception as e:
            self._emit_error(f"Compilation/execution error: {str(e)}")
            
    def _compile_and_run_cpp(self, source_file: str, input_data: Optional[str]):
        """Compile and run C++ file"""
        self.compilationStarted.emit()
        
        # Create temporary executable
        temp_dir = tempfile.gettempdir()
        exe_name = os.path.join(temp_dir, f"validation_temp_{os.getpid()}.exe")
        self.temp_files.append(exe_name)
        
        # Try different C++ compilers
        compilers = ['g++', 'clang++', 'gcc']
        compilation_success = False
        compile_output = ""
        
        for compiler in compilers:
            try:
                # Compilation command
                compile_cmd = [
                    compiler,
                    source_file,
                    '-o', exe_name,
                    '-std=c++17',
                    '-Wall',
                    '-O2'
                ]
                
                self._log_output(f"Compiling with {compiler}...")
                
                result = subprocess.run(
                    compile_cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    compilation_success = True
                    compile_output = f"Compilation successful with {compiler}"
                    break
                else:
                    compile_output += f"{compiler}: {result.stderr}\n"
                    
            except (FileNotFoundError, subprocess.TimeoutExpired) as e:
                compile_output += f"{compiler} not found or timeout\n"
                continue
                
        self.compilationFinished.emit(compilation_success, compile_output)
        
        if compilation_success and os.path.exists(exe_name):
            self._run_executable(exe_name, input_data)
        else:
            self._emit_error("Compilation failed with all available compilers")
            
    def _compile_and_run_c(self, source_file: str, input_data: Optional[str]):
        """Compile and run C file"""
        self.compilationStarted.emit()
        
        temp_dir = tempfile.gettempdir()
        exe_name = os.path.join(temp_dir, f"validation_temp_{os.getpid()}.exe")
        self.temp_files.append(exe_name)
        
        compilers = ['gcc', 'clang']
        compilation_success = False
        compile_output = ""
        
        for compiler in compilers:
            try:
                compile_cmd = [
                    compiler,
                    source_file,
                    '-o', exe_name,
                    '-std=c99',
                    '-Wall',
                    '-O2'
                ]
                
                self._log_output(f"Compiling C with {compiler}...")
                
                result = subprocess.run(
                    compile_cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    compilation_success = True
                    compile_output = f"C compilation successful with {compiler}"
                    break
                else:
                    compile_output += f"{compiler}: {result.stderr}\n"
                    
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
                
        self.compilationFinished.emit(compilation_success, compile_output)
        
        if compilation_success and os.path.exists(exe_name):
            self._run_executable(exe_name, input_data)
        else:
            self._emit_error("C compilation failed")
            
    def _run_python(self, source_file: str, input_data: Optional[str]):
        """Run Python file directly"""
        self.executionStarted.emit()
        self._log_output("Running Python script...")
        
        try:
            # Try python3 first, then python
            for python_cmd in ['python3', 'python']:
                try:
                    result = subprocess.run(
                        [python_cmd, source_file],
                        input=input_data,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    output = result.stdout
                    if result.stderr:
                        output += f"\nErrors:\n{result.stderr}"
                        
                    self.executionFinished.emit(output)
                    return
                    
                except FileNotFoundError:
                    continue
                    
            self._emit_error("Python interpreter not found")
            
        except subprocess.TimeoutExpired:
            self._emit_error("Python script execution timeout")
        except Exception as e:
            self._emit_error(f"Python execution error: {str(e)}")
            
    def _compile_and_run_java(self, source_file: str, input_data: Optional[str]):
        """Compile and run Java file"""
        self.compilationStarted.emit()
        
        # Get class name from file
        class_name = os.path.splitext(os.path.basename(source_file))[0]
        source_dir = os.path.dirname(source_file)
        
        try:
            # Compile
            self._log_output("Compiling Java...")
            compile_result = subprocess.run(
                ['javac', source_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            compilation_success = compile_result.returncode == 0
            compile_output = compile_result.stderr if compile_result.stderr else "Java compilation successful"
            
            self.compilationFinished.emit(compilation_success, compile_output)
            
            if compilation_success:
                # Run
                self.executionStarted.emit()
                self._log_output("Running Java program...")
                
                run_result = subprocess.run(
                    ['java', '-cp', source_dir, class_name],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                output = run_result.stdout
                if run_result.stderr:
                    output += f"\nErrors:\n{run_result.stderr}"
                    
                self.executionFinished.emit(output)
                
                # Clean up class file
                class_file = os.path.join(source_dir, f"{class_name}.class")
                if os.path.exists(class_file):
                    os.remove(class_file)
            else:
                self._emit_error("Java compilation failed")
                
        except FileNotFoundError:
            self._emit_error("Java compiler (javac) not found")
        except subprocess.TimeoutExpired:
            self._emit_error("Java compilation/execution timeout")
        except Exception as e:
            self._emit_error(f"Java error: {str(e)}")
            
    def _run_executable(self, exe_path: str, input_data: Optional[str]):
        """Run compiled executable"""
        self.executionStarted.emit()
        self._log_output("Running executable...")
        
        try:
            result = subprocess.run(
                [exe_path],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nErrors:\n{result.stderr}"
            if result.returncode != 0:
                output += f"\nExit code: {result.returncode}"
                
            self.executionFinished.emit(output)
            
        except subprocess.TimeoutExpired:
            self._emit_error("Execution timeout (10 seconds)")
        except Exception as e:
            self._emit_error(f"Execution error: {str(e)}")
        finally:
            # Clean up temporary file
            if os.path.exists(exe_path):
                try:
                    os.remove(exe_path)
                    if exe_path in self.temp_files:
                        self.temp_files.remove(exe_path)
                except:
                    pass
                    
    def _emit_error(self, message: str):
        """Emit error message"""
        self._log_output(f"ERROR: {message}")
        self.executionFinished.emit(f"ERROR: {message}")
        
    def _log_output(self, message: str):
        """Log output to console if available"""
        if self.console_output:
            self.console_output.append_output(message)
        else:
            logger.info(message)
            
    def cleanup(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
        self.temp_files.clear()
        
    def __del__(self):
        """Destructor to clean up resources"""
        self.cleanup()
