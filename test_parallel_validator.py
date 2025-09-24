#!/usr/bin/env python3
"""
Test script to verify the parallel validator implementation works correctly.
"""

import sys
import os
import tempfile
import time
from multiprocessing import cpu_count

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app.core.tools.validator_runner import ValidatorTestWorker


def create_dummy_executables(workspace_dir):
    """Create dummy executables for testing"""
    
    # Create generator script (Python instead of exe for simplicity)
    generator_script = os.path.join(workspace_dir, 'generator.py')
    with open(generator_script, 'w') as f:
        f.write('''
import random
import sys
print(random.randint(1, 100))
''')
    
    # Create test script
    test_script = os.path.join(workspace_dir, 'test.py')
    with open(test_script, 'w') as f:
        f.write('''
import sys
n = int(input())
print(n * 2)
''')
    
    # Create validator script  
    validator_script = os.path.join(workspace_dir, 'validator.py')
    with open(validator_script, 'w') as f:
        f.write('''
import sys
if len(sys.argv) != 3:
    sys.exit(2)
    
with open(sys.argv[1], 'r') as f:
    input_val = int(f.read().strip())
    
with open(sys.argv[2], 'r') as f:
    output_val = int(f.read().strip())

# Validate: output should be input * 2
if output_val == input_val * 2:
    sys.exit(1)  # Valid
else:
    sys.exit(0)  # Invalid
''')
    
    # Return executables dict (using python to run scripts)
    return {
        'generator': f'python {generator_script}',
        'test': f'python {test_script}',
        'validator': f'python {validator_script}'
    }


def test_parallel_performance():
    """Test that parallel execution is actually faster"""
    print("Testing parallel validator performance...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        executables = create_dummy_executables(temp_dir)
        test_count = 2000
        
        print(f"Running {test_count} tests...")
        print(f"Available CPU cores: {cpu_count()}")
        
        # Test with single worker (sequential)
        print("\n--- Sequential execution (1 worker) ---")
        start_time = time.time()
        worker_sequential = ValidatorTestWorker(temp_dir, executables, test_count, max_workers=1)
        
        # Mock the Qt signals for testing
        class MockSignal:
            def emit(self, *args):
                pass
        
        worker_sequential.testStarted = MockSignal()
        worker_sequential.testCompleted = MockSignal()
        worker_sequential.allTestsCompleted = MockSignal()
        
        worker_sequential.run_tests()
        sequential_time = time.time() - start_time
        print(f"Sequential time: {sequential_time:.2f} seconds")
        
        # Test with multiple workers (parallel)
        print(f"\n--- Parallel execution ({cpu_count()-1} workers) ---")
        start_time = time.time()
        worker_parallel = ValidatorTestWorker(temp_dir, executables, test_count, max_workers=cpu_count()-1)
        
        worker_parallel.testStarted = MockSignal()
        worker_parallel.testCompleted = MockSignal()
        worker_parallel.allTestsCompleted = MockSignal()
        
        worker_parallel.run_tests()
        parallel_time = time.time() - start_time
        print(f"Parallel time: {parallel_time:.2f} seconds")
        
        # Calculate speedup
        speedup = sequential_time / parallel_time if parallel_time > 0 else 0
        print(f"\nSpeedup: {speedup:.2f}x")
        
        if speedup > 1.5:
            print("✅ Parallel execution is significantly faster!")
        elif speedup > 1.1:
            print("✅ Parallel execution shows improvement")
        else:
            print("⚠️  Parallel execution may not be showing expected speedup")
            
        return speedup > 1.1


if __name__ == "__main__":
    try:
        success = test_parallel_performance()
        if success:
            print("\n✅ Parallel validator implementation test PASSED")
        else:
            print("\n❌ Parallel validator implementation test FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)