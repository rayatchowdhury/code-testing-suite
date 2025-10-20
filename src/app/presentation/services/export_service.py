"""
Export Service for Test Results.

Consolidates duplicated export logic from results_window.py and detailed_results_window.py.
Provides reusable functions for exporting test results to ZIP files.
"""

import json


def export_test_cases_to_zip(zipf, test_details: str):
    """
    Export test cases to ZIP file in organized folders.
    
    This consolidates the duplicated test case export logic (~40 lines)
    from results_window.py and detailed_results_window.py.
    
    Args:
        zipf: ZipFile object to write to
        test_details: JSON string containing test case data
    """
    if not test_details:
        return
    
    test_data = json.loads(test_details)
    
    # Separate passed and failed tests
    for i, test_case in enumerate(test_data, 1):
        test_num = test_case.get("test", i)
        status = test_case.get("status", "unknown")

        # Create test case file content
        test_content = f"Test #{test_num}\n"
        test_content += f"Status: {status}\n"
        test_content += f"{'='*50}\n\n"

        if "input" in test_case:
            test_content += f"INPUT:\n{test_case['input']}\n\n"

        if "output" in test_case:
            test_content += f"EXPECTED OUTPUT:\n{test_case['output']}\n\n"

        if "actual_output" in test_case:
            test_content += f"ACTUAL OUTPUT:\n{test_case['actual_output']}\n\n"

        if "error" in test_case:
            test_content += f"ERROR:\n{test_case['error']}\n\n"

        if "execution_time" in test_case:
            test_content += f"Execution Time: {test_case['execution_time']} seconds\n"

        # Save to appropriate folder
        folder = "passed" if status.lower() == "pass" else "failed"
        zipf.writestr(
            f"{folder}/test_{test_num}.txt",
            test_content.encode("utf-8"),
        )


def create_export_summary(test_result) -> str:
    """
    Create a summary text for test results export.
    
    This consolidates the duplicated summary creation logic
    from results_window.py and detailed_results_window.py.
    
    Args:
        test_result: TestResult object with test statistics
        
    Returns:
        str: Formatted summary text
    """
    import os
    
    summary = "Test Results Export\n"
    summary += f"{'='*60}\n\n"
    summary += f"Project: {test_result.project_name}\n"
    summary += f"Test Type: {test_result.test_type}\n"
    summary += f"File: {os.path.basename(test_result.file_path)}\n"
    summary += f"Timestamp: {test_result.timestamp}\n\n"
    summary += "Test Statistics:\n"
    summary += f"  Total Tests: {test_result.test_count}\n"
    summary += f"  Passed: {test_result.passed_tests}\n"
    summary += f"  Failed: {test_result.failed_tests}\n"
    summary += f"  Success Rate: {(test_result.passed_tests/test_result.test_count*100) if test_result.test_count > 0 else 0:.1f}%\n"
    summary += f"  Total Time: {test_result.total_time:.3f} seconds\n\n"

    if test_result.mismatch_analysis:
        summary += "\nMismatch Analysis:\n"
        summary += f"{test_result.mismatch_analysis}\n"
    
    return summary
