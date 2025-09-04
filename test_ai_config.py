"""
Test script to verify AI model configuration and background initialization.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai.core.editor_ai import EditorAI
from views.config.config_manager import ConfigManager
import json

def test_model_configuration():
    """Test the new model configuration system."""
    print("🚀 Testing AI Model Configuration System")
    print("=" * 50)
    
    # Test 1: Check config loading
    print("\n1️⃣ Testing Config Loading...")
    config_manager = ConfigManager()
    try:
        config = config_manager.load_config()
        ai_settings = config.get('ai_settings', {})
        preferred_model = ai_settings.get('preferred_model', '')
        print(f"✅ Preferred model from config: '{preferred_model}' (empty = auto-select)")
    except Exception as e:
        print(f"❌ Config load failed: {e}")
    
    # Test 2: Test EditorAI initialization
    print("\n2️⃣ Testing EditorAI Initialization...")
    try:
        ai = EditorAI()
        current_model = ai.get_current_model_name()
        print(f"✅ AI initialized successfully")
        print(f"📍 Current model: {current_model}")
        print(f"🔧 Model object exists: {ai.model is not None}")
        
        # Test model caching
        print("\n3️⃣ Testing Model Caching...")
        cached_models = ai._cached_models
        print(f"✅ Cached models: {cached_models}")
        
        # Test force refresh
        print("\n4️⃣ Testing Force Refresh...")
        fresh_models = ai.refresh_available_models()
        print(f"✅ Fresh model list: {fresh_models}")
        
    except Exception as e:
        print(f"❌ AI initialization failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test completed!")

if __name__ == "__main__":
    test_model_configuration()
