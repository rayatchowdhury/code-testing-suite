#!/usr/bin/env python3

"""
Test script to verify AI functionality
"""

import asyncio
import logging
from ai.core.editor_ai import EditorAI

# Enable logging to see what's happening
logging.basicConfig(level=logging.INFO)

async def test_ai():
    print("Testing EditorAI setup...")
    
    # Create AI instance
    ai = EditorAI()
    print(f"✓ EditorAI instance created")
    print(f"✓ API key loaded: {bool(ai._load_api_key())}")
    print(f"✓ Model initialized: {bool(ai.model)}")
    
    if not ai.model:
        print("✗ AI model not initialized - cannot test requests")
        return
    
    # Test a simple request
    print("\nTesting AI request...")
    test_code = """
def hello():
    print("Hello, World!")
hello()
"""
    
    try:
        response = await ai.process_explanation("analysis", test_code)
        if response:
            print("✓ AI request successful!")
            print(f"Response length: {len(response)} characters")
            print(f"First 100 chars: {response[:100]}...")
        else:
            print("✗ AI request returned empty response")
    except Exception as e:
        print(f"✗ AI request failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_ai())
