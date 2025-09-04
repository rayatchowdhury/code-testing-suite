#!/usr/bin/env python3
"""
Debug script to check Results window and database content
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager, TestResult
from datetime import datetime
import json

def debug_results():
    print("🔍 Debugging Results Window Issues")
    print("=" * 40)
    
    # Check database
    print("1. Checking database connection...")
    try:
        db = DatabaseManager()
        print("   ✓ Database connected successfully")
        
        # Check if there are any results
        results = db.get_test_results(limit=10)
        print(f"   📊 Found {len(results)} test results in database")
        
        if results:
            print("   📋 Sample results:")
            for i, result in enumerate(results[:3], 1):
                print(f"      {i}. {result.test_type} test - {result.passed_tests}/{result.test_count} passed")
        else:
            print("   ⚠️  No test results found - this might explain empty Results window")
            print("   💡 Try running some stress tests or TLE tests first")
            
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False
    
    # Add some sample data if empty
    if not results:
        print("\n2. Adding sample test data...")
        try:
            # Add sample stress test result
            sample_stress = TestResult(
                test_type="stress",
                file_path="C:\\test\\sample_stress.cpp",
                test_count=5,
                passed_tests=4,
                failed_tests=1,
                total_time=12.5,
                timestamp=datetime.now().isoformat(),
                test_details=json.dumps([
                    {"test_number": 1, "passed": True, "time": 2.1},
                    {"test_number": 2, "passed": True, "time": 1.8},
                    {"test_number": 3, "passed": False, "time": 3.2},
                    {"test_number": 4, "passed": True, "time": 2.4},
                    {"test_number": 5, "passed": True, "time": 3.0}
                ]),
                project_name="Sample Project"
            )
            
            stress_id = db.save_test_result(sample_stress)
            print(f"   ✓ Added sample stress test (ID: {stress_id})")
            
            # Add sample TLE test result
            sample_tle = TestResult(
                test_type="tle",
                file_path="C:\\test\\sample_tle.cpp",
                test_count=3,
                passed_tests=2,
                failed_tests=1,
                total_time=8.2,
                timestamp=datetime.now().isoformat(),
                test_details=json.dumps([
                    {"test_name": "Test 1", "passed": True, "execution_time": 0.8, "time_limit": 1.0},
                    {"test_name": "Test 2", "passed": False, "execution_time": 2.5, "time_limit": 2.0},
                    {"test_name": "Test 3", "passed": True, "execution_time": 1.2, "time_limit": 1.5}
                ]),
                project_name="Sample TLE Project"
            )
            
            tle_id = db.save_test_result(sample_tle)
            print(f"   ✓ Added sample TLE test (ID: {tle_id})")
            
            # Verify data was added
            new_results = db.get_test_results(limit=10)
            print(f"   📊 Database now contains {len(new_results)} test results")
            
        except Exception as e:
            print(f"   ❌ Error adding sample data: {e}")
            return False
    
    # Test statistics
    print("\n3. Testing statistics generation...")
    try:
        stats = db.get_test_statistics()
        print(f"   📈 Total tests: {stats.get('total_tests', 0)}")
        print(f"   📈 Success rate: {stats.get('success_rate', 0):.1f}%")
        print(f"   📈 Test breakdown: {stats.get('by_type', {})}")
    except Exception as e:
        print(f"   ❌ Statistics error: {e}")
    
    print("\n=" * 40)
    print("🎯 Next Steps:")
    print("1. Open the Results window in your application")
    print("2. You should now see the sample test data")
    print("3. Try running actual stress/TLE tests to add real data")
    print("4. If Results window is still empty, check console for errors")
    
    return True

if __name__ == "__main__":
    try:
        debug_results()
    except Exception as e:
        print(f"❌ Debug script failed: {e}")
        import traceback
        traceback.print_exc()
