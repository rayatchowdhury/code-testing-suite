# Presentation Layer Migration Playbook

## Executive Summary

This playbook guides the migration of the PySide6 presentation layer from a mixed structure to a clean "Feature-local MVVM" architecture with centralized design system.

**Target:** Migrate `src/app/presentation` to feature-based MVVM pods while consolidating all styling in `design_system/`.

**Timeline:** 4 phases, each independently testable and revertible.

**Status:** Discovery complete. Ready for execution.

---

## Current State Analysis

### Files Discovered
- **Total files:** 296 (104 Python, 1 font, 191 other)
- **Legacy locations:**
  - `styles/`: 36 Python files
  - `window_controller/`: 3 Python files  
  - Scattered widget styles: 1 file

### Import Statistics
- **Total imports:** 392 (177 internal, 215 external)
- **Top dependencies:** PySide6.QtWidgets (32), PySide6.QtCore (27), PySide6.QtGui (18)
- **Circular imports:** None detected

### Widget Classification
- **Total widgets:** 48
- **Shared widgets:** 38 (editor, console, status_view, sidebar, layout)
- **Feature-local widgets:** 10 (results_widget, main window components)

---

## Target Structure

```
src/app/presentation/
├── base/                      # Base classes (WindowBase, ContentWindowBase, TestWindowBase)
├── navigation/                # Router, WindowManager, Factory
├── design_system/             # ALL STYLES HERE
│   ├── tokens/                # colors, spacing, status_colors
│   ├── styles/                # Python style generators
│   │   ├── components/        # per-component styles
│   │   └── ...
│   ├── assets/                # fonts, icons
│   └── qss/                   # optional QSS files
├── shared/                    # Shared widgets (≥2 features)
│   ├── components/
│   │   ├── editor/
│   │   ├── console/
│   │   ├── sidebar/
│   │   ├── status_view/       # Unified MVVM status view
│   │   └── layout/
│   └── dialogs/
├── windows/                   # Feature pods (MVVM triads)
│   ├── main/
│   │   ├── view.py
│   │   ├── viewmodel.py
│   │   ├── models.py
│   │   └── widgets/           # Feature-local widgets
│   ├── editor/
│   ├── results/
│   ├── help_center/
│   ├── comparator/            # Inherits TestWindowBase
│   ├── validator/
│   └── benchmarker/
└── services/                  # Error handling, export, adapters
```

---

## Migration Phases

### Phase 1: Design System Consolidation (P1) 
**Goal:** Move all styles to `design_system/styles/`

**Files to move:** 36 Python files from `styles/` → `design_system/styles/`

**Key moves:**
- `styles/style.py` → `design_system/styles/style.py`
- `styles/helpers/common_styles.py` → `design_system/styles/common_styles.py`
- `styles/helpers/inline_styles.py` → `design_system/styles/inline_styles.py`
- `styles/components/**` → `design_system/styles/components/**`
- `styles/syntaxhighlighter.py` → `design_system/styles/syntaxhighlighter.py`

**Import rewrites:**
```python
# Before
from src.app.presentation.styles.style import get_style
from src.app.presentation.styles.components.editor import EDITOR_STYLE

# After
from src.app.presentation.design_system.styles.style import get_style
from src.app.presentation.design_system.styles.components.editor import EDITOR_STYLE
```

**Risk:** Medium - Many files import styles  
**Mitigation:** Legacy aliases in `refactor/aliases/presentation/legacy_aliases.py`

**Validation:**
- [ ] All style imports resolve
- [ ] No missing style symbols
- [ ] Windows render correctly
- [ ] StatusView displays properly

**Rollback:** 
```powershell
git checkout src/app/presentation/styles/
git checkout src/app/presentation/design_system/styles/
```

---

### Phase 2: Navigation Unification (P2)
**Goal:** Move `window_controller/` to `navigation/`

**Files to move:** 3 files

