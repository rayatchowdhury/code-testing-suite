"""
Test suite for FilesSnapshot redesign with file extensions and metadata.

Tests the new structure that stores files with full metadata including:
- Filenames with extensions
- Per-file language information
- File roles (generator/correct/test/validator/additional)
- Backward compatibility with old format
"""

import pytest
import json
from src.app.persistence.database.database_manager import FilesSnapshot


class TestNewFilesSnapshotStructure:
    """Test new FilesSnapshot with files dict and metadata"""
    
    def test_create_empty_snapshot(self):
        """Test creating empty snapshot with defaults"""
        snapshot = FilesSnapshot()
        
        assert snapshot.files == {}
        assert snapshot.test_type == ""
        assert snapshot.primary_language == "cpp"
    
    def test_create_snapshot_with_files(self):
        """Test creating snapshot with file data"""
        snapshot = FilesSnapshot(
            files={
                "generator.py": {
                    "content": "import random\nprint('test')",
                    "language": "py",
                    "role": "generator"
                },
                "test.cpp": {
                    "content": "#include <iostream>\nint main() {}",
                    "language": "cpp",
                    "role": "test"
                }
            },
            test_type="comparison",
            primary_language="py"
        )
        
        assert len(snapshot.files) == 2
        assert "generator.py" in snapshot.files
        assert "test.cpp" in snapshot.files
        assert snapshot.test_type == "comparison"
        assert snapshot.primary_language == "py"
    
    def test_serialize_new_format(self):
        """Test to_json() with new structure"""
        snapshot = FilesSnapshot(
            files={
                "generator.cpp": {
                    "content": "int main() { return 0; }",
                    "language": "cpp",
                    "role": "generator"
                }
            },
            test_type="benchmark",
            primary_language="cpp"
        )
        
        json_str = snapshot.to_json()
        data = json.loads(json_str)
        
        assert "files" in data
        assert "test_type" in data
        assert "primary_language" in data
        assert "generator.cpp" in data["files"]
        assert data["files"]["generator.cpp"]["language"] == "cpp"
        assert data["test_type"] == "benchmark"
    
    def test_deserialize_new_format(self):
        """Test from_json() with new format"""
        json_data = {
            "files": {
                "generator.py": {
                    "content": "print('hello')",
                    "language": "py",
                    "role": "generator"
                },
                "correct.java": {
                    "content": "public class Correct {}",
                    "language": "java",
                    "role": "correct"
                }
            },
            "test_type": "validation",
            "primary_language": "java"
        }
        
        snapshot = FilesSnapshot.from_json(json.dumps(json_data))
        
        assert len(snapshot.files) == 2
        assert "generator.py" in snapshot.files
        assert "correct.java" in snapshot.files
        assert snapshot.files["generator.py"]["language"] == "py"
        assert snapshot.files["correct.java"]["language"] == "java"
        assert snapshot.test_type == "validation"
        assert snapshot.primary_language == "java"
    
    def test_empty_json_string(self):
        """Test handling empty JSON string"""
        snapshot = FilesSnapshot.from_json("")
        assert snapshot.files == {}
        
        snapshot = FilesSnapshot.from_json(None)
        assert snapshot.files == {}


class TestOldFormatMigration:
    """Test backward compatibility with old FilesSnapshot format"""
    
    def test_migrate_old_format_cpp(self):
        """Test migrating old format with C++ code"""
        old_data = {
            "generator_code": "#include <iostream>\nint main() {}",
            "correct_code": "#include <iostream>\nint solve() {}",
            "test_code": "#include <iostream>\nvoid test() {}",
            "validator_code": "",
            "additional_files": {}
        }
        
        snapshot = FilesSnapshot.from_json(json.dumps(old_data))
        
        # Should convert to new format with .cpp extensions
        assert "generator.cpp" in snapshot.files
        assert "correct.cpp" in snapshot.files
        assert "test.cpp" in snapshot.files
        assert "validator.cpp" not in snapshot.files  # Empty, shouldn't be added
        
        # Check content preserved
        assert snapshot.files["generator.cpp"]["content"] == old_data["generator_code"]
        assert snapshot.files["generator.cpp"]["language"] == "cpp"
        assert snapshot.files["generator.cpp"]["role"] == "generator"
    
    def test_migrate_old_format_python(self):
        """Test migrating old format with Python code"""
        old_data = {
            "generator_code": "import random\ndef generate():\n    pass",
            "correct_code": "def solve():\n    pass",
            "test_code": "def test():\n    pass",
            "validator_code": "",
            "additional_files": {}
        }
        
        snapshot = FilesSnapshot.from_json(json.dumps(old_data))
        
        # Should detect Python and use .py extensions
        assert "generator.py" in snapshot.files
        assert "correct.py" in snapshot.files
        assert "test.py" in snapshot.files
        
        assert snapshot.files["generator.py"]["language"] == "py"
        assert snapshot.primary_language == "py"
    
    def test_migrate_old_format_java(self):
        """Test migrating old format with Java code"""
        old_data = {
            "generator_code": "public class Generator {\n    public static void main(String[] args) {}\n}",
            "correct_code": "public class Correct {}",
            "test_code": "import java.util.*;\npublic class Test {}",
            "validator_code": "",
            "additional_files": {}
        }
        
        snapshot = FilesSnapshot.from_json(json.dumps(old_data))
        
        # Should detect Java and use proper capitalization
        assert "Generator.java" in snapshot.files
        assert "Correct.java" in snapshot.files
        assert "Test.java" in snapshot.files
        
        assert snapshot.files["Generator.java"]["language"] == "java"
        assert snapshot.primary_language == "java"
    
    def test_migrate_with_additional_files(self):
        """Test migrating old format with additional files"""
        old_data = {
            "generator_code": "int main() {}",
            "correct_code": "",
            "test_code": "void test() {}",
            "validator_code": "",
            "additional_files": {
                "helper.cpp": "#include <helper.h>",
                "utils.py": "def helper(): pass"
            }
        }
        
        snapshot = FilesSnapshot.from_json(json.dumps(old_data))
        
        # Main files
        assert "generator.cpp" in snapshot.files
        assert "test.cpp" in snapshot.files
        assert "correct.cpp" not in snapshot.files  # Empty
        
        # Additional files
        assert "helper.cpp" in snapshot.files
        assert "utils.py" in snapshot.files
        assert snapshot.files["helper.cpp"]["role"] == "additional"
        assert snapshot.files["utils.py"]["language"] == "py"
    
    def test_migrate_validator_code(self):
        """Test migrating old format with validator"""
        old_data = {
            "generator_code": "def gen(): pass",
            "correct_code": "",
            "test_code": "def test(): pass",
            "validator_code": "def validate(): pass",
            "additional_files": {}
        }
        
        snapshot = FilesSnapshot.from_json(json.dumps(old_data))
        
        assert "generator.py" in snapshot.files
        assert "test.py" in snapshot.files
        assert "validator.py" in snapshot.files
        assert "correct.py" not in snapshot.files


