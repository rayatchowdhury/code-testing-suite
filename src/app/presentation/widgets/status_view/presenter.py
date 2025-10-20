"""
Status View Presenter

Implements Presenter pattern to coordinate between:
- TestExecutionState (model)
- StatusViewWidgets (view components)
- Domain-specific status views (controllers)

Responsibility: Translate state changes into widget update calls.
Does NOT contain business logic or UI rendering code.
"""

from typing import Optional
from PySide6.QtCore import QTimer

from .models import TestResult, TestExecutionState, TestStatistics


class StatusViewPresenter:
    """
    Presenter for status view coordination.
    
    Separates concerns:
    - State management (TestExecutionState)
    - Widget manipulation (knows how to update widgets)
    - Event translation (domain events → widget updates)
    """
    
    def __init__(
        self,
        header,  # StatusHeaderSection
        performance,  # PerformancePanelSection
        progress_bar,  # VisualProgressBarSection
        cards_section,  # TestResultsCardsSection
        test_type: str = "comparator"
    ):
        """
        Initialize presenter with widget references.
        
        Args:
            header: Status header widget
            performance: Performance panel widget
            progress_bar: Visual progress bar widget
            cards_section: Test cards section widget
            test_type: Type of test ("comparator", "validator", "benchmarker")
        """
        self.header = header
        self.performance = performance
        self.progress_bar = progress_bar
        self.cards_section = cards_section
        self.test_type = test_type
        
        self.state = TestExecutionState()
        self._active_tests = {}  # {test_number: (worker_id, start_time)}
        self._test_completion_times = {}  # {test_number: completion_time} for 1s display
        self._worker_display_duration = 1.0  # Minimum seconds to show worker status
        
        # Timer to update worker statuses and progress stages
        self._worker_update_timer = QTimer()
        self._worker_update_timer.setInterval(100)  # Check every 100ms
        self._worker_update_timer.timeout.connect(self._update_worker_displays)
    
    def start_test_execution(self, total_tests: int, max_workers: int) -> None:
        """
        Initialize presenter for new test run.
        
        Args:
            total_tests: Total number of tests
            max_workers: Number of parallel workers
        """
        # Reset state
        self.state.reset(total_tests, max_workers)
        self._active_tests = {}
        self._test_completion_times = {}
        
        # Reset all widgets
        self.header.reset(total_tests)
        self.progress_bar.reset(total_tests)
        self.cards_section.clear()
        
        # Setup performance panel
        if max_workers > 0:
            self.performance.setup_workers(max_workers)
            self.performance.update_summary(max_workers, 0.0)
        
        # Start worker update timer
        self._worker_update_timer.start()
    
    def handle_worker_busy(self, worker_id: int, test_number: int) -> None:
        """
        Handle worker starting work on a test (real tracking from base_test_worker).
        
        Args:
            worker_id: Actual worker ID from thread mapping
            test_number: Test being executed
        """
        import time
        
        # Track this test with its real worker
        self._active_tests[test_number] = (worker_id, time.time())
        
        # Update worker display to show test assignment
        self.update_worker_status(worker_id, test_number, 0.0, 0.0,
                                test_type=self.test_type, stage="generate")
    
    def handle_worker_idle(self, worker_id: int) -> None:
        """
        Handle worker becoming idle (real tracking from base_test_worker).
        
        Args:
            worker_id: Worker that finished
        """
        # Find which test this worker was running
        test_num_to_clear = None
        for test_num, (wid, _) in self._active_tests.items():
            if wid == worker_id:
                test_num_to_clear = test_num
                break
        
        # Mark for delayed clearing (will be cleared after display duration)
        if test_num_to_clear and test_num_to_clear not in self._test_completion_times:
            import time
            self._test_completion_times[test_num_to_clear] = time.time()
    
    def mark_test_active(self, test_number: int) -> None:
        """
        Mark a test as active/being processed.
        
        DEPRECATED: This is kept for backwards compatibility with testStarted signal.
        Real worker tracking now happens via handle_worker_busy/handle_worker_idle.
        
        Args:
            test_number: Test that is being processed
        """
        # This method is now a no-op since real worker tracking is handled by
        # handle_worker_busy/handle_worker_idle
        pass
    
    def handle_test_result(self, result: TestResult) -> None:
        """
        Process test result and update all widgets.
        
        Single entry point for test completion events.
        Coordinates all widget updates in proper order.
        
        Args:
            result: Test result from worker
        """
        # Update state
        self.state.record_result(result.passed)
        
        # Update progress bar
        self.progress_bar.add_result(result.test_number, result.passed)
        
        # Update header statistics
        self.header.update_stats(
            completed=self.state.completed_tests,
            total=self.state.total_tests,
            passed=self.state.passed_tests,
            failed=self.state.failed_tests
        )
        
        # Update performance panel
        self.performance.update_summary(
            workers_active=self.state.max_workers,
            speed=self.state.tests_per_second
        )
        
        # Mark test as completed - will be cleared after display duration
        if result.test_number in self._active_tests:
            import time
            worker_id, start_time = self._active_tests[result.test_number]
            self._test_completion_times[result.test_number] = time.time()
            
            # Show completion on final stage
            final_stage = "evaluate" if self.test_type == "comparator" else "validate" if self.test_type == "validator" else "benchmark"
            self.update_worker_status(worker_id, result.test_number, 1.0, result.time,
                                    test_type=self.test_type, stage=final_stage)
    
    def update_worker_status(self, worker_id: int, test_number: Optional[int], 
                            progress: float, elapsed: float, test_type: str = "comparator",
                            stage: Optional[str] = None) -> None:
        """
        Update individual worker status.
        
        Called by domain-specific views when worker signals are received.
        
        Args:
            worker_id: Worker identifier (1-indexed)
            test_number: Currently executing test (None if idle)
            progress: Execution progress (0.0-1.0)
            elapsed: Elapsed time for current test
            test_type: Type of test ("comparator", "validator", "benchmarker")
            stage: Explicit pipeline stage name
        """
        if worker_id <= len(self.performance.worker_bars):
            worker_bar = self.performance.worker_bars[worker_id - 1]
            worker_bar.set_status(test_number, progress, elapsed, stage=stage, test_type=test_type)
    
    def complete_execution(self) -> None:
        """
        Finalize test execution.
        
        Updates widgets to show completion state.
        """
        self.state.mark_complete()
        self.header.mark_complete()
        
        # Stop worker update timer
        self._worker_update_timer.stop()
        
        # Clear all remaining active tests
        for test_num, (worker_id, _) in list(self._active_tests.items()):
            self.update_worker_status(worker_id, None, 0.0, 0.0, test_type=self.test_type)
        
        self._active_tests.clear()
        self._test_completion_times.clear()
    
    def _update_worker_displays(self) -> None:
        """
        Periodic update to:
        1. Progress stages for active tests
        2. Clear completed tests after display duration
        
        Called by timer every 100ms.
        """
        import time
        current_time = time.time()
        
        tests_to_clear = []
        
        # Update active tests
        for test_num, (worker_id, start_time) in list(self._active_tests.items()):
            elapsed = current_time - start_time
            
            # Check if test is completed
            if test_num in self._test_completion_times:
                completion_time = self._test_completion_times[test_num]
                if current_time - completion_time >= self._worker_display_duration:
                    # Clear from active
                    tests_to_clear.append(test_num)
                    self.update_worker_status(worker_id, None, 0.0, 0.0, test_type=self.test_type)
            else:
                # Test still running - progress through stages
                stage_duration = 0.8  # Each stage ~800ms
                stage_idx = int(elapsed / stage_duration)
                
                if self.test_type == "comparator":
                    stages = ["generate", "correct", "evaluate"]
                elif self.test_type == "validator":
                    stages = ["generate", "execute", "validate"]
                elif self.test_type == "benchmarker":
                    stages = ["generate", "benchmark"]
                else:
                    stages = ["generate", "execute", "finalize"]
                
                # Clamp to last stage
                current_stage = stages[min(stage_idx, len(stages) - 1)]
                self.update_worker_status(worker_id, test_num,
                                        progress=min(1.0, stage_idx / len(stages)),
                                        elapsed=elapsed,
                                        test_type=self.test_type,
                                        stage=current_stage)
        
        # Clear completed tests
        for test_num in tests_to_clear:
            del self._active_tests[test_num]
            del self._test_completion_times[test_num]
    
    def get_statistics(self) -> TestStatistics:
        """
        Get current statistics snapshot.
        
        Returns:
            TestStatistics with current state
        """
        return TestStatistics(
            completed=self.state.completed_tests,
            total=self.state.total_tests,
            passed=self.state.passed_tests,
            failed=self.state.failed_tests,
            progress_pct=self.state.progress_percentage,
            elapsed_seconds=self.state.elapsed_time,
            remaining_seconds=self.state.estimated_remaining_seconds,
            tests_per_second=self.state.tests_per_second,
            workers_active=self.state.max_workers
        )
    
    def is_running(self) -> bool:
        """Check if tests are running"""
        return self.state.is_running
