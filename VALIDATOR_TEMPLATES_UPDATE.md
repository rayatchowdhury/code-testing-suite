# Validator Templates Update

**Date:** October 4, 2025

## Changes Made

Updated all three validator templates to correctly use **command-line arguments** instead of stdin.

---

## ✅ Updated Templates

### 1. validator.cpp
```cpp
int main(int argc, char* argv[]) {
    // argv[1] = input file path
    // argv[2] = output file path
    
    ifstream input_file(argv[1]);
    ifstream output_file(argv[2]);
    
    // Read and validate...
    return 0;  // 0=Correct, 1=Wrong Answer, 2=Presentation Error
}
```

### 2. validator.py
```python
def main():
    # sys.argv[1] = input file path
    # sys.argv[2] = output file path
    
    with open(sys.argv[1], 'r') as f:
        # Read input...
    
    with open(sys.argv[2], 'r') as f:
        # Read output...
    
    # Validate...
    sys.exit(0)  # 0=Correct, 1=Wrong Answer, 2=Presentation Error
```

### 3. Validator.java
```java
public static void main(String[] args) {
    // args[0] = input file path
    // args[1] = output file path
    
    Scanner inputFile = new Scanner(new File(args[0]));
    Scanner outputFile = new Scanner(new File(args[1]));
    
    // Read and validate...
    System.exit(0);  // 0=Correct, 1=Wrong Answer, 2=Presentation Error
}
```

---

## Key Features

### ✨ Simple & Clear
- Minimal comments explaining the essentials
- Easy to understand structure
- Example validation logic included

### ✨ Proper File I/O
- ✅ Reads from command-line argument file paths
- ✅ Opens and reads both input and output files
- ✅ Validates output against input

### ✨ Exit Code Convention
All templates use the standard exit codes:
- **0** = Correct (output is valid)
- **1** = Wrong Answer (output is incorrect)
- **2** = Presentation Error (output format is wrong)
- **3** = Validator Error (for argument errors)

### ✨ Example Validation
Each template includes a simple example:
- Reads an array from input
- Reads an array from output
- Checks if they match (you can replace with your logic)

---

## How to Use

When creating a validator, you need to:

1. **Read the test input** from the file at `argv[1]` / `sys.argv[1]` / `args[0]`
2. **Read the program output** from the file at `argv[2]` / `sys.argv[2]` / `args[1]`
3. **Compare/validate** the output against expected results
4. **Return exit code**:
   - `0` if correct
   - `1` if wrong answer
   - `2` if format error

---

## Example Use Case

```
Input file (argv[1]):
5
1 2 3 4 5

Output file (argv[2]):
5
1 2 3 4 5

Validator checks if output matches input → returns 0 (Correct)
```

```
Input file (argv[1]):
5
1 2 3 4 5

Output file (argv[2]):
5
1 2 3 4 6

Validator checks if output matches input → returns 1 (Wrong Answer)
```

---

## What Changed

### Before (WRONG):
```cpp
int main() {
    cin >> n;  // ❌ Reads from stdin
}
```

### After (CORRECT):
```cpp
int main(int argc, char* argv[]) {
    ifstream input_file(argv[1]);  // ✅ Reads from file argument
    input_file >> n;
}
```

---

## Files Updated

- ✅ `src/resources/templates/validator.cpp`
- ✅ `src/resources/templates/validator.py`
- ✅ `src/resources/templates/Validator.java`

All templates now correctly implement the validator protocol used by `ValidatorTestWorker`.
