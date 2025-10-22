"""
Detailed module loading analysis - see what's importing what
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

print("Analyzing import chain...")
print()

# Intercept imports
original_import = __builtins__.__import__
import_chain = []

def tracking_import(name, *args, **kwargs):
    if 'src.app' in name:
        import_chain.append(name)
    return original_import(name, *args, **kwargs)

__builtins__.__import__ = tracking_import

# Now import MainWindow
from src.app.presentation.windows.main import MainWindow

# Restore
__builtins__.__import__ = original_import

print("Import chain for MainWindow:")
print("=" * 80)
for i, module in enumerate(import_chain, 1):
    print(f"{i:3}. {module}")

print()
print("=" * 80)
print("ANALYSIS")
print("=" * 80)

# Find what shouldn't be loaded
unnecessary = []
for mod in import_chain:
    if 'editor' in mod and 'editor' not in ('sidebar', 'display'):
        unnecessary.append(('editor components', mod))
    elif 'ai_panel' in mod:
        unnecessary.append(('AI panel', mod))
    elif 'console' in mod:
        unnecessary.append(('console', mod))
    elif 'results' in mod and 'windows.results' not in mod:
        unnecessary.append(('results styles', mod))
    elif 'test_view' in mod:
        unnecessary.append(('test view styles', mod))

if unnecessary:
    print("\n⚠️  Unnecessary modules loaded at startup:")
    for category, mod in unnecessary:
        print(f"  [{category}] {mod}")
else:
    print("\n✅ No obviously unnecessary modules detected")

print()
print(f"Total src.app modules imported: {len(import_chain)}")
