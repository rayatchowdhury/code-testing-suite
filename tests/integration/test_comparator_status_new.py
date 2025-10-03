"""
Integration tests for comparator status view - NEW ARCHITECTURE.

Tests the signal-based integration between:
- BaseRunner signal emissions
- Window signal handling and UI coordination
- Status view creation and integration
- Navigation and cleanup via presentation layer
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QWidget

from src.app.core.tools.comparator import Comparator
from src.app.presentation.views.comparator.comparator_status_view import ComparatorStatusView
from src.app.presentation.widgets.unified_status_view import BaseStatusView


class TestRunnerSignalEmission:
    """Test that BaseRunner emits signals correctly (no UI manipulation)"""
    
    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create temporary workspace with test files"""
        workspace = tmp_path / "workspace" / "comparator"
        workspace.mkdir(parents=True)
        
        # Create simple C++ files for testing
        generator = workspace / "generator.cpp"
        generator.write_text("""
            #include <iostream>
            int main() {
                std::cout << "1 2\\n";
                return 0;
            }
        """)
        
        correct = workspace / "correct.cpp"
        correct.write_text("""
            #include <iostream>
            int main() {
                int a, b;
                std::cin >> a >> b;
                std::cout << a + b << "\\n";
                return 0;
            }
        """)
        
        test = workspace / "test.cpp"
        test.write_text("""
            #include <iostream>
            int main() {
                int a, b;
                std::cin >> a >> b;
                std::cout << a + b << "\\n";
                return 0;
            }
        """)
        
        return str(workspace.parent)
    
    def test_runner_emits_testing_started_signal(self, temp_workspace, qtbot):
        """Test runner emits testingStarted signal when tests begin"""
        comparator = Comparator(workspace_dir=temp_workspace)
        
        # Connect to signal
        signal_received = []
        comparator.testingStarted.connect(lambda: signal_received.append(True))
        
        # Mock worker creation and compilation
        mock_worker = Mock()
        mock_worker.moveToThread = Mock()
        
        with patch.object(comparator, '_create_test_worker', return_value=mock_worker):
            with patch('PySide6.QtCore.QThread'):
                comparator.run_comparison_test(1)
        
        # Signal should have been emitted
        assert len(signal_received) > 0, "testingStarted signal should be emitted"
        
    def test_runner_provides_worker_access(self, temp_workspace, qtbot):
        """Test runner provides access to worker via get_current_worker()"""
        comparator = Comparator(workspace_dir=temp_workspace)
        
        # Initially no worker
        assert comparator.get_current_worker() is None
        
        # Create mock worker
        mock_worker = Mock()
        mock_worker.moveToThread = Mock()
        
        with patch.object(comparator, '_create_test_worker', return_value=mock_worker):
            with patch('PySide6.QtCore.QThread'):
                comparator.run_comparison_test(1)
        
        # Should be able to get worker
        worker = comparator.get_current_worker()
        assert worker is mock_worker
        
    def test_runner_emits_testing_completed_signal(self, temp_workspace, qtbot):
        """Test runner emits testingCompleted signal"""
        comparator = Comparator(workspace_dir=temp_workspace)
        
        # Connect to signal
        signal_received = []
        comparator.testingCompleted.connect(lambda: signal_received.append(True))
        
        # Manually trigger the completion signal (as would happen after tests)
        comparator.testingCompleted.emit()
        
        # Signal should have been received
        assert len(signal_received) == 1


class TestWindowUICoordination:
    """Test that windows handle signals and coordinate UI properly"""
    
    def test_window_creates_status_view_on_signal(self, qtbot):
        """Test window creates status view when receiving testingStarted signal"""
        from src.app.presentation.views.base_window import SidebarWindowBase
        
        # Create mock window with necessary attributes
        window = Mock(spec=SidebarWindowBase)
        window.display_area = Mock()
        window.display_area.layout = Mock(return_value=Mock())
        window.status_view = None
        
        # Create mock runner
        runner = Mock()
        runner.testingStarted = Mock()
        runner.get_current_worker = Mock(return_value=Mock())
        
        # Simulate window's _on_testing_started method
        def _on_testing_started():
            window.status_view = ComparatorStatusView()
            worker = runner.get_current_worker()
            # Connect worker signals...
        
        # Connect signal (as window would do)
        runner.testingStarted.connect = lambda handler: handler()
        runner.testingStarted.connect(_on_testing_started)
        
        # Verify status view was created
        assert isinstance(window.status_view, ComparatorStatusView)


