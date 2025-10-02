# Workspace Restructuring Plan

**Date**: October 2, 2025  
**Priority**: HIGH - Critical for project organization  
**Estimated Time**: ~10-12 hours total

## Problem Statement

Currently, all workspace files are dumped into a flat structure in the workspace directory:
```
workspace/
├── generator.cpp
├── correct.cpp
├── test.cpp
├── validator.cpp
├── input.txt
├── output.txt
├── input_1.txt
├── output_1.txt
└── ...
```

**Issues:**
1. ❌ No organization by test type (comparator vs validator vs benchmarker)
2. ❌ Source files mixed with I/O files
3. ❌ Difficult to identify which files belong to which testing mode
4. ❌ Confusing when switching between different test types
5. ❌ Hard to clean up or archive specific test sessions

## Proposed Structure

Organize workspace into test-type subdirectories with separate inputs/outputs:

```
workspace/
├── comparator/
│   ├── generator.cpp      (or .py, .java)
│   ├── correct.cpp
│   ├── test.cpp
│   ├── inputs/
│   │   ├── input_1.txt
│   │   ├── input_2.txt
│   │   └── ...
│   └── outputs/
│       ├── test_output_1.txt
│       ├── correct_output_1.txt
│       └── ...
│
├── validator/
│   ├── generator.py
│   ├── test.java
│   ├── validator.cpp
│   ├── inputs/
│   │   └── ...
│   └── outputs/
│       └── ...
│
└── benchmarker/
    ├── generator.cpp
    ├── test.cpp
    ├── inputs/
    │   └── ...
    └── outputs/
        └── ...
```

**Benefits:**
- ✅ Clear separation by test type
- ✅ Source files separated from I/O files
- ✅ Easy to find and manage files for each test mode
- ✅ Supports multi-language testing better
- ✅ Cleaner workspace organization
- ✅ Easier to archive/export specific test sessions

## Current File Locations

### Source Files
| File | Current Location | New Location | Used By |
|------|-----------------|--------------|---------|
| generator.cpp/py/java | `workspace/` | `workspace/{test_type}/` | All test modes |
| correct.cpp/py/java | `workspace/` | `workspace/comparator/` | Comparator only |
| test.cpp/py/java | `workspace/` | `workspace/{test_type}/` | All test modes |
| validator.cpp/py/java | `workspace/` | `workspace/validator/` | Validator only |

### Input/Output Files
| File Pattern | Current Location | New Location | Created By |
|--------------|-----------------|--------------|------------|
| input.txt | `workspace/` | `workspace/{test_type}/inputs/` | Generator |
| output.txt | `workspace/` | `workspace/{test_type}/outputs/` | Test/Correct |
| input_N.txt | `workspace/` | `workspace/{test_type}/inputs/` | Benchmarker |
| output_N.txt | `workspace/` | `workspace/{test_type}/outputs/` | Benchmarker |

### Executables
| File | Current Location | New Location |
|------|-----------------|--------------|
| generator.exe/.class | `workspace/` | `workspace/{test_type}/` |
| correct.exe/.class | `workspace/` | `workspace/comparator/` |
| test.exe/.class | `workspace/` | `workspace/{test_type}/` |
| validator.exe/.class | `workspace/` | `workspace/validator/` |

## Implementation Plan (12 Steps)

### Phase 1: Foundation (2-3 hours)

#### ✅ Step 1: Analyze Current File Organization (30 min) [IN PROGRESS]
**Status**: Documentation complete  
**Files to review**:
- ✅ `editor.py` - file button handling
- ✅ `test_tab_widget.py` - tab-based file creation
- ✅ `comparison_test_worker.py` - test execution
- ✅ `benchmark_status_window.py` - I/O file display

**Key Findings**:
- Files created in flat workspace directory
- File paths hardcoded with `os.path.join(workspace_dir, filename)`
- No test_type awareness in path construction
- Input/output files created directly in workspace root

