"""
Test suite for Code Testing Suite application.

This package contains all test modules organized by component:
- test_utils/: Tests for utility modules
- test_views/: Tests for UI components 
- test_tools/: Tests for compilation and AI tools
- test_integration/: Integration tests
"""

import sys
import os
from pathlib import Path

# Add project root to Python path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Ensure constants are available for tests
try:
    from constants import USER_DATA_DIR, ensure_user_data_dir
    ensure_user_data_dir()
except ImportError:
    # Fallback for tests that run without full application setup
    pass
