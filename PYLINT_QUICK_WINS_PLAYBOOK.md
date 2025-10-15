# Pylint Quick Wins Playbook

**Current Score**: 5.49/10  
**Target Score**: 7.0+/10  
**Estimated Time**: ~60 minutes  
**Potential Fixes**: ~160 warnings

---

## Phase 1: Automated Fixes (5 minutes)

### 1.1 Fix Trailing Whitespace & Formatting
```bash
# Auto-fix trailing whitespace and formatting issues
black src/ --line-length=100

# Verify formatting
black src/ --check --line-length=100
```

**Impact**: ~15 warnings fixed  
**Files affected**: 
- `src/app/presentation/widgets/sidebar_widgets/limits_input_widget.py`
- `src/app/presentation/widgets/sidebar_widgets/test_count_slider.py`
- `src/app/presentation/window_controller/qt_doc_engine.py`

---

## Phase 2: Remove Unused Imports (15 minutes)

### 2.1 AI/Gemini Module
**File**: `src/app/core/ai/gemini_client/gemini_client.py`

Remove lines:
```python
from pathlib import Path  # Line 16
from typing import Any, Dict, List, Optional  # Line 17 - remove Any, Dict, List, Optional, keep Tuple
```

**Warnings fixed**: 5

---

### 2.2 Core Tools
**File**: `src/app/core/tools/compiler_runner.py`

Remove:
```python
import sys  # Line 3 (if unused at top level)
```

**File**: `src/app/core/tools/base/language_compilers.py`

Remove:
```python
from pathlib import Path  # Line 12
```

**File**: `src/app/core/tools/base/base_runner.py`

Remove:
```python
import os  # Line 11 (if unused)
```

**Warnings fixed**: 3

---

### 2.3 Config Module
**File**: `src/app/core/config/core/config_handler.py`

Remove:
```python
from typing import Any, Dict, Optional  # Line 5 - keep only used ones
```

Remove specific unused imports:
- `INFO_MESSAGE_STYLE` from line 18
- `SUCCESS_MESSAGE_STYLE` from line 18
- `MATERIAL_COLORS` from line 23
- `CONFIG_FILE` from line 24

**Warnings fixed**: 7

---

### 2.4 Persistence Module
**File**: `src/app/persistence/database/connection.py`

Remove:
```python
from pathlib import Path  # Line 17
```

**Warnings fixed**: 1

---

### 2.5 Presentation Widgets
**File**: `src/app/presentation/widgets/display_area_widgets/test_tab_widget.py`

Remove:
```python
from PySide6.QtCore import QPoint  # Line 11 (if unused)
from PySide6.QtWidgets import QSpacerItem  # Line 13 (if unused)
```

Remove:
```python
from src.app.presentation.styles.components.test_view_styles import TEST_VIEW_FILE_BUTTON_STYLE
```

**Warnings fixed**: 3

---

### 2.6 File Operations
**File**: `src/app/shared/utils/file_operations.py`

Remove:
```python
import stat  # Line 3
from typing import Dict  # Line 5
```

**File**: `src/app/shared/utils/workspace_utils.py`

Remove:
```python
import shutil  # Line 9
```

**Warnings fixed**: 3

---

### 2.7 Window Management
**File**: `src/app/presentation/window_controller/window_management.py`

Remove:
```python
from typing import Any  # Line 8
from PySide6.QtCore import Qt, QTimer  # Remove Qt and QTimer if unused
```

**Warnings fixed**: 3

---

### 2.8 Sidebar Widgets
**File**: `src/app/presentation/widgets/sidebar_widgets/limits_input_widget.py`

Remove:
```python
from PySide6.QtCore import Qt  # Line 9 (if unused)
from PySide6.QtWidgets import QLabel  # Line 11 (if unused)
```

**File**: `src/app/presentation/widgets/sidebar_widgets/test_count_slider.py`

Remove:
```python
from PySide6.QtWidgets import QLabel  # Line 11 (if unused)
from src.app.presentation.styles.components.test_view_styles import TEST_VIEW_SLIDER_VALUE_LABEL_STYLE
```

**Warnings fixed**: 4

---

### 2.9 Template Files
**File**: `src/resources/templates/generator.py`

Remove:
```python
import sys  # Line 2
```

**File**: `src/resources/templates/correct.py` & `src/resources/templates/test.py`

Remove unused variable `n` or use it:
```python
# Change from:
n = int(input())

# To (if truly unused):
_ = int(input())  # Number of elements (unused)
```

**Warnings fixed**: 5

---

**Total Phase 2 Impact**: ~34 warnings fixed

---

## Phase 3: Remove Unnecessary `pass` Statements (10 minutes)

### 3.1 Config Module
**File**: `src/app/core/config/core/exceptions.py`

```python
# Remove pass after docstring in exception classes
class ConfigError(Exception):
    """Base exception for configuration errors."""
    # Remove: pass
```

