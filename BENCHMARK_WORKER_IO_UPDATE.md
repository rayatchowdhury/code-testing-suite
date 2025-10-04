# Benchmark Test Worker Update - Input/Output Data Support

**Date:** October 4, 2025

## Overview
Updated the `BenchmarkTestWorker` to capture, store, and emit full input/output data and test size, enabling the detail dialog to display actual test data instead of placeholders.

## Changes Made

### 1. `BenchmarkTestWorker` Signal Update (benchmark_test_worker.py)

#### Updated Signal Signature
**Before:**
```python
testCompleted = Signal(str, int, bool, float, float, bool)
# test name, test number, passed, execution time, memory used, memory passed
```

**After:**
```python
testCompleted = Signal(str, int, bool, float, float, bool, str, str, int)
# test name, test number, passed, execution time, memory used, memory passed, 
# input_data, output_data, test_size
```

### 2. Data Storage Changes

#### Full Input/Output Storage
**Before (Truncated):**
```python
'input': input_text.strip()[:200] + ("..." if len(input_text.strip()) > 200 else ""),
'output': stdout.strip()[:200] + ("..." if len(stdout.strip()) > 200 else "")
```

**After (Full Data):**
```python
'input': input_text,  # Store full input
'output': stdout if stdout else "",  # Store full output
'test_size': test_size  # Number of input lines
```

#### Test Size Calculation
Added automatic calculation of test size (number of input lines):
```python
# Calculate test size (number of input lines)
test_size = len(input_text.strip().split('\n')) if input_text.strip() else 0
```

### 3. Signal Emission Updates

#### Updated `testCompleted.emit()` Call
Now emits 9 parameters instead of 6:
```python
self.testCompleted.emit(
    test_result['test_name'],
    test_result['test_number'],
    test_result['passed'],
    test_result['execution_time'],
    test_result['memory_used'],
    test_result['memory_passed'],
    test_result.get('input', ''),        # NEW: Full input data
    test_result.get('output', ''),       # NEW: Full output data
    test_result.get('test_size', 0)      # NEW: Test size (line count)
)
```

#### Error Result Updates
Updated error emission to include empty strings for I/O and 0 for test_size:
```python
self.testCompleted.emit(
    f"Test {completed_tests}",
    error_result['test_number'],
    False,
    0.0,
    0.0,
    False,
    '',   # Empty input
    '',   # Empty output
    0     # Zero test size
)
```

### 4. `_create_error_result()` Method Update
Added input, output, and test_size fields to error results:
```python
return {
    'test_name': f"Test {test_number}",
    'test_number': test_number,
    'passed': False,
    'execution_time': execution_time,
    'memory_used': memory_used,
    'memory_passed': memory_used <= self.memory_limit,
    'time_passed': execution_time <= self.time_limit,
    'error_details': error_msg,
    'generator_time': 0.0,
    'input': "",           # NEW
    'output': "",          # NEW
    'test_size': 0         # NEW
}
```

### 5. `Benchmarker` Class Update (benchmarker.py)

Updated the main `testCompleted` signal to match the worker:
```python
# Updated signal signature to include input/output data
testCompleted = Signal(str, int, bool, float, float, bool, str, str, int)
# test name, test number, passed, execution time, memory used, memory passed, 
# input_data, output_data, test_size
```

### 6. `BenchmarkerStatusView` Update (benchmarker_status_view.py)

#### Updated `on_test_completed()` Method

**New Parameters:**
```python
def on_test_completed(self, test_name: str, test_number: int, passed: bool,
                     execution_time: float, memory_used: float, memory_passed: bool,
                     input_data: str = "", output_data: str = "", test_size: int = 0):
```

**Enhanced Data Storage:**
```python
self.test_data[test_number] = {
    'test_name': test_name,
    'passed': passed,
    'execution_time': execution_time,
    'time_ms': time_ms,
    'memory_used': memory_used,
    'time_passed': passed,
    'memory_passed': memory_passed,
    'time_limit_ms': self.time_limit_ms,
    'memory_limit_mb': self.memory_limit_mb,
    'input_data': input_data,      # NEW
    'output_data': output_data,    # NEW
    'test_size': test_size         # NEW
}
```

