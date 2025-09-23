# Validator Component Implementation Plan

## Overview
Transform the current validator from a static code analyzer into a competitive programming solution validator that can handle problems with multiple valid answers.

## Current State Analysis

### Issues Identified
- ❌ **Wrong Purpose**: Current `validator.py` does static code analysis instead of runtime solution validation
- ❌ **Incorrect UI**: Display area shows `Generator/Validator/Test Code` but should be `Generator/Test Code/Validator Code`
- ❌ **Missing Core Logic**: No implementation for the Generator → Test → Validator workflow
- ❌ **Wrong Integration**: Uses static validation instead of executable-based validation

### Current Architecture vs Target Architecture

**Current (Broken):**
```
Generator.cpp → input.txt
Validator.py (static analysis) ← Test Code.cpp
```

**Target (Correct):**
```
Generator.cpp → input.txt → Test Code.cpp → output.txt → Validator.cpp → exit code (0=valid, 1=invalid)
```

## Implementation Plan

### Phase 1: Core Architecture Setup

#### Step 1.1: Create ValidatorRunner Core Logic
**File**: `src/app/core/tools/validator_runner.py`

**Requirements:**
- Create new file based on `stresser.py` pattern
- Implement 3-stage workflow: Generator → Test → Validator
- Handle compilation of all three executables
- Manage file I/O between stages

**Key Classes:**
```python
class ValidatorTestWorker(QObject):
    """Threaded worker for validation tests"""
    # Signals: testStarted, testCompleted, allTestsCompleted
    
class ValidatorRunner(QObject):
    """Main validator coordination class"""
    # Methods: compile_all(), run_validation_test()
```

**Workflow Implementation:**
```python
def run_validation_cycle(self, test_number):
    # 1. Run generator.exe → input.txt
    # 2. Run test.exe < input.txt → output.txt
    # 3. Run validator.exe input.txt output.txt → exit code
    # 4. Interpret exit code (0=valid, 1=invalid, 2+=error)
```

#### Step 1.2: Update Validator Window Integration
**File**: `src/app/presentation/views/validator/validator_window.py`

**Changes:**
```python
# Replace current validator import
from src.app.core.tools.validator_runner import ValidatorRunner

# Update handle_action_button method
def handle_action_button(self, button_text):
    if button_text == 'Compile':
        self.validator_runner.compile_all()
    elif button_text == 'Run':
        test_count = self.test_count_slider.value()
        self.validator_runner.run_validation_test(test_count)
```

#### Step 1.3: Fix Display Area File Mapping
**File**: `src/app/presentation/views/validator/validator_display_area.py`

**Changes:**
```python
# Fix button order in _setup_ui()
for name in ['Generator', 'Test Code', 'Validator Code']:  # Fixed order

# Update file mapping in _handle_file_button()
file_mapping = {
    'Generator': 'generator.cpp',      # Creates test input
    'Test Code': 'test.cpp',           # Solution to validate  
    'Validator Code': 'validator.cpp'  # Validates test output
}
```

### Phase 2: Status Window and UI Updates

#### Step 2.1: Create Validator Status Window
**File**: `src/app/presentation/views/validator/validator_status_window.py`

**Requirements:**
- Show 3-stage progress: Generator → Test → Validator
- Display validation results with appropriate icons
- Handle different failure modes (compilation, runtime, validation)

**UI Elements:**
```
┌─────────────────────────────────────┐
│ Validation Progress                 │
├─────────────────────────────────────┤
│ ✅ Generator (0.02s)                │
│ ✅ Test Solution (0.15s)            │
│ ✅ Validator (0.01s)                │
│                                     │
│ Test 1/10: VALID ✅                 │
│ Overall: 8/10 tests passed         │
└─────────────────────────────────────┘
```

#### Step 2.2: Add Default Code Templates
**File**: `src/app/presentation/views/validator/validator_display_area.py`

**Method**: `_get_default_content()`