class TestLanguageDetection:
    """Test language detection from content and extensions"""
    
    def test_detect_cpp_from_content(self):
        """Test C++ detection"""
        lang = FilesSnapshot._detect_language_from_content("#include <iostream>\nint main() {}")
        assert lang == "cpp"
        
        lang = FilesSnapshot._detect_language_from_content("std::cout << 'hello';")
        assert lang == "cpp"
    
    def test_detect_python_from_content(self):
        """Test Python detection"""
        lang = FilesSnapshot._detect_language_from_content("import random\ndef test(): pass")
        assert lang == "py"
        
        lang = FilesSnapshot._detect_language_from_content("print('hello world')")
        assert lang == "py"
    
    def test_detect_java_from_content(self):
        """Test Java detection"""
        lang = FilesSnapshot._detect_language_from_content("public class Test {}")
        assert lang == "java"
        
        lang = FilesSnapshot._detect_language_from_content("import java.util.*;\nSystem.out.println();")
        assert lang == "java"
    
    def test_detect_from_extension(self):
        """Test language detection from file extension"""
        assert FilesSnapshot._detect_language_from_extension("test.py") == "py"
        assert FilesSnapshot._detect_language_from_extension("Test.java") == "java"
        assert FilesSnapshot._detect_language_from_extension("test.cpp") == "cpp"
        assert FilesSnapshot._detect_language_from_extension("test.h") == "cpp"


class TestFilenameGeneration:
    """Test filename generation with proper extensions and capitalization"""
    
    def test_generate_cpp_filenames(self):
        """Test C++ filename generation"""
        assert FilesSnapshot._generate_filename("generator", "cpp") == "generator.cpp"
        assert FilesSnapshot._generate_filename("correct", "cpp") == "correct.cpp"
        assert FilesSnapshot._generate_filename("test", "cpp") == "test.cpp"
        assert FilesSnapshot._generate_filename("validator", "cpp") == "validator.cpp"
    
    def test_generate_python_filenames(self):
        """Test Python filename generation"""
        assert FilesSnapshot._generate_filename("generator", "py") == "generator.py"
        assert FilesSnapshot._generate_filename("correct", "py") == "correct.py"
        assert FilesSnapshot._generate_filename("test", "py") == "test.py"
        assert FilesSnapshot._generate_filename("validator", "py") == "validator.py"
    
    def test_generate_java_filenames(self):
        """Test Java filename generation with capitalization"""
        assert FilesSnapshot._generate_filename("generator", "java") == "Generator.java"
        assert FilesSnapshot._generate_filename("correct", "java") == "Correct.java"
        assert FilesSnapshot._generate_filename("test", "java") == "Test.java"
        assert FilesSnapshot._generate_filename("validator", "java") == "Validator.java"


class TestMixedLanguageSupport:
    """Test support for projects with multiple languages"""
    
    def test_mixed_language_snapshot(self):
        """Test snapshot with different languages per file"""
        snapshot = FilesSnapshot(
            files={
                "generator.py": {
                    "content": "import random",
                    "language": "py",
                    "role": "generator"
                },
                "correct.cpp": {
                    "content": "#include <iostream>",
                    "language": "cpp",
                    "role": "correct"
                },
                "Test.java": {
                    "content": "public class Test {}",
                    "language": "java",
                    "role": "test"
                }
            },
            test_type="comparison",
            primary_language="py"
        )
        
        # Verify each file has correct language
        assert snapshot.files["generator.py"]["language"] == "py"
        assert snapshot.files["correct.cpp"]["language"] == "cpp"
        assert snapshot.files["Test.java"]["language"] == "java"
        
        # Serialize and deserialize
        json_str = snapshot.to_json()
        restored = FilesSnapshot.from_json(json_str)
        
        # Verify all languages preserved
        assert restored.files["generator.py"]["language"] == "py"
        assert restored.files["correct.cpp"]["language"] == "cpp"
        assert restored.files["Test.java"]["language"] == "java"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
