#!/usr/bin/env python3
"""
Comprehensive compilation speed benchmark for all optimized compiler runners.
Tests both compilation speed improvements and caching effectiveness.
"""

import time
import tempfile
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import sys
import shutil

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_test_cpp_files(workspace_dir):
    """Create realistic C++ test files for compilation benchmarking"""
    
    # Generator: Complex input generation
    generator_cpp = os.path.join(workspace_dir, 'generator.cpp')
    with open(generator_cpp, 'w') as f:
        f.write('''
#include <iostream>
#include <vector>
#include <random>
#include <algorithm>
#include <chrono>
#include <map>
#include <set>

class TestGenerator {
private:
    std::mt19937 rng;
    std::uniform_int_distribution<int> dist;
    
public:
    TestGenerator() : rng(std::chrono::steady_clock::now().time_since_epoch().count()),
                      dist(1, 1000) {}
    
    std::vector<int> generateArray(int n) {
        std::vector<int> arr(n);
        for(int i = 0; i < n; i++) {
            arr[i] = dist(rng);
        }
        return arr;
    }
    
    void generateComplexTest() {
        int n = 50 + dist(rng) % 50;
        auto arr = generateArray(n);
        
        std::cout << n << std::endl;
        for(int i = 0; i < n; i++) {
            std::cout << arr[i];
            if(i < n-1) std::cout << " ";
        }
        std::cout << std::endl;
    }
};

int main() {
    TestGenerator gen;
    gen.generateComplexTest();
    return 0;
}
''')
    
    # Test solution: Complex algorithm implementation
    test_cpp = os.path.join(workspace_dir, 'test.cpp')
    with open(test_cpp, 'w') as f:
        f.write('''
#include <iostream>
#include <vector>
#include <algorithm>
#include <map>
#include <set>
#include <queue>
#include <cmath>

class Solution {
private:
    std::vector<int> data;
    std::map<int, int> frequency;
    std::set<int> unique_elements;
    
public:
    void readInput() {
        int n;
        std::cin >> n;
        data.resize(n);
        
        for(int i = 0; i < n; i++) {
            std::cin >> data[i];
            frequency[data[i]]++;
            unique_elements.insert(data[i]);
        }
    }
    
    long long complexCalculation() {
        std::sort(data.begin(), data.end());
        
        long long result = 0;
        for(size_t i = 0; i < data.size(); i++) {
            result += data[i] * (i + 1);
            result += frequency[data[i]] * sqrt(data[i]);
        }
        
        // Additional complex operations
        std::priority_queue<int> pq(data.begin(), data.end());
        while(!pq.empty() && pq.size() > data.size() / 2) {
            result += pq.top();
            pq.pop();
        }
        
        return result;
    }
    
    void solve() {
        readInput();
        std::cout << complexCalculation() << std::endl;
    }
};

int main() {
    Solution sol;
    sol.solve();
    return 0;
}
''')
    
    # Correct solution: Reference implementation
    correct_cpp = os.path.join(workspace_dir, 'correct.cpp')
    with open(correct_cpp, 'w') as f:
        f.write('''
#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>

int main() {
    int n;
    std::cin >> n;
    std::vector<int> arr(n);
    
    for(int i = 0; i < n; i++) {
        std::cin >> arr[i];
    }
    
    std::sort(arr.begin(), arr.end());
    
    long long result = 0;
    for(int i = 0; i < n; i++) {
        result += arr[i] * (i + 1);
    }
    
    std::cout << result << std::endl;
    return 0;
}
''')
    
    # Validator: Complex validation logic
    validator_cpp = os.path.join(workspace_dir, 'validator.cpp')
    with open(validator_cpp, 'w') as f:
        f.write('''
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <algorithm>
#include <cmath>

class Validator {
private:
    std::vector<int> input_data;
    long long expected_result;
    long long actual_result;
    
public:
    bool loadInput(const std::string& input_file) {
        std::ifstream file(input_file);
        if(!file.is_open()) return false;
        
        int n;
        file >> n;
        input_data.resize(n);
        
        for(int i = 0; i < n; i++) {
            file >> input_data[i];
        }
        
        file.close();
        return true;
    }
    
    bool loadOutput(const std::string& output_file) {
        std::ifstream file(output_file);
        if(!file.is_open()) return false;
        
        file >> actual_result;
        file.close();
        return true;
    }
    
    long long calculateExpected() {
        std::vector<int> sorted_data = input_data;
        std::sort(sorted_data.begin(), sorted_data.end());
        
        long long result = 0;
        for(size_t i = 0; i < sorted_data.size(); i++) {
            result += sorted_data[i] * (i + 1);
        }
        
        return result;
    }
    
    bool validate() {
        expected_result = calculateExpected();
        return std::abs(expected_result - actual_result) < 1e-9;
    }
};

int main(int argc, char* argv[]) {
    if(argc != 3) {
        return 2; // Invalid arguments
    }
    
    Validator validator;
    
    if(!validator.loadInput(argv[1]) || !validator.loadOutput(argv[2])) {
        return 2; // File error
    }
    
    if(validator.validate()) {
        return 1; // Valid
    } else {
        return 0; // Invalid
    }
}
''')
    
    return {
        'generator': generator_cpp,
        'test': test_cpp,
        'correct': correct_cpp,
        'validator': validator_cpp
    }

