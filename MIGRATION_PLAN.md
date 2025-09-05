# Migration Plan (v3) - Detailed & Atomic

This document outlines a highly detailed, atomic migration path to safely transition the repository. Each step is a minimal, reversible change that can be tested independently.

## Pre-Migration: Bloat Analysis & Optimization

**Current Binary Size Issues Identified:**
1. **QtWebEngine bloat** - Used only for HTML rendering in main window and help center
2. **Duplicate AI validators** - Same code in `utils/` and `ai/validation/`
3. **Heavy PySide6-AddOns** - May not be fully utilized
4. **Complex styling system** - 17+ component style files with deep dependencies

**Optimization Recommendations:**
- Replace QtWebEngine with QTextBrowser for static HTML content
- Consolidate duplicate validation code
- Audit PySide6-AddOns usage
- Preserve current styling system during migration

---

## Phase 1: Preparation & Safety (Steps 0-2)

### Step 0.1 — Create Backup & Testing Infrastructure

**Scope:** Setup safety nets before any changes
**Duration:** 1-2 hours
**Files Created:**
- `backup_current_state.py` - Script to backup current working state
- `test_basic_functionality.py` - Smoke tests for all windows
- `check_imports.py` - Script to validate all imports work

**Actions:**
```bash
# Create backup script
python backup_current_state.py

# Test current functionality
python test_basic_functionality.py
```

**Risks:** None - only adds safety infrastructure
**Rollback:** Delete new files

**PR Checklist:**
- [ ] Backup script successfully creates archive
- [ ] Smoke tests pass on current codebase
- [ ] All windows open without errors

### Step 0.2 — Initialize pyproject.toml (Minimal)