#### Step 2: Create Workspace Structure Constants (45 min)
**File**: `src/app/shared/constants/paths.py`

**Add constants**:
```python
# Workspace subdirectories by test type
WORKSPACE_COMPARATOR_SUBDIR = "comparator"
WORKSPACE_VALIDATOR_SUBDIR = "validator"
WORKSPACE_BENCHMARKER_SUBDIR = "benchmarker"

# I/O subdirectories
WORKSPACE_INPUTS_SUBDIR = "inputs"
WORKSPACE_OUTPUTS_SUBDIR = "outputs"
```

**Add helper functions**:
```python
def get_test_type_dir(workspace_dir: str, test_type: str) -> str:
    """Get directory for specific test type (comparator/validator/benchmarker)."""
    
def get_inputs_dir(workspace_dir: str, test_type: str) -> str:
    """Get inputs directory for specific test type."""
    
def get_outputs_dir(workspace_dir: str, test_type: str) -> str:
    """Get outputs directory for specific test type."""
    
def get_source_file_path(workspace_dir: str, test_type: str, 
                         role: str, language: str) -> str:
    """Get path for source file (generator/correct/test/validator)."""
```

#### Step 3: Create Directory Initialization Utility (1 hour)
**New File**: `src/app/shared/utils/workspace_utils.py`

**Functions to implement**:
```python
def ensure_workspace_structure(workspace_dir: str) -> None:
    """
    Create complete workspace directory structure.
    
    Creates:
    - workspace/comparator/
    - workspace/comparator/inputs/
    - workspace/comparator/outputs/
    - workspace/validator/
    - workspace/validator/inputs/
    - workspace/validator/outputs/
    - workspace/benchmarker/
    - workspace/benchmarker/inputs/
    - workspace/benchmarker/outputs/
    """

def get_test_type_from_path(file_path: str) -> Optional[str]:
    """Extract test type from file path."""
    
def migrate_flat_to_nested(workspace_dir: str) -> bool:
    """Migrate old flat structure to new nested structure."""
```

**Integration Points**:
- Call `ensure_workspace_structure()` on app startup
- Call on workspace directory change in config dialog
- Call before any file operations

#### Step 4: Create File Constants Module (45 min)
**New File**: `src/app/shared/constants/file_constants.py`

```python
from typing import Dict, List

# File roles for each test type
TEST_TYPE_FILES: Dict[str, List[str]] = {
    'comparison': ['generator', 'correct', 'test'],
    'comparator': ['generator', 'correct', 'test'],  # Alias
    'validator': ['generator', 'test', 'validator'],
    'benchmark': ['generator', 'test'],
    'benchmarker': ['generator', 'test'],  # Alias
}

# Language file extensions
LANGUAGE_EXTENSIONS: Dict[str, str] = {
    'cpp': '.cpp',
    'py': '.py',
    'java': '.java',
}

# Executable extensions by platform and language
EXECUTABLE_EXTENSIONS: Dict[str, str] = {
    'cpp': '.exe',  # Windows
    'py': '.py',    # Interpreted
    'java': '.class',  # Bytecode
}

def get_source_filename(role: str, language: str) -> str:
    """Get source filename for role and language."""
    
def get_executable_name(role: str, language: str) -> str:
    """Get executable/bytecode name for role and language."""
```

### Phase 2: Core Path Updates (3-4 hours)

#### Step 5: Update test_tab_widget.py (1 hour)
**File**: `src/app/presentation/widgets/display_area_widgets/test_tab_widget.py`

**Changes needed**:
```python
# Line ~461: _get_current_file_path()
# OLD:
return os.path.join(self.workspace_dir, file_name)

# NEW:
from src.app.shared.constants.paths import get_source_file_path
return get_source_file_path(self.workspace_dir, self.test_type, 
                            self.tab_role, language)

# Line ~569: _handle_tab_click()
# Ensure directories exist before file creation
file_dir = os.path.dirname(file_path)
os.makedirs(file_dir, exist_ok=True)
```

