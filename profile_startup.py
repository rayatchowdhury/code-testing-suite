#!/usr/bin/env python3
"""Simple startup profiler to identify slow imports."""

import time
import sys
import os

def time_import(module_name, description=""):
    """Time how long it takes to import a module."""
    print(f"Importing {module_name}... {description}")
    start = time.time()
    try:
        if module_name == "main_components":
            # Special case for main components
            os.environ['QT_API'] = 'pyside6'
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import Qt
            from PySide6.QtGui import QIcon
            import qasync
            import asyncio
        elif module_name == "logging_config":
            from utils.logging_config import LoggingConfig
            LoggingConfig.initialize()
        elif module_name == "main_window":
            from views.main_window import MainWindow
        elif module_name == "constants":
            from constants import APP_ICON
        else:
            __import__(module_name)
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return None
    
    elapsed = time.time() - start
    print(f"  ✓ {elapsed:.3f}s")
    return elapsed

def main():
    print("🔍 Profiling application startup...")
    total_start = time.time()
    
    times = {}
    
    # Profile individual components
    times['constants'] = time_import("constants", "App icons and paths")
    times['logging'] = time_import("logging_config", "Logging setup")
    times['main_components'] = time_import("main_components", "PySide6, qasync, etc.")
    times['main_window'] = time_import("main_window", "Main application window")
    
    total_time = time.time() - total_start
    
    print(f"\n📊 Startup Profile Results:")
    print(f"{'Component':<15} {'Time (s)':<10} {'% of Total':<10}")
    print("-" * 35)
    
    for name, elapsed in times.items():
        if elapsed is not None:
            percentage = (elapsed / total_time) * 100
            print(f"{name:<15} {elapsed:<10.3f} {percentage:<10.1f}%")
    
    print("-" * 35)
    print(f"{'TOTAL':<15} {total_time:<10.3f} {'100.0%':<10}")

if __name__ == "__main__":
    main()
