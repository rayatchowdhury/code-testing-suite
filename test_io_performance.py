#!/usr/bin/env python3
"""
Performance test comparing file I/O vs in-memory approaches for validator.
"""

import time
import tempfile
import os
from io import StringIO
import subprocess

def test_file_io_performance():
    """Test different I/O approaches for validator performance"""
    
    test_data = {
        'input': "42\n10 20 30\nhello world\n" * 100,  # Larger test data
        'output': "84\n60\nhello world hello world\n" * 100
    }
    
    num_tests = 50
    
    print("Testing I/O performance for validator...")
    print(f"Test data size: {len(test_data['input'])} chars input, {len(test_data['output'])} chars output")
    print(f"Running {num_tests} iterations of each approach...\n")
    
    # Method 1: Traditional file I/O (current approach)
    print("--- Method 1: Traditional File I/O ---")
    start_time = time.time()
    
    for i in range(num_tests):
        input_file_path = f"temp_input_{i}.txt"
        output_file_path = f"temp_output_{i}.txt"
        
        # Write files
        with open(input_file_path, "w") as f:
            f.write(test_data['input'])
        with open(output_file_path, "w") as f:
            f.write(test_data['output'])
        
        # Read files back (simulating validator reading)
        with open(input_file_path, "r") as f:
            read_input = f.read()
        with open(output_file_path, "r") as f:
            read_output = f.read()
        
        # Cleanup
        os.unlink(input_file_path)
        os.unlink(output_file_path)
    
    traditional_time = time.time() - start_time
    print(f"Traditional file I/O: {traditional_time:.4f} seconds")
    
    # Method 2: NamedTemporaryFile (optimized approach)
    print("\n--- Method 2: NamedTemporaryFile ---")
    start_time = time.time()
    
    for i in range(num_tests):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as input_temp:
            input_temp.write(test_data['input'])
            input_temp.flush()
            input_path = input_temp.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as output_temp:
            output_temp.write(test_data['output'])
            output_temp.flush()
            output_path = output_temp.name
        
        # Read back
        with open(input_path, 'r') as f:
            read_input = f.read()
        with open(output_path, 'r') as f:
            read_output = f.read()
        
        # Cleanup
        os.unlink(input_path)
        os.unlink(output_path)
    
    temp_file_time = time.time() - start_time
    print(f"NamedTemporaryFile: {temp_file_time:.4f} seconds")
    
    # Method 3: In-memory only (theoretical best case)
    print("\n--- Method 3: Pure In-Memory ---")
    start_time = time.time()
    
    for i in range(num_tests):
        # Simulate reading from memory
        read_input = test_data['input']
        read_output = test_data['output']
        
        # Simulate some processing
        result = len(read_input) + len(read_output)
    
    memory_time = time.time() - start_time
    print(f"Pure in-memory: {memory_time:.4f} seconds")
    
    # Calculate improvements
    print("\n--- Performance Comparison ---")
    traditional_vs_temp = traditional_time / temp_file_time
    traditional_vs_memory = traditional_time / memory_time
    temp_vs_memory = temp_file_time / memory_time
    
    print(f"NamedTemporaryFile is {traditional_vs_temp:.2f}x faster than traditional I/O")
    print(f"Pure memory is {traditional_vs_memory:.2f}x faster than traditional I/O")  
    print(f"Pure memory is {temp_vs_memory:.2f}x faster than NamedTemporaryFile")
    
    return {
        'traditional': traditional_time,
        'temp_file': temp_file_time,
        'memory': memory_time
    }

if __name__ == "__main__":
    results = test_file_io_performance()
    
    print(f"\n✅ File I/O optimization analysis complete")
    print(f"Recommended: Use NamedTemporaryFile for {results['traditional']/results['temp_file']:.1f}x speedup")
    if results['traditional']/results['temp_file'] > 2.0:
        print("🚀 Significant I/O performance gains possible!")