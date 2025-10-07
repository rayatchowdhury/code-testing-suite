# FilesSnapshot Redesign - Comprehensive Plan

## 📋 Current Problems

### 1. **No File Extension Information**
Current structure:
```json
{
  "generator_code": "content...",
  "correct_code": "content...",
  "test_code": "content...",
  "validator_code": "content...",
  "additional_files": {}
}
```

**Problem**: We don't know if it's `.cpp`, `.py`, or `.java`!

### 2. **All Files Saved Regardless of Test Type**
- Benchmarker saves `correct_code` and `validator_code` (WRONG!)
- Wastes storage space
- Creates confusion

### 3. **Multi-Language Not Properly Supported**
- Can't have `generator.py` + `test.cpp` + `correct.java`
- Single language detection guesses from content
- User can't see which files are which language

## ✅ Correct File Requirements per Test Type

### **Comparator** (3 files):
- `generator.*` (cpp/py/java)
- `correct.*` (cpp/py/java) 
- `test.*` (cpp/py/java)

### **Validator** (3 files):
- `generator.*` (cpp/py/java)
- `validator.*` (cpp/py/java)
- `test.*` (cpp/py/java)

### **Benchmarker** (2 files):
- `generator.*` (cpp/py/java)
- `test.*` (cpp/py/java)

## 🎯 New FilesSnapshot Structure

### **Design A: File-Centric with Metadata** (RECOMMENDED)
```json
{
  "files": {
    "generator.py": {
      "content": "import random\n...",
      "language": "py",
      "role": "generator"
    },
    "correct.cpp": {
      "content": "#include <iostream>\n...",
      "language": "cpp",
      "role": "correct"
    },
    "test.java": {
      "content": "public class Test {\n...",
      "language": "java",
      "role": "test"
    },
    "helper.cpp": {
      "content": "// Helper functions\n...",
      "language": "cpp",
      "role": "additional"
    }
  },
  "test_type": "comparison",
  "primary_language": "cpp"
}
```

**Benefits**:
- ✅ Filename with extension stored
- ✅ Per-file language info
- ✅ Clear role assignment
- ✅ Supports mixed languages
- ✅ Includes additional files naturally
- ✅ Easy to filter by test_type
- ✅ Easy to write back to workspace

### **Design B: Hybrid (Backward Compatible)** (FALLBACK)
```json
{
  "generator_code": "content...",
  "generator_file": "generator.py",
  "generator_language": "py",
  "correct_code": "content...",
  "correct_file": "correct.cpp",
  "correct_language": "cpp",
  "test_code": "content...",
  "test_file": "test.cpp",
  "test_language": "cpp",
  "validator_code": "",
  "validator_file": "",
  "validator_language": "",
  "additional_files": {
    "helper.cpp": "content..."
  }
}
```

**Trade-offs**:
- ✅ Easier migration from old format
- ✅ Backward compatible field names
- ❌ More verbose
- ❌ Still has empty fields for benchmarker

## 📐 Implementation Plan

### **Phase 1: Update Data Structure** ✅ Design A

```python
@dataclass
class FilesSnapshot:
    """Data class for code files snapshot with full metadata"""
    files: Dict[str, Dict[str, str]] = field(default_factory=dict)
    test_type: str = ""
    primary_language: str = "cpp"
    
    # Structure of files dict:
    # {
    #   "filename.ext": {
    #       "content": "file content...",
    #       "language": "cpp/py/java",
    #       "role": "generator/correct/test/validator/additional"
    #   }
    # }
    
    def to_json(self) -> str:
        """Serialize with new structure"""
        return json.dumps({
            'files': self.files,
            'test_type': self.test_type,
            'primary_language': self.primary_language
        }, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'FilesSnapshot':
        """Deserialize with backward compatibility"""
        if not json_str:
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
            
            # OLD FORMAT: Has generator_code, correct_code, etc
            else:
                # Convert old format to new format
                return cls._migrate_old_format(data)
        
        except Exception as e:
            logger.error(f"Error deserializing FilesSnapshot: {e}")
            return cls()
    
    @classmethod
    def _migrate_old_format(cls, old_data: dict) -> 'FilesSnapshot':
        """Convert old format to new format"""
        new_snapshot = cls()
        
        # Map old keys to roles
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
                ext = {'cpp': '.cpp', 'py': '.py', 'java': '.java'}[lang]
                
                # Handle Java capitalization
                if lang == 'java':
                    filename = base_name.capitalize() + ext if base_name != 'correct' else 'Correct' + ext
                else:
                    filename = base_name + ext
                
                new_snapshot.files[filename] = {
                    'content': content,
                    'language': lang,
                    'role': role
                }
        
        # Handle additional_files
        for filename, content in old_data.get('additional_files', {}).items():
            if filename not in new_snapshot.files:
                lang = cls._detect_language_from_extension(filename)
                new_snapshot.files[filename] = {
                    'content': content,
                    'language': lang,
                    'role': 'additional'
                }
        
        return new_snapshot
    
    @staticmethod
    def _detect_language_from_content(content: str) -> str:
        """Detect language from code content"""
        if 'import java' in content or 'public class' in content:
            return 'java'
        elif 'def ' in content or 'import ' in content:
            return 'py'
        else:
            return 'cpp'
    
    @staticmethod
    def _detect_language_from_extension(filename: str) -> str:
        """Detect language from file extension"""
        if filename.endswith('.py'):
            return 'py'
        elif filename.endswith('.java'):
            return 'java'
        else:
            return 'cpp'
```

