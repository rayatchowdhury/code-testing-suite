# Enhanced Benchmarker - Memory and Performance Monitoring

## Summary of Changes

The benchmarker has been enhanced to provide comprehensive performance monitoring including:

### 1. Test Count Slider
- **Location**: `src/app/presentation/views/benchmarker/test_count_slider.py`
- **Range**: 1 to 100 tests
- **Default**: 5 tests
- **Purpose**: Run multiple benchmark tests for statistical reliability

### 2. Limits Input Widget
- **Location**: `src/app/presentation/views/benchmarker/limits_input_widget.py`
- **Layout**: Parallel input boxes with divider
- **Time Limit**: 10ms to 60,000ms (1 minute) range
- **Memory Limit**: 1MB to 8,192MB (8GB) range
- **Style**: Bordered input boxes with labels positioned above
- **Section Name**: "Limits" with both inputs in the same section

### 3. Enhanced Memory Monitoring
- **Technology**: Uses `psutil` library for real-time memory tracking
- **Monitoring**: Tracks RSS (Resident Set Size) memory usage during execution
- **Resolution**: Samples every 10ms for accurate peak memory detection

### 4. Enhanced TLE Runner
- **Location**: `src/app/core/tools/tle_runner.py`
- **Features**:
  - Multiple test execution support
  - Memory usage monitoring for both generator and test programs
  - Pass/fail status based on both time and memory limits
  - Detailed performance metrics storage
  - Real-time process monitoring
  - Unique input/output files for each test (input_1.txt, input_2.txt, etc.)

### 5. Enhanced Benchmark Status Window
- **Location**: `src/app/presentation/views/benchmarker/benchmark_status_window.py`
- **New Features**:
  - Progress bar for multiple tests
  - Memory usage display with limit comparison
  - Color-coded status (green for pass, red for exceed limits)
  - Detailed history showing both time and memory for each test
  - Constraint violation reporting (time vs memory)
  - Test numbering and progress tracking

### 6. Enhanced Database Storage
- **Memory Metrics**: Stores peak memory usage, memory limits
- **Test Count**: Records number of tests executed
- **Performance Ratios**: Calculates time and memory utilization ratios
- **Detailed Analysis**: Tracks which constraint was violated (time/memory)

## How It Works

1. **Test Execution**: 
   - Multiple test cycles are executed based on the test count slider
   - Each test generates unique input using the generator
   - Programs are executed with `psutil` monitoring
   - Memory usage is sampled every 10ms
   - Peak memory usage is recorded for each test

2. **Constraint Checking**:
   - Time limit: Compared against execution duration for each test
   - Memory limit: Compared against peak memory usage for each test
   - Overall pass: Both constraints must be satisfied for each test

3. **Result Display**:
   - Real-time status updates during execution
   - Progress bar showing test completion (e.g., "Test 3/10")
   - Color-coded results (green=pass, red=fail)
   - Detailed breakdown showing which limits were exceeded
   - History panel showing all test results with metrics

## Usage

1. Set number of tests using the test count slider (1-100)
2. Set time limit using the time input box (ms)  
3. Set memory limit using the memory input box (MB)
4. Write generator.cpp and test.cpp in the benchmarker
5. Click "Compile" to build the programs
6. Click "Run" to execute multiple tests with monitoring
7. View real-time progress and results with time and memory metrics
8. Check "Results" panel for detailed performance history

## Example Output

For multiple tests:
```
Running Test 3 - Solution (3/10)
Progress: [████████████████████████████████████████████████████████████████████████████████████] 60%

Test 3 - Solution: ✓
Time taken: 0.123s (limit: 1.000s)
Memory used: 45.67 MB (limit: 256 MB)
```

History shows all tests:
```
Test 10 - Solution: ✓  Time: 0.134s  Memory: 67.23 MB
Test 10 - Generator: ✓  Time: 0.045s  Memory: 12.45 MB
Test 9 - Solution: ✗  Time: 1.200s  Memory: 89.12 MB
Test 9 - Generator: ✓  Time: 0.038s  Memory: 11.23 MB
...
```

## Technical Implementation

- **Memory Monitoring**: `psutil.Process().memory_info().rss`
- **Time Monitoring**: Standard `time.time()` with subprocess timeout
- **Multiple Tests**: Loop-based execution with unique file naming
- **Process Management**: Proper cleanup on timeout or memory exceed
- **Data Storage**: Enhanced database schema with memory and test count metrics
- **UI Updates**: Real-time signal-slot architecture for status updates
- **Progress Tracking**: Progress bar calculation based on test completion