**Templates:**
```cpp
// Generator template
#include <iostream>
#include <random>
using namespace std;

int main() {
    // Generate random test case
    return 0;
}

// Test Code template  
#include <iostream>
using namespace std;

int main() {
    // Your solution here
    return 0;
}

// Validator template
#include <iostream>
#include <fstream>
using namespace std;

int main(int argc, char* argv[]) {
    if (argc < 3) {
        cerr << "Usage: ./validator input.txt output.txt\n";
        return 2;  // Error
    }
    
    ifstream in(argv[1]);   // test input
    ifstream out(argv[2]);  // test output
    
    // Validation logic here
    // Return 0 if valid, 1 if invalid, 2+ if error
    
    return 0;  // Valid by default
}
```

### Phase 3: Database Integration

#### Step 3.1: Update Database Schema
**File**: `src/app/persistence/database/database_manager.py`

**Add validator test type support:**
```python
# In TestResult dataclass, update test_type field documentation
test_type: str = ""  # 'stress', 'tle', or 'validator'

# Add validator-specific analysis structure
validator_analysis = {
    'generator_success': bool,
    'test_success': bool, 
    'validator_success': bool,
    'validator_exit_code': int,
    'validation_message': str,
    'execution_times': {
        'generator': float,
        'test': float, 
        'validator': float
    },
    'stage_failures': []  # Track which stage failed and why
}
```

#### Step 3.2: Implement Result Saving
**File**: `src/app/core/tools/validator_runner.py`

**Method**: `_save_validation_results()`
```python
def _save_validation_results(self, all_passed):
    """Save validation results to database"""
    # Calculate statistics for all three stages
    # Store detailed execution information
    # Handle partial failures gracefully
```

### Phase 4: Error Handling and Edge Cases

#### Step 4.1: Compilation Error Handling
**Files**: `validator_runner.py`, `validator_status_window.py`

**Requirements:**
- Handle individual component compilation failures
- Show specific error messages per component
- Allow partial workflow execution where possible

**Error Scenarios:**
```python
compilation_scenarios = {
    'generator_fails': "Show generator compilation errors",
    'test_fails': "Show test solution compilation errors", 
    'validator_fails': "Show validator compilation errors",
    'multiple_fail': "Show all compilation errors with priorities"
}
```

#### Step 4.2: Runtime Error Handling
**File**: `src/app/core/tools/validator_runner.py`

**Error Types:**
```python
runtime_errors = {
    'generator_timeout': "Generator took too long",
    'generator_crash': "Generator crashed or returned non-zero",
    'test_timeout': "Test solution exceeded time limit", 
    'test_crash': "Test solution crashed",
    'validator_timeout': "Validator took too long",
    'validator_crash': "Validator crashed unexpectedly",
    'file_io_error': "Could not read/write intermediate files"
}
```

#### Step 4.3: Validator Exit Code Interpretation
**File**: `src/app/core/tools/validator_runner.py`

**Exit Code Mapping:**
```python
validator_exit_codes = {
    0: "Valid output",
    1: "Invalid output", 
    2: "Validator error (wrong usage)",
    124: "Timeout",
    125: "Validator not found",
    126: "Validator not executable", 
    127: "Validator command not found",
    -1: "Validator killed/crashed"
}
```

### Phase 5: Advanced Features

#### Step 5.1: Multi-Test Validation
**File**: `src/app/core/tools/validator_runner.py`

**Features:**
- Run configurable number of validation cycles
- Aggregate success/failure statistics
- Stop on first failure vs. run all tests
- Performance metrics per stage

#### Step 5.2: Enhanced Reporting
**File**: `src/app/presentation/views/validator/validator_status_window.py`

**Reporting Features:**
```
┌─────────────────────────────────────────┐
│ Validation Results Summary              │
├─────────────────────────────────────────┤
│ Tests Run: 50                           │
│ Valid: 47 (94%)                         │
│ Invalid: 2 (4%)                         │
│ Errors: 1 (2%)                          │
│                                         │
│ Average Times:                          │
│ • Generator: 0.02s                      │
│ • Test: 0.15s                          │
│ • Validator: 0.01s                      │
│                                         │
│ Failed Tests: #23, #31                  │
└─────────────────────────────────────────┘
```

