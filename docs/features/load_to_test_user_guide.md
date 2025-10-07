# Load to Test Feature - User Guide

**Version**: 2.0  
**Status**: ✅ Production Ready  
**Last Updated**: October 2025

---

## Overview

The **Load to Test** feature allows you to restore source code files from saved test results back into your workspace for retesting, modification, or analysis.

### What's New in Version 2.0

- ✅ **Simple & Fast**: Files are written directly to workspace (no complex navigation)
- ✅ **Extension Preservation**: All file extensions maintained (`generator.cpp`, `test.py`)
- ✅ **Multi-Language Support**: Mixed-language projects fully supported
- ✅ **Automatic Migration**: Works with both old and new result formats
- ✅ **Confirmation Dialog**: Preview files before overwriting

---

## How to Use

### Step 1: View Test Results

1. Navigate to **Results** window
2. Click on a test result to view details
3. Click the **"Load to Test"** button

![Detailed Results View](../readme/results.png)

### Step 2: Review Files

A confirmation dialog shows:
- Project name
- Test type (Comparator, Validator, Benchmarker)
- Primary language
- List of files to be loaded
- Target directory path

**Example**:
```
Load code files to workspace?

Project: My Algorithm Project
Test Type: Comparator
Language: CPP
Files (3):
  • generator.cpp
  • correct.cpp
  • test.cpp

This will overwrite any existing files in:
C:\Users\YourName\AppData\Local\CodeTestingSuite\workspace\comparator\

Continue?
```

### Step 3: Confirm

- Click **Yes** to load files
- Click **No** to cancel

### Step 4: Open Test Window

After loading:
1. Success message appears
2. Automatically opens the appropriate test window (Comparator/Validator/Benchmarker)
3. Files are ready in the workspace

---

## File Organization

Files are organized by test type in separate directories:

```
workspace/
├── comparator/          # Comparator test files
│   ├── generator.cpp
│   ├── correct.cpp
│   └── test.cpp
├── validator/           # Validator test files
│   ├── generator.py
│   ├── validator.py
│   └── test.py
└── benchmarker/         # Benchmarker test files
    ├── Generator.java
    └── Test.java
```

### Test Type Mapping

| Test Result Type | Target Directory | Window Opened |
|------------------|------------------|---------------|
| Comparison | `workspace/comparator/` | Comparator Window |
| Validation | `workspace/validator/` | Validator Window |
| Benchmark | `workspace/benchmarker/` | Benchmarker Window |

---

## File Counts by Test Type

Different test types load different numbers of files:

| Test Type | Files Loaded | Example |
|-----------|--------------|---------|
| **Comparator** | 3 files | generator.cpp, correct.cpp, test.cpp |
| **Validator** | 3 files | generator.py, validator.py, test.py |
| **Benchmarker** | 2 files | Generator.java, Test.java (no correct!) |

**Note**: Additional helper files (like `utils.h`, `helper.cpp`) are also loaded if they were part of the original test.

---

## Mixed Language Support

Load to Test fully supports mixed-language projects:

**Example - Python Generator + C++ Test**:
```
Files loaded:
  • generator.py (Python)
  • correct.cpp (C++)
  • test.cpp (C++)
```

All files maintain their:
- ✅ Original extensions
- ✅ Language metadata
- ✅ Proper naming (Java capitalization, etc.)

---

## Safety Features

### Overwrite Protection

- ⚠️ **Warning**: Load to Test will overwrite existing files in the target directory
- ✅ **Confirmation**: Always asks before overwriting
- ✅ **Preview**: Shows which files will be written and where

### Recommended Workflow

1. **Save Current Work**: If you have unsaved changes in the test window, save them first
2. **Load Previous Result**: Use Load to Test to restore old files
3. **Make Changes**: Modify and retest as needed
4. **Save New Result**: Run tests to create a new result with your changes

### File Conflict Example

If you have:
- Current `generator.cpp` in workspace (v2)
- Want to load `generator.cpp` from old result (v1)

Load to Test will:
1. Show confirmation: "This will overwrite generator.cpp"
2. Wait for your confirmation
3. If confirmed: Replace v2 with v1
4. If cancelled: Keep v2 unchanged

---

## Common Use Cases

### 1. **Retest Old Solution**

Scenario: Want to rerun tests on code from last week

Steps:
1. Find the old test result in Results window
2. Click "Load to Test"
3. Confirm to load files
4. Run tests again in the opened window

### 2. **Compare Versions**

Scenario: Compare current code with previous version

Steps:
1. Export current files manually (copy to another folder)
2. Load old result
3. Compare files side-by-side
4. Reload current files or continue with old

### 3. **Recover Lost Code**

Scenario: Accidentally deleted generator.cpp

Steps:
1. Find most recent test result that includes it
2. Load to Test
3. Files restored to workspace
4. Continue working

### 4. **Analyze Failed Test**

Scenario: Want to understand why a test failed last month

Steps:
1. View detailed results for failed test
2. Load to Test to restore exact code that failed
3. Examine code in editor
4. Make fixes and retest

---

## Technical Details

### What Happens Behind the Scenes

1. **Parse Result**: FilesSnapshot is parsed from database
   - Automatically migrates old format if needed
   - Extracts all file metadata

