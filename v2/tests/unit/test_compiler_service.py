"""
Unit tests for BasicCompilationService

Tests the compilation service implementation
"""
import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from infrastructure.compilation.compiler_service import BasicCompilationService
from domain.models.compilation import CompilationStatus, CompilationResult

class TestBasicCompilationService:
    """Test basic compilation service"""
    
    def test_observer_management(self):
        """Test adding and removing observers"""
        service = BasicCompilationService()
        observer = Mock()
        
        # Add observer
        service.add_observer(observer)
        assert observer in service._observers
        
        # Add same observer again (should not duplicate)
        service.add_observer(observer)
        assert service._observers.count(observer) == 1
        
        # Remove observer
        service.remove_observer(observer)
        assert observer not in service._observers
    
    @pytest.mark.asyncio
    async def test_compile_unsupported_file_type(self):
        """Test compilation of unsupported file type"""
        service = BasicCompilationService()
        observer = Mock()
        service.add_observer(observer)
        
        file_path = Path("test.unknown")
        result = await service.compile_file(file_path)
        
        assert result.file_path == file_path
        assert result.status == CompilationStatus.FAILED
        assert "Unsupported file type" in result.error_output
        
        # Verify observer was called
        observer.on_compilation_started.assert_called_once_with("test.unknown")
        observer.on_compilation_finished.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('py_compile.compile')
    async def test_compile_python_file_success(self, mock_compile):
        """Test successful Python file validation"""
        service = BasicCompilationService()
        observer = Mock()
        service.add_observer(observer)
        
        file_path = Path("test.py")
        mock_compile.return_value = None  # py_compile.compile returns None on success
        
        result = await service.compile_file(file_path)
        
        assert result.file_path == file_path
        assert result.status == CompilationStatus.SUCCESS
        assert "validation passed" in result.output.lower()
        assert result.executable_path == file_path
        
        # Verify py_compile was called
        mock_compile.assert_called_once_with(str(file_path), doraise=True)
        
        # Verify observer notifications
        observer.on_compilation_started.assert_called_once_with("test.py")
        observer.on_compilation_finished.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('py_compile.compile')
    async def test_compile_python_file_failure(self, mock_compile):
        """Test Python file validation failure"""
        import py_compile
        
        service = BasicCompilationService()
        file_path = Path("test.py")
        
        # Mock compilation error
        mock_compile.side_effect = py_compile.PyCompileError("Syntax error")
        
        result = await service.compile_file(file_path)
        
        assert result.status == CompilationStatus.FAILED
        assert "Syntax error" in result.error_output
    
    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    async def test_compile_cpp_file_success(self, mock_subprocess):
        """Test successful C++ compilation"""
        service = BasicCompilationService()
        file_path = Path("test.cpp")
        
        # Mock successful subprocess
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b"Success", b""))
        mock_subprocess.return_value = mock_process
        
        result = await service.compile_file(file_path)
        
        assert result.status == CompilationStatus.SUCCESS
        assert result.output == "Success"
        assert result.executable_path == Path("test.exe")
        
        # Verify subprocess was called correctly
        mock_subprocess.assert_called_once_with(
            'g++', str(file_path), '-o', str(Path("test.exe")),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    
    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    async def test_compile_cpp_file_failure(self, mock_subprocess):
        """Test C++ compilation failure"""
        service = BasicCompilationService()
        file_path = Path("test.cpp")
        
        # Mock failed subprocess
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.communicate = AsyncMock(return_value=(b"", b"Compilation error"))
        mock_subprocess.return_value = mock_process
        
        result = await service.compile_file(file_path)
        
        assert result.status == CompilationStatus.FAILED
        assert result.error_output == "Compilation error"
    
    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    async def test_compile_cpp_compiler_not_found(self, mock_subprocess):
        """Test C++ compilation when g++ is not found"""
        service = BasicCompilationService()
        file_path = Path("test.cpp")
        
        # Mock FileNotFoundError (g++ not found)
        mock_subprocess.side_effect = FileNotFoundError()
        
        result = await service.compile_file(file_path)
        
        assert result.status == CompilationStatus.FAILED
        assert "g++ compiler not found" in result.error_output
    
    @pytest.mark.asyncio
    async def test_compile_files_multiple(self):
        """Test compiling multiple files"""
        service = BasicCompilationService()
        observer = Mock()
        service.add_observer(observer)
        
        file_paths = [Path("test1.unknown"), Path("test2.unknown")]
        results = []
        
        async for result in service.compile_files(file_paths):
            results.append(result)
        
        assert len(results) == 2
        assert all(r.status == CompilationStatus.FAILED for r in results)
        
        # Verify final notification
        observer.on_all_compilations_finished.assert_called_once_with(False, "Compiled 0/2 files successfully")
    
    def test_cancel_compilation(self):
        """Test compilation cancellation"""
        service = BasicCompilationService()
        
        service.cancel_compilation()
        assert service._is_cancelled is True
