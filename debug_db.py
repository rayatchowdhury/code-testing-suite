#!/usr/bin/env python3
"""
Debug script to examine database content and find crash causes
"""

from database.database_manager import DatabaseManager
import json

def main():
    db = DatabaseManager()
    results = db.get_test_results(limit=10)  # Get recent results
    
    print(f"Found {len(results)} test results in database")
    print("=" * 50)
    
    for i, result in enumerate(results):
        print(f'Result {i+1}:')
        print(f'  ID: {result.id}')
        print(f'  Type: {result.test_type}')
        print(f'  Test count: {result.test_count}')
        print(f'  Passed: {result.passed_tests}')
        print(f'  Failed: {result.failed_tests}')
        print(f'  Total time: {result.total_time}')
        print(f'  test_details length: {len(result.test_details) if result.test_details else 0}')
        print(f'  files_snapshot length: {len(result.files_snapshot) if result.files_snapshot else 0}')
        print(f'  mismatch_analysis length: {len(result.mismatch_analysis) if result.mismatch_analysis else 0}')
        
        # Test parsing test_details
        if result.test_details:
            try:
                details = json.loads(result.test_details)
                print(f'  test_details type: {type(details)}')
                print(f'  test_details length: {len(details) if isinstance(details, list) else "Not list"}')
                
                if isinstance(details, list) and details:
                    first_test = details[0]
                    print(f'  first test case type: {type(first_test)}')
                    if isinstance(first_test, dict):
                        print(f'  first test case keys: {list(first_test.keys())}')
                        
                        # Check for problematic fields
                        for key, value in first_test.items():
                            print(f'    {key}: {type(value)} - {str(value)[:100]}...' if isinstance(value, str) and len(str(value)) > 100 else f'    {key}: {type(value)} - {value}')
                    else:
                        print(f'  first test case: {first_test}')
            except Exception as e:
                print(f'  test_details parse error: {e}')
        
        # Test parsing files_snapshot
        if result.files_snapshot:
            try:
                files_data = json.loads(result.files_snapshot)
                print(f'  files_snapshot type: {type(files_data)}')
                if isinstance(files_data, dict):
                    print(f'  files_snapshot keys: {list(files_data.keys())}')
            except Exception as e:
                print(f'  files_snapshot parse error: {e}')
        
        # Test parsing mismatch_analysis
        if result.mismatch_analysis:
            try:
                mismatch_data = json.loads(result.mismatch_analysis)
                print(f'  mismatch_analysis type: {type(mismatch_data)}')
                if isinstance(mismatch_data, dict):
                    print(f'  mismatch_analysis keys: {list(mismatch_data.keys())}')
            except Exception as e:
                print(f'  mismatch_analysis parse error: {e}')
        
        print()

if __name__ == "__main__":
    main()
