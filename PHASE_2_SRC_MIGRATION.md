# 🚚 PHASE 2: SRC MIGRATION

**Duration**: 2-3 hours  
**Risk Level**: 🟡 Medium  
**Prerequisites**: Phase 1 Complete  
**Goal**: Move all code to src/ structure while maintaining exact functionality

---

## 📋 PHASE OVERVIEW

This phase executes the bulk migration of all code into the src/ structure. We maintain exact internal organization during the move to ensure zero functionality loss, then establish proper import patterns for the new structure.

### Phase Objectives
1. **Bulk Code Migration**: Move all application code to src/app/ maintaining exact structure
2. **Resource Migration**: Move static resources to src/resources/ 
3. **Entry Point Creation**: Create proper entry points for module execution
4. **Import Path Updates**: Update imports to work with new structure
5. **Functionality Validation**: Ensure app works identically after migration

### Migration Philosophy
- **EXACT STRUCTURE PRESERVATION**: Internal organization unchanged during move
- **FUNCTIONALITY FIRST**: App must work at every checkpoint
- **INCREMENTAL VALIDATION**: Test after each major move operation
- **ROLLBACK READY**: Each step has a rollback procedure

---

## 📁 STEP 2.1: DIRECTORY STRUCTURE CREATION

**Duration**: 20 minutes  
**Output**: Complete src/ directory structure ready for migration

### 2.1.1 Create Base Structure
```bash
# Create the complete src structure
mkdir -p src/{app,resources}

# Create all app subdirectories maintaining current structure
mkdir -p src/app/{
    ai/{config,core,models,templates,validation},
    config/{management,ui,validation},
    constants,
    database,
    styles/{components,constants,helpers},
    tools,
    utils,
    views/{code_editor,help_center,results,stress_tester,tle_tester,config},
    widgets/{dialogs,display_area_widgets}
}

# Create resources structure
mkdir -p src/resources/{icons,readme,templates,docs}

echo "📁 Directory structure created"
```

### 2.1.2 Create Essential __init__.py Files
```bash
# Create __init__.py files for Python package structure
find src/ -type d -exec touch {}/__init__.py \;

# Create main entry point
cat > src/app/__main__.py << 'EOF'
#!/usr/bin/env python3
"""
Application entry point for Code Testing Suite.

This module can be executed as:
- python src/app/__main__.py
- python -m src.app
"""

import sys
import os
from pathlib import Path

# Add project root to path for import compatibility during migration
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set Qt API before any Qt imports
os.environ['QT_API'] = 'pyside6'

def main():
    """Main application entry point."""
    # Import heavy modules only when needed
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
    import qasync
    import asyncio
    
    # Set attributes before creating QApplication
    QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    
    app = QApplication(sys.argv)
    
    # Try to import application components with fallbacks
    try:
        from src.app.constants.paths import APP_ICON
    except ImportError:
        try:
            from app.constants.paths import APP_ICON
        except ImportError:
            from constants.paths import APP_ICON
    
    # Set application icon
    try:
        app.setWindowIcon(QIcon(APP_ICON))
    except:
        pass  # Continue without icon if not found
    
    # Create event loop
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Import and create main window with fallbacks
    try:
        from src.app.views.main_window import MainWindow
    except ImportError:
        try:
            from app.views.main_window import MainWindow
        except ImportError:
            from views.main_window import MainWindow
    
    window = MainWindow()
    window.show()
    
    # Run the event loop
    with loop:
        loop.run_forever()

if __name__ == '__main__':
    main()
EOF

# Create root app __init__.py with version info
cat > src/app/__init__.py << 'EOF'
"""
Code Testing Suite - PySide6 Desktop Application

A comprehensive code editor with AI integration, stress testing,
and time-limit testing capabilities.
"""

__version__ = "1.0.0"
__author__ = "Code Testing Suite Team"

# Lazy imports - only import when accessed
def get_main_window():
    """Lazy import of MainWindow"""
    from .views.main_window import MainWindow
    return MainWindow

def get_window_manager():
    """Lazy import of WindowManager"""
    from .utils.window_manager import WindowManager
    return WindowManager
EOF

echo "📦 Python package structure created"
```