**Add to __init__**:
```python
self.test_type = test_type  # Pass from parent window
self.tab_role_map = {  # Map tab names to roles
    'Generator': 'generator',
    'Correct Code': 'correct',
    'Test Code': 'test',
    'Validator': 'validator'
}
```

#### Step 6: Update editor.py File Button Handling (1 hour)
**File**: `src/app/presentation/widgets/display_area_widgets/editor.py`

**Changes needed**:
```python
# Line ~686: _handle_file_button()
def _handle_file_button(self, button_name):
    # ... existing button state code ...
    
    # Determine test type from context (comparator is default)
    test_type = 'comparator'  # Could be passed from parent
    
    role_map = {
        'Generator': 'generator',
        'Correct Code': 'correct',
        'Test Code': 'test'
    }
    role = role_map[button_name]
    
    # Get file path using helper
    from src.app.shared.constants.paths import get_source_file_path
    file_path = get_source_file_path(
        self.workspace_dir, 
        test_type, 
        role, 
        'cpp'  # Default to cpp, determine from config
    )
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # ... rest of existing code ...
```

#### Step 7: Update Base Compiler and Runner Classes (1.5 hours)
**Files**: 
- `src/app/core/tools/base/base_compiler.py`
- `src/app/core/tools/base/base_runner.py`

**base_compiler.py changes**:
```python
# Line ~44: __init__
def __init__(self, workspace_dir: str, files_dict: Dict[str, str], 
             config: Optional[Dict] = None, test_type: str = 'comparison'):
    """
    Args:
        workspace_dir: Root workspace directory
        files_dict: Map of role -> file path (can be relative or absolute)
        config: Configuration dictionary
        test_type: Type of test (comparison/validator/benchmark)
    """
    self.workspace_dir = workspace_dir
    self.test_type = test_type
    
    # Resolve relative paths to nested structure
    self.files = self._resolve_file_paths(files_dict)
    
def _resolve_file_paths(self, files_dict: Dict[str, str]) -> Dict[str, str]:
    """Resolve relative paths within test type directory."""
    from src.app.shared.constants.paths import get_test_type_dir
    
    resolved = {}
    test_dir = get_test_type_dir(self.workspace_dir, self.test_type)
    
    for role, path in files_dict.items():
        if os.path.isabs(path):
            resolved[role] = path
        else:
            # If just filename, put in test type directory
            resolved[role] = os.path.join(test_dir, path)
    
    return resolved
```

**base_runner.py changes**:
```python
# Similar test_type parameter addition
# Update get_workspace_files() to search in test_type subdirectory
```

#### Step 8: Update Comparator, Validator, Benchmarker Tools (1 hour)
**Files**:
- `src/app/core/tools/comparator.py`
- `src/app/core/tools/validator.py`
- `src/app/core/tools/benchmarker.py`

**comparator.py changes**:
```python
# Line ~30-48: __init__
def __init__(self, workspace_dir, files=None, config=None):
    from src.app.shared.constants.paths import get_test_type_dir
    
    if files is None:
        test_dir = get_test_type_dir(workspace_dir, 'comparator')
        files = {
            'generator': os.path.join(test_dir, 'generator.cpp'),
            'correct': os.path.join(test_dir, 'correct.cpp'),
            'test': os.path.join(test_dir, 'test.cpp')
        }
    
    # Pass test_type to base class
    super().__init__(workspace_dir, files, test_type='comparison', config=config)
```

**validator.py changes**:
```python
# Similar pattern, use 'validator' test type
test_dir = get_test_type_dir(workspace_dir, 'validator')
files = {
    'generator': os.path.join(test_dir, 'generator.cpp'),
    'test': os.path.join(test_dir, 'test.cpp'),
    'validator': os.path.join(test_dir, 'validator.cpp')
}
super().__init__(workspace_dir, files, test_type='validator', config=config)
```