### **Phase 2: Update create_files_snapshot()**

```python
@staticmethod
def create_files_snapshot(workspace_dir: str, test_type: str) -> FilesSnapshot:
    """
    Create a snapshot of relevant files for the test type.
    
    Args:
        workspace_dir: Root workspace directory (~/.code_testing_suite/workspace)
        test_type: 'comparison', 'validation', or 'benchmark'
    
    Returns:
        FilesSnapshot with only relevant files for the test type
    """
    # Map test types to subdirectories
    test_type_map = {
        'comparison': 'comparator',
        'validation': 'validator',
        'benchmark': 'benchmarker'
    }
    
    test_subdir = test_type_map.get(test_type, 'comparator')
    test_type_dir = os.path.join(workspace_dir, test_subdir)
    
    snapshot = FilesSnapshot(test_type=test_type)
    
    # Define which files are needed per test type
    required_files = {
        'comparison': ['generator', 'correct', 'test'],
        'validation': ['generator', 'validator', 'test'],
        'benchmark': ['generator', 'test']
    }
    
    required = required_files.get(test_type, [])
    
    # File role mapping
    role_map = {
        'generator': 'generator',
        'correct': 'correct',
        'test': 'test',
        'validator': 'validator'
    }
    
    try:
        if not os.path.exists(test_type_dir):
            logger.warning(f"Test type directory not found: {test_type_dir}")
            return snapshot
        
        # Read all source files in test type directory
        for filename in os.listdir(test_type_dir):
            filepath = os.path.join(test_type_dir, filename)
            
            # Skip directories (inputs/outputs)
            if os.path.isdir(filepath):
                continue
            
            # Only process source files
            if not filename.endswith(('.cpp', '.h', '.py', '.java')):
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Determine role
                base_name = filename.split('.')[0].lower()
                role = 'additional'
                
                for req in required:
                    if req in base_name:
                        role = role_map[req]
                        break
                
                # Skip files not required for this test type
                if role == 'additional':
                    # Only include if it's truly an additional file
                    if not any(req in base_name for req in ['generator', 'correct', 'test', 'validator']):
                        role = 'additional'
                    else:
                        # It's a main file not needed for this test type, skip it
                        continue
                
                # Detect language from extension
                if filename.endswith('.py'):
                    language = 'py'
                elif filename.endswith('.java'):
                    language = 'java'
                else:
                    language = 'cpp'
                
                # Store file
                snapshot.files[filename] = {
                    'content': content,
                    'language': language,
                    'role': role
                }
                
                # Track primary language (most common)
                if role != 'additional' and not snapshot.primary_language:
                    snapshot.primary_language = language
                
            except Exception as e:
                logger.warning(f"Error reading file {filename}: {e}")
        
        logger.info(f"Created snapshot for {test_type}: {len(snapshot.files)} files")
        return snapshot
        
    except Exception as e:
        logger.error(f"Error creating files snapshot: {e}", exc_info=True)
        return snapshot
```

### **Phase 3: Update Test Runners**

Need to update all places that call `create_files_snapshot()`:
- Comparator runner
- Validator runner  
- Benchmarker runner

