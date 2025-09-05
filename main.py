#!/usr/bin/env python3
"""
Legacy entry point for Code Testing Suite.

This script provides backward compatibility during migration.
It delegates to the new src/app structure while maintaining
the old interface.

Usage: python main.py
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def main():
    """Delegate to the new entry point"""
    try:
        # Import and run the new main
        from app.__main__ import main as app_main
        app_main()
    except ImportError as e:
        print(f"❌ Failed to start application: {e}")
        print("The application structure may be incomplete.")
        print("Try running: python -m src.app")
        sys.exit(1)

if __name__ == '__main__':
    main()
