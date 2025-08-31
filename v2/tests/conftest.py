# v2 Testing Configuration
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture
def mock_config_service():
    """Mock configuration service for testing."""
    service = Mock()
    service.get_ai_settings.return_value = Mock(enabled=False, api_key="")
    service.get_workspace_path.return_value = Path("/tmp/test_workspace")
    return service

@pytest.fixture
def test_config_file(tmp_path):
    """Temporary config file for testing."""
    config_file = tmp_path / "test_config.json"
    config_file.write_text('{"cpp_version": "c++17", "workspace_folder": ""}')
    return config_file