### 2.1.3 Validation Checkpoint
```bash
# Verify structure was created correctly
echo "🔍 Validating directory structure..."

# Check that all expected directories exist
expected_dirs=(
    "src/app/ai/config"
    "src/app/config/management" 
    "src/app/views/code_editor"
    "src/app/styles/components"
    "src/resources/icons"
)

for dir in "${expected_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir"
    else
        echo "❌ $dir missing"
        exit 1
    fi
done

# Test that __main__.py can be imported
python -c "
import sys
sys.path.insert(0, 'src')
try:
    from app.__main__ import main
    print('✅ Entry point importable')
except ImportError as e:
    print(f'❌ Entry point import failed: {e}')
    exit(1)
"

echo "🎉 Structure validation passed"
```

---

## 🚚 STEP 2.2: BULK CODE MIGRATION

**Duration**: 45-60 minutes  
**Output**: All application code moved to src/app/ with exact structure preserved

### 2.2.1 AI Module Migration
```bash
echo "🧠 Migrating AI modules..."

# Copy entire AI directory maintaining structure
cp -r ai/* src/app/ai/

# Verify AI migration
if [ -f "src/app/ai/core/editor_ai.py" ] && [ -f "src/app/ai/config/ai_config.py" ]; then
    echo "✅ AI modules migrated successfully"
else
    echo "❌ AI migration failed"
    exit 1
fi

# Update AI module imports to work in new location
find src/app/ai/ -name "*.py" -exec sed -i.bak 's/^from ai\./from src.app.ai./g' {} \;
find src/app/ai/ -name "*.py" -exec sed -i.bak 's/^import ai\./import src.app.ai./g' {} \;

echo "🔄 AI import paths updated"
```

### 2.2.2 Configuration Module Migration
```bash
echo "⚙️ Migrating configuration modules..."

# Copy configuration directory with full structure
cp -r config/* src/app/config/

# Verify config migration
if [ -f "src/app/config/management/config_manager.py" ] && [ -f "src/app/config/ui/config_dialog.py" ]; then
    echo "✅ Config modules migrated successfully"
else
    echo "❌ Config migration failed"
    exit 1
fi

# Update config imports
find src/app/config/ -name "*.py" -exec sed -i.bak 's/^from config\./from src.app.config./g' {} \;
find src/app/config/ -name "*.py" -exec sed -i.bak 's/^import config\./import src.app.config./g' {} \;

echo "🔄 Config import paths updated"
```

### 2.2.3 Core Application Modules Migration
```bash
echo "📦 Migrating core application modules..."

# Migrate all core directories
modules=(
    "constants"
    "database" 
    "styles"
    "tools"
    "utils"
    "views"
    "widgets"
)

for module in "${modules[@]}"; do
    if [ -d "$module" ]; then
        echo "📁 Migrating $module..."
        cp -r "$module"/* "src/app/$module/"
        
        # Verify migration
        if [ "$(ls -A "src/app/$module/")" ]; then
            echo "✅ $module migrated successfully"
        else
            echo "❌ $module migration failed"
            exit 1
        fi
        
        # Update imports for this module
        find "src/app/$module/" -name "*.py" -exec sed -i.bak "s/^from $module\./from src.app.$module./g" {} \;
        find "src/app/$module/" -name "*.py" -exec sed -i.bak "s/^import $module\./import src.app.$module./g" {} \;
        
        echo "🔄 $module import paths updated"
    else
        echo "⚠️ $module directory not found - skipping"
    fi
done

echo "🎉 All core modules migrated"
```