**File**: `src/app/core/config/logging_config.py`

Remove `pass` statements from lines 145, 151, 157 (in empty exception handlers that have comments).

**Warnings fixed**: 4

---

### 3.2 Language Compilers
**File**: `src/app/core/tools/base/language_compilers.py`

Remove all unnecessary `pass` statements (lines 41, 46, 68, 82, 101, 132):

```python
# Change from:
def get_compile_command(self, source_path: str, output_path: str) -> list:
    """Get compilation command for the language."""
    pass

# To:
def get_compile_command(self, source_path: str, output_path: str) -> list:
    """Get compilation command for the language."""
    raise NotImplementedError("Subclasses must implement get_compile_command")
```

**Warnings fixed**: 7

---

### 3.3 Persistence
**File**: `src/app/persistence/database/database_manager.py`

Remove `pass` on line 31.

**Warnings fixed**: 1

---

### 3.4 Config Views
**File**: `src/app/core/config/views/config_dialog.py`

Remove unnecessary `pass` statements (lines 689, 697, 751, 756, 761).

**Warnings fixed**: 5

---

### 3.5 Base Compiler
**File**: `src/app/core/tools/base/base_compiler.py`

Remove `pass` on line 460.

**Warnings fixed**: 1

---

### 3.6 Window Controllers
**File**: `src/app/presentation/window_controller/base_window.py`

Remove `pass` statements on lines 77, 142, 151, 278.

**Warnings fixed**: 4

---

**Total Phase 3 Impact**: ~22 warnings fixed

---

## Phase 4: Replace Bare `except:` with Specific Exceptions (10 minutes)

### 4.1 Editor AI
**File**: `src/app/core/ai/core/editor_ai.py`

Lines 221, 233, 250, 262:
```python
# Change from:
except:
    pass

# To:
except Exception:
    pass  # Safely ignore errors during cleanup
```

**Warnings fixed**: 4

---

### 4.2 Config Handler
**File**: `src/app/core/config/core/config_handler.py`

Lines 237, 248, 359:
```python
# Change from:
except:
    # fallback

# To:
except Exception:
    # fallback
```

**Warnings fixed**: 3

---

### 4.3 Compiler Runner
**File**: `src/app/core/tools/compiler_runner.py`

Line 294:
```python
# Change from:
except:
    pass

# To:
except Exception:
    pass  # Process cleanup - ignore errors
```

**Warnings fixed**: 1

---

### 4.4 Test Workers
**File**: `src/app/core/tools/specialized/benchmark_test_worker.py`

Line 319:
```python
# Change from:
try:
    if process.stdin:
        process.stdin.close()
except:
    pass

# To:
try:
    if process.stdin:
        process.stdin.close()
except (OSError, ValueError):
    pass  # Already closed or invalid file descriptor
```

**File**: `src/app/core/tools/specialized/comparison_test_worker.py`

Lines 288, 340:
```python
# Same fix as above for stdin.close()
except (OSError, ValueError):
    pass
```

**File**: `src/app/core/tools/specialized/validator_test_worker.py`

Line 299:
```python
# Same fix as above for stdin.close()
except (OSError, ValueError):
    pass
```

**Warnings fixed**: 4

---

**Total Phase 4 Impact**: ~12 warnings fixed

---

## Phase 5: Remove Unnecessary `else` After `return` (20 minutes)

### 5.1 Editor AI
**File**: `src/app/core/ai/core/editor_ai.py`

Line 57:
```python
# Change from:
if not self.gemini_ai:
    logger.error("GeminiAI not initialized")
    return None
else:
    try:
        # ... code

# To:
if not self.gemini_ai:
    logger.error("GeminiAI not initialized")
    return None

try:
    # ... code (de-indent)
```

Line 188:
```python
# Similar pattern - remove elif after return
```

**Warnings fixed**: 2

---

### 5.2 Gemini Client
**File**: `src/app/core/ai/gemini_client/gemini_client.py`

Lines 119, 176, 207:
```python
# Remove else/elif after return statements
```

**Warnings fixed**: 3

---

### 5.3 Language Compilers
**File**: `src/app/core/tools/base/language_compilers.py`

Lines 119, 207, 369:
```python
# Change from:
if condition:
    return value
else:
    return other_value

# To:
if condition:
    return value
return other_value
```

**Warnings fixed**: 3

---

### 5.4 Prompt Templates
**File**: `src/app/core/ai/templates/prompt_templates.py`

Line 319:
```python
# Remove else after return
```

**Warnings fixed**: 1

---

