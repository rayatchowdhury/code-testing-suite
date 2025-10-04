# Validator Architecture Analysis

**Date:** October 4, 2025

## Overview
This document explains how the validator system works in the code testing suite, with special focus on how command-line arguments are passed to validator programs.

---

## Architecture Overview

### Three-Tier Structure

```
ValidatorRunner (Controller)
    ↓
ValidatorTestWorker (Worker/Executor)  
    ↓
3-Stage Validation Process
```

---

## 1. ValidatorRunner (Controller Layer)

**File:** `src/app/core/tools/validator.py`

### Responsibilities:
- Main controller that inherits from `BaseRunner`
- Manages compilation through `BaseCompiler`
- Creates and manages `ValidatorTestWorker` instances
- Handles signal routing between worker and UI
- Creates test results for database storage

### Key Features:
```python
class ValidatorRunner(BaseRunner):
    # Validation-specific signal
    testCompleted = Signal(int, bool, str, str, str, str, int)
    
    def __init__(self, workspace_dir, files=None, config=None):
        # Uses nested validator directory structure
        files = {
            'generator': '.../validator/generator.cpp',
            'test': '.../validator/test.cpp',
            'validator': '.../validator/validator.cpp'
        }
        
    def _create_test_worker(self, test_count, max_workers=None, **kwargs):
        # Generates execution commands for multi-language support
        execution_commands = {
            'generator': self.compiler.get_execution_command('generator'),
            'test': self.compiler.get_execution_command('test'),
            'validator': self.compiler.get_execution_command('validator')
        }
        return ValidatorTestWorker(...)
```

### Multi-Language Support:
- Handles C++, Python, and Java validators
- Uses `BaseCompiler` to generate appropriate execution commands
- Commands are lists: `['./validator.exe']`, `['python', 'validator.py']`, or `['java', 'Validator']`

---

## 2. ValidatorTestWorker (Execution Layer)

**File:** `src/app/core/tools/specialized/validator_test_worker.py`

### Responsibilities:
- Executes validation tests in parallel using ThreadPoolExecutor
- Manages the 3-stage validation process
- Tracks performance metrics (time, memory)
- Handles temporary file creation for validator arguments
- Saves test I/O to nested directories

### Signal Flow:
```python
testStarted = Signal(int, int)  # current test, total tests
testCompleted = Signal(int, bool, str, str, str, str, int, float, float)  
    # test_number, passed, input, test_output, validation_message, 
    # error_details, validator_exit_code, time, memory
allTestsCompleted = Signal(bool)
```

---

## 3. The 3-Stage Validation Process

### Stage 1: Generator
```python
generator_process = subprocess.Popen(
    self.execution_commands['generator'],  # e.g., ['./generator.exe']
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
```
- **Input:** None
- **Output:** Test input data (via stdout)
- **Purpose:** Generate random test cases

### Stage 2: Test Solution
```python
test_process = subprocess.Popen(
    self.execution_commands['test'],  # e.g., ['python', 'test.py']
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
test_process.stdin.write(input_text)
```
- **Input:** Generated input (via stdin)
- **Output:** Program output (via stdout)
- **Purpose:** Run user's solution on generated input

### Stage 3: Validator (THE KEY PART)
```python
# Create temporary files
with tempfile.NamedTemporaryFile(...) as input_temp:
    input_temp.write(input_text)
    input_temp_path = input_temp.name

with tempfile.NamedTemporaryFile(...) as output_temp:
    output_temp.write(test_output)
    output_temp_path = output_temp.name

# Build validator command WITH FILE ARGUMENTS
validator_command = self.execution_commands['validator'] + [input_temp_path, output_temp_path]
# Example result: ['./validator.exe', '/tmp/vld_in_abc123.txt', '/tmp/vld_out_xyz789.txt']

validator_process = subprocess.Popen(
    validator_command,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
```

---

## ⭐ How Arguments Are Passed to Validator

### The Critical Lines (Line 281 in validator_test_worker.py):
```python
# Build validator command with file arguments
validator_command = self.execution_commands['validator'] + [input_temp_path, output_temp_path]
```

### What This Means:

**For C++ Validator:**
```bash
# Execution command base: ['./validator.exe']
# With arguments added: ['./validator.exe', '/tmp/vld_in_abc.txt', '/tmp/vld_out_xyz.txt']
# Equivalent to running: ./validator.exe /tmp/vld_in_abc.txt /tmp/vld_out_xyz.txt
```

**For Python Validator:**
```bash
# Execution command base: ['python', 'validator.py']
# With arguments added: ['python', 'validator.py', '/tmp/vld_in_abc.txt', '/tmp/vld_out_xyz.txt']
# Equivalent to running: python validator.py /tmp/vld_in_abc.txt /tmp/vld_out_xyz.txt
```

**For Java Validator:**
```bash
# Execution command base: ['java', 'Validator']
# With arguments added: ['java', 'Validator', '/tmp/vld_in_abc.txt', '/tmp/vld_out_xyz.txt']
# Equivalent to running: java Validator /tmp/vld_in_abc.txt /tmp/vld_out_xyz.txt
```

---

## What Validator Programs Should Look Like

### Current Template (INCORRECT - Reads from stdin):
```cpp
#include <iostream>
using namespace std;

int main() {
    // Read input
    int n;
    cin >> n;  // ❌ WRONG: Reads from stdin, not from file arguments
    
    // Validate...
    return 0;
}
```

