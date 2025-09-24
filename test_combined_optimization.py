#!/usr/bin/env python3
"""
Performance test for the fully optimized validator with parallel execution + I/O optimization.
"""

import time
import tempfile
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

def create_test_executables(workspace_dir):
    """Create test executables that simulate real validator behavior"""
    
    # Generator: Creates test input
    generator_script = os.path.join(workspace_dir, 'generator.py')
    with open(generator_script, 'w') as f:
        f.write('''
import random
import time
# Simulate some computation time
time.sleep(0.01)  # 10ms to simulate real generator work
print(random.randint(1, 1000))
''')
    
    # Test solution: Processes input  
    test_script = os.path.join(workspace_dir, 'test.py')
    with open(test_script, 'w') as f:
        f.write('''
import sys
import time
# Simulate computation time
time.sleep(0.005)  # 5ms to simulate real solution work
n = int(input())
print(n * 2)
''')
    
    # Validator: Checks if output is correct
    validator_script = os.path.join(workspace_dir, 'validator.py')
    with open(validator_script, 'w') as f:
        f.write('''
import sys
import time
# Simulate validation time
time.sleep(0.003)  # 3ms to simulate real validator work

if len(sys.argv) != 3:
    sys.exit(2)
    
with open(sys.argv[1], 'r') as f:
    input_val = int(f.read().strip())
    
with open(sys.argv[2], 'r') as f:
    output_val = int(f.read().strip())

# Check if output is double the input
if output_val == input_val * 2:
    sys.exit(1)  # Valid  
else:
    sys.exit(0)  # Invalid
''')
    
    return {
        'generator': f'python {generator_script}',
        'test': f'python {test_script}',
        'validator': f'python {validator_script}'
    }

