"""
Unit tests for FileService

Tests the core file operations extracted from v1/utils/file_operations.py
"""
import pytest
from pathlib import Path
from infrastructure.file_system.file_service import FileService, FileResult

class TestFileService:
    """Test file service operations"""
    
    def test_save_file_creates_new_file(self, tmp_path):
        """Test basic file saving functionality"""
        service = FileService()
        file_path = tmp_path / "test.cpp"
        content = "#include <iostream>\nint main() { return 0; }"
        
        result = service.save_file(file_path, content)
        
        assert result.success
        assert result.error_message is None
        assert file_path.exists()
        assert file_path.read_text() == content
    
    def test_save_file_creates_backup_when_requested(self, tmp_path):
        """Test backup creation functionality"""
        service = FileService()
        file_path = tmp_path / "test.cpp"
        original_content = "original content"
        new_content = "new content"
        
        # Create initial file
        file_path.write_text(original_content)
        
        # Save with backup
        result = service.save_file(file_path, new_content, create_backup=True)
        
        assert result.success
        assert file_path.read_text() == new_content
        
        backup_path = file_path.with_suffix(".cpp.bak")
        assert backup_path.exists()
        assert backup_path.read_text() == original_content
    
    def test_save_file_creates_parent_directories(self, tmp_path):
        """Test automatic parent directory creation"""
        service = FileService()
        file_path = tmp_path / "nested" / "dir" / "test.cpp"
        content = "test content"
        
        result = service.save_file(file_path, content)
        
        assert result.success
        assert file_path.exists()
        assert file_path.read_text() == content
    
    def test_load_file_returns_content(self, tmp_path):
        """Test basic file loading"""
        service = FileService()
        file_path = tmp_path / "test.cpp"
        content = "#include <iostream>\nint main() { return 0; }"
        file_path.write_text(content)
        
        result = service.load_file(file_path)
        
        assert result.success
        assert result.data == content
        assert result.error_message is None
    
    def test_load_file_handles_missing_file(self, tmp_path):
        """Test error handling for missing files"""
        service = FileService()
        file_path = tmp_path / "nonexistent.cpp"
        
        result = service.load_file(file_path)
        
        assert not result.success
        assert result.error_message == "File not found"
        assert result.data is None
    
    def test_get_file_type_identifies_cpp(self):
        """Test file type detection for C++ files"""
        service = FileService()
        
        assert service.get_file_type(Path("test.cpp")) == "cpp"
        assert service.get_file_type(Path("test.h")) == "cpp"
        assert service.get_file_type(Path("test.hpp")) == "cpp"
    
    def test_get_file_type_identifies_python(self):
        """Test file type detection for Python files"""
        service = FileService()
        
        assert service.get_file_type(Path("test.py")) == "python"
    
    def test_get_file_type_identifies_java(self):
        """Test file type detection for Java files"""
        service = FileService()
        
        assert service.get_file_type(Path("test.java")) == "java"
    
    def test_get_file_type_returns_none_for_unknown(self):
        """Test unknown file type handling"""
        service = FileService()
        
        assert service.get_file_type(Path("test.txt")) is None
        assert service.get_file_type(Path("test.unknown")) is None
    
    def test_ensure_extension_adds_missing_extension(self):
        """Test automatic extension addition"""
        service = FileService()
        
        result = service.ensure_extension(Path("test"), "cpp")
        assert result == Path("test.cpp")
    
    def test_ensure_extension_keeps_valid_extension(self):
        """Test that valid extensions are preserved"""
        service = FileService()
        
        result = service.ensure_extension(Path("test.cpp"), "cpp")
        assert result == Path("test.cpp")
        
        result = service.ensure_extension(Path("test.h"), "cpp")
        assert result == Path("test.h")