### Correct Template (Should read from argv):
```cpp
#include <iostream>
#include <fstream>
#include <cassert>
using namespace std;

int main(int argc, char* argv[]) {
    // ✅ CORRECT: Read file paths from command-line arguments
    assert(argc == 3);  // Expect: program_name input_file output_file
    
    string input_file = argv[1];
    string output_file = argv[2];
    
    // Read input from file
    ifstream input(input_file);
    int n;
    input >> n;
    
    // Read output from file
    ifstream output(output_file);
    // Validate the output...
    
    // Return exit code:
    // 0 = Correct
    // 1 = Wrong Answer
    // 2 = Presentation Error
    return 0;
}
```

### Python Validator Template:
```python
import sys

def main():
    # ✅ Read file paths from command-line arguments
    assert len(sys.argv) == 3, "Usage: validator.py <input_file> <output_file>"
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Read input from file
    with open(input_file, 'r') as f:
        n = int(f.readline())
    
    # Read output from file
    with open(output_file, 'r') as f:
        # Validate the output...
        pass
    
    # Exit with appropriate code
    # 0 = Correct, 1 = Wrong Answer, 2 = Presentation Error
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### Java Validator Template:
```java
import java.io.*;
import java.util.*;

public class Validator {
    public static void main(String[] args) throws Exception {
        // ✅ Read file paths from command-line arguments
        assert args.length == 2 : "Usage: Validator <input_file> <output_file>";
        
        String inputFile = args[0];
        String outputFile = args[1];
        
        // Read input from file
        Scanner inputScanner = new Scanner(new File(inputFile));
        int n = inputScanner.nextInt();
        
        // Read output from file
        Scanner outputScanner = new Scanner(new File(outputFile));
        // Validate the output...
        
        // Exit with appropriate code
        // 0 = Correct, 1 = Wrong Answer, 2 = Presentation Error
        System.exit(0);
    }
}
```

---

## Exit Code Convention

The validator uses specific exit codes to communicate validation results:

| Exit Code | Meaning | Description |
|-----------|---------|-------------|
| **0** | Correct | Output is valid and correct |
| **1** | Wrong Answer | Output is incorrect |
| **2** | Presentation Error | Output format is incorrect |
| **>2** | Validator Error | Validator crashed or failed |
| **-1** | Execution Error | Failed to run validator |
| **-2** | Timeout | Validator took too long |
| **-3** | System Error | Unexpected system error |

These are interpreted in `validator_test_worker.py` (lines 312-337):
```python
if validator_exit_code == 0:
    validation_message = "Correct"
    passed = True
elif validator_exit_code == 1:
    validation_message = "Wrong Answer"
    passed = False
elif validator_exit_code == 2:
    validation_message = "Presentation Error"
    passed = False
else:
    validation_message = "Validator Error"
    passed = False
```

---

## Performance Tracking

The worker tracks metrics for each stage:

```python
{
    'generator_time': 0.05,      # seconds
    'test_time': 0.12,           # seconds  
    'validator_time': 0.03,      # seconds
    'total_time': 0.20,          # seconds
    'memory': 15.3               # MB (peak across all stages)
}
```

Memory is tracked using `psutil`:
```python
proc = psutil.Process(validator_process.pid)
while validator_process.poll() is None:
    mem_mb = proc.memory_info().rss / (1024 * 1024)
    peak_memory_mb = max(peak_memory_mb, mem_mb)
```

---

## File Organization

### Temporary Files (During Validation):
```
/tmp/
├── vld_in_abc123.txt    # Input data (temporary)
└── vld_out_xyz789.txt   # Output data (temporary)
```
These are deleted after validation completes.

### Saved I/O Files (Persistent):
```
workspace/
└── validator/
    ├── inputs/
    │   ├── input_1.txt
    │   ├── input_2.txt
    │   └── ...
    └── outputs/
        ├── output_1.txt
        ├── output_2.txt
        └── ...
```

Saved by `_save_test_io()` method (lines 84-104).

---

## Key Issues Found

### 🔴 PROBLEM: Current Validator Templates Are Wrong!

The templates in `src/resources/templates/validator.*` currently read from **stdin** instead of **command-line arguments**.

This doesn't match how the system actually calls validators:
- System passes file paths as arguments: `validator.exe input.txt output.txt`
- Templates read from stdin: `cin >> n` (wrong!)

### ✅ SOLUTION: Update Templates

Need to update all three validator templates to:
1. Accept two command-line arguments (input file path, output file path)
2. Read input data from the first file
3. Read output data from the second file
4. Return appropriate exit codes (0, 1, or 2)

---

## Summary

### How It Works:
1. **ValidatorRunner** compiles code and creates worker with execution commands
2. **ValidatorTestWorker** runs tests in parallel using ThreadPoolExecutor
3. For each test:
   - Generator creates input → saved to temp file
   - Test solution processes input → saved to temp file
   - **Validator is called with TWO file paths as arguments**
   - Validator reads files, checks correctness, returns exit code
4. Results are collected and emitted via signals
5. I/O files are saved to nested directories
6. Metrics (time, memory) are tracked throughout

### Critical Insight:
**Validators receive file paths as command-line arguments, NOT data via stdin!**

This is the key architectural decision that current templates don't reflect.

---

## Recommended Actions

1. ✅ Update `validator.cpp` template to use `argc`/`argv` and `fstream`
2. ✅ Update `validator.py` template to use `sys.argv` and file I/O
3. ✅ Update `Validator.java` template to use `args[]` and `File` I/O
4. ✅ Add comments explaining the exit code convention
5. ✅ Add example validation logic (e.g., comparing expected vs actual output)
