"""
Integration tests for comparator status view.

Tests the complete integration between:
- BaseRunner and status view
- ComparatorWindow and display area
- Status view and test cards
- Navigation and cleanup
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from PySide6.QtWidgets import QWidget

from src.app.core.tools.comparator import Comparator
from src.app.presentation.views.comparator.comparator_status_view import ComparatorStatusView
from src.app.presentation.widgets.unified_status_view import BaseStatusView


class TestComparatorRunnerIntegration:
    """Test runner integration with status view"""
    
    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create temporary workspace with test files"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        
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
        
        return str(workspace)
    
    def test_runner_creates_status_view_with_parent(self, temp_workspace, qtbot):
        """Test runner creates status view when parent window is set"""
        comparator = Comparator(workspace_dir=temp_workspace)
        
        # Create mock parent window
        parent = Mock()
        parent.display_area = Mock()
        parent.display_area.set_content = Mock()
        parent.display_area.layout = Mock()
        parent.display_area.layout.count = Mock(return_value=0)
        
        # Set parent window
        comparator.set_parent_window(parent)
        
        assert comparator.parent_window == parent
        
    def test_runner_creates_status_view_correct_type(self, temp_workspace, qtbot):
        """Test runner creates ComparatorStatusView"""
        comparator = Comparator(workspace_dir=temp_workspace)
        
        # Create mock parent window
        parent = Mock()
        parent.display_area = Mock()
        
        comparator.set_parent_window(parent)
        
        # Create status view
        status_view = comparator._create_test_status_window()
        
        assert isinstance(status_view, ComparatorStatusView)
        assert isinstance(status_view, BaseStatusView)
        
    def test_runner_requires_parent_window(self, temp_workspace, qtbot):
        """Test runner requires parent window to create status view"""
        comparator = Comparator(workspace_dir=temp_workspace)
        
        # Set parent window (required for new architecture)
        mock_parent = qtbot.addWidget(QWidget())
        comparator.set_parent_window(mock_parent)
        
        status_view = comparator._create_test_status_window()
        
        # Should create ComparatorStatusView with parent window
        assert status_view is not None
        assert isinstance(status_view, ComparatorStatusView)


class TestDisplayAreaIntegration:
    """Test display area integration"""
    
    def test_status_view_integrates_with_display_area(self, qtbot):
        """Test status view is added to display area"""
        from src.app.core.tools.base.base_runner import BaseRunner
        
        # Create mock runner
        runner = BaseRunner.__new__(BaseRunner)
        runner.test_type = 'test'
        
        # Create mock parent window with display area
        parent = Mock()
        parent.display_area = Mock()
        parent.display_area.set_content = Mock()
        parent.display_area.layout = Mock()
        parent.display_area.layout.count = Mock(return_value=1)
        parent.display_area.layout.itemAt = Mock(return_value=Mock(widget=Mock(return_value=Mock())))
        
        runner.parent_window = parent
        runner.status_view = ComparatorStatusView()
        
        # Integrate status view
        runner._integrate_status_view()
        
        # Check display area was updated
        parent.display_area.set_content.assert_called_once_with(runner.status_view)
        
    def test_original_content_stored_for_restoration(self, qtbot):
        """Test original display content is stored"""
        from src.app.core.tools.base.base_runner import BaseRunner
        
        runner = BaseRunner.__new__(BaseRunner)
        runner.test_type = 'test'
        
        # Create mock with original content
        original_widget = Mock()
        parent = Mock()
        parent.display_area = Mock()
        parent.display_area.set_content = Mock()
        parent.display_area.layout = Mock()
        parent.display_area.layout.count = Mock(return_value=1)
        parent.display_area.layout.itemAt = Mock(return_value=Mock(widget=Mock(return_value=original_widget)))
        
        runner.parent_window = parent
        runner.status_view = ComparatorStatusView()
        
        runner._integrate_status_view()
        
        assert runner.original_display_content == original_widget


class TestNavigationAndCleanup:
    """Test navigation and cleanup behavior"""
    
    def test_back_request_restores_display(self, qtbot):
        """Test back button restores original display"""
        from src.app.core.tools.base.base_runner import BaseRunner
        
        runner = BaseRunner.__new__(BaseRunner)
        runner.test_type = 'test'
        
        # Setup with original content
        original_widget = Mock()
        parent = Mock()
        parent.display_area = Mock()
        parent.display_area.set_content = Mock()
        
        runner.parent_window = parent
        runner.original_display_content = original_widget
        
        # Handle back request
        runner._handle_back_request()
        
        # Check original content was restored
        parent.display_area.set_content.assert_called_once_with(original_widget)
        assert runner.original_display_content is None
        
    def test_stop_restores_display(self, qtbot):
        """Test stop button restores display"""
        from src.app.core.tools.base.base_runner import BaseRunner
        
        runner = BaseRunner.__new__(BaseRunner)
        runner.test_type = 'test'
        runner.worker = None
        runner.thread = None
        runner.status_window = None
        runner.compiler = None
        
        # Setup status view
        original_widget = Mock()
        parent = Mock()
        parent.display_area = Mock()
        parent.display_area.set_content = Mock()
        
        runner.parent_window = parent
        runner.status_view = ComparatorStatusView()
        runner.original_display_content = original_widget
        
        # Stop should restore display
        runner.stop()
        
        # Check restoration
        parent.display_area.set_content.assert_called_with(original_widget)
        assert runner.status_view is None


class TestStatusViewSignals:
    """Test signal connections between runner and status view"""
    
    def test_stop_signal_connected(self, qtbot):
        """Test stopRequested signal is connected to runner.stop()"""
        status_view = ComparatorStatusView()
        qtbot.addWidget(status_view)
        
        # Create mock runner with stop method
        runner = Mock()
        runner.stop = Mock()
        
        # Connect signal
        status_view.stopRequested.connect(runner.stop)
        
        # Simulate tests running and trigger stop via _handle_stop
        status_view.on_tests_started(5)
        status_view._handle_stop()  # Call method directly since stop button is in sidebar now
        
        # Check stop was called
        runner.stop.assert_called_once()
        
    def test_back_signal_connected(self, qtbot):
        """Test backRequested signal is connected"""
        status_view = ComparatorStatusView()
        qtbot.addWidget(status_view)
        
        # Create mock runner
        runner = Mock()
        runner._handle_back_request = Mock()
        
        # Connect signal
        status_view.backRequested.connect(runner._handle_back_request)
        
        # Emit back signal (when not running)
        status_view._handle_back()
        
        # Check handler was called
        runner._handle_back_request.assert_called_once()


class TestCardCreation:
    """Test card creation during test execution"""
    
    def test_test_completed_creates_card(self, qtbot):
        """Test on_test_completed creates comparator card"""
        status_view = ComparatorStatusView()
        qtbot.addWidget(status_view)
        
        # Start tests
        status_view.on_tests_started(3)
        
        # Complete a test
        status_view.on_test_completed(
            test_number=1,
            passed=True,
            input_text="5 10",
            correct_output="15",
            test_output="15",
            time=0.123,
            memory=45.6
        )
        
        # Check card was created
        assert len(status_view.cards_section.passed_cards) == 1
        card = status_view.cards_section.passed_cards[0]
        assert card.test_number == 1
        assert card.passed == True
        assert card.input_text == "5 10"
        
    def test_failed_test_switches_layout(self, qtbot):
        """Test first failed test switches to split layout"""
        status_view = ComparatorStatusView()
        qtbot.addWidget(status_view)
        status_view.show()
        
        status_view.on_tests_started(3)
        
        # Add passed test - should stay single layout
        status_view.on_test_completed(
            test_number=1,
            passed=True,
            input_text="1 2",
            correct_output="3",
            test_output="3"
        )
        assert status_view.cards_section.layout_mode == 'single'
        
        # Add failed test - should switch to split
        status_view.on_test_completed(
            test_number=2,
            passed=False,
            input_text="5 5",
            correct_output="10",
            test_output="9"
        )
        assert status_view.cards_section.layout_mode == 'split'
        
    def test_test_data_stored_for_details(self, qtbot):
        """Test test data is stored for detail view"""
        status_view = ComparatorStatusView()
        qtbot.addWidget(status_view)
        
        status_view.on_tests_started(1)
        
        status_view.on_test_completed(
            test_number=1,
            passed=False,
            input_text="10 20",
            correct_output="30",
            test_output="31",
            time=0.5,
            memory=100.0
        )
        
        # Check data stored
        assert 1 in status_view.test_data
        data = status_view.test_data[1]
        assert data['input_text'] == "10 20"
        assert data['correct_output'] == "30"
        assert data['test_output'] == "31"
        assert data['time'] == 0.5
        assert data['memory'] == 100.0


class TestProgressUpdates:
    """Test progress updates during execution"""
    
    def test_progress_updates_on_completion(self, qtbot):
        """Test progress section updates as tests complete"""
        status_view = ComparatorStatusView()
        qtbot.addWidget(status_view)
        
        status_view.on_tests_started(3)
        
        # Complete tests
        status_view.on_test_completed(1, True, "in1", "out1", "out1")
        assert status_view.completed_tests == 1
        assert status_view.passed_tests == 1
        
        status_view.on_test_completed(2, False, "in2", "out2", "wrong")
        assert status_view.completed_tests == 2
        assert status_view.failed_tests == 1
        
        status_view.on_test_completed(3, True, "in3", "out3", "out3")
        assert status_view.completed_tests == 3
        assert status_view.passed_tests == 2
        
    def test_all_tests_completed_updates_state(self, qtbot):
        """Test all tests completed updates UI state"""
        status_view = ComparatorStatusView()
        qtbot.addWidget(status_view)
        
        status_view.on_tests_started(2)
        status_view.on_test_completed(1, True, "i1", "o1", "o1")
        status_view.on_test_completed(2, True, "i2", "o2", "o2")
        
        # Mark as complete
        status_view.on_all_tests_completed(all_passed=True)
        
        assert status_view.tests_running == False
        # Note: stop button now in sidebar, not in controls panel