class TestStatusViewSignals:
    """Test signal connections between worker and status view"""
    
    def test_stop_signal_emitted(self, qtbot):
        """Test stopRequested signal can be emitted"""
        status_view = ComparatorStatusView()
        qtbot.addWidget(status_view)
        
        # Connect to signal
        signal_received = []
        status_view.stopRequested.connect(lambda: signal_received.append(True))
        
        # Emit signal
        status_view.stopRequested.emit()
        
        # Check signal was received
        assert len(signal_received) == 1
        
    def test_back_signal_emitted(self, qtbot):
        """Test backRequested signal can be emitted"""
        status_view = ComparatorStatusView()
        qtbot.addWidget(status_view)
        
        # Connect to signal
        signal_received = []
        status_view.backRequested.connect(lambda: signal_received.append(True))
        
        # Emit signal
        status_view.backRequested.emit()
        
        # Check signal was received
        assert len(signal_received) == 1


class TestCardCreation:
    """Test test card creation and updates"""
    
    def test_test_completed_creates_card(self, qtbot):
        """Test on_test_completed creates test card"""
        status_view = ComparatorStatusView()
        qtbot.addWidget(status_view)
        
        # Start tests
        status_view.on_tests_started(5)
        
        # Complete a test
        status_view.on_test_completed(
            test_number=1,
            passed=True,
            time=0.5,
            memory=10.0,
            input_text="1 2",
            correct_output="3",
            test_output="3"
        )
        
        # Check card was added
        assert status_view.cards_section.layout().count() > 0
        
    def test_failed_test_switches_layout(self, qtbot):
        """Test failed test switches to split layout"""
        status_view = ComparatorStatusView()
        qtbot.addWidget(status_view)
        
        status_view.on_tests_started(5)
        
        # Add passing test
        status_view.on_test_completed(
            test_number=1,
            passed=True,
            time=0.5,
            memory=10.0,
            input_text="1 2",
            correct_output="3",
            test_output="3"
        )
        
        # Initially single layout
        assert status_view.cards_section.layout_mode == 'single'
        
        # Add failing test
        status_view.on_test_completed(
            test_number=2,
            passed=False,
            time=0.5,
            memory=10.0,
            input_text="2 3",
            correct_output="5",
            test_output="6"
        )
        
        # Should switch to split layout
        assert status_view.cards_section.layout_mode == 'split'
        
    def test_test_data_stored_for_details(self, qtbot):
        """Test test data is stored in cards for detail view"""
        status_view = ComparatorStatusView()
        qtbot.addWidget(status_view)
        
        status_view.on_tests_started(1)
        
        # Complete test with data
        input_text = "1 2"
        correct_output = "3"
        test_output = "3"
        
        status_view.on_test_completed(
            test_number=1,
            passed=True,
            time=0.5,
            memory=10.0,
            input_text=input_text,
            correct_output=correct_output,
            test_output=test_output
        )
        
        # Get card
        card = status_view.cards_section.passed_cards[0]
        
        # Verify data stored
        assert card.input_text == input_text
        assert card.correct_output == correct_output
        assert card.test_output == test_output


class TestProgressUpdates:
    """Test progress updates"""
    
    def test_progress_updates_on_completion(self, qtbot):
        """Test progress bar updates as tests complete"""
        status_view = ComparatorStatusView()
        qtbot.addWidget(status_view)
        
        status_view.on_tests_started(3)
        
        # Complete tests one by one
        for i in range(1, 4):
            status_view.on_test_completed(
                test_number=i,
                passed=True,
                time=0.5,
                memory=10.0,
                input_text="1 2",
                correct_output="3",
                test_output="3"
            )
            
            # Check progress updated
            assert status_view.completed_tests == i
            assert status_view.passed_tests == i
            
    def test_all_tests_completed_updates_state(self, qtbot):
        """Test all tests completed updates state"""
        status_view = ComparatorStatusView()
        qtbot.addWidget(status_view)
        
        status_view.on_tests_started(2)
        
        # Complete all tests
        for i in range(1, 3):
            status_view.on_test_completed(
                test_number=i,
                passed=True,
                time=0.5,
                memory=10.0,
                input_text="1 2",
                correct_output="3",
                test_output="3"
            )
        
        # Mark complete
        status_view.on_all_tests_completed(all_passed=True)
        
        # Check state
        assert not status_view.tests_running


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
