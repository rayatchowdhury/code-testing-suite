"""
Phase 6 Task 3: Performance Benchmarking Tests
Measures query performance and storage efficiency at scale.

This benchmark suite validates:
1. SQL date filtering performance (7 days, 30 days, 90 days)
2. Test type filtering performance
3. Combined filter performance
4. Database storage growth
5. Query scaling (100, 500, 1000 results)
6. Files snapshot storage efficiency
7. SQL vs Python filtering comparison
"""

import pytest
import json
import tempfile
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

from src.app.persistence.database.database_manager import (
    DatabaseManager,
    TestResult
)
from tests.fixtures.test_adapters import TestDataFactory


class TestQueryPerformance:
    """Benchmark query performance at scale"""
    
    @pytest.fixture
    def small_db(self):
        """Database with 100 test results"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "benchmark_small.db"
            db = DatabaseManager(db_path=str(db_path))
            
            # Create 100 results spanning 100 days
            now = datetime.now()
            for i in range(100):
                result = TestDataFactory.create_test_result(
                    project_name=f"Project_{i:03d}",
                    test_type=["comparison", "validation", "benchmark"][i % 3],
                    test_count=10 + (i % 20),
                    passed_tests=5 + (i % 10),
                    failed_tests=(i % 5),
                    timestamp=(now - timedelta(days=i)).isoformat()
                )
                result.files_snapshot = json.dumps({
                    f"generator_{i}.py": f"# Generator {i}\n" + "x = 1\n" * 50,
                    f"correct_{i}.py": f"# Correct {i}\n" + "y = 2\n" * 50,
                })
                db.save_test_result(result)
            
            yield db
            if hasattr(db, 'connection') and db.connection:
                db.connection.close()
    
    @pytest.fixture
    def medium_db(self):
        """Database with 500 test results"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "benchmark_medium.db"
            db = DatabaseManager(db_path=str(db_path))
            
            # Create 500 results
            now = datetime.now()
            for i in range(500):
                result = TestDataFactory.create_test_result(
                    project_name=f"MediumProject_{i:04d}",
                    test_type=["comparison", "validation", "benchmark"][i % 3],
                    test_count=10 + (i % 20),
                    passed_tests=5 + (i % 10),
                    failed_tests=(i % 5),
                    timestamp=(now - timedelta(days=i % 180)).isoformat()
                )
                result.files_snapshot = json.dumps({
                    f"gen_{i}.py": f"# Gen {i}\n" + "x = 1\n" * 30,
                    f"sol_{i}.py": f"# Sol {i}\n" + "y = 2\n" * 30,
                })
                db.save_test_result(result)
            
            yield db
            if hasattr(db, 'connection') and db.connection:
                db.connection.close()
    
    @pytest.fixture
    def large_db(self):
        """Database with 1000 test results"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "benchmark_large.db"
            db = DatabaseManager(db_path=str(db_path))
            
            # Create 1000 results
            now = datetime.now()
            for i in range(1000):
                result = TestDataFactory.create_test_result(
                    project_name=f"LargeProject_{i:04d}",
                    test_type=["comparison", "validation", "benchmark"][i % 3],
                    test_count=10 + (i % 20),
                    passed_tests=5 + (i % 10),
                    failed_tests=(i % 5),
                    timestamp=(now - timedelta(days=i % 365)).isoformat()
                )
                result.files_snapshot = json.dumps({
                    f"g_{i}.py": f"# G{i}\n" + "x=1\n" * 20,
                    f"s_{i}.py": f"# S{i}\n" + "y=2\n" * 20,
                })
                db.save_test_result(result)
            
            yield db
            if hasattr(db, 'connection') and db.connection:
                db.connection.close()
    
    def test_sql_date_filter_7days_scaling(self, small_db, medium_db, large_db):
        """Benchmark SQL 7-day filter across different dataset sizes"""
        results = {}
        
        # Test 100 results
        start = time.perf_counter()
        small_results = small_db.get_test_results(days=7, limit=200)
        small_time = time.perf_counter() - start
        results['100_results'] = small_time
        
        # Test 500 results
        start = time.perf_counter()
        medium_results = medium_db.get_test_results(days=7, limit=200)
        medium_time = time.perf_counter() - start
        results['500_results'] = medium_time
        
        # Test 1000 results
        start = time.perf_counter()
        large_results = large_db.get_test_results(days=7, limit=200)
        large_time = time.perf_counter() - start
        results['1000_results'] = large_time
        
        # Print results
        print(f"\n⚡ SQL 7-Day Filter Performance Scaling:")
        print(f"  100 results:  {small_time*1000:.2f}ms ({len(small_results)} matches)")
        print(f"  500 results:  {medium_time*1000:.2f}ms ({len(medium_results)} matches)")
        print(f"  1000 results: {large_time*1000:.2f}ms ({len(large_results)} matches)")
        
        # Calculate scaling factor
        if small_time > 0:
            scale_10x = large_time / small_time
            print(f"  📊 10x data scaling factor: {scale_10x:.2f}x slower")
        
        # All should be fast (<200ms)
        assert small_time < 0.2, f"100 results query too slow: {small_time*1000:.2f}ms"
        assert medium_time < 0.2, f"500 results query too slow: {medium_time*1000:.2f}ms"
        assert large_time < 0.2, f"1000 results query too slow: {large_time*1000:.2f}ms"
    
    def test_sql_date_filter_30days_scaling(self, small_db, medium_db, large_db):
        """Benchmark SQL 30-day filter across different dataset sizes"""
        results = {}
        
        # Test 100 results
        start = time.perf_counter()
        small_results = small_db.get_test_results(days=30, limit=200)
        small_time = time.perf_counter() - start
        
        # Test 500 results
        start = time.perf_counter()
        medium_results = medium_db.get_test_results(days=30, limit=200)
        medium_time = time.perf_counter() - start
        
        # Test 1000 results
        start = time.perf_counter()
        large_results = large_db.get_test_results(days=30, limit=200)
        large_time = time.perf_counter() - start
        
        # Print results
        print(f"\n⚡ SQL 30-Day Filter Performance Scaling:")
        print(f"  100 results:  {small_time*1000:.2f}ms ({len(small_results)} matches)")
        print(f"  500 results:  {medium_time*1000:.2f}ms ({len(medium_results)} matches)")
        print(f"  1000 results: {large_time*1000:.2f}ms ({len(large_results)} matches)")
        
        # All should be fast
        assert small_time < 0.2, f"Query too slow: {small_time*1000:.2f}ms"
        assert medium_time < 0.2, f"Query too slow: {medium_time*1000:.2f}ms"
        assert large_time < 0.2, f"Query too slow: {large_time*1000:.2f}ms"
    
    def test_test_type_filter_scaling(self, small_db, medium_db, large_db):
        """Benchmark test_type filter across different dataset sizes"""
        # Test comparison filter
        start = time.perf_counter()
        small_results = small_db.get_test_results(test_type="comparison", limit=200)
        small_time = time.perf_counter() - start
        
        start = time.perf_counter()
        medium_results = medium_db.get_test_results(test_type="comparison", limit=200)
        medium_time = time.perf_counter() - start
        
        start = time.perf_counter()
        large_results = large_db.get_test_results(test_type="comparison", limit=200)
        large_time = time.perf_counter() - start
        
        print(f"\n⚡ Test Type Filter Performance:")
        print(f"  100 results:  {small_time*1000:.2f}ms ({len(small_results)} matches)")
        print(f"  500 results:  {medium_time*1000:.2f}ms ({len(medium_results)} matches)")
        print(f"  1000 results: {large_time*1000:.2f}ms ({len(large_results)} matches)")
        
        # Should be very fast
        assert small_time < 0.15, f"Filter too slow: {small_time*1000:.2f}ms"
        assert medium_time < 0.15, f"Filter too slow: {medium_time*1000:.2f}ms"
        assert large_time < 0.15, f"Filter too slow: {large_time*1000:.2f}ms"
    
    def test_combined_filter_performance(self, large_db):
        """Benchmark combined filters on large dataset"""
        # Test combined: date + type + project
        start = time.perf_counter()
        results = large_db.get_test_results(
            days=30,
            test_type="comparison",
            project_name="LargeProject",
            limit=200
        )
        elapsed = time.perf_counter() - start
        
        print(f"\n⚡ Combined Filter Performance (1000 results):")
        print(f"  Filters: 30 days + test_type + project_name")
        print(f"  Time: {elapsed*1000:.2f}ms")
        print(f"  Matches: {len(results)}")
        
        # Should still be fast with multiple filters
        assert elapsed < 0.2, f"Combined filter too slow: {elapsed*1000:.2f}ms"
    
    def test_status_filter_performance(self, large_db):
        """Benchmark status filter on large dataset"""
        # Test passed filter
        start = time.perf_counter()
        passed_results = large_db.get_test_results(status="passed", limit=200)
        passed_time = time.perf_counter() - start
        
        # Test failed filter
        start = time.perf_counter()
        failed_results = large_db.get_test_results(status="failed", limit=200)
        failed_time = time.perf_counter() - start
        
        print(f"\n⚡ Status Filter Performance (1000 results):")
        print(f"  Passed: {passed_time*1000:.2f}ms ({len(passed_results)} matches)")
        print(f"  Failed: {failed_time*1000:.2f}ms ({len(failed_results)} matches)")
        
        assert passed_time < 0.2, f"Passed filter too slow: {passed_time*1000:.2f}ms"
        assert failed_time < 0.2, f"Failed filter too slow: {failed_time*1000:.2f}ms"


class TestStorageEfficiency:
    """Benchmark storage efficiency at scale"""
    
    @pytest.fixture
    def storage_db(self):
        """Database for storage testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "storage_benchmark.db"
            db = DatabaseManager(db_path=str(db_path))
            yield db, db_path
            if hasattr(db, 'connection') and db.connection:
                db.connection.close()
    
    def test_database_growth_rate(self, storage_db):
        """Measure database growth with increasing results"""
        db, db_path = storage_db
        sizes = {}
        
        # Baseline
        sizes[0] = os.path.getsize(db_path)
        
        # Add 100 results
        now = datetime.now()
        for i in range(100):
            result = TestDataFactory.create_test_result(
                project_name=f"GrowthTest_{i:03d}",
                timestamp=(now - timedelta(days=i % 30)).isoformat()
            )
            result.files_snapshot = json.dumps({
                f"gen_{i}.py": f"# Generator {i}\n" + "code = 1\n" * 50,
                f"sol_{i}.py": f"# Solution {i}\n" + "answer = 2\n" * 50,
            })
            db.save_test_result(result)
            
            # Measure at checkpoints
            if (i + 1) in [10, 25, 50, 100]:
                sizes[i + 1] = os.path.getsize(db_path)
        
        # Print growth analysis
        print(f"\n💾 Database Growth Rate Analysis:")
        for count, size in sorted(sizes.items()):
            kb_size = size / 1024
            if count > 0:
                per_result = size / count
                print(f"  {count:3d} results: {kb_size:7.1f} KB ({per_result:,.0f} bytes/result)")
            else:
                print(f"  {count:3d} results: {kb_size:7.1f} KB (empty database)")
        
        # Verify reasonable growth
        size_100 = sizes[100]
        assert size_100 < 1_000_000, f"Database too large: {size_100:,} bytes"
        
        # Average per result should be < 10KB
        avg_per_result = size_100 / 100
        print(f"  📊 Average per result: {avg_per_result:,.0f} bytes ({avg_per_result/1024:.2f} KB)")
        assert avg_per_result < 10_000, f"Per-result size too large: {avg_per_result:,.0f} bytes"
    
    def test_files_snapshot_compression(self, storage_db):
        """Measure files snapshot storage efficiency"""
        db, db_path = storage_db
        
        # Create result with large code files
        result = TestDataFactory.create_test_result(
            project_name="Compression Test"
        )
        
        # Simulate realistic code files (3 files, ~500 lines each)
        large_generator = "# Generator\n" + "def generate(n):\n    return n * 2\n" * 200
        large_solution = "# Solution\n" + "def solve(input):\n    return process(input)\n" * 200
        large_test = "# Tests\n" + "import unittest\nclass TestCase(unittest.TestCase):\n    pass\n" * 100
        
        result.files_snapshot = json.dumps({
            "generator.py": large_generator,
            "correct.py": large_solution,
            "test.py": large_test
        })
        
        # Save and measure
        result_id = db.save_test_result(result)
        
        # Retrieve to measure storage
        retrieved = db.get_test_results(project_name="Compression Test")[0]
        json_size = len(retrieved.files_snapshot.encode('utf-8'))
        
        # Measure original size
        original_size = len(large_generator) + len(large_solution) + len(large_test)
        
        # Calculate compression
        compression_ratio = (1 - (json_size / original_size)) * 100 if original_size > 0 else 0
        
        print(f"\n📦 Files Snapshot Compression Analysis:")
        print(f"  Original code size: {original_size:,} bytes ({original_size/1024:.1f} KB)")
        print(f"  JSON storage size:  {json_size:,} bytes ({json_size/1024:.1f} KB)")
        print(f"  Compression ratio:  {compression_ratio:.1f}%")
        
        # JSON should be roughly same size (minimal overhead)
        overhead = json_size - original_size
        overhead_percent = (overhead / original_size) * 100 if original_size > 0 else 0
        print(f"  JSON overhead:      {overhead:,} bytes ({overhead_percent:.1f}%)")
        
        # Overhead should be minimal (<20%)
        assert overhead_percent < 20, f"JSON overhead too high: {overhead_percent:.1f}%"
    
    def test_storage_vs_old_format_estimation(self, storage_db):
        """Compare storage efficiency vs old format (estimated)"""
        db, db_path = storage_db
        
        # Create 50 realistic results
        now = datetime.now()
        for i in range(50):
            result = TestDataFactory.create_test_result(
                project_name=f"OldFormat_{i:02d}",
                test_count=20,
                passed_tests=15,
                failed_tests=5,
                timestamp=(now - timedelta(days=i)).isoformat()
            )
            result.files_snapshot = json.dumps({
                f"gen_{i}.py": f"# Gen {i}\n" + "x = 1\n" * 80,
                f"sol_{i}.py": f"# Sol {i}\n" + "y = 2\n" * 80,
                f"test_{i}.py": f"# Test {i}\n" + "z = 3\n" * 40,
            })
            db.save_test_result(result)
        
        # Measure new format size
        new_size = os.path.getsize(db_path)
        
        # Estimate old format size (based on TestCaseResult structure)
        # Old: ~24KB per result (file paths, individual test cases, redundant data)
        old_estimated_size = 50 * 24_000
        
        # Calculate reduction
        reduction_percent = ((old_estimated_size - new_size) / old_estimated_size) * 100
        
        print(f"\n📊 Storage Reduction vs Old Format (50 results):")
        print(f"  Old format (estimated): {old_estimated_size:,} bytes ({old_estimated_size/1024:.1f} KB)")
        print(f"  New format (actual):    {new_size:,} bytes ({new_size/1024:.1f} KB)")
        print(f"  Reduction:              {reduction_percent:.1f}%")
        print(f"  Space saved:            {old_estimated_size - new_size:,} bytes ({(old_estimated_size - new_size)/1024:.1f} KB)")
        
        # Should achieve significant reduction (>70%)
        assert reduction_percent > 70, f"Storage reduction insufficient: {reduction_percent:.1f}%"