### 5.5 Various Files
Apply same pattern to:
- `src/app/core/tools/base/language_detector.py` (lines 287, 342)
- `src/app/core/tools/base/base_runner.py` (line 343)
- `src/app/shared/utils/file_operations.py` (line 47)
- `src/app/shared/constants/file_constants.py` (line 241)
- `src/app/shared/utils/workspace_utils.py` (lines 175, 209)
- `src/app/presentation/widgets/display_area_widgets/test_tab_widget.py` (lines 471, 550, 711, 797, 810, 951)
- `src/app/core/tools/specialized/benchmark_test_worker.py` (line 382)
- `src/app/presentation/views/comparator/comparator_window.py` (line 302)
- `src/app/persistence/database/connection.py` (line 152)

**Warnings fixed**: ~15

---

**Total Phase 5 Impact**: ~24 warnings fixed

---

## Phase 6: Fix f-string Without Interpolation (5 minutes)

### 6.1 Logging Config
**File**: `src/app/core/config/logging_config.py`

Line 185:
```python
# Change from:
migration_logger.info(f"Migration complete")

# To:
migration_logger.info("Migration complete")
```

**Warnings fixed**: 1

---

### 6.2 Compiler Runner
**File**: `src/app/core/tools/compiler_runner.py`

Lines 138, 145, 178:
```python
# Change from:
self.console.append_output(f"Compiling...")

# To:
self.console.append_output("Compiling...")
```

**Warnings fixed**: 3

---

### 6.3 Limits Input Widget
**File**: `src/app/presentation/widgets/sidebar_widgets/limits_input_widget.py`

Line 105:
```python
# Remove f-string if no variables used
```

**Warnings fixed**: 1

---

**Total Phase 6 Impact**: ~5 warnings fixed

---

## Phase 7: Fix Reimports and Redefine-Outer-Name (10 minutes)

### 7.1 Main Module
**File**: `src/app/__main__.py`

Line 60:
```python
# Change from:
import sys  # Already imported at top

# To:
# Remove this duplicate import, use the one from line 15
```

**Warnings fixed**: 2

---

### 7.2 Compiler Runner
**File**: `src/app/core/tools/compiler_runner.py`

Line 70:
```python
# Change from:
import os  # Already imported at line 2

# To:
# Remove duplicate import
```

**Warnings fixed**: 2

---

### 7.3 Gemini Handler
**File**: `src/app/core/config/gemini/gemini_handler.py`

Line 70:
```python
# Change from:
import json  # Already imported at line 11

# To:
# Remove duplicate import
```

**Warnings fixed**: 2

---

**Total Phase 7 Impact**: ~6 warnings fixed

---

## Verification Commands

After each phase, run:

```bash
# Check specific file
pylint src/app/core/ai/gemini_client/gemini_client.py --disable=C0114,C0115,C0116,R0903,R0913,W0613

# Check all files
pylint src/ --disable=C0114,C0115,C0116,R0903,R0913,W0613 --exit-zero

# Get just the score
pylint src/ --disable=C0114,C0115,C0116,R0903,R0913,W0613 --exit-zero | grep "rated at"
```

---

## Summary

| Phase | Task | Time | Warnings Fixed | Difficulty |
|-------|------|------|----------------|------------|
| 1 | Automated formatting | 5 min | ~15 | Very Easy |
| 2 | Remove unused imports | 15 min | ~34 | Easy |
| 3 | Remove unnecessary pass | 10 min | ~22 | Easy |
| 4 | Replace bare except | 10 min | ~12 | Medium |
| 5 | Remove else after return | 20 min | ~24 | Medium |
| 6 | Fix f-string issues | 5 min | ~5 | Easy |
| 7 | Fix reimports | 10 min | ~6 | Easy |
| **Total** | | **75 min** | **~118** | |

**Expected Final Score**: 7.0-7.5/10

---

## Additional Notes

### Low Priority Items (Can Skip)
- **Line too long (C0301)**: Already handled by Black with `--line-length=100`
- **Too many branches/statements (R0912/R0915)**: Requires refactoring, not quick wins
- **Import errors (E0401)**: False positives from pylint, ignore these
- **PySide6 import errors (E0611)**: False positives, ignore these
- **Duplicate code (R0801)**: Requires architectural changes, not quick wins

### Testing After Changes
```bash
# Run unit tests
pytest tests/unit/ -v

# Run integration tests (if time permits)
pytest tests/integration/ -v -k "not slow"

# Verify Black compliance
black src/ --check --line-length=100

# Verify isort compliance  
isort src/ --check-only
```

---

## Git Workflow

```bash
# Create feature branch
git checkout -b refactor/pylint-quick-wins

# Commit after each phase
git add .
git commit -m "refactor: Phase 1 - Auto-format with Black"
git commit -m "refactor: Phase 2 - Remove unused imports"
git commit -m "refactor: Phase 3 - Remove unnecessary pass statements"
# ... etc

# Push when done
git push origin refactor/pylint-quick-wins
```

---

**Last Updated**: October 14, 2025  
**Pylint Version**: Latest  
**Python Version**: 3.12+
