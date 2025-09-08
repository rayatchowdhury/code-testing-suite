#!/usr/bin/env python3
"""
Debug config loading specifically.
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.app.shared.constants import CONFIG_FILE

def debug_config_loading():
    print("🔍 Debugging Config Loading...")
    print(f"CONFIG_FILE: {CONFIG_FILE}")
    print(f"Config exists: {os.path.exists(CONFIG_FILE)}")
    
    if os.path.exists(CONFIG_FILE):
        print("\nReading config file directly:")
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        print("Full config:", json.dumps(config_data, indent=2))
        
        gemini_config = config_data.get("gemini", {})
        print(f"\nGemini section: {gemini_config}")
        print(f"Enabled: {gemini_config.get('enabled')}")
        print(f"API Key: {'SET' if gemini_config.get('api_key') else 'EMPTY'}")
        print(f"Model: {gemini_config.get('model')}")
    
    print("\nTesting GeminiAI client...")
    from src.app.core.ai.gemini_client.gemini_client import GeminiAI
    
    # Test 1: No config file
    print("\n1. Client with no config file:")
    client1 = GeminiAI()
    print(f"   Enabled: {client1._enabled}")
    print(f"   API Key: {'SET' if client1._api_key else 'EMPTY'}")
    
    # Test 2: With config file
    print(f"\n2. Client with config file: {CONFIG_FILE}")
    client2 = GeminiAI(CONFIG_FILE)
    print(f"   Enabled: {client2._enabled}")
    print(f"   API Key: {'SET' if client2._api_key else 'EMPTY'}")
    print(f"   Model: {client2._model_name}")
    
    # Test 3: Manual load_config call
    print(f"\n3. Manual load_config call:")
    client3 = GeminiAI()
    client3.load_config(CONFIG_FILE)
    print(f"   Enabled: {client3._enabled}")
    print(f"   API Key: {'SET' if client3._api_key else 'EMPTY'}")
    print(f"   Model: {client3._model_name}")

if __name__ == "__main__":
    debug_config_loading()