class TestSQLvsPythonFiltering:
    """Compare SQL filtering vs Python filtering performance"""
    
    @pytest.fixture
    def comparison_db(self):
        """Database with 500 results for comparison"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "comparison_benchmark.db"
            db = DatabaseManager(db_path=str(db_path))
            
            # Create 500 results spanning 180 days
            now = datetime.now()
            for i in range(500):
                result = TestDataFactory.create_test_result(
                    project_name=f"CompareProject_{i:03d}",
                    test_type=["comparison", "validation", "benchmark"][i % 3],
                    test_count=10 + (i % 20),
                    passed_tests=5 + (i % 10),
                    failed_tests=(i % 5),
                    timestamp=(now - timedelta(days=i % 180)).isoformat()
                )
                db.save_test_result(result)
            
            yield db
            if hasattr(db, 'connection') and db.connection:
                db.connection.close()
    
    def test_date_filter_sql_vs_python_7days(self, comparison_db):
        """Compare SQL vs Python filtering for 7-day date filter"""
        now = datetime.now()
        cutoff = now - timedelta(days=7)
        
        # Method 1: SQL filtering
        sql_start = time.perf_counter()
        sql_results = comparison_db.get_test_results(days=7, limit=500)
        sql_time = time.perf_counter() - sql_start
        
        # Method 2: Python filtering
        python_start = time.perf_counter()
        all_results = comparison_db.get_test_results(limit=500)
        python_results = [
            r for r in all_results 
            if datetime.fromisoformat(r.timestamp) >= cutoff
        ]
        python_time = time.perf_counter() - python_start
        
        # Verify same results
        assert len(sql_results) == len(python_results), "Result count mismatch"
        
        # Calculate speedup
        speedup = python_time / sql_time if sql_time > 0 else 1.0
        
        print(f"\n🏎️  Date Filter: SQL vs Python (7 days, 500 results)")
        print(f"  SQL filtering:    {sql_time*1000:.2f}ms ({len(sql_results)} matches)")
        print(f"  Python filtering: {python_time*1000:.2f}ms ({len(python_results)} matches)")
        print(f"  Speedup:          {speedup:.2f}x")
        
        if speedup > 1.0:
            print(f"  ✅ SQL is {speedup:.2f}x faster")
        else:
            print(f"  SQL is comparable to Python")
        
        # SQL should not be significantly slower
        assert sql_time <= python_time * 2.0, "SQL filtering unexpectedly slow"
    
    def test_date_filter_sql_vs_python_30days(self, comparison_db):
        """Compare SQL vs Python filtering for 30-day date filter"""
        now = datetime.now()
        cutoff = now - timedelta(days=30)
        
        # SQL filtering
        sql_start = time.perf_counter()
        sql_results = comparison_db.get_test_results(days=30, limit=500)
        sql_time = time.perf_counter() - sql_start
        
        # Python filtering
        python_start = time.perf_counter()
        all_results = comparison_db.get_test_results(limit=500)
        python_results = [
            r for r in all_results 
            if datetime.fromisoformat(r.timestamp) >= cutoff
        ]
        python_time = time.perf_counter() - python_start
        
        speedup = python_time / sql_time if sql_time > 0 else 1.0
        
        print(f"\n🏎️  Date Filter: SQL vs Python (30 days, 500 results)")
        print(f"  SQL filtering:    {sql_time*1000:.2f}ms ({len(sql_results)} matches)")
        print(f"  Python filtering: {python_time*1000:.2f}ms ({len(python_results)} matches)")
        print(f"  Speedup:          {speedup:.2f}x")
        
        assert sql_time <= python_time * 2.0, "SQL filtering unexpectedly slow"
    
    def test_test_type_filter_sql_vs_python(self, comparison_db):
        """Compare SQL vs Python filtering for test_type"""
        # SQL filtering
        sql_start = time.perf_counter()
        sql_results = comparison_db.get_test_results(test_type="comparison", limit=500)
        sql_time = time.perf_counter() - sql_start
        
        # Python filtering
        python_start = time.perf_counter()
        all_results = comparison_db.get_test_results(limit=500)
        python_results = [r for r in all_results if r.test_type == "comparison"]
        python_time = time.perf_counter() - python_start
        
        speedup = python_time / sql_time if sql_time > 0 else 1.0
        
        print(f"\n🏎️  Test Type Filter: SQL vs Python (500 results)")
        print(f"  SQL filtering:    {sql_time*1000:.2f}ms ({len(sql_results)} matches)")
        print(f"  Python filtering: {python_time*1000:.2f}ms ({len(python_results)} matches)")
        print(f"  Speedup:          {speedup:.2f}x")
        
        assert sql_time <= python_time * 2.0, "SQL filtering unexpectedly slow"


class TestScalabilityLimits:
    """Test performance at extreme scales"""
    
    def test_query_performance_5000_results(self):
        """Test query performance with 5000 results"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "extreme_scale.db"
            db = DatabaseManager(db_path=str(db_path))
            
            print(f"\n🚀 Creating 5000 test results...")
            
            # Create 5000 results
            now = datetime.now()
            creation_start = time.perf_counter()
            
            for i in range(5000):
                result = TestDataFactory.create_test_result(
                    project_name=f"Extreme_{i:05d}",
                    test_type=["comparison", "validation", "benchmark"][i % 3],
                    timestamp=(now - timedelta(days=i % 730)).isoformat()
                )
                result.files_snapshot = json.dumps({
                    f"g_{i}.py": f"# {i}\n" + "x=1\n" * 10,
                })
                db.save_test_result(result)
                
                if (i + 1) % 1000 == 0:
                    print(f"  Created {i + 1} results...")
            
            creation_time = time.perf_counter() - creation_start
            
            # Measure database size
            db_size = os.path.getsize(db_path)
            
            print(f"\n📊 Extreme Scale Performance (5000 results):")
            print(f"  Creation time:  {creation_time:.2f}s")
            print(f"  Database size:  {db_size:,} bytes ({db_size/1024/1024:.2f} MB)")
            print(f"  Avg per result: {db_size/5000:,.0f} bytes")
            
            # Test various queries
            print(f"\n  Query Performance:")
            
            # Date filter
            start = time.perf_counter()
            results_7d = db.get_test_results(days=7, limit=500)
            time_7d = time.perf_counter() - start
            print(f"    7-day filter:  {time_7d*1000:.2f}ms ({len(results_7d)} matches)")
            
            start = time.perf_counter()
            results_30d = db.get_test_results(days=30, limit=500)
            time_30d = time.perf_counter() - start
            print(f"    30-day filter: {time_30d*1000:.2f}ms ({len(results_30d)} matches)")
            
            # Type filter
            start = time.perf_counter()
            results_type = db.get_test_results(test_type="comparison", limit=500)
            time_type = time.perf_counter() - start
            print(f"    Type filter:   {time_type*1000:.2f}ms ({len(results_type)} matches)")
            
            # Combined filter
            start = time.perf_counter()
            results_combined = db.get_test_results(
                days=30, 
                test_type="comparison",
                limit=500
            )
            time_combined = time.perf_counter() - start
            print(f"    Combined:      {time_combined*1000:.2f}ms ({len(results_combined)} matches)")
            
            # Cleanup
            if hasattr(db, 'connection') and db.connection:
                db.connection.close()
            
            # Verify performance is still acceptable
            assert time_7d < 0.5, f"7-day query too slow at scale: {time_7d*1000:.2f}ms"
            assert time_30d < 0.5, f"30-day query too slow at scale: {time_30d*1000:.2f}ms"
            assert time_type < 0.5, f"Type query too slow at scale: {time_type*1000:.2f}ms"
            assert time_combined < 0.5, f"Combined query too slow at scale: {time_combined*1000:.2f}ms"
            
            # Database should be < 10MB
            assert db_size < 10_000_000, f"Database too large at scale: {db_size/1024/1024:.2f} MB"


if __name__ == "__main__":
    # Run benchmarks with verbose output
    pytest.main([__file__, "-v", "--tb=short", "-s"])
