# Presentation Layer Baseline Metrics
**Generated:** October 21, 2025  
**Branch:** refactor/presentation-incremental-extraction  
**Commit:** Initial baseline before MVVM refactoring

---

## File Statistics

- **Total Python files:** 100
- **Total lines of code:** 15,439
- **Directory structure:**
  - base/ (5 files)
  - views/ (35+ files across 7 window packages)
  - widgets/ (40+ files)
  - services/ (2 files)
  - window_controller/ (2 files)
  - styles/ (15+ files)

---

## Import Analysis

### Import Rule Violations: 0 ✅

**Checked Rules:**
- ✅ No windows/** → windows/** imports
- ✅ No widgets/** → windows/** imports

**Current State:** Clean baseline with zero cross-window dependencies

### Circular Dependencies: 0 ✅

No circular import cycles detected in presentation layer.

---

## Code Duplication Analysis

### Status View Duplication
- **Implementation 1:** `widgets/status_view/` (~1,130 lines)
- **Implementation 2:** `views/benchmarker/benchmarker_status_view.py` (170 lines)
- **Implementation 3:** `views/comparator/comparator_status_view.py` (160 lines)
- **Implementation 4:** `views/validator/validator_status_view.py` (155 lines)
- **Total duplication:** ~485 lines (43% of per-tool status views)

### Detailed Results Duplication
- **Implementation 1:** `views/results/detailed_results_window.py` (620 lines)
- **Implementation 2:** `widgets/detailed_results_window.py` (580 lines)
- **Estimated duplication:** ~400 lines (65%)

### Navigation Service Usage
- **Total call sites:** 19
- **Singleton pattern:** Yes (to be replaced with injectable router)
- **Files affected:**
  - benchmarker_window.py (1)
  - comparator_window.py (1)
  - validator_window.py (1)
  - code_editor_window.py (4)
  - results_window.py (2)
  - main_window.py (2)
  - base_window.py (1)
  - test_window_base.py (1)
  - content_window_base.py (1)
  - detailed_results_window.py (1)
  - navigation_service.py (4 self-references)

---

## Window Dependencies

### Current Import Graph

**window_management.py imports:**
- views.main_window.main_window
- views.code_editor.code_editor_window
- views.benchmarker.benchmarker_window
- views.comparator.comparator_window
- views.validator.validator_window
- views.help_center.help_center_window
- views.results.results_window

**Cross-window imports:** 44 total matches of `from src.app.presentation.views`

**Key findings:**
- window_management.py acts as central import hub (potential bottleneck)
- Lazy imports used to avoid circular dependencies
- No direct window→window imports (good!)

---

## Test Coverage (Pre-Refactoring)

**Current coverage:** ~70% (estimated)

**Areas with low coverage:**
- ViewModels: N/A (not yet extracted)
- Navigation router: N/A (still using singleton)
- Status view logic: ~60%
- Window lifecycle: ~75%

**Target coverage after refactoring:** 85%+

---

## Architectural Violations to Fix

### High Priority
1. **NavigationService singleton:** 19 call sites to replace
2. **Status view duplication:** 485 lines to consolidate
3. **Detailed results duplication:** 400 lines to merge
4. **Circular dependency risk:** window_management.py imports all windows

### Medium Priority
1. **MVVM separation:** Extract ViewModels from 7 windows
2. **Per-window packages:** Restructure from flat views/ to windows/<name>/
3. **Style organization:** Move constants to design_system/tokens.py
4. **Widget packaging:** Organize into logical packages

### Low Priority
1. **Documentation:** Update architecture docs
2. **Dead code removal:** Post-refactoring cleanup
3. **Test coverage:** Increase from 70% to 85%+

---

## Expected Impact

### Lines to Remove
- Status view consolidation: ~485 lines
- Detailed results merge: ~400 lines
- Dead code cleanup: ~300 lines
- Navigation service deletion: ~150 lines
- Refactoring overhead: ~800 lines
- **Total reduction:** ~2,135 lines

### Lines to Add
- ViewModels (7 windows): ~1,400 lines
- Navigation router: ~200 lines
- Status view presets: ~100 lines
- Test coverage: ~800 lines
- **Total addition:** ~2,500 lines

### Net Change
- **Files:** 100 → 109 (+9)
- **Lines:** 15,439 → 15,804 (+365)
- **Quality:** Improved maintainability, testability, and architectural clarity

---

## Validation Checklist

- [x] Import rules checker created
- [x] Baseline import violations: 0
- [x] Baseline circular dependencies: 0
- [x] File count documented: 100
- [x] Line count documented: 15,439
- [x] Duplication identified: ~885 lines
- [x] NavigationService usage mapped: 19 sites
- [ ] All tests passing (to be verified)

---

**Status:** ✅ Baseline metrics captured successfully

**Next Steps:**
1. Verify all tests pass with `pytest -v`
2. Commit Phase 1 changes
3. Begin Phase 2: Navigation Singleton Removal