def run_single_test_original(test_number, workspace_dir, executables):
    """Original approach: sequential + file I/O"""
    try:
        # Stage 1: Generator -> file
        input_file = os.path.join(workspace_dir, f"input_{test_number}.txt")
        with open(input_file, "w") as f:
            result = subprocess.run(
                executables['generator'].split(),
                stdout=f,
                stderr=subprocess.PIPE,
                timeout=10
            )
        
        if result.returncode != 0:
            return False
        
        # Stage 2: Test solution file->file  
        output_file = os.path.join(workspace_dir, f"output_{test_number}.txt")
        with open(input_file, "r") as inp, open(output_file, "w") as out:
            result = subprocess.run(
                executables['test'].split(),
                stdin=inp,
                stdout=out,
                stderr=subprocess.PIPE,
                timeout=10
            )
        
        if result.returncode != 0:
            return False
        
        # Stage 3: Validator with files
        result = subprocess.run(
            executables['validator'].split() + [input_file, output_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10
        )
        
        # Cleanup
        try:
            os.unlink(input_file)
            os.unlink(output_file)
        except:
            pass
        
        return result.returncode == 1
        
    except Exception:
        return False

def run_single_test_optimized(test_number, workspace_dir, executables):
    """Optimized approach: memory pipes + temp files"""
    try:
        # Stage 1: Generator -> memory
        result = subprocess.run(
            executables['generator'].split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            text=True
        )
        
        if result.returncode != 0:
            return False
        
        input_text = result.stdout
        
        # Stage 2: Test solution memory->memory
        result = subprocess.run(
            executables['test'].split(),
            input=input_text,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            text=True
        )
        
        if result.returncode != 0:
            return False
        
        test_output = result.stdout
        
        # Stage 3: Validator with optimized temp files
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as input_temp:
            input_temp.write(input_text)
            input_temp.flush()
            input_path = input_temp.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as output_temp:
            output_temp.write(test_output)
            output_temp.flush()
            output_path = output_temp.name
        
        try:
            result = subprocess.run(
                executables['validator'].split() + [input_path, output_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
                text=True
            )
            
            return result.returncode == 1
            
        finally:
            try:
                os.unlink(input_path)
                os.unlink(output_path)
            except:
                pass
        
    except Exception:
        return False

def benchmark_validator_performance():
    """Compare original vs optimized validator performance"""
    
    with tempfile.TemporaryDirectory() as workspace:
        executables = create_test_executables(workspace)
        test_count = 40
        max_workers = min(8, max(1, multiprocessing.cpu_count() - 1))
        
        print(f"🧪 Validator Performance Benchmark")
        print(f"Tests: {test_count}")
        print(f"CPU cores: {multiprocessing.cpu_count()}")
        print(f"Max workers: {max_workers}")
        print("-" * 50)
        
        # Test 1: Original sequential approach
        print("\\n1️⃣  Original: Sequential + File I/O")
        start_time = time.time()
        
        original_results = []
        for i in range(test_count):
            result = run_single_test_original(i, workspace, executables)
            original_results.append(result)
        
        original_time = time.time() - start_time
        original_passed = sum(original_results)
        print(f"   Time: {original_time:.3f}s")
        print(f"   Passed: {original_passed}/{test_count}")
        
        # Test 2: Parallel + Original I/O  
        print("\\n2️⃣  Parallel + File I/O")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            parallel_orig_results = list(executor.map(
                lambda i: run_single_test_original(i, workspace, executables),
                range(test_count)
            ))
        
        parallel_orig_time = time.time() - start_time
        parallel_orig_passed = sum(parallel_orig_results)
        print(f"   Time: {parallel_orig_time:.3f}s")
        print(f"   Passed: {parallel_orig_passed}/{test_count}")
        
        # Test 3: Sequential + Optimized I/O
        print("\\n3️⃣  Sequential + Optimized I/O")
        start_time = time.time()
        
        optimized_seq_results = []
        for i in range(test_count):
            result = run_single_test_optimized(i, workspace, executables)
            optimized_seq_results.append(result)
        
        optimized_seq_time = time.time() - start_time
        optimized_seq_passed = sum(optimized_seq_results)
        print(f"   Time: {optimized_seq_time:.3f}s")
        print(f"   Passed: {optimized_seq_passed}/{test_count}")
        
        # Test 4: Parallel + Optimized I/O (our final approach)
        print("\\n4️⃣  Parallel + Optimized I/O (Final)")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            final_results = list(executor.map(
                lambda i: run_single_test_optimized(i, workspace, executables),
                range(test_count)
            ))
        
        final_time = time.time() - start_time
        final_passed = sum(final_results)
        print(f"   Time: {final_time:.3f}s")
        print(f"   Passed: {final_passed}/{test_count}")
        
        # Performance analysis
        print("\\n" + "=" * 50)
        print("📊 PERFORMANCE ANALYSIS")
        print("=" * 50)
        
        parallel_speedup = original_time / parallel_orig_time
        io_speedup = original_time / optimized_seq_time  
        combined_speedup = original_time / final_time
        
        print(f"Parallelization alone: {parallel_speedup:.2f}x speedup")
        print(f"I/O optimization alone: {io_speedup:.2f}x speedup")
        print(f"Combined optimization: {combined_speedup:.2f}x speedup")
        
        print(f"\\n🎯 TOTAL PERFORMANCE GAIN: {combined_speedup:.1f}x faster")
        
        if combined_speedup > 3.0:
            print("🚀 EXCELLENT: Major performance improvement!")
        elif combined_speedup > 2.0:
            print("✅ GOOD: Significant performance improvement!")  
        elif combined_speedup > 1.5:
            print("👍 DECENT: Noticeable performance improvement!")
        else:
            print("⚠️  MINIMAL: Limited performance improvement")
            
        return {
            'original_time': original_time,
            'final_time': final_time,
            'speedup': combined_speedup,
            'parallel_contribution': parallel_speedup,
            'io_contribution': io_speedup
        }

if __name__ == "__main__":
    try:
        results = benchmark_validator_performance()
        print(f"\\n✅ Benchmark completed successfully")
        print(f"Final optimized validator is {results['speedup']:.1f}x faster")
    except Exception as e:
        print(f"\\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()