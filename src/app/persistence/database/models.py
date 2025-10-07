"""
Database models and data classes.

Migrated from database_manager.py during Phase 1 refactoring.
All dataclasses remain unchanged to maintain backward compatibility.
"""
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class FilesSnapshot:
    """
    Data class for code files snapshot with full metadata.
    
    New structure stores files with extensions and per-file language information.
    Supports multi-language projects and filters files by test type.
    
    Structure:
        files: {
            "generator.py": {
                "content": "import random...",
                "language": "py",
                "role": "generator"
            },
            "correct.cpp": {
                "content": "#include <iostream>...",
                "language": "cpp",
                "role": "correct"
            }
        }
    """
    files: Dict[str, Dict[str, str]] = field(default_factory=dict)
    test_type: str = ""  # 'comparison', 'validation', 'benchmark'
    primary_language: str = "cpp"  # Most common language in files
    
    def to_json(self) -> str:
        """
        Serialize FilesSnapshot to JSON string with new structure.
        
        Returns:
            str: JSON representation with files dict containing metadata
        """
        return json.dumps({
            'files': self.files,
            'test_type': self.test_type,
            'primary_language': self.primary_language
        }, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'FilesSnapshot':
        """
        Deserialize FilesSnapshot from JSON string with backward compatibility.
        
        Supports both NEW format (with 'files' dict) and OLD format (generator_code, etc).
        Automatically migrates old format to new structure.
        
        Args:
            json_str: JSON string to deserialize
            
        Returns:
            FilesSnapshot: Deserialized snapshot instance
        """
        if not json_str or json_str == "":
            return cls()
        
        try:
            data = json.loads(json_str)
            
            # NEW FORMAT: Has 'files' key
            if 'files' in data:
                return cls(
                    files=data.get('files', {}),
                    test_type=data.get('test_type', ''),
                    primary_language=data.get('primary_language', 'cpp')
                )
            
            # OLD FORMAT: Has generator_code, correct_code, etc - migrate it
            else:
                logger.info("Migrating old FilesSnapshot format to new structure")
                return cls._migrate_old_format(data)
                
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Error deserializing FilesSnapshot: {e}")
            return cls()
    
    @classmethod
    def _migrate_old_format(cls, old_data: dict) -> 'FilesSnapshot':
        """
        Convert old FilesSnapshot format to new format.
        
        Old format: {generator_code: "...", correct_code: "...", ...}
        New format: {files: {"generator.cpp": {content, language, role}, ...}}
        
        Args:
            old_data: Dictionary with old format keys
            
        Returns:
            FilesSnapshot: New format instance
        """
        new_snapshot = cls()
        
        # Map old keys to (base_name, role)
        role_map = {
            'generator_code': ('generator', 'generator'),
            'correct_code': ('correct', 'correct'),
            'test_code': ('test', 'test'),
            'validator_code': ('validator', 'validator')
        }
        
        for old_key, (base_name, role) in role_map.items():
            content = old_data.get(old_key, '')
            if content:
                # Detect language from content
                lang = cls._detect_language_from_content(content)
                
                # Generate filename with proper capitalization for Java
                filename = cls._generate_filename(base_name, lang)
                
                new_snapshot.files[filename] = {
                    'content': content,
                    'language': lang,
                    'role': role
                }
                
                # Set primary language from first main file
                if not new_snapshot.primary_language or new_snapshot.primary_language == 'cpp':
                    new_snapshot.primary_language = lang
        
        # Handle additional_files
        for filename, content in old_data.get('additional_files', {}).items():
            if filename not in new_snapshot.files:
                lang = cls._detect_language_from_extension(filename)
                new_snapshot.files[filename] = {
                    'content': content,
                    'language': lang,
                    'role': 'additional'
                }
        
        logger.info(f"Migrated old format: {len(new_snapshot.files)} files converted")
        return new_snapshot
    
    @staticmethod
    def _generate_filename(base_name: str, language: str) -> str:
        """Generate filename with proper extension and capitalization"""
        ext_map = {'cpp': '.cpp', 'py': '.py', 'java': '.java'}
        ext = ext_map.get(language, '.cpp')
        
        if language == 'java':
            # Java files need capitalization
            if base_name == 'generator':
                return 'Generator.java'
            elif base_name == 'correct':
                return 'Correct.java'
            elif base_name == 'test':
                return 'Test.java'
            elif base_name == 'validator':
                return 'Validator.java'
        
        return base_name + ext
    
    @staticmethod
    def _detect_language_from_content(content: str) -> str:
        """
        Detect programming language from code content.
        
        Looks for language-specific patterns in the code.
        
        Args:
            content: Source code content
            
        Returns:
            str: Language code ('cpp', 'py', 'java')
        """
        if 'import java' in content or 'public class' in content or 'System.out' in content:
            return 'java'
        elif 'def ' in content or 'import ' in content or 'print(' in content:
            return 'py'
        else:
            return 'cpp'
    
    @staticmethod
    def _detect_language_from_extension(filename: str) -> str:
        """
        Detect programming language from file extension.
        
        Args:
            filename: File name with extension
            
        Returns:
            str: Language code ('cpp', 'py', 'java')
        """
        if filename.endswith('.py'):
            return 'py'
        elif filename.endswith('.java'):
            return 'java'
        else:
            return 'cpp'


@dataclass
class TestResult:
    """Data class for test results"""
    id: Optional[int] = None
    test_type: str = ""  # 'stress' or 'benchmark'
    file_path: str = ""
    test_count: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    total_time: float = 0.0
    timestamp: str = ""
    test_details: str = ""  # JSON string of detailed results
    project_name: str = ""
    files_snapshot: str = ""  # JSON string of all file contents
    mismatch_analysis: str = ""  # JSON string of detailed mismatch analysis


@dataclass
class Session:
    """Data class for editor sessions"""
    id: Optional[int] = None
    session_name: str = ""
    open_files: str = ""  # JSON string of file paths
    active_file: str = ""
    timestamp: str = ""
    project_name: str = ""


@dataclass
class ProjectData:
    """Data class for project information"""
    id: Optional[int] = None
    project_name: str = ""
    project_path: str = ""
    last_accessed: str = ""
    file_count: int = 0
    total_lines: int = 0
    languages: str = ""  # JSON string of languages used