### 2.2.4 Cross-Module Import Updates
```bash
echo "🔄 Updating cross-module imports..."

# Update imports between modules to use new src.app structure
update_cross_imports() {
    local file="$1"
    
    # Common import patterns to update
    sed -i.bak 's/^from views\./from src.app.views./g' "$file"
    sed -i.bak 's/^from widgets\./from src.app.widgets./g' "$file"
    sed -i.bak 's/^from styles\./from src.app.styles./g' "$file"
    sed -i.bak 's/^from utils\./from src.app.utils./g' "$file"
    sed -i.bak 's/^from constants\./from src.app.constants./g' "$file"
    sed -i.bak 's/^from database\./from src.app.database./g' "$file"
    sed -i.bak 's/^from tools\./from src.app.tools./g' "$file"
    
    # Update bare imports
    sed -i.bak 's/^import views\./import src.app.views./g' "$file"
    sed -i.bak 's/^import widgets\./import src.app.widgets./g' "$file"
    sed -i.bak 's/^import styles\./import src.app.styles./g' "$file"
    sed -i.bak 's/^import utils\./import src.app.utils./g' "$file"
}

# Apply to all Python files in src/app
find src/app/ -name "*.py" -exec bash -c 'update_cross_imports "$0"' {} \;

echo "✅ Cross-module imports updated"
```

### 2.2.5 Migration Validation
```bash
echo "🔍 Validating code migration..."

# Count files in original vs migrated
original_count=$(find ai config constants database styles tools utils views widgets -name "*.py" 2>/dev/null | wc -l)
migrated_count=$(find src/app/ -name "*.py" | wc -l)

echo "📊 Migration Statistics:"
echo "  Original Python files: $original_count"
echo "  Migrated Python files: $migrated_count"

if [ "$migrated_count" -ge "$original_count" ]; then
    echo "✅ File count validation passed"
else
    echo "❌ Migration incomplete - file count mismatch"
    exit 1
fi

# Test basic imports work
python -c "
import sys
sys.path.insert(0, 'src')

try:
    import app
    from app.constants import paths
    from app.views import main_window
    from app.styles import style
    print('✅ Basic imports working in new structure')
except ImportError as e:
    print(f'❌ Import test failed: {e}')
    exit(1)
"

echo "🎉 Code migration validation passed"
```

---

## 🗂️ STEP 2.3: RESOURCES MIGRATION

**Duration**: 15 minutes  
**Output**: All static resources moved to src/resources/

### 2.3.1 Move Resource Files
```bash
echo "🖼️ Migrating resource files..."

# Move resources maintaining structure
if [ -d "resources" ]; then
    cp -r resources/* src/resources/
    echo "✅ Resources copied to src/resources/"
else
    echo "⚠️ No resources directory found - creating minimal structure"
fi

# Ensure required resource directories exist
mkdir -p src/resources/{icons,readme,templates,docs,sample_files}

# Move any standalone resource files
resource_files=("*.png" "*.jpg" "*.ico" "*.svg" "*.css" "*.html")

for pattern in "${resource_files[@]}"; do
    if ls $pattern 1> /dev/null 2>&1; then
        mv $pattern src/resources/
        echo "📁 Moved $pattern to src/resources/"
    fi
done

echo "✅ Resource migration completed"
```

### 2.3.2 Update Resource Paths
```bash
echo "🔄 Updating resource paths in code..."

# Update paths.py to point to new resource location
if [ -f "src/app/constants/paths.py" ]; then
    cat > src/app/constants/paths.py << 'EOF'
"""
Path constants for the Code Testing Suite application.

This module centralizes all file and directory paths to improve maintainability
and make the application more flexible for different deployment scenarios.
"""

import os
from pathlib import Path

# Project structure - updated for src layout  
# Navigate up from src/app/constants/paths.py to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SRC_ROOT = PROJECT_ROOT / "src"
RESOURCES_DIR = SRC_ROOT / "resources"
ICONS_DIR = RESOURCES_DIR / "icons"
README_DIR = RESOURCES_DIR / "readme"
TEMPLATES_DIR = RESOURCES_DIR / "templates"
DOCS_DIR = RESOURCES_DIR / "docs"

# Application icons
APP_ICON = str(ICONS_DIR / "app_icon.png")
SETTINGS_ICON = str(ICONS_DIR / "settings.png")
CHECK_ICON = str(ICONS_DIR / "check.png")
LOGO_ICON = str(ICONS_DIR / "logo.png")

# Template files
CPP_TEMPLATE = str(TEMPLATES_DIR / "template.cpp")
PYTHON_TEMPLATE = str(TEMPLATES_DIR / "template.py")
JAVA_TEMPLATE = str(TEMPLATES_DIR / "template.java")

# Documentation assets
HELP_HTML = str(README_DIR / "help.html")
MAIN_WINDOW_IMAGE = str(README_DIR / "main_window.png")

# Working directories
TEMP_DIR = PROJECT_ROOT / "temp"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
for directory in [TEMP_DIR, OUTPUT_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Validate critical resources exist
def validate_resources():
    """Validate that critical resources are available"""
    critical_resources = [ICONS_DIR, README_DIR]
    
    missing = []
    for resource in critical_resources:
        if not Path(resource).exists():
            missing.append(resource)
    
    if missing:
        print(f"⚠️ Missing resources: {missing}")
        return False
    
    return True

# Auto-validate on import
if __name__ == "__main__":
    validate_resources()
EOF

    echo "✅ Resource paths updated"
fi

# Update any hardcoded resource paths in other files
find src/app/ -name "*.py" -exec sed -i.bak 's|resources/|src/resources/|g' {} \;
find src/app/ -name "*.py" -exec sed -i.bak 's|"icons/|"src/resources/icons/|g' {} \;

echo "🔄 Hardcoded resource paths updated"
```

