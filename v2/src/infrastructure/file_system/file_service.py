# TODO: Extract file operations from v1 and improve with proper error handling
"""
File Service - Clean file operations without UI dependencies

This module provides a clean interface for file operations that was previously
mixed with UI concerns in utils/file_operations.py
"""
import os
from pathlib import Path
from typing import Optional, Tuple, NamedTuple
from dataclasses import dataclass

@dataclass
class FileResult:
    """Result of a file operation"""
    success: bool
    error_message: Optional[str] = None
    data: Optional[str] = None

class FileService:
    """
    File operations service without UI dependencies.
    
    ASSUMPTION: This extracts core file operations from v1/utils/file_operations.py
    without the QFileDialog dependencies (those move to presentation layer).
    """
    
    FILE_EXTENSIONS = {
        'cpp': ['.cpp', '.h', '.hpp'],
        'python': ['.py'],
        'java': ['.java']
    }
    
    def save_file(self, filepath: Path, content: str, create_backup: bool = False) -> FileResult:
        """Save content to file with optional backup creation"""
        try:
            filepath = Path(filepath)
            
            # Create backup if requested and file exists
            if create_backup and filepath.exists():
                backup_path = filepath.with_suffix(filepath.suffix + '.bak')
                backup_path.write_text(filepath.read_text(encoding='utf-8'), encoding='utf-8')
            
            # Ensure parent directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            filepath.write_text(content, encoding='utf-8')
            
            return FileResult(success=True)
            
        except Exception as e:
            return FileResult(success=False, error_message=str(e))
    
    def load_file(self, filepath: Path) -> FileResult:
        """Load file content with encoding fallback"""
        try:
            filepath = Path(filepath)
            
            if not filepath.exists():
                return FileResult(success=False, error_message="File not found")
            
            # Try UTF-8 first
            try:
                content = filepath.read_text(encoding='utf-8')
                return FileResult(success=True, data=content)
            except UnicodeDecodeError:
                # Fallback to latin-1
                content = filepath.read_text(encoding='latin-1')
                return FileResult(success=True, data=content)
                
        except Exception as e:
            return FileResult(success=False, error_message=str(e))
    
    def get_file_type(self, filepath: Path) -> Optional[str]:
        """Determine file type based on extension"""
        suffix = Path(filepath).suffix.lower()
        
        for file_type, extensions in self.FILE_EXTENSIONS.items():
            if suffix in extensions:
                return file_type
        return None
    
    def ensure_extension(self, filepath: Path, file_type: str) -> Path:
        """Ensure file has appropriate extension for its type"""
        if file_type not in self.FILE_EXTENSIONS:
            return filepath
            
        current_suffix = filepath.suffix.lower()
        valid_extensions = self.FILE_EXTENSIONS[file_type]
        
        if current_suffix not in valid_extensions:
            # Add default extension for file type
            default_ext = valid_extensions[0]
            return filepath.with_suffix(default_ext)
        
        return filepath