#### Step 5.3: Template System
**File**: `src/app/presentation/views/validator/validator_display_area.py`

**Template Categories:**
```python
validator_templates = {
    'basic': "Simple valid/invalid check",
    'numerical': "Floating point tolerance validation",
    'graph': "Graph structure validation", 
    'sequence': "Array/sequence validation",
    'geometric': "Computational geometry validation",
    'custom': "Blank template for custom logic"
}
```

## Implementation Timeline

### Week 1: Core Infrastructure
- [ ] Create `ValidatorRunner` class with basic workflow
- [ ] Fix UI file mapping and button order
- [ ] Implement basic compilation and execution chain
- [ ] Add simple status window

### Week 2: Error Handling & Polish
- [ ] Add comprehensive error handling for all stages
- [ ] Implement validator exit code interpretation
- [ ] Add default code templates
- [ ] Test with various edge cases

### Week 3: Database & Reporting
- [ ] Update database schema for validator results
- [ ] Implement result persistence
- [ ] Add enhanced status reporting
- [ ] Integration testing with existing components

### Week 4: Advanced Features
- [ ] Multi-test validation support
- [ ] Template system for common validators
- [ ] Performance optimizations
- [ ] Documentation and user guides

## Testing Strategy

### Unit Tests
- [ ] ValidatorRunner workflow execution
- [ ] Exit code interpretation logic
- [ ] File I/O operations
- [ ] Error handling scenarios

### Integration Tests
- [ ] UI component interactions
- [ ] Database save/load operations
- [ ] Cross-component communication
- [ ] End-to-end validation workflows

### User Testing Scenarios
```cpp
// Test Scenario 1: Basic validation
Generator: Output "5\n1 2 3 4 5"
Test: Read array, output sum
Validator: Check if sum equals 15

// Test Scenario 2: Multiple valid answers
Generator: Output graph edges
Test: Find any valid spanning tree
Validator: Check if result is actually a spanning tree

// Test Scenario 3: Tolerance validation
Generator: Output floating point numbers
Test: Compute average
Validator: Check if answer within 1e-6 tolerance
```

## Success Criteria

### Functional Requirements
- ✅ Generator → Test → Validator workflow executes correctly
- ✅ UI displays correct file buttons in proper order
- ✅ Compilation errors are handled gracefully for each component
- ✅ Validator exit codes are interpreted correctly
- ✅ Results are saved to database with proper categorization

### Performance Requirements
- ✅ Validation tests complete within reasonable time limits
- ✅ UI remains responsive during long validation runs
- ✅ Memory usage stays within acceptable bounds
- ✅ Database operations are efficient

### User Experience Requirements
- ✅ Clear progress indication during validation
- ✅ Informative error messages for failures
- ✅ Intuitive file switching between Generator/Test/Validator
- ✅ Consistent behavior with Comparator and Benchmarker components

## Files Modified/Created Summary

### New Files
- `src/app/core/tools/validator_runner.py` - Core validation logic
- `src/app/presentation/views/validator/validator_status_window.py` - Progress UI

### Modified Files
- `src/app/presentation/views/validator/validator_window.py` - Integration updates
- `src/app/presentation/views/validator/validator_display_area.py` - UI fixes
- `src/app/persistence/database/database_manager.py` - Schema updates
- `src/app/core/tools/validator.py` - Replace or rename existing file

### Configuration Files
- Update imports in `__init__.py` files as needed
- Add validator templates to resources if implementing template system

---

## Notes

- This plan follows the established patterns from Comparator and Benchmarker components
- Implementation prioritizes core functionality first, then advanced features
- Error handling is emphasized throughout to ensure robust operation
- The validator supports complex validation scenarios beyond simple string comparison