**benchmarker.py changes**:
```python
# Similar pattern, use 'benchmarker' test type
```

### Phase 3: Test Workers and I/O (2-3 hours)

#### Step 9: Update Test Workers for Input/Output Organization (1.5 hours)
**Files**:
- `src/app/core/tools/specialized/comparison_test_worker.py`
- `src/app/core/tools/specialized/validator_test_worker.py`
- `src/app/core/tools/specialized/benchmark_test_worker.py`

**comparison_test_worker.py changes**:
```python
# Add test_type parameter to __init__
def __init__(self, workspace_dir: str, executables: Dict[str, str], 
             test_count: int, max_workers: Optional[int] = None,
             execution_commands: Optional[Dict[str, list]] = None,
             test_type: str = 'comparator'):
    # ... existing code ...
    self.test_type = test_type

# Update I/O file paths in _run_single_comparison_test
def _save_test_io(self, test_number: int, input_data: str, 
                  test_output: str, correct_output: str):
    """Save test input and outputs to nested directories."""
    from src.app.shared.constants.paths import get_inputs_dir, get_outputs_dir
    
    inputs_dir = get_inputs_dir(self.workspace_dir, self.test_type)
    outputs_dir = get_outputs_dir(self.workspace_dir, self.test_type)
    
    # Ensure directories exist
    os.makedirs(inputs_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)
    
    # Save files
    input_file = os.path.join(inputs_dir, f"input_{test_number}.txt")
    test_output_file = os.path.join(outputs_dir, f"test_output_{test_number}.txt")
    correct_output_file = os.path.join(outputs_dir, f"correct_output_{test_number}.txt")
```

**Similar updates for validator_test_worker.py and benchmark_test_worker.py**

#### Step 10: Update Benchmark Status Window I/O Display (45 min)
**File**: `src/app/presentation/views/benchmarker/benchmark_status_window.py`

**Changes needed**:
```python
# Line ~166-173: Update file path construction
def _update_io_display(self, test_number: int):
    """Update input/output display from nested directories."""
    from src.app.shared.constants.paths import get_inputs_dir, get_outputs_dir
    
    if self.workspace_dir:
        test_type = 'benchmarker'  # Or get from context
        inputs_dir = get_inputs_dir(self.workspace_dir, test_type)
        outputs_dir = get_outputs_dir(self.workspace_dir, test_type)
        
        input_file = os.path.join(inputs_dir, f"input_{test_number}.txt")
        output_file = os.path.join(outputs_dir, f"output_{test_number}.txt")
        
        # Fallback to non-numbered files
        if not os.path.exists(input_file):
            input_file = os.path.join(inputs_dir, "input.txt")
        if not os.path.exists(output_file):
            output_file = os.path.join(outputs_dir, "output.txt")
        
        # ... rest of display logic ...
```

### Phase 4: Persistence and Migration (2-3 hours)

#### Step 11: Update Database Snapshot and File Operations (1.5 hours)
**File**: `src/app/persistence/database/database_manager.py`

**Changes needed**:
```python
# Line ~639: create_files_snapshot
@staticmethod
def create_files_snapshot(workspace_dir: str) -> FilesSnapshot:
    """Create snapshot with nested workspace structure."""
    snapshot = FilesSnapshot(files={})
    
    # Traverse nested structure
    test_types = ['comparator', 'validator', 'benchmarker']
    
    for test_type in test_types:
        test_dir = os.path.join(workspace_dir, test_type)
        if os.path.exists(test_dir):
            # Include source files
            for filename in os.listdir(test_dir):
                filepath = os.path.join(test_dir, filename)
                if os.path.isfile(filepath):
                    # Store with relative path
                    relative_path = os.path.join(test_type, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        snapshot.files[relative_path] = f.read()
            
            # Optionally include I/O files (might be too large)
            # Could add separate snapshot type for I/O
    
    return snapshot
```