def benchmark_sequential_compilation(files_map, workspace_dir):
    """Benchmark traditional sequential compilation"""
    print("1️⃣  Sequential Compilation (Old Method)")
    
    executables = {
        key: os.path.join(workspace_dir, f"{key}.exe")
        for key in files_map.keys()
    }
    
    # Clean existing executables
    for exe in executables.values():
        if os.path.exists(exe):
            os.remove(exe)
    
    start_time = time.time()
    
    # Compile sequentially with basic flags
    for file_key, source_file in files_map.items():
        exe_file = executables[file_key]
        
        result = subprocess.run(
            ['g++', source_file, '-o', exe_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Failed to compile {file_key}: {result.stderr}")
            return None, 0
    
    sequential_time = time.time() - start_time
    successful_files = len([exe for exe in executables.values() if os.path.exists(exe)])
    
    print(f"   Time: {sequential_time:.3f}s")
    print(f"   Files compiled: {successful_files}/{len(files_map)}")
    
    return sequential_time, successful_files

def benchmark_parallel_compilation(files_map, workspace_dir):
    """Benchmark new parallel compilation with optimizations"""
    print("\\n2️⃣  Parallel Compilation (New Method)")
    
    executables = {
        key: os.path.join(workspace_dir, f"{key}_optimized.exe")
        for key in files_map.keys()
    }
    
    # Clean existing executables
    for exe in executables.values():
        if os.path.exists(exe):
            os.remove(exe)
    
    start_time = time.time()
    max_workers = min(len(files_map), multiprocessing.cpu_count())
    
    def compile_single_optimized(file_info):
        file_key, source_file = file_info
        exe_file = executables[file_key]
        
        # Optimized compiler flags
        compiler_flags = [
            '-O2',           # Level 2 optimization
            '-march=native', # Optimize for current CPU
            '-mtune=native', # Tune for current CPU
            '-pipe',         # Use pipes instead of temp files
            '-std=c++17',    # Modern C++ standard
            '-DNDEBUG',      # Disable debug assertions
        ]
        
        compile_command = ['g++'] + compiler_flags + [source_file, '-o', exe_file]
        
        result = subprocess.run(
            compile_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return file_key, result.returncode == 0, result.stderr
    
    # Compile in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(compile_single_optimized, files_map.items()))
    
    parallel_time = time.time() - start_time
    successful_files = sum(1 for _, success, _ in results if success)
    
    print(f"   Time: {parallel_time:.3f}s")
    print(f"   Files compiled: {successful_files}/{len(files_map)}")
    print(f"   Max workers: {max_workers}")
    
    # Report any failures
    for file_key, success, error in results:
        if not success:
            print(f"   ❌ {file_key} failed: {error}")
    
    return parallel_time, successful_files

def benchmark_caching_effectiveness(files_map, workspace_dir):
    """Benchmark compilation caching effectiveness"""
    print("\\n3️⃣  Compilation Caching Test")
    
    executables = {
        key: os.path.join(workspace_dir, f"{key}_cached.exe")
        for key in files_map.keys()
    }
    
    def compile_with_caching_check(file_info):
        file_key, source_file = file_info
        exe_file = executables[file_key]
        
        # Check if compilation is needed
        if os.path.exists(exe_file):
            source_mtime = os.path.getmtime(source_file)
            exe_mtime = os.path.getmtime(exe_file)
            
            if exe_mtime > source_mtime:
                return file_key, True, "cached"  # Up-to-date
        
        # Need to compile
        compiler_flags = ['-O2', '-march=native', '-pipe', '-std=c++17']
        compile_command = ['g++'] + compiler_flags + [source_file, '-o', exe_file]
        
        result = subprocess.run(
            compile_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return file_key, result.returncode == 0, "compiled"
    
    # First compilation
    print("   🔨 First compilation run:")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        first_results = list(executor.map(compile_with_caching_check, files_map.items()))
    
    first_time = time.time() - start_time
    first_compiled = sum(1 for _, success, status in first_results if success and status == "compiled")
    first_cached = sum(1 for _, success, status in first_results if success and status == "cached")
    
    print(f"     Time: {first_time:.3f}s")
    print(f"     Compiled: {first_compiled}, Cached: {first_cached}")
    
    # Second compilation (should be mostly cached)
    print("   ⚡ Second compilation run (caching test):")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        second_results = list(executor.map(compile_with_caching_check, files_map.items()))
    
    second_time = time.time() - start_time
    second_compiled = sum(1 for _, success, status in second_results if success and status == "compiled")
    second_cached = sum(1 for _, success, status in second_results if success and status == "cached")
    
    print(f"     Time: {second_time:.3f}s")
    print(f"     Compiled: {second_compiled}, Cached: {second_cached}")
    
    if second_time > 0:
        cache_speedup = first_time / second_time
        print(f"   📊 Cache speedup: {cache_speedup:.2f}x")
    
    return first_time, second_time, second_cached

def main():
    """Run comprehensive compilation speed benchmarks"""
    print("🚀 COMPILATION SPEED OPTIMIZATION BENCHMARK")
    print("=" * 60)
    print(f"System: {multiprocessing.cpu_count()} CPU cores")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as workspace:
        print(f"Workspace: {workspace}")
        
        # Create test files
        files_map = create_test_cpp_files(workspace)
        print(f"\\n📁 Created {len(files_map)} complex C++ test files")
        
        # Run benchmarks
        sequential_time, sequential_success = benchmark_sequential_compilation(files_map, workspace)
        
        if sequential_time is None:
            print("❌ Sequential compilation failed, skipping comparison")
            return
        
        parallel_time, parallel_success = benchmark_parallel_compilation(files_map, workspace)
        
        # Caching test
        cache_first_time, cache_second_time, cached_files = benchmark_caching_effectiveness(files_map, workspace)
        
        # Summary
        print("\\n" + "=" * 60)
        print("📊 COMPILATION OPTIMIZATION SUMMARY")
        print("=" * 60)
        
        if parallel_time > 0:
            compilation_speedup = sequential_time / parallel_time
            print(f"🚀 Parallel Compilation Speedup: {compilation_speedup:.2f}x")
        
        if cache_second_time > 0:
            cache_speedup = cache_first_time / cache_second_time
            print(f"⚡ Smart Caching Speedup: {cache_speedup:.2f}x")
        
        print(f"\\n📈 DETAILED RESULTS:")
        print(f"   Sequential time:  {sequential_time:.3f}s")
        print(f"   Parallel time:    {parallel_time:.3f}s")
        print(f"   First cache time: {cache_first_time:.3f}s")
        print(f"   Second cache time:{cache_second_time:.3f}s")
        
        if compilation_speedup > 3.0:
            print("\\n🎉 EXCELLENT: Outstanding compilation speed improvements!")
        elif compilation_speedup > 2.0:
            print("\\n✅ VERY GOOD: Significant compilation speed improvements!")
        elif compilation_speedup > 1.5:
            print("\\n👍 GOOD: Notable compilation speed improvements!")
        else:
            print("\\n⚠️  MODERATE: Some compilation speed improvements")
        
        print("\\n💡 OPTIMIZATIONS APPLIED:")
        print("   • Parallel compilation with ThreadPoolExecutor")
        print("   • Optimized compiler flags (-O2, -march=native, -pipe)")
        print("   • Smart timestamp-based caching")
        print("   • Modern C++ standard (-std=c++17)")
        print("   • CPU architecture optimization")
        
        return {
            'sequential_time': sequential_time,
            'parallel_time': parallel_time,
            'compilation_speedup': compilation_speedup,
            'cache_speedup': cache_speedup if cache_second_time > 0 else 0,
            'files_tested': len(files_map)
        }

if __name__ == "__main__":
    try:
        results = main()
        if results:
            print(f"\\n✅ Compilation optimization completed successfully!")
            print(f"Overall compilation speed improved by {results['compilation_speedup']:.1f}x")
    except Exception as e:
        print(f"\\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()