Add `test_type` parameter to each call.

### **Phase 4: Simplified Load to Test**

```python
def _load_to_test(self):
    """Load code files back to workspace and open test window"""
    try:
        # Parse files_snapshot
        snapshot = FilesSnapshot.from_json(self.test_result.files_snapshot)
        
        if not snapshot.files:
            QMessageBox.warning(self, "No Files", "No code files to load.")
            return
        
        # Determine test window
        test_type_map = {
            'comparison': 'comparator',
            'validation': 'validator',
            'benchmark': 'benchmarker'
        }
        
        test_subdir = test_type_map.get(snapshot.test_type or self.test_result.test_type.lower())
        window_name = test_subdir
        
        # Get workspace directory
        from src.app.shared.constants.paths import WORKSPACE_DIR
        target_dir = os.path.join(WORKSPACE_DIR, test_subdir)
        
        # Check if files exist and warn about overwrite
        existing_files = []
        for filename in snapshot.files.keys():
            filepath = os.path.join(target_dir, filename)
            if os.path.exists(filepath):
                existing_files.append(filename)
        
        if existing_files:
            reply = QMessageBox.question(
                self,
                "Overwrite Files?",
                f"The following files will be overwritten:\n\n" +
                "\n".join(existing_files) +
                f"\n\nAny unsaved changes in {window_name.title()} window will be lost.\n\n" +
                "Continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # Write files to workspace
        os.makedirs(target_dir, exist_ok=True)
        
        for filename, file_data in snapshot.files.items():
            filepath = os.path.join(target_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(file_data['content'])
        
        # Open test window (it will read files automatically!)
        window_manager = self.parent.window_manager
        window_manager.show_window(window_name)
        
        QMessageBox.information(
            self,
            "Loaded Successfully",
            f"Loaded {len(snapshot.files)} files to {window_name.title()} window.\n\n" +
            f"Files written to: {target_dir}"
        )
        
    except Exception as e:
        QMessageBox.critical(
            self,
            "Load Error",
            f"Failed to load files: {str(e)}"
        )
```

## 🧪 Testing Strategy

### Test 1: New Snapshot Structure
- Create FilesSnapshot with mixed languages
- Serialize to JSON
- Deserialize back
- Verify all data intact

### Test 2: Old Format Migration
- Create old format JSON
- Deserialize with from_json()
- Verify conversion to new format
- Check language detection worked

### Test 3: Test Type Filtering
- Run comparator test → Check only 3 files saved
- Run validator test → Check only 3 files saved
- Run benchmarker test → Check only 2 files saved
- Verify no extra files in snapshot

### Test 4: Mixed Language Support
- Create test with generator.py, correct.cpp, test.java
- Save and retrieve
- Verify each file has correct language
- Load to test and verify files written correctly

### Test 5: Load to Test
- Load old test result
- Verify files written to workspace/{test_type}/
- Check window opens
- Verify window reads files correctly

### Test 6: Export with Extensions
- Export test result
- Check ZIP contains correct filenames (generator.py, test.cpp, etc)
- Verify no generic names like "generator_code"

## 📊 Migration Strategy

### Auto-Migration on Load
When old format detected in `from_json()`:
1. Detect language from content
2. Assign default extension
3. Convert to new structure
4. Log migration for debugging

### Database Update (Optional)
- Could run migration script to update all records
- Or migrate on-demand when loaded
- Keep old format for true backward compat

## ✅ Success Criteria

1. ✅ FilesSnapshot stores filenames with extensions
2. ✅ Per-file language information stored
3. ✅ Only relevant files saved per test type
4. ✅ Benchmarker saves 2 files (generator + test)
5. ✅ Comparator saves 3 files (generator + correct + test)
6. ✅ Validator saves 3 files (generator + validator + test)
7. ✅ Load to Test writes files to workspace
8. ✅ Test windows automatically read files
9. ✅ Multi-language mixing supported
10. ✅ Old format migrates transparently
11. ✅ Export creates properly named files
12. ✅ No complex widget navigation needed

## 🚀 Next Steps

1. Update FilesSnapshot dataclass
2. Test new structure
3. Update create_files_snapshot()
4. Test filtering by test type
5. Update all test runners
6. Test with real tests
7. Implement simple load to test
8. Test loading functionality
9. Update export
10. Test export
11. Full integration testing
12. Documentation
