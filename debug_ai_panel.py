#!/usr/bin/env python3
"""
Debug script to test AI panel visibility within application context.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Qt API
os.environ['QT_API'] = 'pyside6'

from PySide6.QtWidgets import QApplication
from src.app.presentation.widgets.display_area_widgets.ai_panel import AIPanel
from src.app.core.ai.gemini_client import should_show_ai_panel, get_gemini_client
from src.app.shared.constants import CONFIG_FILE

def debug_ai_panel():
    print("🧪 Debugging AI Panel Visibility...")
    
    # Check config file
    print("0. Configuration check:")
    print(f"   CONFIG_FILE: {CONFIG_FILE}")
    print(f"   Config exists: {os.path.exists(CONFIG_FILE)}")
    
    # Check client state
    print("\n1. Testing client state:")
    client = get_gemini_client()
    print(f"   Client enabled: {client._enabled}")
    print(f"   Client API key: {'SET' if client._api_key else 'EMPTY'}")
    print(f"   Client model: {client._model_name}")
    
    # Load with explicit config file
    print(f"\n2. Loading client with explicit config:")
    client_explicit = get_gemini_client(CONFIG_FILE)
    print(f"   Explicit client enabled: {client_explicit._enabled}")
    print(f"   Explicit client API key: {'SET' if client_explicit._api_key else 'EMPTY'}")
    print(f"   Explicit client model: {client_explicit._model_name}")
    
    # Test the function directly
    print("\n3. Testing should_show_ai_panel() directly:")
    should_show = should_show_ai_panel()
    print(f"   Result: {should_show}")
    
    # Create AI panel
    print("\n4. Creating AI Panel...")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    panel = AIPanel(panel_type="editor")
    print(f"   Panel created successfully")
    
    # Test panel's internal check
    print("\n5. Testing panel's _should_show_ai_panel():")
    panel_check = panel._should_show_ai_panel()
    print(f"   Result: {panel_check}")
    
    # Check initial visibility
    print(f"\n6. Panel visibility after creation:")
    print(f"   isVisible(): {panel.isVisible()}")
    print(f"   isHidden(): {panel.isHidden()}")
    print(f"   Has layout: {panel.layout() is not None}")
    
    # Force refresh
    print(f"\n7. Calling refresh_visibility()...")
    panel.refresh_visibility()
    
    print(f"   After refresh:")
    print(f"   isVisible(): {panel.isVisible()}")
    print(f"   isHidden(): {panel.isHidden()}")
    print(f"   Has layout: {panel.layout() is not None}")
    
    if panel.layout():
        print(f"   Layout count: {panel.layout().count()}")
        print(f"   Layout type: {type(panel.layout())}")
    
    # Force enable for testing
    print(f"\n8. Force enabling client for test...")
    client._enabled = True
    if not client._api_key:
        client._api_key = "test_key"
    
    print(f"   Now should_show_ai_panel(): {should_show_ai_panel()}")
    panel.refresh_visibility()
    print(f"   Panel visible after force enable: {panel.isVisible()}")
    
    print(f"\n✅ Debug complete!")

if __name__ == "__main__":
    debug_ai_panel()
