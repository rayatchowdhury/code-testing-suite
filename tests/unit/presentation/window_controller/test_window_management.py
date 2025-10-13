"""
Unit tests for WindowFactory and WindowManager.

Tests window creation, navigation stack, and lifecycle management.
"""

import pytest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QWidget

from src.app.presentation.window_controller.window_management import (
    WindowFactory,
    WindowManager
)


@pytest.fixture(autouse=True)
def reset_factory():
    """Reset WindowFactory registry before each test."""
    WindowFactory.clear_registry()
    yield
    WindowFactory.clear_registry()


class TestWindowFactoryRegistration:
    """Test window creator registration."""
    
    def test_register_window_creator(self):
        """Should register window creator function."""
        def mock_creator():
            return QWidget
        
        WindowFactory.register_window_creator('test_window', mock_creator)
        
        assert 'test_window' in WindowFactory._window_creators
    
    def test_registers_default_creators(self):
        """Should register default window creators."""
        WindowFactory._ensure_registered()
        
        # Should have common windows registered
        creators = WindowFactory._window_creators
        assert 'main' in creators
        assert 'code_editor' in creators
        assert 'comparator' in creators
        assert 'benchmarker' in creators
        assert 'validator' in creators


class TestWindowFactoryCreation:
    """Test window instance creation."""
    
    def test_creates_window_from_registered_creator(self, qtbot):
        """Should create window instance from registered creator."""
        # Create mock window class
        class MockWindow(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
        
        def mock_creator():
            return MockWindow
        
        WindowFactory.register_window_creator('mock', mock_creator)
        
        window = WindowFactory.create_window('mock')
        qtbot.addWidget(window)
        
        assert window is not None
        assert isinstance(window, MockWindow)
    
    def test_returns_none_for_unknown_window(self):
        """Should return None for unregistered window type."""
        window = WindowFactory.create_window('nonexistent')
        
        assert window is None
    
    def test_passes_parent_to_window(self, qtbot):
        """Should pass parent widget to created window."""
        class MockWindow(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.test_parent = parent
        
        def mock_creator():
            return MockWindow
        
        WindowFactory.register_window_creator('mock', mock_creator)
        
        parent = QWidget()
        qtbot.addWidget(parent)
        
        window = WindowFactory.create_window('mock', parent)
        qtbot.addWidget(window)
        
        assert window.test_parent is parent


class TestWindowFactoryClassRetrieval:
    """Test window class retrieval."""
    
    def test_gets_window_class(self):
        """Should return window class without creating instance."""
        class MockWindow(QWidget):
            pass
        
        def mock_creator():
            return MockWindow
        
        WindowFactory.register_window_creator('mock', mock_creator)
        
        window_class = WindowFactory.get_window_class('mock')
        
        assert window_class is MockWindow
    
    def test_returns_none_for_unknown_class(self):
        """Should return None for unknown window class."""
        window_class = WindowFactory.get_window_class('nonexistent')
        
        assert window_class is None


class TestWindowFactoryListing:
    """Test listing available windows."""
    
    def test_lists_available_windows(self):
        """Should list all registered window types."""
        def mock_creator():
            return QWidget
        
        WindowFactory.register_window_creator('window1', mock_creator)
        WindowFactory.register_window_creator('window2', mock_creator)
        
        windows = WindowFactory.list_available_windows()
        
        assert 'window1' in windows
        assert 'window2' in windows
    
    def test_lists_default_windows(self):
        """Should list default registered windows."""
        windows = WindowFactory.list_available_windows()
        
        assert 'main' in windows
        assert 'code_editor' in windows
        assert 'comparator' in windows


class TestWindowFactoryCleanup:
    """Test registry cleanup."""
    
    def test_clears_registry(self):
        """Should clear window creator registry."""
        def mock_creator():
            return QWidget
        
        WindowFactory.register_window_creator('test', mock_creator)
        assert len(WindowFactory._window_creators) > 0
        
        WindowFactory.clear_registry()
        
        assert len(WindowFactory._window_creators) == 0
        assert WindowFactory._registered is False


class TestWindowManagerInitialization:
    """Test WindowManager initialization."""
    
    def test_creates_window_manager(self, qtbot):
        """Should create WindowManager instance."""
        manager = WindowManager()
        qtbot.addWidget(manager)
        
        assert manager is not None
        assert manager.windows == {}
        assert manager.current_window is None
        assert manager.window_history == []


class TestWindowManagerWindowCreation:
    """Test window creation and display."""
    
    def test_shows_window(self, qtbot):
        """Should show window and create if needed."""
        # Register mock window
        class MockWindow(QWidget):
            pass
        
        WindowFactory.register_window_creator('mock', lambda: MockWindow)
        
        manager = WindowManager()
        qtbot.addWidget(manager)
        
        result = manager.show_window('mock')
        
        assert result is True
        assert 'mock' in manager.windows
        assert manager.current_window == 'mock'
    
    def test_reuses_existing_window(self, qtbot):
        """Should reuse existing window instance."""
        class MockWindow(QWidget):
            pass
        
        WindowFactory.register_window_creator('mock', lambda: MockWindow)
        
        manager = WindowManager()
        qtbot.addWidget(manager)
        
        # Show window twice
        manager.show_window('mock')
        first_window = manager.windows['mock']
        
        manager.show_window('mock')
        second_window = manager.windows['mock']
        
        # Should be the same instance
        assert first_window is second_window


class TestWindowManagerNavigation:
    """Test navigation and history management."""
    
    def test_maintains_window_history(self, qtbot):
        """Should maintain navigation history."""
        class MockWindow(QWidget):
            pass
        
        WindowFactory.register_window_creator('window1', lambda: MockWindow)
        WindowFactory.register_window_creator('window2', lambda: MockWindow)
        
        manager = WindowManager()
        qtbot.addWidget(manager)
        
        manager.show_window('window1')
        manager.show_window('window2')
        
        # History should contain window1
        assert 'window1' in manager.window_history
    
    def test_go_back_returns_to_previous(self, qtbot):
        """Should navigate back to previous window."""
        class MockWindow(QWidget):
            pass
        
        WindowFactory.register_window_creator('window1', lambda: MockWindow)
        WindowFactory.register_window_creator('window2', lambda: MockWindow)
        
        manager = WindowManager()
        qtbot.addWidget(manager)
        
        manager.show_window('window1')
        manager.show_window('window2')
        
        result = manager.go_back()
        
        assert result is True
        assert manager.current_window == 'window1'
    
    def test_go_back_returns_false_when_no_history(self, qtbot):
        """Should return False when no history to go back to."""
        manager = WindowManager()
        qtbot.addWidget(manager)
        
        result = manager.go_back()
        
        assert result is False


class TestWindowManagerWindowRetrieval:
    """Test window retrieval."""
    
    def test_gets_current_window(self, qtbot):
        """Should return currently active window."""
        class MockWindow(QWidget):
            pass
        
        WindowFactory.register_window_creator('mock', lambda: MockWindow)
        
        manager = WindowManager()
        qtbot.addWidget(manager)
        
        manager.show_window('mock')
        current = manager.get_current_window()
        
        assert current is not None
        assert isinstance(current, MockWindow)


class TestWindowManagerCleanup:
    """Test window cleanup and resource management."""
    
    def test_cleanup_window(self, qtbot):
        """Should clean up specific window."""
        class MockWindow(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.cleanup_called = False
            
            def cleanup(self):
                self.cleanup_called = True
        
        WindowFactory.register_window_creator('mock', lambda: MockWindow)
        
        manager = WindowManager()
        qtbot.addWidget(manager)
        
        manager.show_window('mock')
        window = manager.windows['mock']
        
        manager.cleanup_window('mock')
        
        assert 'mock' not in manager.windows
        assert window.cleanup_called is True
    
    def test_cleanup_all(self, qtbot):
        """Should clean up all windows."""
        class MockWindow(QWidget):
            pass
        
        WindowFactory.register_window_creator('window1', lambda: MockWindow)
        WindowFactory.register_window_creator('window2', lambda: MockWindow)
        
        manager = WindowManager()
        qtbot.addWidget(manager)
        
        manager.show_window('window1')
        manager.show_window('window2')
        
        manager.cleanup_all()
        
        assert len(manager.windows) == 0