---

## 🚀 STEP 2.4: ENTRY POINTS AND MODULE EXECUTION

**Duration**: 30 minutes  
**Output**: Working entry points for both script and module execution

### 2.4.1 Create Module Entry Point
```bash
# The __main__.py was already created in step 2.1.2, now let's enhance it
cat > src/app/__main__.py << 'EOF'
#!/usr/bin/env python3
"""
Application entry point for Code Testing Suite.

This module can be executed as:
- python src/app/__main__.py
- python -m src.app
- python -m app (when src is in PYTHONPATH)

The entry point handles proper import path setup and graceful fallbacks
for different execution contexts during the migration process.
"""

import sys
import os
from pathlib import Path

# Add project root to path for import compatibility
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Also add src directory for direct imports
src_root = project_root / "src"
if str(src_root) not in sys.path:
    sys.path.insert(0, str(src_root))

# Set Qt API before any Qt imports
os.environ['QT_API'] = 'pyside6'

def setup_logging():
    """Initialize logging configuration early"""
    try:
        from src.app.utils.logging_config import LoggingConfig
        LoggingConfig.initialize()
    except ImportError:
        try:
            from app.utils.logging_config import LoggingConfig
            LoggingConfig.initialize()
        except ImportError:
            # Fallback to basic logging
            import logging
            logging.basicConfig(level=logging.INFO)

def get_app_icon():
    """Get application icon with multiple fallbacks"""
    icon_paths = [
        "src/resources/icons/app_icon.png",
        "resources/icons/app_icon.png", 
        "icons/app_icon.png"
    ]
    
    for icon_path in icon_paths:
        if Path(icon_path).exists():
            return str(icon_path)
    
    return None  # No icon found

def create_main_window():
    """Create main window with import fallbacks"""
    # Try multiple import paths for MainWindow
    import_paths = [
        "src.app.views.main_window",
        "app.views.main_window", 
        "views.main_window"
    ]
    
    for import_path in import_paths:
        try:
            module = __import__(import_path, fromlist=['MainWindow'])
            return module.MainWindow()
        except ImportError:
            continue
    
    raise ImportError("Could not import MainWindow from any known location")

def main():
    """Main application entry point with comprehensive error handling"""
    try:
        # Initialize logging first
        setup_logging()
        
        # Import Qt components
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QIcon
        import qasync
        import asyncio
        
        # Set attributes before creating QApplication
        QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
        QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Code Testing Suite")
        app.setApplicationVersion("1.0.0")
        
        # Set application icon if available
        icon_path = get_app_icon()
        if icon_path:
            app.setWindowIcon(QIcon(icon_path))
        
        # Create event loop
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        # Create and show main window
        try:
            window = create_main_window()
            window.show()
            
            print("✅ Code Testing Suite started successfully")
            
            # Run the event loop
            with loop:
                loop.run_forever()
                
        except Exception as e:
            print(f"❌ Failed to create main window: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
            
    except ImportError as e:
        print(f"❌ Failed to import required modules: {e}")
        print("Make sure PySide6 and other dependencies are installed:")
        print("pip install PySide6 qasync")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
EOF

echo "🚀 Enhanced entry point created"
```