**Key moves:**
- `window_controller/window_management.py` → `navigation/window_manager.py`
- `window_controller/base_window.py` → `_deprecated/base_window.py` (will remove later)
- Create `navigation/factory.py` with window registry

**Import rewrites:**
```python
# Before
from src.app.presentation.window_controller.window_management import WindowManager, WindowFactory

# After
from src.app.presentation.navigation.window_manager import WindowManager
from src.app.presentation.navigation.factory import WindowFactory
```

**Risk:** High - Central navigation component  
**Mitigation:** Thorough testing of window stack, navigation history, back button

**Validation:**
- [ ] All windows open correctly
- [ ] Navigation history works
- [ ] Back navigation functions
- [ ] Window stack managed properly
- [ ] No circular imports

**Rollback:**
```powershell
git checkout src/app/presentation/window_controller/
git checkout src/app/presentation/navigation/
```

---

### Phase 3: Feature Pods (P3)
**Goal:** Organize windows into MVVM feature pods

**Files to move:** 9 feature-local widgets

**Example moves:**
- `windows/results/widgets/results_widget.py` → stays (already in pod)
- Move any shared widget code out of feature directories
- Ensure feature-local widgets stay within feature boundary

**Import rules:**
```
windows/<feature>/ → {shared/, base/, design_system/, services/, navigation/}
windows/<feature>/ ✗ windows/<other_feature>/  (no sideways imports)
```

**Risk:** Low - Feature isolation  
**Mitigation:** Import linting, factory pattern for cross-feature dependencies

**Validation:**
- [ ] Each feature window works independently
- [ ] No sideways imports detected
- [ ] Shared components still accessible
- [ ] Test windows (comparator, validator, benchmarker) inherit TestWindowBase correctly

**Rollback:**
```powershell
git checkout src/app/presentation/windows/
```

---

### Phase 4: Cleanup (P4)
**Goal:** Remove legacy code and aliases

**Actions:**
- Remove `_deprecated/` folder
- Remove `styles/` folder (now empty)
- Remove `window_controller/` folder (now empty)
- Remove `refactor/aliases/presentation/legacy_aliases.py`
- Run codemods with strict mode (no fallbacks)

**Risk:** Low - All migrations complete  
**Mitigation:** Final smoke test suite

**Validation:**
- [ ] No import errors
- [ ] All tests pass
- [ ] App launches successfully
- [ ] All windows accessible
- [ ] No dead code remains

**Rollback:** Not needed (can restore from P3 state)

---

## Import Rules & Constraints

### Allowed Import Directions
```
windows/<feature>/ → {shared/, base/, design_system/, services/, navigation/}
shared/ → {base/, design_system/}
navigation/ → {base/, windows/ via factory}
services/ → {design_system/, base/, domain outside presentation}
design_system/ → {PySide6 only}
base/ → {PySide6 only}
```

### Forbidden Patterns
- ❌ `windows/<feature>/ → windows/<other_feature>/` (sideways)
- ❌ `base/ → windows/` (upward)
- ❌ `design_system/ → windows/` (upward)
- ❌ Circular imports at any level

### Circular Import Mitigation
- Use `navigation/factory.py` for window creation
- Inject dependencies via constructors
- Use protocols/interfaces for loose coupling

---

## Risk Matrix

| Phase | Risk Level | Impact | Mitigation |
|-------|-----------|--------|------------|
| P1 - Styles | Medium | High | Legacy aliases, incremental testing |
| P2 - Navigation | High | Critical | Backup, thorough nav testing |
| P3 - Feature Pods | Low | Medium | Import linting, isolated testing |
| P4 - Cleanup | Low | Low | Final smoke tests |

---

## Execution Commands

### Phase 1: Style Consolidation
```powershell
# Dry run
python scripts\win\00_dry_run.py --phase P1

# Apply moves
python scripts\win\01_apply_moves.py --phase P1

# Run codemods
python scripts\win\02_run_codemods.py --phase P1

# Build and smoke test
python scripts\win\03_build_and_smoke.py --phase P1
```

