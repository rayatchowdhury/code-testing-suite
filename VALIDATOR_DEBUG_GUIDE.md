# Validator Debugging Guide

**Date:** October 4, 2025

## Current Status

You're seeing "Execution Error" in the validator test detail view. I've added debug output to help diagnose the issue.

## Your Code Setup

### Generator (Python):
```python
import random
print(random.randint(1,2))
```
**Output:** `1` or `2`

### Test Code (C++):
```cpp
int main() {
    int n;
    cin >> n;
    cout << 1 << endl;
    return 0;
}
```
**Input:** reads the random number  
**Output:** always `1`

### Validator (C++):
```cpp
int main(int argc, char* argv[]) {
    // Reads input file and output file
    // Checks if output == input
    // Returns 0 if match, 1 if different
}
```

## The Problem

Your test code always outputs `1`, but when the generator produces `2`, the validator will correctly report "Wrong Answer" (exit code 1), not "Execution Error".

"Execution Error" means the validator itself is crashing or failing to run.

## Debug Output Added

I've added debug prints to show:
1. The exact validator command being run
2. The temp file paths
3. The input and output content
4. The validator's exit code and output

## Next Steps

**RUN THIS:**
1. Start the app: `py -m src.app`
2. Open Validator window
3. Make sure your generator.py, test.cpp, and validator.cpp are set
4. Run a few tests
5. **Look at the terminal output** - you'll see lines starting with `DEBUG:`

## What to Look For

The debug output will show something like:
```
DEBUG: Validator command: ['path/to/validator.exe', 'C:\\Temp\\vld_in_xxx.txt', 'C:\\Temp\\vld_out_yyy.txt']
DEBUG: Input temp file: C:\\Temp\\vld_in_xxx.txt
DEBUG: Output temp file: C:\\Temp\\vld_out_yyy.txt
DEBUG: Input text: '2\n'
DEBUG: Test output: '1\n'
DEBUG: Validator exit code: 1
DEBUG: Validator stdout: ''
DEBUG: Validator stderr: ''
```

## Possible Issues

### 1. Validator Not Compiled
**Symptom:** `FileNotFoundError` or similar
**Fix:** Make sure the validator C++ file is compiled

### 2. Validator Command Wrong
**Symptom:** Command doesn't look right
**Fix:** Check multi-language compilation settings

### 3. Validator Crashing
**Symptom:** Exit code 3 or strange error
**Fix:** Check if validator.cpp has syntax errors or can't read files

### 4. Expected Behavior
If generator outputs `2` and test outputs `1`:
- **Expected:** Validator exit code `1` (Wrong Answer)
- **Not error!** This is correct behavior

## Share Debug Output

After running tests, **copy the DEBUG lines from the terminal** and share them so I can see exactly what's happening!