## Data Flow

```
BenchmarkTestWorker
    ↓ _run_single_benchmark_test()
    ↓ - Captures full input from generator
    ↓ - Captures full output from test solution
    ↓ - Calculates test_size (line count)
    ↓ - Stores in test_results dictionary
    ↓
    ↓ testCompleted.emit(9 parameters)
    ↓
Benchmarker (passes through signal)
    ↓
BenchmarkerStatusView.on_test_completed()
    ↓ Stores in self.test_data[test_number]
    ↓
BenchmarkerDetailDialog
    ↓ Displays in 3 sections:
    ↓ 1. Input (full data)
    ↓ 2. Output (full data)
    ↓ 3. Performance Summary (with line count)
```

## Benefits

✅ **Full Data Visibility** - No more truncated input/output  
✅ **Automatic Line Counting** - Test size calculated from actual input  
✅ **Better Debugging** - Users can see exactly what was tested  
✅ **Performance Context** - Line count provides scale reference  
✅ **Complete Test Records** - All I/O data saved to workspace files  
✅ **Backwards Compatible** - Default parameters prevent breaking existing code  

## Performance Impact

- **Memory:** Storing full I/O data instead of truncated versions may use slightly more memory for large test inputs/outputs
- **I/O:** Full data is already being saved to files via `_save_test_io()`, so no additional file I/O overhead
- **Processing:** Line counting (`split('\n')`) is a fast O(n) operation on the input string

## Example Output

When viewing a benchmark test detail dialog, users will now see:

### Input Section:
```
1 2 3 4 5
6 7 8 9 10
11 12 13 14 15
...
(Full input data, not truncated)
```

### Output Section:
```
15
150
1650
...
(Full output data, not truncated)
```

### Performance Summary:
```
📝 Number of Input Lines: 100

📦 Test Size: 100 elements
⏱️  Time per Element: 0.015 ms
💾 Memory per Element: 0.025 MB

⚡ Total Execution Time: 0.015 seconds
🎯 Total Memory Used: 2.50 MB

✅ Performance within acceptable limits
```

## Testing

To test the updated worker:
1. Run the application: `py -m src.app`
2. Go to Benchmarker tab
3. Set up generator and test files
4. Run benchmark tests
5. Click on any test card to open detail dialog
6. Verify:
   - Input section shows full input data
   - Output section shows full output data
   - Performance Summary shows correct line count
   - Line count matches actual input lines

## Migration Notes

**Signal Compatibility:**
- All existing code that emits the old 6-parameter signal will need to be updated
- The worker now always emits 9 parameters
- `BenchmarkerStatusView.on_test_completed()` has default parameters for backward compatibility

**Testing Requirements:**
- Integration tests may need updates to match new signal signature
- Any mocks or test fixtures should emit 9 parameters instead of 6

## Files Modified

1. `src/app/core/tools/specialized/benchmark_test_worker.py`
   - Updated `testCompleted` signal signature
   - Modified test result storage to include full I/O and test_size
   - Updated signal emission calls
   - Enhanced `_create_error_result()` method

2. `src/app/core/tools/benchmarker.py`
   - Updated `testCompleted` signal signature to match worker

3. `src/app/presentation/views/benchmarker/benchmarker_status_view.py`
   - Updated `on_test_completed()` method signature
   - Enhanced test_data storage with I/O fields

4. `src/app/presentation/widgets/test_detail_view.py`
   - Already updated in previous commit to accept I/O data

## Conclusion

The benchmarker system now has complete input/output data capture and display capabilities, matching the functionality of the validator system. Users can see exactly what input was generated, what output was produced, and how many lines of input were processed, providing much better context for performance analysis and debugging.
