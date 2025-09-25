"""
Comparator - Main controller for comparison testing workflow.

This module has been refactored as part of Phase 4 migration to inherit 
from BaseRunner, eliminating ~100 lines of duplicate runner code while
maintaining 100% API compatibility.
"""

import os
import json
from datetime import datetime
from PySide6.QtCore import Signal
from src.app.core.tools.base.base_runner import BaseRunner
from src.app.presentation.views.comparator.compare_status_window import CompareStatusWindow
from src.app.persistence.database import TestResult
from src.app.core.tools.specialized.comparison_test_worker import ComparisonTestWorker


class Comparator(BaseRunner):
    """
    Main controller for comparison testing workflow.
    
    This class has been refactored to inherit from BaseRunner, eliminating
    duplicate runner code while maintaining exact API compatibility.
    """
    
    # Stress-specific signal signature (must match original)
    testCompleted = Signal(int, bool, str, str, str)  # test number, passed, input, correct output, test output

    def __init__(self, workspace_dir):
        # Define files specific to comparison testing
        files = {
            'generator': os.path.join(workspace_dir, 'generator.cpp'),
            'correct': os.path.join(workspace_dir, 'correct.cpp'),
            'test': os.path.join(workspace_dir, 'test.cpp')
        }
        
        # Initialize BaseRunner with comparison-specific configuration
        super().__init__(workspace_dir, files, test_type='comparison')

    def _get_compiler_flags(self):
        """Get comparison-specific compiler optimization flags"""
        return [
            '-O2',           # Level 2 optimization for good performance/compile time balance
            '-march=native', # Optimize for current CPU architecture
            '-mtune=native', # Tune for current CPU
            '-pipe',         # Use pipes instead of temporary files
            '-std=c++17',    # Use modern C++ standard
            '-Wall',         # Enable common warnings
        ]

    def _create_test_worker(self, test_count, max_workers=None, **kwargs):
        """Create ComparisonTestWorker for comparison testing"""
        return ComparisonTestWorker(
            self.workspace_dir, 
            self.executables, 
            test_count, 
            max_workers
        )

    def _create_test_status_window(self):
        """Create stress-specific status window"""
        return CompareStatusWindow()

    def _connect_worker_signals(self, worker):
        """Connect stress-specific signals"""
        # Call parent to connect common signals  
        super()._connect_worker_signals(worker)
        
        # Connect stress-specific testCompleted signal
        if hasattr(worker, 'testCompleted'):
            worker.testCompleted.connect(self.testCompleted)

    def _create_test_result(self, all_passed, test_results, passed_tests, failed_tests, total_time):
        """
        Create stress-specific TestResult object.
        
        This method implements the template method pattern, providing
        stress-specific analysis and database result creation.
        """
        # Get the test file path
        test_file_path = self._get_test_file_path()
        
        # Create files snapshot
        files_snapshot = self._create_files_snapshot()
        
        # Compile comparison test analysis
        stress_analysis = {
            'test_count': self.test_count,
            'comparison_summary': {
                'matching_outputs': sum(1 for r in test_results if r.get('passed', False)),
                'mismatched_outputs': sum(1 for r in test_results if not r.get('passed', True) and not r.get('error_details')),
                'generator_failures': sum(1 for r in test_results if 'Generator failed' in r.get('error_details', '')),
                'test_failures': sum(1 for r in test_results if 'Test solution failed' in r.get('error_details', '')),
                'correct_failures': sum(1 for r in test_results if 'Correct solution failed' in r.get('error_details', '')),
                'timeouts': sum(1 for r in test_results if 'Timeout' in r.get('error_details', ''))
            },
            'execution_times': {
                'avg_generator': sum(r.get('generator_time', 0) for r in test_results) / len(test_results) if test_results else 0,
                'avg_test': sum(r.get('test_time', 0) for r in test_results) / len(test_results) if test_results else 0,
                'avg_correct': sum(r.get('correct_time', 0) for r in test_results) / len(test_results) if test_results else 0,
                'avg_comparison': sum(r.get('comparison_time', 0) for r in test_results) / len(test_results) if test_results else 0
            },
            'failed_tests': [r for r in test_results if not r.get('passed', True)]
        }
        
        # Create and return TestResult object
        return TestResult(
            test_type="stress",
            file_path=test_file_path,
            test_count=self.test_count,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_time=total_time,
            timestamp=datetime.now().isoformat(),
            test_details=json.dumps(test_results),
            project_name=os.path.basename(self.workspace_dir),
            files_snapshot=json.dumps(files_snapshot),
            mismatch_analysis=json.dumps(stress_analysis)
        )

    def run_stress_test(self, test_count, max_workers=None):
        """
        Start stress tests - maintains original API for backward compatibility.
        
        This method preserves the original public API while using
        the BaseRunner infrastructure for thread management.
        """
        # Use BaseRunner's run_tests method with comparison-specific parameters
        self.run_tests(test_count, max_workers=max_workers)
    
    def run_comparison_test(self, test_count, max_workers=None):
        """
        Start comparison tests - modern API.
        
        This method provides the modern API while using
        the BaseRunner infrastructure for thread management.
        """
        # Use BaseRunner's run_tests method with comparison-specific parameters
        self.run_tests(test_count, max_workers=max_workers)