# TODO: Implement compilation service based on v1 tools/compiler_runner.py
"""
Compilation Service Implementation

Implementation of CompilationService interface based on v1 tools/compiler_runner.py
Removes direct dependency on UI components.
"""
import asyncio
import subprocess
from pathlib import Path
from typing import AsyncIterator, List
from domain.models.compilation import CompilationResult, CompilationStatus
from domain.services.compilation_service import CompilationService, CompilationObserver
from domain.views.view_factory import StatusViewFactory

class BasicCompilationService:
    """
    Basic implementation of compilation service without UI dependencies.
    
    ASSUMPTION: Migrates core logic from v1/tools/compiler_runner.py
    without the PySide6 QProcess dependencies for now.
    """
    
    def __init__(self, status_view_factory=None):
        self._observers: List[CompilationObserver] = []
        self._is_cancelled = False
        self._status_view_factory = status_view_factory
    
    def add_observer(self, observer: CompilationObserver) -> None:
        """Add compilation observer"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: CompilationObserver) -> None:
        """Remove compilation observer"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    async def compile_file(self, file_path: Path) -> CompilationResult:
        """Compile a single file"""
        file_name = file_path.name
        
        # Notify observers
        for observer in self._observers:
            observer.on_compilation_started(file_name)
        
        try:
            # Determine output executable path
            if file_path.suffix.lower() in ['.cpp', '.c', '.cc']:
                exe_path = file_path.with_suffix('.exe')
                result = await self._compile_cpp(file_path, exe_path)
            elif file_path.suffix.lower() == '.py':
                # Python doesn't need compilation, just validate syntax
                result = await self._validate_python(file_path)
            else:
                result = CompilationResult(
                    file_path=file_path,
                    status=CompilationStatus.FAILED,
                    error_output=f"Unsupported file type: {file_path.suffix}"
                )
            
            # Notify observers
            for observer in self._observers:
                observer.on_compilation_finished(file_name, result)
            
            return result
            
        except Exception as e:
            result = CompilationResult(
                file_path=file_path,
                status=CompilationStatus.FAILED,
                error_output=str(e)
            )
            
            for observer in self._observers:
                observer.on_compilation_finished(file_name, result)
            
            return result
    
    async def compile_files(self, file_paths: List[Path]) -> AsyncIterator[CompilationResult]:
        """Compile multiple files"""
        self._is_cancelled = False
        success_count = 0
        total_count = len(file_paths)
        
        for file_path in file_paths:
            if self._is_cancelled:
                break
                
            result = await self.compile_file(file_path)
            if result.status == CompilationStatus.SUCCESS:
                success_count += 1
            
            yield result
        
        # Notify all compilations finished
        all_success = success_count == total_count and not self._is_cancelled
        message = f"Compiled {success_count}/{total_count} files successfully"
        
        for observer in self._observers:
            observer.on_all_compilations_finished(all_success, message)
    
    def cancel_compilation(self) -> None:
        """Cancel ongoing compilation"""
        self._is_cancelled = True
    
    async def _compile_cpp(self, source_path: Path, exe_path: Path) -> CompilationResult:
        """Compile C++ file using g++"""
        try:
            # Use asyncio.subprocess for non-blocking compilation
            process = await asyncio.create_subprocess_exec(
                'g++', str(source_path), '-o', str(exe_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return CompilationResult(
                    file_path=source_path,
                    status=CompilationStatus.SUCCESS,
                    output=stdout.decode('utf-8'),
                    executable_path=exe_path
                )
            else:
                return CompilationResult(
                    file_path=source_path,
                    status=CompilationStatus.FAILED,
                    error_output=stderr.decode('utf-8')
                )
                
        except FileNotFoundError:
            return CompilationResult(
                file_path=source_path,
                status=CompilationStatus.FAILED,
                error_output="g++ compiler not found. Please install GCC."
            )
        except Exception as e:
            return CompilationResult(
                file_path=source_path,
                status=CompilationStatus.FAILED,
                error_output=f"Compilation error: {str(e)}"
            )
    
    async def _validate_python(self, python_path: Path) -> CompilationResult:
        """Validate Python syntax"""
        try:
            # Use py_compile to check syntax
            import py_compile
            py_compile.compile(str(python_path), doraise=True)
            
            return CompilationResult(
                file_path=python_path,
                status=CompilationStatus.SUCCESS,
                output="Python syntax validation passed",
                executable_path=python_path  # Python files are executable as-is
            )
            
        except py_compile.PyCompileError as e:
            return CompilationResult(
                file_path=python_path,
                status=CompilationStatus.FAILED,
                error_output=str(e)
            )