**Update file restoration**:
```python
def restore_files_snapshot(workspace_dir: str, snapshot: FilesSnapshot):
    """Restore files to nested structure."""
    for relative_path, content in snapshot.files.items():
        full_path = os.path.join(workspace_dir, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
```

#### Step 12: Migration and Testing (1.5 hours)
**New File**: `src/app/shared/utils/workspace_migration.py`

**Migration utility**:
```python
import os
import shutil
from typing import Dict, List

def detect_flat_workspace(workspace_dir: str) -> bool:
    """Check if workspace has old flat structure."""
    # Look for source files in root
    indicators = ['generator.cpp', 'generator.py', 'generator.java',
                  'test.cpp', 'test.py', 'Test.java']
    
    for indicator in indicators:
        if os.path.exists(os.path.join(workspace_dir, indicator)):
            return True
    return False

def migrate_workspace(workspace_dir: str) -> Dict[str, List[str]]:
    """
    Migrate flat workspace to nested structure.
    
    Returns:
        Dict mapping test types to lists of migrated files
    """
    from src.app.shared.utils.workspace_utils import ensure_workspace_structure
    
    if not detect_flat_workspace(workspace_dir):
        return {}  # Already migrated or empty
    
    # Create nested structure
    ensure_workspace_structure(workspace_dir)
    
    migrated = {
        'comparator': [],
        'validator': [],
        'benchmarker': []
    }
    
    # Define migration rules
    file_moves = {
        # Comparator files
        'generator.cpp': 'comparator/generator.cpp',
        'generator.py': 'comparator/generator.py',
        'Generator.java': 'comparator/Generator.java',
        'correct.cpp': 'comparator/correct.cpp',
        'correct.py': 'comparator/correct.py',
        'Correct.java': 'comparator/Correct.java',
        'test.cpp': 'comparator/test.cpp',
        'test.py': 'comparator/test.py',
        'Test.java': 'comparator/Test.java',
        
        # Validator files (if they exist separately)
        'validator.cpp': 'validator/validator.cpp',
        'validator.py': 'validator/validator.py',
        'Validator.java': 'validator/Validator.java',
    }
    
    # Move source files
    for old_name, new_path in file_moves.items():
        old_path = os.path.join(workspace_dir, old_name)
        if os.path.exists(old_path):
            new_full_path = os.path.join(workspace_dir, new_path)
            shutil.move(old_path, new_full_path)
            
            test_type = new_path.split('/')[0]
            migrated[test_type].append(old_name)
    
    # Move input/output files to comparator (default)
    for filename in os.listdir(workspace_dir):
        if filename.startswith('input') and filename.endswith('.txt'):
            old_path = os.path.join(workspace_dir, filename)
            new_path = os.path.join(workspace_dir, 'comparator', 'inputs', filename)
            shutil.move(old_path, new_path)
            migrated['comparator'].append(filename)
        elif filename.startswith('output') and filename.endswith('.txt'):
            old_path = os.path.join(workspace_dir, filename)
            new_path = os.path.join(workspace_dir, 'comparator', 'outputs', filename)
            shutil.move(old_path, new_path)
            migrated['comparator'].append(filename)
    
    return migrated
```

**Integration in app startup** (`src/app/__main__.py` or main window):
```python
from src.app.shared.utils.workspace_migration import migrate_workspace, detect_flat_workspace

# On startup
workspace_dir = config.get('workspace_folder')
if workspace_dir and detect_flat_workspace(workspace_dir):
    # Show migration dialog
    reply = QMessageBox.question(
        None,
        "Workspace Migration",
        "Old workspace structure detected. Migrate to new organized structure?",
        QMessageBox.Yes | QMessageBox.No
    )
    
    if reply == QMessageBox.Yes:
        migrated = migrate_workspace(workspace_dir)
        # Show migration summary
```

## Testing Plan

