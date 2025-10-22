"""
Measure startup time and identify bottlenecks in application startup.

This script profiles the import chain and identifies what's actually slow.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

print("=" * 80)
print("STARTUP PERFORMANCE ANALYSIS")
print("=" * 80)
print()

# Measure overall import time
start = time.perf_counter()

print("Phase 1: Qt imports...")
t0 = time.perf_counter()
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
t1 = time.perf_counter()
print(f"  Qt imports: {(t1-t0)*1000:.1f}ms")

print("\nPhase 2: App structure imports...")
t0 = time.perf_counter()
from src.app.shared.constants import WORKSPACE_DIR, ensure_user_data_dir
from src.app.shared.utils.workspace_utils import ensure_workspace_structure
t1 = time.perf_counter()
print(f"  Shared utilities: {(t1-t0)*1000:.1f}ms")

print("\nPhase 3: Main window import...")
t0 = time.perf_counter()
from src.app.presentation.windows.main import MainWindow
t1 = time.perf_counter()
print(f"  MainWindow import: {(t1-t0)*1000:.1f}ms")

print("\nPhase 4: Other heavy imports...")
t0 = time.perf_counter()
import qasync
t1 = time.perf_counter()
print(f"  qasync: {(t1-t0)*1000:.1f}ms")

total = time.perf_counter() - start
print()
print(f"TOTAL IMPORT TIME: {total*1000:.1f}ms")
print()

# Now let's see what modules are loaded
print("=" * 80)
print("LOADED MODULES ANALYSIS")
print("=" * 80)
print()

src_modules = [name for name in sys.modules.keys() if 'src.app' in name]
print(f"Total src.app modules loaded: {len(src_modules)}")
print()

# Group by category
window_modules = [m for m in src_modules if 'windows' in m]
component_modules = [m for m in src_modules if 'components' in m]
core_modules = [m for m in src_modules if 'core' in m]
database_modules = [m for m in src_modules if 'database' in m]

print(f"Window modules: {len(window_modules)}")
for m in sorted(window_modules)[:10]:
    print(f"  - {m}")
if len(window_modules) > 10:
    print(f"  ... and {len(window_modules) - 10} more")

print(f"\nComponent modules: {len(component_modules)}")
for m in sorted(component_modules)[:10]:
    print(f"  - {m}")
if len(component_modules) > 10:
    print(f"  ... and {len(component_modules) - 10} more")

print(f"\nCore modules: {len(core_modules)}")
for m in sorted(core_modules)[:10]:
    print(f"  - {m}")

print(f"\nDatabase modules: {len(database_modules)}")
for m in sorted(database_modules):
    print(f"  - {m}")

print()
print("=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)
print()

if len(window_modules) > 3:
    print("⚠️  WARNING: Too many window modules loaded at startup!")
    print(f"   Expected: 1-2 (main window only)")
    print(f"   Actual: {len(window_modules)}")
    print("   → Check for eager imports in __init__.py files")
    print()

if len(component_modules) > 20:
    print("⚠️  WARNING: Too many component modules loaded!")
    print(f"   Loaded: {len(component_modules)}")
    print("   → Some components may not be lazy loaded properly")
    print()

if 'pygments' in str(sys.modules.keys()).lower():
    print("⚠️  WARNING: Pygments loaded at startup!")
    print("   → Syntax highlighting should be lazy loaded")
    print()

if 'markdown' in str(sys.modules.keys()).lower():
    print("⚠️  WARNING: Markdown loaded at startup!")
    print("   → Markdown rendering should be lazy loaded")
    print()

print("✅ Analysis complete!")
