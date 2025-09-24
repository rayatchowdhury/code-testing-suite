"""
Test script to validate the new base classes work correctly.
"""

import os
import tempfile
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_base_compiler():
    """Test BaseCompiler functionality."""
    print("Testing BaseCompiler...")
    
    from src.app.core.tools.base import BaseCompiler
    
    # Create temporary workspace
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a simple C++ file
        test_file = os.path.join(temp_dir, "test.cpp")
        with open(test_file, 'w') as f:
            f.write('''
#include <iostream>
int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
''')
        
        files_dict = {"test": test_file}
        compiler = BaseCompiler(temp_dir, files_dict)
        
        # Test compiler flags
        flags = compiler.get_compiler_flags()
        assert '-O2' in flags
        assert '-std=c++17' in flags
        print("✅ BaseCompiler flags correct")
        
        # Test needs recompilation (executable doesn't exist)
        assert compiler._needs_recompilation("test") == True
        print("✅ BaseCompiler recompilation detection works")
        
    print("✅ BaseCompiler tests passed")


def test_process_executor():
    """Test ProcessExecutor functionality."""
    print("Testing ProcessExecutor...")
    
    from src.app.core.tools.base import ProcessExecutor
    
    # Test simple command execution (Windows compatible)
    if os.name == 'nt':
        result = ProcessExecutor.run_with_monitoring(['cmd', '/c', 'echo Hello World'], timeout=5.0)
    else:
        result = ProcessExecutor.run_with_monitoring(['echo', 'Hello World'], timeout=5.0)
    
    assert result.returncode == 0
    assert 'Hello World' in result.stdout
    print("✅ ProcessExecutor basic execution works")
    
    # Test timeout handling
    if os.name == 'nt':
        result = ProcessExecutor.run_with_monitoring(['cmd', '/c', 'timeout', '10'], timeout=1.0)
    else:
        result = ProcessExecutor.run_with_monitoring(['sleep', '10'], timeout=1.0)
    
    assert result.timed_out == True
    print("✅ ProcessExecutor timeout handling works")
    
    print("✅ ProcessExecutor tests passed")


def test_base_test_worker():
    """Test BaseTestWorker functionality."""
    print("Testing BaseTestWorker...")
    
    from src.app.core.tools.base import BaseTestWorker
    
    # Create a simple test worker implementation
    class TestWorker(BaseTestWorker):
        def _run_single_test(self, test_number):
            return {
                'test_number': test_number,
                'passed': test_number % 2 == 0,  # Even numbers pass
                'result': f'Test {test_number} result'
            }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        worker = TestWorker(temp_dir, {}, 4, max_workers=2)
        
        # Test optimal worker calculation
        assert worker.max_workers == 2
        print("✅ BaseTestWorker worker count configuration works")
        
        # Test error result creation
        error_result = worker._create_error_result(1, "Test error")
        assert error_result['test_number'] == 1
        assert error_result['passed'] == False
        assert 'Test error' in error_result['error_details']
        print("✅ BaseTestWorker error handling works")
        
    print("✅ BaseTestWorker tests passed")


def test_base_runner():
    """Test BaseRunner functionality."""
    print("Testing BaseRunner...")
    
    from src.app.core.tools.base import BaseRunner
    from src.app.persistence.database import TestResult
    
    # Create a simple runner implementation  
    class TestRunner(BaseRunner):
        def _create_test_worker(self, test_count, **kwargs):
            return None  # Not testing worker creation here
            
        def _create_test_result(self, all_passed, test_results, passed_tests, failed_tests, total_time):
            return TestResult(
                test_type=self.test_type,
                file_path=self._get_test_file_path(),
                test_count=len(test_results),
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                total_time=total_time,
                timestamp="2025-09-24T12:00:00",
                test_details="[]",
                project_name="test",
                files_snapshot="{}",
                mismatch_analysis="{}"
            )
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        test_file = os.path.join(temp_dir, "test.cpp") 
        with open(test_file, 'w') as f:
            f.write("int main(){return 0;}")
        
        files_dict = {"test": test_file}
        runner = TestRunner(temp_dir, files_dict, "test")
        
        # Test file path detection
        assert runner._get_test_file_path() == test_file
        print("✅ BaseRunner file path detection works")
        
        # Test compilation check
        assert runner.is_compiled() == False  # No executable exists yet
        print("✅ BaseRunner compilation status check works")
        
    print("✅ BaseRunner tests passed")


if __name__ == "__main__":
    try:
        test_base_compiler()
        test_process_executor()
        test_base_test_worker()
        test_base_runner()
        
        print("\n🎉 All base class tests passed successfully!")
        print("✅ Phase 1: Base Classes implementation complete")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)