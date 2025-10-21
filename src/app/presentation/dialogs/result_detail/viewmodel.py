"""
DetailedResultViewModel

Phase 4: Results Detail Consolidation
Pure Python business logic for detailed result dialog, separated from Qt UI.
"""

import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from src.app.persistence.database import TestResult


class DetailedResultViewModel:
    """ViewModel for detailed result dialog - handles data loading and formatting.
    
    Responsibilities:
    - Load and parse test result data
    - Format summary statistics
    - Parse JSON fields (test_details, files_snapshot, mismatch_analysis)
    - Filter tests by passed/failed status
    - Prepare data for UI rendering
    
    Does NOT:
    - Create Qt widgets
    - Handle UI events
    - Manage UI state
    """

    def __init__(self, test_result: TestResult):
        """Initialize with test result model."""
        self.test_result = test_result
        self._test_details_cache = None
        self._files_snapshot_cache = None
        self._mismatch_analysis_cache = None

    # Data Loading Methods

    def get_summary_data(self) -> Dict:
        """Get formatted summary statistics for display."""
        success_rate = (
            (self.test_result.passed_tests / self.test_result.test_count * 100)
            if self.test_result.test_count > 0
            else 0
        )

        return {
            "test_type": self.test_result.test_type.upper(),
            "project_name": self.test_result.project_name or "Unknown",
            "file_path": self.test_result.file_path,
            "timestamp": self._format_timestamp(self.test_result.timestamp),
            "total_tests": self.test_result.test_count,
            "passed_tests": self.test_result.passed_tests,
            "failed_tests": self.test_result.failed_tests,
            "success_rate": f"{success_rate:.1f}%",
            "total_time": f"{self.test_result.total_time:.3f}s",
        }

    def get_test_details(self) -> List[Dict]:
        """Parse and return test details as list of dicts."""
        if self._test_details_cache is not None:
            return self._test_details_cache

        try:
            if self.test_result.test_details:
                self._test_details_cache = json.loads(self.test_result.test_details)
                if not isinstance(self._test_details_cache, list):
                    self._test_details_cache = []
            else:
                self._test_details_cache = []
        except (json.JSONDecodeError, TypeError):
            self._test_details_cache = []

        return self._test_details_cache

    def get_files_snapshot(self) -> Dict:
        """Parse and return files snapshot as dict."""
        if self._files_snapshot_cache is not None:
            return self._files_snapshot_cache

        try:
            if self.test_result.files_snapshot:
                self._files_snapshot_cache = json.loads(
                    self.test_result.files_snapshot
                )
                if not isinstance(self._files_snapshot_cache, dict):
                    self._files_snapshot_cache = {}
            else:
                self._files_snapshot_cache = {}
        except (json.JSONDecodeError, TypeError):
            self._files_snapshot_cache = {}

        return self._files_snapshot_cache

    def get_mismatch_analysis(self) -> Optional[Dict]:
        """Parse and return mismatch analysis as dict, or None if not present."""
        if self._mismatch_analysis_cache is not None:
            return self._mismatch_analysis_cache

        try:
            if self.test_result.mismatch_analysis:
                self._mismatch_analysis_cache = json.loads(
                    self.test_result.mismatch_analysis
                )
                if not isinstance(self._mismatch_analysis_cache, dict):
                    self._mismatch_analysis_cache = None
            else:
                self._mismatch_analysis_cache = None
        except (json.JSONDecodeError, TypeError):
            self._mismatch_analysis_cache = None

        return self._mismatch_analysis_cache

    # Filtering Methods

    def get_passed_tests(self) -> List[Dict]:
        """Return only passed test cases."""
        all_tests = self.get_test_details()
        return [t for t in all_tests if self._is_test_passed(t)]

    def get_failed_tests(self) -> List[Dict]:
        """Return only failed test cases."""
        all_tests = self.get_test_details()
        return [t for t in all_tests if not self._is_test_passed(t)]

    def _is_test_passed(self, test: Dict) -> bool:
        """Check if a test case passed."""
        return test.get("passed", test.get("status", "").lower() == "pass")

    # Formatting Methods

    def _format_timestamp(self, timestamp: str) -> str:
        """Format ISO timestamp to human-readable string."""
        try:
            if timestamp:
                dt = datetime.fromisoformat(timestamp)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            return "Unknown"
        except (ValueError, AttributeError):
            return f"Invalid ({timestamp})"

    def get_code_file_tabs(self) -> List[Tuple[str, str]]:
        """Get list of (label, content) tuples for code file tabs.
        
        Returns:
            List of (tab_label, code_content) tuples
        """
        files = self.get_files_snapshot()
        if not files:
            return []

        # Known file type mappings
        file_mappings = [
            ("generator_code", "🔢 Generator"),
            ("correct_code", "✅ Correct"),
            ("test_code", "🧪 Test"),
            ("validator_code", "✔️ Validator"),
        ]

        tabs = []
        for attr_name, display_name in file_mappings:
            content = files.get(attr_name)
            if content:
                tabs.append((display_name, str(content)))

        # Add additional files if present
        if "additional_files" in files and isinstance(files["additional_files"], dict):
            for filename, content in files["additional_files"].items():
                tabs.append((str(filename), str(content)))

        return tabs

    def get_test_case_display_data(self, test: Dict) -> Dict:
        """Extract and format data for displaying a single test case.
        
        Args:
            test: Test case dict from test_details
            
        Returns:
            Dict with formatted test case data ready for UI display
        """
        passed = self._is_test_passed(test)

        return {
            "test_number": test.get("test", test.get("test_number", "?")),
            "passed": passed,
            "execution_time": test.get("execution_time", test.get("total_time")),
            "input": test.get("input", ""),
            "expected_output": test.get(
                "output", test.get("expected_output", test.get("correct_output", ""))
            ),
            "actual_output": test.get("actual_output", test.get("test_output", "")),
            "error": test.get("error", test.get("error_details", "")),
            "mismatch_analysis": test.get("mismatch_analysis", {}),
        }

    def has_code_files(self) -> bool:
        """Check if test result has any code files."""
        files = self.get_files_snapshot()
        return bool(files)

    def get_export_file_name(self) -> str:
        """Generate default export filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"test_export_{self.test_result.project_name}_{timestamp}.zip"
