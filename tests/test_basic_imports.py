"""Basic import tests to ensure migration doesn't break imports"""
import sys
from pathlib import Path

# Add src to Python path for testing
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

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
        from src.app.views import main_window
        from src.app.widgets import sidebar
        from src.app.utils import window_manager
        assert True
    except ImportError as e:
        assert False, f"Failed to import core components: {e}"

def test_database_import():
    """Test that database components can be imported"""
    try:
        from src.app.database import database_manager
        from src.app.database import models
        assert True
    except ImportError as e:
        assert False, f"Failed to import database components: {e}"

def test_ai_import():
    """Test that AI components can be imported"""
    try:
        from src.app.ai.core import editor_ai
        from src.app.ai.models import model_manager
        assert True
    except ImportError as e:
        assert False, f"Failed to import AI components: {e}"
