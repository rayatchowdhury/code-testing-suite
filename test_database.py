#!/usr/bin/env python3
"""
Simple test script to verify database integration works correctly.
Run this script to test the database functionality before integrating into the main application.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager, TestResult, Session, ProjectData
from datetime import datetime
import json

def test_database_functionality():
    """Test all database operations"""
    print("🧪 Testing Code Testing Suite Database Integration")
    print("=" * 50)
    
    # Initialize database
    print("1. Initializing database...")
    db = DatabaseManager()
    print("   ✓ Database initialized successfully")
    
    # Test saving a stress test result
    print("\n2. Testing stress test result saving...")
    stress_result = TestResult(
        test_type="stress",
        file_path="/test/path/test.cpp",
        test_count=10,
        passed_tests=8,
        failed_tests=2,
        total_time=45.5,
        timestamp=datetime.now().isoformat(),
        test_details=json.dumps([
            {"test_number": 1, "passed": True, "time": 0.5},
            {"test_number": 2, "passed": False, "time": 1.2}
        ]),
        project_name="Test Project"
    )
    
    stress_id = db.save_test_result(stress_result)
    print(f"   ✓ Stress test result saved with ID: {stress_id}")
    
    # Test saving a TLE test result
    print("\n3. Testing TLE test result saving...")
    tle_result = TestResult(
        test_type="tle",
        file_path="/test/path/tle_test.cpp",
        test_count=5,
        passed_tests=3,
        failed_tests=2,
        total_time=120.0,
        timestamp=datetime.now().isoformat(),
        test_details=json.dumps([
            {"test_name": "Test 1", "passed": True, "execution_time": 0.8},
            {"test_name": "Test 2", "passed": False, "execution_time": 2.5}
        ]),
        project_name="TLE Test Project"
    )
    
    tle_id = db.save_test_result(tle_result)
    print(f"   ✓ TLE test result saved with ID: {tle_id}")
    
    # Test retrieving results
    print("\n4. Testing result retrieval...")
    all_results = db.get_test_results(limit=10)
    print(f"   ✓ Retrieved {len(all_results)} test results")
    
    stress_results = db.get_test_results(test_type="stress", limit=5)
    print(f"   ✓ Retrieved {len(stress_results)} stress test results")
    
    tle_results = db.get_test_results(test_type="tle", limit=5)
    print(f"   ✓ Retrieved {len(tle_results)} TLE test results")
    
    # Test session saving
    print("\n5. Testing session management...")
    session = Session(
        session_name="Test Editor Session",
        open_files=json.dumps(["/test/file1.cpp", "/test/file2.py"]),
        active_file="/test/file1.cpp",
        timestamp=datetime.now().isoformat(),
        project_name="Test Project"
    )
    
    session_id = db.save_session(session)
    print(f"   ✓ Session saved with ID: {session_id}")
    
    # Test retrieving sessions
    sessions = db.get_sessions(limit=5)
    print(f"   ✓ Retrieved {len(sessions)} sessions")
    
    # Test project data
    print("\n6. Testing project data management...")
    project = ProjectData(
        project_name="Test Project",
        project_path="/test/project/path",
        last_accessed=datetime.now().isoformat(),
        file_count=5,
        total_lines=250,
        languages=json.dumps(["C++", "Python"])
    )
    
    project_id = db.save_project_data(project)
    print(f"   ✓ Project data saved with ID: {project_id}")
    
    # Test retrieving projects
    projects = db.get_projects(limit=5)
    print(f"   ✓ Retrieved {len(projects)} projects")
    
    # Test statistics
    print("\n7. Testing statistics generation...")
    stats = db.get_test_statistics()
    print(f"   ✓ Statistics generated:")
    print(f"      - Total tests: {stats.get('total_tests', 0)}")
    print(f"      - Success rate: {stats.get('success_rate', 0):.1f}%")
    print(f"      - By type: {stats.get('by_type', {})}")
    
    print("\n" + "=" * 50)
    print("🎉 All database tests completed successfully!")
    print("✅ Database integration is working correctly.")
    print("\nYou can now:")
    print("  • Run stress tests and see results saved automatically")
    print("  • Run TLE tests and see results saved automatically") 
    print("  • View results in the new Results window")
    print("  • Track your testing history and performance trends")

if __name__ == "__main__":
    try:
        test_database_functionality()
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        print("Please check the database configuration and try again.")
        sys.exit(1)
