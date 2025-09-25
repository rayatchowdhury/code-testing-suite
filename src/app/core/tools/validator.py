"""
Validator - Main controller for validation testing workflow.

This module has been refactored as part of Phase 4 migration to inherit 
from BaseRunner, eliminating ~100 lines of duplicate runner code while
maintaining 100% API compatibility.
"""

import os
import json
from datetime import datetime
from PySide6.QtCore import Signal
from src.app.core.tools.base.base_runner import BaseRunner
from src.app.presentation.views.validator.validator_status_window import ValidatorStatusWindow
from src.app.persistence.database import TestResult
from src.app.core.tools.specialized.validator_test_worker import ValidatorTestWorker


class ValidatorRunner(BaseRunner):
    """
    Main controller for validation testing workflow.
    
    This class has been refactored to inherit from BaseRunner, eliminating
    duplicate runner code while maintaining exact API compatibility.
    """
    
    # Validation-specific signal signature (must match original)
    testCompleted = Signal(int, bool, str, str, str, str, int)  # test number, passed, input, test_output, validation_message, error_details, validator_exit_code

    def __init__(self, workspace_dir):
        # Define files specific to validation testing
        files = {
            'generator': os.path.join(workspace_dir, 'generator.cpp'),
            'test': os.path.join(workspace_dir, 'test.cpp'),
            'validator': os.path.join(workspace_dir, 'validator.cpp')
        }
        
        # Initialize BaseRunner with validation-specific configuration
        super().__init__(workspace_dir, files, test_type='validator')

    def _create_test_worker(self, test_count, max_workers=None, **kwargs):
        """Create ValidatorTestWorker for validation testing"""
        return ValidatorTestWorker(
            self.workspace_dir, 
            self.executables, 
            test_count, 
            max_workers
        )

    def _create_test_status_window(self):
        """Create validation-specific status window"""
        return ValidatorStatusWindow()

    def _connect_worker_signals(self, worker):
        """Connect validator-specific signals"""
        # Call parent to connect common signals  
        super()._connect_worker_signals(worker)
        
        # Connect validation-specific testCompleted signal
        if hasattr(worker, 'testCompleted'):
            worker.testCompleted.connect(self.testCompleted)

    def _create_test_result(self, all_passed, test_results, passed_tests, failed_tests, total_time):
        """
        Create validation-specific TestResult object.
        
        This method implements the template method pattern, providing
        validation-specific analysis and database result creation.
        """
        # Get the test file path
        test_file_path = self._get_test_file_path()
        
        # Create files snapshot
        files_snapshot = self._create_files_snapshot()
        
        # Compile validation-specific analysis
        validation_analysis = {
            'test_count': self.test_count,
            'validation_summary': {
                'correct_outputs': sum(1 for r in test_results if r.get('validator_exit_code') == 0),
                'wrong_answers': sum(1 for r in test_results if r.get('validator_exit_code') == 1),
                'presentation_errors': sum(1 for r in test_results if r.get('validator_exit_code') == 2),
                'validator_errors': sum(1 for r in test_results if r.get('validator_exit_code', 0) > 2),
                'timeouts': sum(1 for r in test_results if r.get('validator_exit_code') == -2),
                'system_errors': sum(1 for r in test_results if r.get('validator_exit_code') == -3)
            },
            'execution_times': {
                'avg_generator': sum(r.get('generator_time', 0) for r in test_results) / len(test_results) if test_results else 0,
                'avg_test': sum(r.get('test_time', 0) for r in test_results) / len(test_results) if test_results else 0,
                'avg_validator': sum(r.get('validator_time', 0) for r in test_results) / len(test_results) if test_results else 0
            },
            'failed_tests': [r for r in test_results if not r.get('passed', True)]
        }
        
        # Create and return TestResult object
        return TestResult(
            test_type="validator",
            file_path=test_file_path,
            test_count=self.test_count,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_time=total_time,
            timestamp=datetime.now().isoformat(),
            test_details=json.dumps(test_results),
            project_name=os.path.basename(self.workspace_dir),
            files_snapshot=json.dumps(files_snapshot),
            mismatch_analysis=json.dumps(validation_analysis)
        )

    def run_validation_test(self, test_count, max_workers=None):
        """
        Start validation tests - maintains original API.
        
        This method preserves the original public API while using
        the BaseRunner infrastructure for thread management.
        """
        # Use BaseRunner's run_tests method with validation-specific parameters
        self.run_tests(test_count, max_workers=max_workers)