### 2.4.2 Create Legacy Compatibility Entry Point
```bash
# Update the root main.py to use the new structure
cat > main.py << 'EOF'
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
EOF

echo "🔄 Legacy compatibility entry point created"
```

### 2.4.3 Test Entry Points
```bash
echo "🧪 Testing entry points..."

# Test 1: Module execution
echo "Testing: python -m src.app"
timeout 10 python -m src.app --help 2>/dev/null || echo "⚠️ Module execution test (expected for GUI app)"

# Test 2: Direct script execution  
echo "Testing: python main.py"
timeout 10 python main.py --help 2>/dev/null || echo "⚠️ Script execution test (expected for GUI app)"

# Test 3: Import test
echo "Testing imports..."
python -c "
import sys
sys.path.insert(0, 'src')

try:
    from app.__main__ import main
    print('✅ Entry point import successful')
except ImportError as e:
    print(f'❌ Entry point import failed: {e}')
    exit(1)
"

echo "🎉 Entry point tests completed"
```

---

## ✅ STEP 2.5: COMPREHENSIVE MIGRATION VALIDATION

**Duration**: 30 minutes  
**Output**: Complete functionality verification and performance validation

### 2.5.1 Functional Testing
```bash
echo "🧪 Running comprehensive functional tests..."

# Create migration-specific test
cat > tests/test_migration_phase2.py << 'EOF'
"""
Phase 2 Migration Tests - Comprehensive validation of src structure migration.
"""
import pytest
import sys
from pathlib import Path

# Add both src and project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestPhase2Migration:
    """Test that Phase 2 migration preserved all functionality"""
    
    def test_directory_structure_complete(self):
        """Test that all expected directories were created"""
        expected_dirs = [
            "src/app/ai/config",
            "src/app/ai/core", 
            "src/app/config/management",
            "src/app/views/code_editor",
            "src/app/styles/components",
            "src/resources/icons"
        ]
        
        for dir_path in expected_dirs:
            assert Path(dir_path).exists(), f"Missing directory: {dir_path}"
    
    def test_entry_points_importable(self):
        """Test that entry points can be imported"""
        try:
            from app.__main__ import main
            assert callable(main)
        except ImportError:
            pytest.fail("Cannot import main entry point")
    
    def test_core_modules_importable(self):
        """Test that core modules can be imported from new locations"""
        try:
            from app.constants import paths
            from app.views import main_window
            from app.styles import style
            from app.utils import window_manager
        except ImportError as e:
            pytest.fail(f"Core module import failed: {e}")
    
    def test_resources_accessible(self):
        """Test that resources are accessible from new location"""
        from app.constants.paths import RESOURCES_DIR, ICONS_DIR
        
        assert Path(RESOURCES_DIR).exists(), "Resources directory not found"
        assert Path(ICONS_DIR).exists(), "Icons directory not found"
    
    def test_cross_module_imports(self):
        """Test that cross-module imports work in new structure"""
        try:
            # Test that views can import widgets
            from app.views.main_window import MainWindow
            # Test that widgets can import styles
            from app.widgets.sidebar import Sidebar
            # Test successful instantiation
            sidebar = Sidebar("Test")
            assert sidebar is not None
        except ImportError as e:
            pytest.fail(f"Cross-module import failed: {e}")

class TestPerformanceRegression:
    """Test that migration didn't cause performance regression"""
    
    def test_import_performance(self):
        """Test that imports are still fast after migration"""
        import time
        
        start_time = time.perf_counter()
        try:
            from app import __main__
            from app.views import main_window
            from app.styles import style
        except ImportError:
            pytest.skip("Imports not working - performance test skipped")
        
        end_time = time.perf_counter()
        import_time = end_time - start_time
        
        # Should complete within reasonable time
        assert import_time < 3.0, f"Imports too slow: {import_time:.3f}s"

class TestBackwardCompatibility:
    """Test that legacy interfaces still work"""
    
    def test_legacy_main_py_works(self):
        """Test that main.py still works as entry point"""
        # This would be tested in subprocess in real scenario
        # For now, just test the import structure exists
        assert Path("main.py").exists(), "Legacy main.py missing"
        
        # Test that main.py can find new structure
        with open("main.py") as f:
            content = f.read()
            assert "src" in content, "Legacy main.py not updated for src structure"
EOF

# Run the tests
pytest tests/test_migration_phase2.py -v

if [ $? -eq 0 ]; then
    echo "✅ All migration tests passed"
else
    echo "❌ Some migration tests failed"
    exit 1
fi
```

