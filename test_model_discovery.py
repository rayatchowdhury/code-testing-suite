#!/usr/bin/env python3

"""
Test script to verify dynamic model discovery
"""

import logging
from ai.core.editor_ai import EditorAI

# Enable logging to see what's happening
logging.basicConfig(level=logging.INFO)

def main():
    print("Testing dynamic Gemini model discovery...")
    
    # Create AI instance
    ai = EditorAI()
    
    print(f"✓ EditorAI instance created")
    print(f"✓ API key loaded: {bool(ai._load_api_key())}")
    print(f"✓ Model initialized: {bool(ai.model)}")
    
    if ai.model:
        print(f"✓ Current model: {ai.get_current_model_name()}")
    else:
        print("✗ No model available")
    
    # Test model discovery directly
    print("\nTesting model discovery...")
    try:
        available_models = ai._get_available_models()
        print(f"Available models: {available_models}")
    except Exception as e:
        print(f"Error discovering models: {e}")

if __name__ == "__main__":
    main()
