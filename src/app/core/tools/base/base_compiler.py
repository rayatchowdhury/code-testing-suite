"""
BaseCompiler - Consolidated compilation logic for all tools.

This class consolidates the 450+ lines of duplicated compilation logic
from validator.py, benchmarker.py, and comparator.py into a single
reusable base class with consistent optimizations and caching.
"""

import os
import multiprocessing
import subprocess
import threading
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from PySide6.QtCore import QObject, Signal
import logging

logger = logging.getLogger(__name__)


class BaseCompiler(QObject):
    """
    Base compiler with parallel compilation, smart caching, and optimizations.
    
    This class consolidates compilation logic that was duplicated across multiple
    tool implementations, providing:
    - Parallel compilation with optimal worker count
    - Smart timestamp-based caching to avoid unnecessary recompilation
    - Consistent optimization flags across all tools
    - Unified error handling and status reporting
    - Template method pattern for customization
    """
    
    # Signals for compilation progress and results
    compilationFinished = Signal(bool)  # True if successful, False if failed
    compilationOutput = Signal(str, str)  # (message, type)
    
    def __init__(self, workspace_dir: str, files_dict: Dict[str, str], 
                 optimization_level: str = 'O2'):
        """
        Initialize the base compiler.
        
        Args:
            workspace_dir: Directory containing source files
            files_dict: Dictionary mapping file keys to source file paths
            optimization_level: Compiler optimization level ('O0', 'O1', 'O2', 'O3')
        """
        super().__init__()
        self.workspace_dir = workspace_dir
        self.files = files_dict
        self.optimization_level = optimization_level
        self.compilation_failed = False
        
        # Create executables dict from files dict
        self.executables = {
            key: os.path.join(workspace_dir, f"{key}.exe")
            for key in files_dict.keys()
        }
        
    def compile_all(self) -> bool:
        """
        Compile all files in parallel with optimizations and caching.
        
        Returns:
            bool: True if all files compiled successfully, False otherwise
        """
        self.compilation_failed = False
        
        # Start parallel compilation in a separate thread to avoid blocking UI
        compile_thread = threading.Thread(target=self._parallel_compile_all)
        compile_thread.daemon = True
        compile_thread.start()
        
        return True  # Return immediately, actual result comes via signal
    
    def _parallel_compile_all(self) -> None:
        """
        Compile all files in parallel with smart caching and optimization.
        
        This method consolidates the identical logic from validator_runner.py,
        benchmarker.py, and comparator.py.
        """
        files_to_compile = list(self.files.keys())
        max_workers = min(len(files_to_compile), multiprocessing.cpu_count())
        
        self.compilationOutput.emit("🚀 Starting optimized parallel compilation...\n", 'info')
        
        # Check which files need recompilation
        files_needing_compilation = []
        for file_key in files_to_compile:
            if self._needs_recompilation(file_key):
                files_needing_compilation.append(file_key)
            else:
                self.compilationOutput.emit(
                    f"✅ {file_key}.exe is up-to-date, skipping compilation\n", 'success'
                )
        
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
                    else:
                        all_success = False
                        self.compilationOutput.emit(f"❌ Failed to compile {file_key}.cpp:\n{output}\n", 'error')
                        
                except Exception as e:
                    all_success = False
                    error_msg = f"Compilation error for {file_key}: {str(e)}"
                    self.compilationOutput.emit(f"❌ {error_msg}\n", 'error')
        
        # Final result
        if all_success:
            self.compilationOutput.emit("\n🎉 All files compiled successfully with optimizations!\n", 'success')
            self.compilationFinished.emit(True)
        else:
            self.compilationOutput.emit("\n❌ Some files failed to compile.\n", 'error')
            self.compilationFinished.emit(False)
    
    def _needs_recompilation(self, file_key: str) -> bool:
        """
        Check if file needs recompilation based on timestamps.
        
        This method consolidates the identical logic from all three runner classes.
        
        Args:
            file_key: Key identifying the file to check
            
        Returns:
            bool: True if recompilation is needed, False if executable is up-to-date
        """
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
    
    def _compile_single_file(self, file_key: str) -> Tuple[bool, str]:
        """
        Compile a single file with optimization flags.
        
        This method consolidates the identical logic from all three runner classes
        and provides consistent optimization flags.
        
        Args:
            file_key: Key identifying the file to compile
            
        Returns:
            Tuple[bool, str]: (success, output/error_message)
        """
        source_file = self.files[file_key]
        executable_file = self.executables[file_key]
        
        # Get compiler flags (customizable by subclasses)
        compiler_flags = self.get_compiler_flags()
        
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
    
    def get_compiler_flags(self) -> List[str]:
        """
        Get compiler flags for compilation.
        
        This method can be overridden by subclasses to customize compilation flags
        for specific use cases while maintaining consistent base optimizations.
        
        Returns:
            List[str]: List of compiler flags
        """
        # Standard optimization flags used across all tools
        return [
            f'-{self.optimization_level}',  # Optimization level (O2 by default)
            '-march=native',                # Optimize for current CPU architecture
            '-mtune=native',               # Tune for current CPU
            '-pipe',                       # Use pipes instead of temporary files
            '-std=c++17',                  # Use modern C++ standard
            '-Wall',                       # Enable common warnings
        ]
    
    def get_debug_flags(self) -> List[str]:
        """
        Get debug-specific compiler flags.
        
        Returns:
            List[str]: List of debug compiler flags
        """
        return [
            '-g',                          # Include debug information
            '-DDEBUG',                     # Define DEBUG macro
            '-fsanitize=address',          # Enable address sanitizer
            '-fsanitize=undefined',        # Enable undefined behavior sanitizer
        ]
    
    def get_release_flags(self) -> List[str]:
        """
        Get release-specific compiler flags.
        
        Returns:
            List[str]: List of release compiler flags
        """
        return [
            '-DNDEBUG',                    # Disable debug assertions
            '-flto',                       # Link-time optimization
            '-fomit-frame-pointer',        # Omit frame pointer for better performance
        ]
    
    def stop(self) -> None:
        """Stop any running compilation process."""
        # This method can be extended by subclasses if they need
        # to stop specific compilation processes
        pass
            
    def __del__(self):
        """Destructor to ensure proper cleanup."""
        self.stop()