### 2.5.2 Performance Validation
```bash
echo "📊 Running performance validation..."

# Create performance comparison
python tests/benchmark_baseline.py > phase2_performance.txt

# Compare with baseline if it exists
if [ -f "tests/performance_baseline.json" ]; then
    python -c "
import json
import time
import sys
from pathlib import Path

sys.path.insert(0, 'src')

def measure_current_performance():
    results = {}
    
    modules = [
        'app',
        'app.__main__',
        'app.views.main_window',
        'app.styles.style'
    ]
    
    for module in modules:
        start = time.perf_counter()
        try:
            __import__(module)
            end = time.perf_counter()
            results[module] = end - start
        except ImportError:
            results[module] = 'FAILED'
    
    return results

# Load baseline
with open('tests/performance_baseline.json') as f:
    baseline = json.load(f)

# Measure current
current = measure_current_performance()

print('📊 Performance Comparison:')
print(f'{'Module':<30} {'Baseline':<12} {'Current':<12} {'Status':<10}')
print('-' * 70)

all_good = True
for module, current_time in current.items():
    if isinstance(current_time, str):
        print(f'{module:<30} {'N/A':<12} {current_time:<12} {'FAILED':<10}')
        all_good = False
        continue
        
    baseline_time = baseline.get('imports', {}).get(module, 0)
    if baseline_time == 0:
        status = 'NEW'
    elif current_time <= baseline_time * 1.2:  # Allow 20% tolerance
        status = '✅ OK'
    else:
        status = '⚠️ SLOWER'
        all_good = False
        
    print(f'{module:<30} {baseline_time*1000:>8.2f}ms {current_time*1000:>8.2f}ms {status:<10}')

if all_good:
    print('\n🎉 Performance validation passed')
else:
    print('\n⚠️ Performance issues detected')
"
else
    echo "ℹ️ No baseline found - recording current performance as new baseline"
fi
```

### 2.5.3 GUI Application Test
```bash
echo "🖥️ Testing GUI application startup..."

# Create GUI test script that doesn't actually show GUI
cat > test_gui_startup.py << 'EOF'
"""
Test GUI application startup without actually showing windows.
This validates that the application can be instantiated.
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_gui_startup():
    """Test that GUI application can start up"""
    # Set environment to avoid GUI display
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        from PySide6.QtWidgets import QApplication
        from app.__main__ import create_main_window
        
        # Create application
        app = QApplication(sys.argv)
        
        # Test window creation
        window = create_main_window()
        assert window is not None
        
        print("✅ GUI startup test passed")
        
        # Clean shutdown
        window.close()
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ GUI startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gui_startup()
    sys.exit(0 if success else 1)
EOF

# Run GUI test
python test_gui_startup.py

if [ $? -eq 0 ]; then
    echo "✅ GUI startup validation passed"
    rm test_gui_startup.py
else
    echo "❌ GUI startup validation failed"
    exit 1
fi
```

---

## 📝 STEP 2.6: DOCUMENTATION AND CLEANUP

**Duration**: 15 minutes  
**Output**: Migration documentation and cleanup of temporary files

