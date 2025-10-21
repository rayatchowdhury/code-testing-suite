# Phase 8: Critical Cleanup & Consolidation

**Date Started:** 2025-10-21  
**Branch:** `refactor/presentation-incremental-extraction`  
**Status:** 🔴 In Progress

## Overview

This phase removes inconsistencies and legacy code left from previous migrations:
- Duplicate navigation systems (NavigationService vs NavigationRouter)
- Inconsistent base classes (SidebarWindowBase vs ContentWindowBase)
- Duplicate status view implementations
- Duplicate detail dialog systems
- Legacy window_controller patterns

## Critical Issues Identified

### 1. NavigationService Still Active (24+ references)
- **Problem:** Both `NavigationService` (singleton) and `NavigationRouter` (injectable) coexist
- **Impact:** Confusing navigation, potential bugs
- **Solution:** Replace all NavigationService with injected NavigationRouter

### 2. Base Class Drift
- **Problem:** Some windows use `SidebarWindowBase`, others use `ContentWindowBase`
- **Files:** `windows/editor/view.py`, `windows/help_center/view.py`
- **Solution:** Standardize on `ContentWindowBase` for all content windows

### 3. Legacy Status View Base
- **Problem:** `base/status_view_base.py` still exists alongside unified `widgets/status_view/*`
- **Solution:** Delete legacy base, ensure all imports use widget version

### 4. Duplicate Detail Dialogs
- **Problem:** `widgets/test_detail_view.py` AND `dialogs/result_detail/view.py`
- **Solution:** Keep dialogs package, remove widget version

### 5. Dual Navigation Layers
- **Problem:** `navigation/router.py` + `window_controller/window_management.py`
- **Solution:** Keep Router, phase out window_controller

## Implementation Plan

### Task 8.1: Kill NavigationService ✅ DONE
**Objective:** Remove all NavigationService singleton usage

**Steps:**
1. ✅ Find all NavigationService references
2. ✅ Replace with NavigationRouter (constructor injection)
3. ✅ Delete `services/navigation_service.py`
4. ✅ Run import checker: zero violations

**Affected Files:**
- All window classes that call `NavigationService.instance().navigate_to()`
- Main window initialization

**Verification:**
```bash
rg "NavigationService" src/app/presentation/
# Should return: 0 matches
```

### Task 8.2: Normalize Base Classes 🔄 IN PROGRESS
**Objective:** Consistent inheritance across all windows

**Standards:**
- `MainWindow` → `QMainWindow` (top-level app window)
- Test windows (Benchmarker, Validator, Comparator) → `TestWindowBase`
- Content windows (Editor, Results, HelpCenter) → `ContentWindowBase`

**Steps:**
1. 🔄 Fix `windows/editor/view.py`: Change from `SidebarWindowBase` to `ContentWindowBase`
2. ⏸️ Fix `windows/help_center/view.py`: Change from `SidebarWindowBase` to `ContentWindowBase`
3. ⏸️ Fix `windows/results/view.py`: Verify uses `ContentWindowBase`
4. ⏸️ Run tests: All windows open correctly

**Files to Update:**
- `src/app/presentation/windows/editor/view.py`
- `src/app/presentation/windows/help_center/view.py`
- `src/app/presentation/windows/results/view.py`

### Task 8.3: Remove Legacy Status Base ⏸️ PENDING
**Objective:** Delete duplicate status view base class

**Steps:**
1. Verify no imports of `base/status_view_base.py`
2. Delete `src/app/presentation/base/status_view_base.py`
3. Ensure all status views import from `widgets/status_view/*`

**Verification:**
```bash
rg "from.*base.*status_view_base" src/app/presentation/
rg "StatusViewBase" src/app/presentation/
```

### Task 8.4: Consolidate Detail Dialogs ⏸️ PENDING
**Objective:** Single detail dialog system

**Current State:**
- `widgets/test_detail_view.py`: Old test-specific wrappers
- `dialogs/result_detail/view.py`: New unified dialog with MVVM

**Steps:**
1. Find all uses of `widgets/test_detail_view.py` classes
2. Replace with `dialogs/result_detail/view.py`
3. Delete `widgets/test_detail_view.py`

**Affected:**
- Status view implementations showing detail dialogs
- Any test result detail views

### Task 8.5: Retire window_controller ⏸️ PENDING
**Objective:** Single navigation responsibility

**Current State:**
- `window_controller/window_management.py`: WindowManager + WindowFactory
- `navigation/router.py`: NavigationRouter (newer, injectable)

**Decision:** Keep both temporarily
- WindowManager: Window lifecycle (create, cache, show)
- NavigationRouter: Navigation history + routing logic
- Router USES WindowManager for display

**Steps:**
1. Verify NavigationRouter properly uses WindowManager
2. Document the separation of concerns
3. Consider future: merge or keep separate?

**Action:** Document pattern, defer deletion

### Task 8.6: Prune Empty Directories ⏸️ PENDING
**Objective:** Remove empty/unused directories

**Candidates:**
- `design_system/qss/` (if empty)
- `widgets/display_area_widgets/` (already deleted)
- `widgets/sidebar_widgets/` (already deleted)
- `views/` (already deleted)

**Steps:**
1. Check each directory for files
2. Delete if empty or unused
3. Update import paths if needed

## Success Criteria

### Phase 8 Complete When:
- ✅ Zero NavigationService references
- ✅ All content windows use ContentWindowBase
- ✅ No legacy status_view_base imports
- ✅ Single detail dialog system
- ✅ Clean import graph (zero violations)
- ✅ All tests pass
- ✅ Navigation works end-to-end

## Rollback Plan

If issues arise:
```bash
git reset --hard HEAD
git checkout main
git branch -D refactor/presentation-incremental-extraction
```

## Notes

### Key Learnings
- Phase 7 left significant technical debt
- Need better migration completion checklist
- Import checker is essential but not sufficient

### Follow-Up Questions
- Should WindowManager and NavigationRouter merge?
- Is ContentWindowBase too generic? Need SidebarContentWindow?
- Status view pattern: Keep separate or merge with base?

## Commit Strategy

Each task gets its own commit:
- `refactor(nav): remove NavigationService singleton`
- `refactor(base): normalize window base classes`
- `refactor(status): remove legacy status_view_base`
- `refactor(dialogs): consolidate detail dialog system`
- `docs(cleanup): update architecture after Phase 8`

## Timeline

- **Started:** 2025-10-21 (Phase 8.1)
- **Target Completion:** 2025-10-21 (same day)
- **Actual Completion:** TBD
