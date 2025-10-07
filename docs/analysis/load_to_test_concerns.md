# Load to Test Feature - Problems & Redesign

## 🔴 Critical Issues Identified

### Issue 1: Files Snapshot Stores ALL Files Regardless of Test Type
**Problem**: Benchmark test result contains `correct_code` and `validator_code` even though benchmarker only needs `test_code`.

**Root Cause**: `create_files_snapshot()` reads ALL files from workspace indiscriminately.

**Impact**: Wastes storage space, creates confusion about which files belong to which test type.

### Issue 2: No File Extension Information Stored
**Problem**: `files_snapshot` stores content as:
```json
{
  "generator_code": "content here...",
  "correct_code": "content here...",
  "test_code": "content here..."
}
```

**Missing**: File extensions! We don't know if:
- `generator_code` is `generator.cpp`, `generator.py`, or `Generator.java`
- Each file could be a **different language**!

### Issue 3: Language Detection is Unreliable
**Current Method**: Guess from content patterns (`import`, `#include`, `public class`)

**Problems**:
- Simple code might not contain language-specific keywords
- Mixed-language projects can't be detected properly
- User could have Java generator, C++ correct code, Python test

### Issue 4: Overly Complex Loading Logic
**Current Approach**:
1. Parse files_snapshot
2. Detect language from content
3. Access WindowManager
4. Get window instance
5. Navigate widget hierarchy (window → display_area → test_tabs → editor)
6. Switch language per tab
7. Activate tab
8. Get codeEditor from EditorWidget
9. Set content via setPlainText

**Problems**:
- Too many layers of abstraction
- Fragile (breaks if widget structure changes)
- Doesn't handle multi-language properly
- Manual tab activation is error-prone

### Issue 5: Wrong Files for Wrong Test Types
**What Should Happen**:
- **Benchmarker**: Only `test_code` (1 file)
- **Comparator**: `generator_code`, `correct_code`, `test_code` (3 files)
- **Validator**: `generator_code`, `validator_code`, `test_code` (3 files)

**Current**: Tries to load all 5 files regardless!

### Issue 6: additional_files Mystery
**What is it?**: Any helper files like `helper.cpp`, `utils.py`, etc.
**Storage**: `{"comparator/helper.cpp": "content..."}`
**Problem**: We're ignoring these completely!

## ✅ Simple Solution

### **User's Suggestion (CORRECT!):**
1. Write files back to workspace directory
2. Open the test window
3. Let window read files naturally
4. Use existing language selector UI

### **Why This is Better:**
- ✅ Reuses existing file I/O logic
- ✅ Workspace is the source of truth
- ✅ Test windows already know how to read files
- ✅ Language switching handled by UI
- ✅ No fragile widget hierarchy navigation
- ✅ Handles multi-language properly
- ✅ Includes additional_files automatically

## 📝 Redesign Plan

### Step 1: Improve Files Snapshot Storage
**Problem**: No extension information

**Solution A (Minimal Change)**: Store extensions in additional metadata
```json
{
  "generator_code": "content...",
  "generator_ext": ".py",
  "correct_code": "content...",
  "correct_ext": ".cpp",
  ...
}
```

**Solution B (Better)**: Store actual filenames
```json
{
  "generator.py": "content...",
  "correct.cpp": "content...",
  "test.cpp": "content..."
}
```

### Step 2: Filter Files by Test Type
**When Saving**: Only save relevant files
- Benchmarker: Only `test.*`
- Comparator: Only `generator.*`, `correct.*`, `test.*`
- Validator: Only `generator.*`, `validator.*`, `test.*`

### Step 3: Simplified Load to Test
```python
def _load_to_test(self):
    # 1. Get files_snapshot (with extensions)
    files = parse_files_with_extensions(self.test_result.files_snapshot)
    
    # 2. Get workspace directory
    workspace_dir = get_workspace_directory()
    test_type_dir = os.path.join(workspace_dir, test_type)
    
    # 3. Write files to workspace
    for filename, content in files.items():
        filepath = os.path.join(test_type_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
    
    # 4. Open test window (window reads files automatically!)
    window_manager.show_window(window_name)
    
    # Done! Let user switch language via UI if needed
```

### Step 4: Language Detection (Per-File)
**Store language per file** in files_snapshot:
```json
{
  "files": {
    "generator.py": {"content": "...", "language": "py"},
    "correct.cpp": {"content": "...", "language": "cpp"},
    "test.java": {"content": "...", "language": "java"}
  }
}
```

## 🎯 Implementation Priority

### Phase 1: Quick Fix (Immediate)
- [ ] Simplify load logic to write files to workspace
- [ ] Remove complex widget navigation
- [ ] Let window read files naturally

### Phase 2: Data Structure (Next)
- [ ] Update FilesSnapshot to store extensions/filenames
- [ ] Filter files by test type when saving
- [ ] Store language per file

### Phase 3: Migration (Later)
- [ ] Migrate old test results to new format
- [ ] Update database schema if needed

## 🔧 Questions to Answer

1. **Workspace Location**: Where is workspace_dir stored/accessible?
2. **File Reading**: Do test windows auto-read on show, or need trigger?
3. **Backward Compatibility**: Handle old results without extension info?
4. **Confirmation**: Warn before overwriting workspace files?
5. **Additional Files**: Should these be loaded too?

## 📊 Current State

- ❌ Complex widget hierarchy navigation
- ❌ No file extension information
- ❌ Unreliable language detection
- ❌ Saves all files regardless of test type
- ❌ Ignores additional_files
- ❌ Doesn't handle multi-language

## 🎯 Target State

- ✅ Simple: Write to workspace, open window
- ✅ File extensions preserved
- ✅ Per-file language information
- ✅ Only relevant files saved per test type
- ✅ Additional files included
- ✅ Multi-language support
- ✅ Uses existing UI for language switching