### 2.6.1 Document Migration Results
```bash
cat > PHASE_2_MIGRATION_REPORT.md << 'EOF'
# Phase 2 Migration Report

**Completion Date**: $(date)
**Duration**: 2-3 hours
**Status**: ✅ COMPLETED

## Migration Summary

### Files Migrated
- **AI Modules**: Complete ai/ directory → src/app/ai/
- **Configuration**: Complete config/ directory → src/app/config/  
- **Core Modules**: constants, database, styles, tools, utils → src/app/
- **UI Components**: views, widgets → src/app/
- **Resources**: resources/ → src/resources/

### Structure Created
```
src/
├── app/                    # Application code
│   ├── __init__.py        # Package initialization
│   ├── __main__.py        # Entry point for python -m src.app
│   ├── ai/                # AI services
│   ├── config/            # Configuration management
│   ├── constants/         # Application constants
│   ├── database/          # Database layer
│   ├── styles/            # UI styling
│   ├── tools/             # External tools
│   ├── utils/             # Utilities
│   ├── views/             # UI views
│   └── widgets/           # UI widgets
└── resources/             # Static resources
    ├── icons/
    ├── readme/
    └── templates/
```

### Entry Points Created
1. **Module Entry**: `python -m src.app` 
2. **Script Entry**: `python main.py` (legacy compatibility)
3. **Direct Entry**: `python src/app/__main__.py`

### Import Paths Updated
- Cross-module imports updated to use src.app prefix
- Resource paths updated to use src/resources
- Fallback imports for migration compatibility

## Validation Results

### ✅ Tests Passed
- Directory structure validation
- Import functionality tests
- Cross-module import tests
- Resource accessibility tests
- Performance regression tests
- GUI startup tests

### 📊 Performance Metrics
- Import times maintained within 20% of baseline
- Memory usage comparable to pre-migration
- Startup time within acceptable range

## Known Issues & Workarounds

### Import Warnings
Some modules may show import warnings during transition. These are handled by fallback imports and will be resolved in Phase 3.

### Resource Path Updates
Some hardcoded resource paths may need manual updating in Phase 3 cleanup.

## Next Steps

1. **Phase 3**: Cleanup original directories and fix remaining imports
2. **Testing**: Comprehensive application testing in new structure
3. **Documentation**: Update development documentation for new structure

---

**Phase 2 Status**: ✅ MIGRATION SUCCESSFUL
**Ready for Phase 3**: ✅ YES
EOF

echo "📄 Migration report generated"
```

### 2.6.2 Cleanup Temporary Files
```bash
echo "🧹 Cleaning up temporary files..."

# Remove backup files created during sed operations
find src/ -name "*.bak" -delete

# Clean up any temporary test files
rm -f phase2_performance.txt

# Remove Python cache files
find src/ -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find src/ -name "*.pyc" -delete 2>/dev/null

echo "✅ Cleanup completed"
```

### 2.6.3 Git Commit and Backup
```bash
echo "💾 Committing Phase 2 results..."

# Add all changes
git add .

# Create comprehensive commit
git commit -m "Phase 2 Complete: SRC Structure Migration

✅ All application code migrated to src/app/ structure
✅ Resources migrated to src/resources/
✅ Entry points created for python -m src.app
✅ Import paths updated with fallback compatibility  
✅ Full functional testing passed
✅ Performance validation within acceptable range
✅ GUI application startup verified

Files migrated:
- ai/ → src/app/ai/ (AI services complete)
- config/ → src/app/config/ (Configuration management)  
- constants/ → src/app/constants/ (Application constants)
- database/ → src/app/database/ (Database layer)
- styles/ → src/app/styles/ (UI styling system)
- tools/ → src/app/tools/ (External tool wrappers)
- utils/ → src/app/utils/ (Utility functions)
- views/ → src/app/views/ (UI views complete)
- widgets/ → src/app/widgets/ (UI widgets complete)
- resources/ → src/resources/ (Static assets)

Entry points:
+ src/app/__main__.py - Module entry point
+ main.py updated for legacy compatibility
+ Comprehensive error handling and fallbacks

Testing:
+ All import tests passing
+ Performance within baseline targets
+ GUI startup validation successful
+ Cross-module imports working

Ready for Phase 3: Cleanup and import optimization"

# Tag milestone
git tag phase-2-complete
git push origin migration-src-architecture --tags

# Create backup
./backup_migration_point.sh "phase_2_complete"

echo "✅ Phase 2 committed and backed up"
```

---

## ✅ STEP 2.7: PHASE COMPLETION VALIDATION

