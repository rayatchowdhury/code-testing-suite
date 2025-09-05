"""
Performance baseline benchmarking.
Run before and after migration to ensure no performance regression.
"""
import time
import psutil
import sys
import json
from pathlib import Path
import importlib

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def benchmark_imports():
    """Benchmark import performance"""
    modules_to_test = [
        'main',
        'views.main_window',
        'widgets.sidebar',
        'utils.window_manager',
        'database.database_manager',
        'ai.core.editor_ai'
    ]
    
    results = {}
    
    for module_name in modules_to_test:
        # Clear module if already imported
        if module_name in sys.modules:
            del sys.modules[module_name]
        
        start_time = time.perf_counter()
        try:
            importlib.import_module(module_name)
            end_time = time.perf_counter()
            results[module_name] = end_time - start_time
        except ImportError as e:
            results[module_name] = f"FAILED: {e}"
    
    return results

def benchmark_memory():
    """Benchmark memory usage"""
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Import all core modules
    import main
    from views import main_window
    from widgets import sidebar, display_area
    from utils import window_manager
    from database import database_manager
    
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_used = final_memory - initial_memory
    
    return {
        'initial_memory_mb': initial_memory,
        'final_memory_mb': final_memory, 
        'memory_used_mb': memory_used
    }

if __name__ == "__main__":
    print("=== PERFORMANCE BASELINE ===")
    
    print("\n📦 Import Performance:")
    import_results = benchmark_imports()
    for module, time_taken in import_results.items():
        if isinstance(time_taken, float):
            print(f"  {module:<30}: {time_taken*1000:6.2f}ms")
        else:
            print(f"  {module:<30}: {time_taken}")
    
    print("\n💾 Memory Usage:")
    memory_results = benchmark_memory()
    for metric, value in memory_results.items():
        print(f"  {metric:<20}: {value:6.1f} MB")
    
    # Save baseline for comparison
    baseline_data = {
        'imports': {k: v for k, v in import_results.items() if isinstance(v, float)},
        'memory': memory_results,
        'timestamp': time.time()
    }
    
    baseline_file = Path(__file__).parent / 'performance_baseline.json'
    with open(baseline_file, 'w') as f:
        json.dump(baseline_data, f, indent=2)
    
    print(f"\n✅ Baseline saved to {baseline_file}")