### Phase 2-4: Same pattern
Replace `--phase P1` with `P2`, `P3`, `P4`

### All phases at once (advanced)
```powershell
python scripts\win\01_apply_moves.py --phase all
python scripts\win\02_run_codemods.py --phase all
python scripts\win\03_build_and_smoke.py
```

---

## Validation Strategy

### Per-Window Smoke Tests
Each window should:
1. Open without errors
2. Display all UI elements correctly
3. Apply styles properly
4. Handle navigation (back button)
5. Close cleanly

### Windows to Test
- [ ] Main Window
- [ ] Editor Window
- [ ] Results Window
- [ ] Help Center Window
- [ ] Comparator Window (TestWindowBase)
- [ ] Validator Window (TestWindowBase)
- [ ] Benchmarker Window (TestWindowBase)

### StatusView Validation
- [ ] Displays in all test windows
- [ ] Updates on runner progress
- [ ] Shows correct test counts
- [ ] Applies correct status colors
- [ ] Renders cards properly

### Navigation Validation
- [ ] Window stack management
- [ ] Back button navigation
- [ ] History tracking
- [ ] Window creation via factory

---

## Troubleshooting

### Import Errors
**Symptom:** `ModuleNotFoundError` or `ImportError`

**Solution:**
1. Check `refactor/aliases/presentation/legacy_aliases.py` for missing alias
2. Run `python scripts\win\02_run_codemods.py` to reapply import rewrites
3. Verify `__init__.py` exports in target packages

### Style Not Applied
**Symptom:** UI elements render without styles

**Solution:**
1. Check import path in view/widget file
2. Verify style file moved to correct location in `design_system/`
3. Check `design_system/styles/__init__.py` exports

### Circular Import
**Symptom:** `ImportError: cannot import name '...' from partially initialized module`

**Solution:**
1. Move offending import inside function (late import)
2. Use factory pattern for window creation
3. Refactor to use protocols/interfaces

### Window Creation Fails
**Symptom:** Window doesn't open or crashes on open

**Solution:**
1. Check `navigation/factory.py` registry
2. Verify window class constructor signature
3. Check for missing dependencies in window's `__init__`

---

## Success Criteria

- ✅ All 104 Python files compile without errors
- ✅ All imports resolve correctly
- ✅ Zero circular imports
- ✅ All windows open and render correctly
- ✅ StatusView displays in test windows
- ✅ Navigation works (forward/back)
- ✅ All existing tests pass
- ✅ No performance degradation
- ✅ Code follows import rules

---

## Post-Migration Tasks

1. **Update Documentation**
   - Architecture docs
   - Developer onboarding
   - Code style guide

2. **Enable Import Linting**
   - Add import-linter config
   - Enforce import rules in CI

3. **Refactor Opportunities**
   - Extract common patterns
   - Reduce widget duplication
   - Improve MVVM separation

4. **Performance Review**
   - Profile window load times
   - Optimize style application
   - Review memory usage

---

## Timeline Estimate

- **Phase 1 (Styles):** 2-3 hours (high file count)
- **Phase 2 (Navigation):** 1-2 hours (careful testing)
- **Phase 3 (Feature Pods):** 1 hour (low complexity)
- **Phase 4 (Cleanup):** 30 minutes (simple removal)

**Total:** ~5-7 hours including testing

---

## Team Communication

### Before Starting
- [ ] Notify team of migration start
- [ ] Ensure no conflicting PRs in progress
- [ ] Create backup branch

### During Migration
- [ ] Push after each successful phase
- [ ] Update task tracking
- [ ] Document any deviations

### After Completion
- [ ] Demo new structure
- [ ] Share validation results
- [ ] Update team wiki

---

*Last Updated: 2025-10-21*  
*Generated by: Presentation Layer Migration Tool*
