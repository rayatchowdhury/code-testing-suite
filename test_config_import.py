#!/usr/bin/env python3
"""Test the new modular config structure."""

try:
    from config import ConfigView
    print("✅ Import successful - Config modular structure working!")
    print("ConfigView class:", ConfigView)
    print("ConfigView module:", ConfigView.__module__)
    print("✨ Config module refactoring complete!")
except Exception as e:
    print("❌ Import failed:", e)
    import traceback
    traceback.print_exc()