**Scope:** Add pyproject.toml alongside requirements.txt (don't replace yet)
**Duration:** 30 minutes
**Files Created/Modified:**
- `pyproject.toml` - Basic project definition
- `.gitignore` - Add `dist/`, `*.egg-info/`, `__pycache__/`

**pyproject.toml content:**
```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "code-testing-suite"
version = "0.1.0"
dependencies = [
    "PySide6>=6.5.0",
    "qasync>=0.23.0",
    "pygments>=2.15.0",
]

[project.optional-dependencies]
ai = [
    "google-generativeai>=0.3.0",
    "aiohttp>=3.8.0",
]
dev = [
    "pytest>=7.0.0",
    "pytest-qt>=4.2.0",
]
```

**Risks:** None - only adds files
**Rollback:** Delete pyproject.toml and revert .gitignore

**PR Checklist:**
- [ ] `pip install -e .` works
- [ ] Application still runs with `python main.py`
- [ ] No dependency conflicts

### Step 0.3 — Create src/ Structure (Empty)

**Scope:** Create directory structure without moving files
**Duration:** 15 minutes
**Files Created:**
```
src/
└── app/
    ├── __init__.py
    ├── core/
    │   └── __init__.py
    ├── persistence/
    │   └── __init__.py  
    ├── presentation/
    │   └── __init__.py
    └── shared/
        └── __init__.py
```

**Actions:**
- Create directories with empty `__init__.py` files
- Add `src/` to Python path temporarily for testing

**Risks:** None - only directory creation
**Rollback:** Delete src/ directory

---

## Phase 2: Incremental Code Movement (Steps 1-3)

### Step 1.1 — Move main.py Only

**Scope:** Move only the entry point, test thoroughly
**Duration:** 1 hour
**Files Moved:**
- `main.py` -> `src/app/__main__.py`
- Update imports in `__main__.py` to use absolute imports

**New __main__.py content:**
```python
import sys
import os
# Add current directory to path for import compatibility
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Set Qt API before any Qt imports
os.environ['QT_API'] = 'pyside6'

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import qasync
import asyncio
from constants import APP_ICON

# ... rest unchanged
```

**Testing:**
- `python src/app/__main__.py` works
- `python -m app` works (from project root)
- All functionality intact

**Risks:** Low - only entry point changes
**Rollback:** Move `__main__.py` back to `main.py`

### Step 1.2 — Move constants/ (Safest First)

**Scope:** Move constants package - has minimal dependencies
**Duration:** 45 minutes
**Files Moved:**
- `constants/` -> `src/app/shared/constants/`
- Update `paths.py` to use new PROJECT_ROOT
- Create compatibility import in old location

**Compatibility Shim (`constants/__init__.py`):**
```python
# Backward compatibility shim
import sys
import warnings
from app.shared.constants import *

warnings.warn(
    "Importing from 'constants' is deprecated. Use 'app.shared.constants' instead.",
    DeprecationWarning,
    stacklevel=2
)
```

**Files Updated:**
- `src/app/__main__.py` - Update import to `from app.shared.constants import APP_ICON`
- All other files keep old imports for now

**Testing:** 
- Application starts normally
- All icons load correctly
- Path resolution works

**Risks:** Low - constants are leaf dependencies
**Rollback:** Move back to `constants/`, remove shim

### Step 1.3 — Move utils/ (Second Safest)

**Scope:** Move utils package with deduplication
**Duration:** 2 hours
**Files Moved:**
- `utils/` -> `src/app/shared/utils/`
- **Deduplication:** Remove duplicate `api_validator.py` (keep the one in `ai/validation/`)
- Create compatibility shim

**Actions:**
1. Compare `utils/api_validator.py` vs `ai/validation/api_validator.py`
2. Keep the more comprehensive version in `ai/validation/`
3. Create import alias in `utils/` location

**Compatibility Shim (`utils/__init__.py`):**
```python
# Backward compatibility - redirect to new locations
import warnings
from app.shared.utils.file_operations import *
from app.shared.utils.window_factory import *
from app.shared.utils.window_manager import *
from app.shared.utils.logging_config import *
# Redirect api_validator to ai package
from app.core.ai.validation.api_validator import *

warnings.warn("Use app.shared.utils or app.core.ai.validation", DeprecationWarning)
```

**Testing:**
- All file operations work
- Window management intact
- Logging configuration active

**Risks:** Medium - utils are widely used
**Rollback:** Move back, restore duplicate file

---

## Phase 3: Layer Organization (Steps 2-4)

### Step 2.1 — Move database/ to persistence/

**Scope:** Move database package to persistence layer
**Duration:** 45 minutes
**Files Moved:**
- `database/` -> `src/app/persistence/`
- Add `file_store.py` for non-database file operations

**New file_store.py:**
```python
"""File storage operations separate from database."""
import os
import json
from pathlib import Path
from app.shared.constants.paths import USER_DATA_DIR

class FileStore:
    """Handles file-based storage operations."""
    
    @staticmethod
    def ensure_user_dir():
        """Ensure user data directory exists."""
        Path(USER_DATA_DIR).mkdir(parents=True, exist_ok=True)
    
    # ... other file operations
```

**Compatibility Shim:**
```python
# database/__init__.py
from app.persistence import *
import warnings
warnings.warn("Use app.persistence", DeprecationWarning)
```

**Testing:**
- Database connections work
- Results saving/loading intact
- File operations function

### Step 2.2 — Move styles/ to presentation/styles/ (CRITICAL)

**Scope:** Move styling system while preserving ALL current appearance
**Duration:** 3-4 hours (most critical step)
**Files Moved:**
- `styles/` -> `src/app/presentation/styles/`
- Preserve exact import structure
- Create comprehensive compatibility layer

**Detailed Actions:**

1. **Preserve Import Structure:**
```python
# src/app/presentation/styles/__init__.py
# Exact copy of current styles/__init__.py structure
from .constants import COLORS, MATERIAL_COLORS
from .components import *
# ... keep everything identical
```

2. **Maintain Component Imports:**
```python
# src/app/presentation/styles/components/__init__.py  
# Keep exact same exports as current system
from .scrollbar import SCROLLBAR_STYLE
from .sidebar import SIDEBAR_STYLE, SIDEBAR_BUTTON_STYLE
# ... all existing imports preserved
```

3. **Create Comprehensive Compatibility Shim:**
```python
# styles/__init__.py (compatibility)
"""
CRITICAL: This compatibility layer preserves exact styling behavior
Do not modify until all imports are updated
"""
import sys
from app.presentation.styles import *
from app.presentation.styles.constants import *
from app.presentation.styles.components import *

# Re-export everything to maintain compatibility
__all__ = [
    # ... exact copy of all current __all__ exports
]
```

**Testing Protocol (MANDATORY):**
- [ ] Take screenshots of all windows before changes
- [ ] After migration, compare pixel-perfect with before screenshots  
- [ ] Test all themes/color schemes
- [ ] Verify all syntax highlighting works
- [ ] Check all custom widgets (sliders, buttons, etc.)
- [ ] Validate scrollbars, splitters, console colors
- [ ] Test all dialog styles
- [ ] Verify AI panel styling
- [ ] Check results table formatting

**Risks:** HIGH - Styling affects entire application appearance
**Rollback Strategy:** Keep exact backup of styles/ until Phase 4 complete

### Step 2.3 — Move views/ and widgets/ to presentation/

**Scope:** Move UI components to presentation layer
**Duration:** 2 hours
**Files Moved:**
- `views/` -> `src/app/presentation/views/`
- `widgets/` -> `src/app/presentation/widgets/`

**Compatibility Shims:**
```python
# views/__init__.py
from app.presentation.views import *

# widgets/__init__.py  
from app.presentation.widgets import *
```

**Testing:**
- All windows open correctly
- Widget functionality intact
- Event handling works

---

## Phase 4: Architecture Refactoring (Steps 3-5)

### Step 3.1 — Move ai/ to core/ai/

**Scope:** Move AI package to core layer
**Duration:** 1.5 hours
**Files Moved:**
- `ai/` -> `src/app/core/ai/`
- Keep internal structure identical initially

**Testing:**
- AI features work
- API validation functions
- Configuration loading works

### Step 3.2 — Move tools/ to core/tools/

**Scope:** Move tools to core layer  
**Duration:** 1 hour
**Files Moved:**
- `tools/` -> `src/app/core/tools/`

**Testing:**
- Compilation works
- Stress testing runs  
- TLE testing functions

### Step 3.3 — Move config/ Logic to core/, UI to presentation/

**Scope:** Separate config logic from UI
**Duration:** 2 hours
**Files Moved:**
- `config/management/` -> `src/app/core/config/`
- `config/validation/` -> `src/app/core/config/`  
- `config/ui/` -> `src/app/presentation/features/config/`
- `config/config_exceptions.py` -> `src/app/shared/exceptions.py`

**Testing:**
- Configuration dialog opens
- Settings save/load correctly
- Validation works

---

## Phase 5: Feature Organization (Steps 4-6)

### Step 4.1 — Create presentation/features/ Structure

**Scope:** Create feature directories without moving files yet
**Duration:** 30 minutes
**Directories Created:**
```
src/app/presentation/features/
├── code_editor/
├── stress_tester/
├── tle_tester/ 
├── results/
├── help_center/
└── config/
```

### Step 4.2 — Move Code Editor Feature

**Scope:** Move all code editor related files to one feature directory
**Duration:** 1.5 hours
**Files Moved:**
- `src/app/presentation/views/code_editor/` -> `src/app/presentation/features/code_editor/views/`
- Related widgets from `presentation/widgets/display_area_widgets/editor.py` -> `features/code_editor/widgets/`
- Editor-specific styles remain in main styles (for now)

**Testing:**
- Code editor opens
- Syntax highlighting works
- File operations function
- AI panel integration works

### Step 4.3 — Move Stress Tester Feature  

**Similar process for stress tester components**

### Step 4.4 — Move TLE Tester Feature

**Similar process for TLE tester components**  

### Step 4.5 — Move Results Feature

**Similar process for results components**

### Step 4.6 — Create shared_widgets/

**Scope:** Identify truly shared widgets and move them
**Duration:** 2 hours
**Analysis Required:**
- `sidebar.py` - Used by all windows (shared)
- `display_area.py` - Used by multiple features (shared)  
- `console.py` - Used by editor and testers (shared)
- `dialogs/` - Used across features (shared)

**Files Moved:**
- Core shared widgets to `src/app/presentation/shared_widgets/`
- Feature-specific widgets stay in their feature directories

---

## Phase 6: Cleanup & Testing (Steps 5-7)

### Step 5.1 — Remove Compatibility Shims (Gradual)

**Scope:** Remove backward compatibility layer once all imports updated
**Duration:** 1 hour per major component
**Process:**
1. Update all imports to use new paths
2. Remove one compatibility shim at a time  
3. Test after each removal

### Step 5.2 — Optimize Dependencies

**Scope:** Remove bloat and optimize imports
**Duration:** 2-3 hours
**Actions:**
1. **Replace QtWebEngine with QTextBrowser:**
   - Update `views/main_window.py`
   - Update `views/help_center/help_center_window.py`
   - Remove QtWebEngine imports and styles
2. **Audit PySide6-AddOns usage:**
   - Check if all AddOns components are needed
   - Remove unused imports
3. **Optimize Requirements:**
   - Mark AI dependencies as optional
   - Use lighter alternatives where possible

### Step 6.1 — Add Basic Tests

**Scope:** Add smoke tests for refactored code
**Duration:** 2 hours
**Files Created:**
- `tests/unit/core/test_ai_service.py`
- `tests/unit/persistence/test_database.py`  
- `tests/integration/test_window_creation.py`

### Step 7.1 — Final Validation & Documentation

**Scope:** Comprehensive testing and documentation update
**Duration:** 2-3 hours
**Actions:**
- Run full application test suite
- Update documentation
- Create architecture decision record (ADR)
- Update README with new structure

---

## Risk Mitigation & Rollback Strategy

### Before Each Step:
1. **Create checkpoint:** `git tag checkpoint-stepX.Y`  
2. **Run smoke tests:** Ensure current functionality works
3. **Take screenshots:** For UI-related changes
4. **Time-box changes:** Don't exceed estimated duration

### Rollback Process:
1. **Immediate rollback:** `git reset --hard checkpoint-stepX.Y`
2. **Partial rollback:** Revert specific commits
3. **Recovery:** Use backup script to restore known-good state

### High-Risk Steps (Extra Caution):
- **Step 2.2 (styles):** Most critical - affects entire UI appearance
- **Step 1.2-1.3 (utils/constants):** Widely imported modules  
- **Step 4.1-4.6 (feature reorganization):** Complex import changes

### Success Criteria for Each Phase:
- **Phase 1:** Application starts and runs identically to before
- **Phase 2:** All UI components look and function exactly the same
- **Phase 3:** All features work with new core organization
- **Phase 4:** Feature-based organization complete
- **Phase 5:** Codebase is clean and well-organized
- **Phase 6:** Tests pass, documentation updated

# Recommendations

### How to Handle Blocking IO in UI Code

The project already uses `qasync`, which is excellent. To build on this:

-   **Always Offload I/O:** Ensure every operation that can block is performed off the main UI thread. This includes:
    -   **File I/O:** Use `aiofiles` for async file operations or run synchronous file I/O in a `QThreadPool`.
    -   **Network Requests:** All AI API calls must be `async` and `await`-ed.
    -   **Subprocesses:** Use `asyncio.create_subprocess_exec` or `asyncio.create_subprocess_shell` to run compilers and other external tools without blocking the event loop.
-   **Encapsulate in Services:** The `core` service layer is the perfect place to manage this. A view should make a single `async` call to a service method (e.g., `await stress_test_service.run()`). The service is then responsible for managing the background tasks and reporting progress back to the UI.

### How to Separate Services from Views

The migration to a `core` service layer is the key. The relationship should be:

1.  **One-Way Dependency:** The `presentation` layer (views, widgets) depends on the `core` layer (services), but the `core` layer **must not** depend on the `presentation` layer. It should have no `import PySide6` statements.
2.  **Dependency Injection:** Create service instances in your main application entry point (`src/app/main.py`). Pass these instances to the windows and widgets that need them through their constructors.

    ```python
    # In main.py
    ai_service = AIService()
    main_window = MainWindow(ai_service=ai_service)
    ```

3.  **Communication from Service to View:** When a service needs to notify the UI of progress or completion, use Qt's signal/slot mechanism. A service can inherit from `QObject` and define its own signals.

    ```python
    # In ai_service.py
    class AIService(QObject):
        analysis_complete = Signal(dict)

        async def analyze(self, code):
            # ... perform analysis ...
            result = await self._call_api(code)
            self.analysis_complete.emit(result)

    # In a view
    self.ai_service.analysis_complete.connect(self.display_analysis)
    ```

### How to Add Tests Incrementally

With the new structure, testing becomes much easier.

1.  **Start with the Core and Persistence Layers:** These layers have no UI dependencies and can be tested like any standard Python code using `pytest`. Use `unittest.mock` to patch external dependencies like network calls or the database.
2.  **Test Shared Utilities:** Write unit tests for all functions in the `shared` package. They should be small and self-contained.
3.  **Write Integration Tests:** Create tests in `tests/integration/` that verify the interaction between your components. For example, does the `StressTestService` correctly use the `CompilerRunner` from `tool_runners`?
4.  **Introduce UI Testing:** Use `pytest-qt` to test the `presentation` layer. You can simulate button clicks and other user interactions and assert that the UI updates correctly. Start with a simple "smoke test" that ensures each window can be opened without crashing.
5.  **Automate with CI:** Integrate `pytest` into a CI/CD pipeline (e.g., GitHub Actions) to run all tests automatically on every pull request. This is the best way to prevent regressions.
