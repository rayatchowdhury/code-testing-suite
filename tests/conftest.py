import pytest
import sys
from pathlib import Path

# Add project root to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for testing"""
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    app.quit()