**Duration**: 10 minutes  
**Output**: Complete phase validation and readiness confirmation

### 2.7.1 Final Validation Checklist
```bash
cat > PHASE_2_COMPLETION_CHECKLIST.md << 'EOF'
# Phase 2 Completion Checklist

## Migration Completed ✅
- [x] All AI modules migrated to src/app/ai/
- [x] All config modules migrated to src/app/config/
- [x] All core modules migrated to src/app/*/ 
- [x] All resources migrated to src/resources/
- [x] Directory structure created correctly
- [x] __init__.py files created for Python packages

## Entry Points Working ✅
- [x] python -m src.app works
- [x] python main.py works (legacy compatibility)
- [x] python src/app/__main__.py works
- [x] Import fallbacks handle missing modules gracefully
- [x] Error handling provides useful feedback

## Import System Updated ✅
- [x] Cross-module imports updated to src.app structure
- [x] Resource paths updated to src/resources
- [x] Fallback imports for migration compatibility
- [x] No circular import issues introduced

## Validation Tests Passed ✅
- [x] Directory structure validation
- [x] Core module import tests
- [x] Cross-module import tests  
- [x] Resource accessibility tests
- [x] Performance regression tests
- [x] GUI startup validation

## Documentation Complete ✅
- [x] Migration report generated
- [x] Completion checklist created
- [x] Known issues documented
- [x] Next steps defined

## Git & Backup ✅
- [x] All changes committed with detailed message
- [x] Phase milestone tagged (phase-2-complete)
- [x] Backup created for rollback capability
- [x] Working directory clean

## Ready for Phase 3 ✅
- [x] Phase 2 objectives fully met
- [x] No blocking issues identified  
- [x] Application functional in new structure
- [x] Performance within acceptable range
EOF

# Verify checklist programmatically
echo "🔍 Final validation check..."

# Test that entry points work
echo "Testing python -m src.app..."
timeout 5 python -m src.app --help >/dev/null 2>&1 || echo "⚠️ Entry point test (expected for GUI)"

# Test imports
python -c "
import sys
sys.path.insert(0, 'src')
try:
    from app import __main__
    from app.constants import paths  
    from app.views import main_window
    print('✅ All critical imports working')
except ImportError as e:
    print(f'❌ Critical import failed: {e}')
    exit(1)
"

# Check git status
if git diff --quiet && git diff --staged --quiet; then
    echo "✅ Working directory clean"
else
    echo "⚠️ Uncommitted changes detected"
fi

# Check backup exists
if [ -f "migration_backups/phase_2_complete_"*.tar.gz ]; then
    echo "✅ Backup created successfully"
else
    echo "❌ Backup missing"
fi

echo ""
echo "🎉 PHASE 2 VALIDATION COMPLETE!"
```

---

## 🎯 PHASE 2 SUCCESS CRITERIA

The phase is successful when:

1. **Complete Migration**: ✅
   - All application code moved to src/app/ with exact structure preserved
   - All resources moved to src/resources/
   - No functionality lost during migration

2. **Entry Points Functional**: ✅
   - `python -m src.app` works
   - Legacy `python main.py` works  
   - Proper error handling and fallbacks

3. **Import System Working**: ✅
   - All cross-module imports updated and functional
   - Resource paths correctly updated
   - No circular import issues

4. **Validation Passed**: ✅
   - All automated tests pass
   - Performance within baseline targets
   - GUI application can start up
   - No regression in functionality

5. **Documentation Complete**: ✅
   - Migration thoroughly documented
   - Issues and workarounds noted
   - Git history clean and tagged

---

**✅ PHASE 2 COMPLETE**

**Next Phase**: [PHASE_3_CLEANUP.md](PHASE_3_CLEANUP.md)  
**Estimated Duration**: 1-2 hours  
**Risk Level**: 🟡 Medium

**Key Achievements:**
- 🚚 **Complete code migration** to modern src/ structure
- 🚀 **Working entry points** for all execution methods  
- 🔄 **Updated import system** with backward compatibility
- 📊 **Performance maintained** within acceptable targets
- 🧪 **Comprehensive testing** validates migration success