2. **Write Files**: Files are written to workspace directory
   ```python
   for filename, file_data in snapshot.files.items():
       file_path = os.path.join(target_dir, filename)
       with open(file_path, 'w', encoding='utf-8') as f:
           f.write(file_data['content'])
   ```

3. **Open Window**: Target test window is opened
   - Window automatically reads files from workspace
   - No manual file opening needed

### Why This Is Better Than Before

**Old Approach** (v1.0):
- Emit signal to main window
- Navigate through widget hierarchy  
- Manually populate each editor widget
- ~100 lines of complex code
- Fragile (breaks if UI changes)

**New Approach** (v2.0):
- Simply write files to workspace
- Test windows read automatically
- ~30 lines of clean code
- Robust (uses file system)

---

## Troubleshooting

### Issue: "No Code Files" Error

**Cause**: Test result has no file snapshot saved

**Solution**: 
- This result was saved before file snapshots were implemented
- Or the test failed before files could be captured
- Cannot load files from this result

### Issue: Files Not Appearing in Editor

**Cause**: Test window was already open

**Solution**:
1. Close the test window
2. Use Load to Test again
3. Window will reopen with fresh files

### Issue: Wrong Files Loaded

**Cause**: Loaded from wrong test result

**Solution**:
1. Check which result you selected
2. Use Load to Test from correct result
3. Files will be overwritten with correct ones

### Issue: Permission Error

**Cause**: Workspace directory is read-only or locked

**Solution**:
1. Check workspace directory permissions
2. Close any programs that might have files open
3. Try Load to Test again

---

## Keyboard Shortcuts

| Action | Shortcut | Description |
|--------|----------|-------------|
| Open Results | `Ctrl+R` | Open Results window |
| Load to Test | (none) | Click button in detailed view |
| Close Window | `Ctrl+W` | Close current window |

---

## FAQ

**Q: Will Load to Test save my current work?**  
A: No, it will overwrite files. Save your work first!

**Q: Can I load files from multiple results?**  
A: Not simultaneously. Load from one result at a time.

**Q: What if I loaded the wrong files?**  
A: Simply load from a different result to overwrite them.

**Q: Can I edit files after loading?**  
A: Yes! Files are fully editable in the test window.

**Q: Are file extensions always preserved?**  
A: Yes! Version 2.0 always preserves exact filenames and extensions.

**Q: What happens to additional files like helper.cpp?**  
A: They're loaded too if they were part of the original test.

**Q: Does it work with Java files (capitalized)?**  
A: Yes! Java capitalization (Generator.java, Test.java) is preserved.

**Q: Can I load Python files into a C++ test?**  
A: Yes! Mixed-language is fully supported.

**Q: Will it work with old test results?**  
A: Yes! Old format is automatically migrated when loaded.

---

## Best Practices

### ✅ Do

- **Save work first**: Always save current changes before using Load to Test
- **Review confirmation**: Check the file list in the confirmation dialog
- **Keep backups**: Export important results regularly
- **Use descriptive project names**: Easier to find results later

### ❌ Don't

- **Don't skip confirmation**: Always review what will be overwritten
- **Don't load during tests**: Wait for current test to finish
- **Don't edit loaded files immediately**: Review them first
- **Don't rely solely on Load to Test**: Keep external backups of important code

---

## Example Workflows

### Workflow 1: Bug Fix Verification

1. Find the test result where bug was first introduced
2. Load to Test → Confirm
3. Examine code to identify bug
4. Make fix in editor
5. Run tests to verify fix
6. New result saved with fixed code

### Workflow 2: Performance Comparison

1. Load baseline version (v1)
2. Run benchmarker tests
3. Note performance metrics
4. Load optimized version (v2)
5. Run benchmarker tests again
6. Compare results

### Workflow 3: Code Review

1. Team member saves test result
2. You open Results window
3. Load their code
4. Review in editor
5. Make suggestions
6. They load your suggested changes

---

## Related Features

- **Export**: Save results to ZIP file for backup
- **Detailed View**: Examine test results before loading
- **Test Windows**: Edit and run tests with loaded files
- **Database Management**: Clean up old results

---

## Version History

### Version 2.0 (October 2025) - Current
- ✅ Simplified implementation (write to workspace)
- ✅ File extension preservation
- ✅ Mixed-language support
- ✅ Automatic migration
- ✅ Enhanced confirmation dialog

### Version 1.0 (Legacy)
- ❌ Complex widget navigation
- ❌ Lost file extensions
- ❌ Single language only
- ❌ Fragile implementation

---

## Summary

**Load to Test** is a powerful feature for:
- ✅ Restoring previous code versions
- ✅ Comparing different implementations
- ✅ Recovering accidentally deleted files
- ✅ Analyzing test failures
- ✅ Sharing code with team members

**Key Benefits**:
- Simple and fast
- File extensions preserved
- Multi-language support
- Backward compatible
- Safe with confirmation

---

**Need Help?**  
- Check the FAQ section above
- Review troubleshooting guide
- See example workflows
- Refer to API documentation

**Status**: ✅ Production Ready  
**Version**: 2.0  
**Tested**: 60/60 tests passing

