"""Basic import tests to ensure migration doesn't break imports"""

def test_main_import():
    """Test that main entry point can be imported"""
    try:
        import main
        assert hasattr(main, 'main')
        assert callable(main.main)
    except ImportError as e:
        assert False, f"Failed to import main module: {e}"

def test_core_components_import():
    """Test that core components can be imported"""
    try:
        from views import main_window
        from widgets import sidebar
        from utils import window_manager
        assert True
    except ImportError as e:
        assert False, f"Failed to import core components: {e}"

def test_database_import():
    """Test that database components can be imported"""
    try:
        from database import database_manager
        from database import models
        assert True
    except ImportError as e:
        assert False, f"Failed to import database components: {e}"

def test_ai_import():
    """Test that AI components can be imported"""
    try:
        from ai.core import editor_ai
        from ai.models import model_manager
        assert True
    except ImportError as e:
        assert False, f"Failed to import AI components: {e}"