### Unit Tests
- ✅ Test path helper functions in `paths.py`
- ✅ Test workspace structure creation in `workspace_utils.py`
- ✅ Test file constant helpers in `file_constants.py`
- ✅ Test migration detection and execution

### Integration Tests
- ✅ Test comparator workflow with nested structure
- ✅ Test validator workflow with nested structure
- ✅ Test benchmarker workflow with nested structure
- ✅ Test file creation in correct directories
- ✅ Test I/O file reading/writing
- ✅ Test database snapshot with nested structure
- ✅ Test migration from flat to nested
- ✅ Test multi-language support with nested structure

### Manual Testing Checklist
- [ ] Create new workspace - verify directory structure created
- [ ] Open editor - verify files saved in correct test type folder
- [ ] Run comparator - verify executables and I/O in comparator/
- [ ] Run validator - verify files in validator/
- [ ] Run benchmarker - verify files in benchmarker/
- [ ] Switch test types - verify file isolation
- [ ] Migrate old workspace - verify files moved correctly
- [ ] Load database snapshot - verify restore to nested structure

## Backward Compatibility

### Migration Strategy
1. **Automatic Detection**: Detect old flat structure on app startup
2. **User Prompt**: Ask user if they want to migrate
3. **Safe Migration**: Copy files to new structure, keep backup
4. **Graceful Fallback**: If migration fails, continue with flat structure

### Dual Structure Support (Optional)
For transition period, support both structures:
```python
def get_file_path_with_fallback(workspace_dir, test_type, role, language):
    """Try nested structure first, fallback to flat."""
    nested_path = get_source_file_path(workspace_dir, test_type, role, language)
    if os.path.exists(nested_path):
        return nested_path
    
    # Fallback to flat structure
    flat_name = f"{role}.{LANGUAGE_EXTENSIONS[language]}"
    flat_path = os.path.join(workspace_dir, flat_name)
    if os.path.exists(flat_path):
        return flat_path
    
    # Return nested path for new files
    return nested_path
```

## Risk Assessment

### High Risk
- ❌ **File path breakage**: Many hardcoded paths throughout codebase
- ❌ **Database incompatibility**: Snapshots with old paths
- ❌ **Test failures**: Integration tests with flat structure expectations

### Medium Risk
- ⚠️ **Migration data loss**: Files could be lost if migration fails
- ⚠️ **Performance impact**: More nested directory operations
- ⚠️ **User confusion**: Existing users with flat structure

### Mitigation Strategies
1. **Comprehensive testing**: Test every file operation path
2. **Backup mechanism**: Create backup before migration
3. **Gradual rollout**: Support both structures initially
4. **Clear documentation**: Update user docs with new structure
5. **Error handling**: Graceful fallback to flat structure if needed

## Success Criteria

- ✅ All source files organized by test type
- ✅ Input/output files in separate subdirectories
- ✅ Zero file path errors in any workflow
- ✅ All tests pass with new structure
- ✅ Migration works for existing workspaces
- ✅ Database snapshots include nested structure
- ✅ Multi-language support maintained
- ✅ Performance not degraded

## Timeline

**Total Estimated Time**: 10-12 hours

| Phase | Tasks | Time | Dependencies |
|-------|-------|------|-------------|
| Phase 1 | Steps 1-4 | 2-3 hours | None |
| Phase 2 | Steps 5-8 | 3-4 hours | Phase 1 complete |
| Phase 3 | Steps 9-10 | 2-3 hours | Phase 2 complete |
| Phase 4 | Steps 11-12 | 2-3 hours | Phase 3 complete |

**Recommended Approach**: Complete one phase, test thoroughly, then proceed to next phase.

## Notes

- Consider adding workspace cleanup utility to remove old I/O files
- Could add "Export Test Session" feature leveraging organized structure
- Future: Add workspace templates with pre-configured structures
- Future: Add workspace statistics showing file organization
