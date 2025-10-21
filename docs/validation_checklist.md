# Validation Checklist - Presentation Layer Migration

## Overview
This checklist ensures each migration phase maintains functional correctness.

---

## Pre-Migration Baseline

### Capture Current State
- [ ] Run all unit tests: `pytest tests/unit/`
- [ ] Run integration tests: `pytest tests/integration/`
- [ ] Run e2e tests: `pytest tests/e2e/`
- [ ] Launch app: `python -m src.app`
- [ ] Screenshot all windows in baseline state
- [ ] Document any existing issues

### Baseline Metrics
```powershell
# Capture test coverage
pytest --cov=src.app.presentation --cov-report=html

# Capture import violations
python scripts\check_import_rules.py

# Capture complexity
python scripts\analyze_complexity.py
```

---

## Phase 1: Design System Consolidation

### Import Resolution
- [ ] No `ModuleNotFoundError` in any Python file
- [ ] All style imports resolve correctly
- [ ] Legacy aliases working (temporary)

### Style Application
- [ ] Main window renders with correct styles
- [ ] Editor syntax highlighting works
- [ ] Console displays with proper colors
- [ ] Sidebar components styled correctly
- [ ] Splitters have correct handle styles
- [ ] Scrollbars display custom styles
- [ ] Buttons render correctly
- [ ] Input fields have proper styling
- [ ] Labels display with correct fonts/colors

### Window Rendering
- [ ] Main Window opens
- [ ] Editor Window opens
- [ ] Results Window opens
- [ ] Help Center opens
- [ ] Comparator Window opens
- [ ] Validator Window opens
- [ ] Benchmarker Window opens

### StatusView (Critical)
- [ ] StatusView displays in Comparator
- [ ] StatusView displays in Validator
- [ ] StatusView displays in Benchmarker
- [ ] Status cards render correctly
- [ ] Status colors match design tokens
- [ ] Progress updates display
- [ ] Test counts show accurately

### Design System Structure
- [ ] `design_system/tokens/colors.py` accessible
- [ ] `design_system/tokens/spacing.py` accessible
- [ ] `design_system/tokens/status_colors.py` accessible
- [ ] `design_system/styles/style.py` exports correctly
- [ ] `design_system/styles/common_styles.py` functions
- [ ] `design_system/styles/inline_styles.py` functions
- [ ] All component styles under `design_system/styles/components/`

### Tests
- [ ] Unit tests pass: `pytest tests/unit/presentation/`
- [ ] No new import errors
- [ ] Style-related tests pass

---

## Phase 2: Navigation Unification

### Import Resolution
- [ ] WindowManager imports correctly
- [ ] WindowFactory imports correctly (if created)
- [ ] NavigationRouter imports correctly
- [ ] No circular import errors

### Navigation Functions
- [ ] Open Main Window
- [ ] Navigate from Main → Editor
- [ ] Navigate from Main → Results
- [ ] Navigate from Main → Help Center
- [ ] Navigate from Main → Comparator
- [ ] Navigate from Main → Validator
- [ ] Navigate from Main → Benchmarker

### Back Navigation
- [ ] Back from Editor → Main
- [ ] Back from Results → Main
- [ ] Back from Help Center → Main
- [ ] Back from Comparator → Main
- [ ] Back from Validator → Main
- [ ] Back from Benchmarker → Main

### Window Stack Management
- [ ] Window stack maintains correct order
- [ ] Previous window restores on back
- [ ] Window state preserved during navigation
- [ ] Multiple back actions work correctly
- [ ] Forward navigation after back works

### Window Lifecycle
- [ ] Windows created via factory
- [ ] Windows destroyed properly on close
- [ ] Memory cleaned up (no leaks)
- [ ] Signals disconnected on close

### Edge Cases
- [ ] Navigate to already-open window
- [ ] Back when stack is empty
- [ ] Close window not on top of stack
- [ ] Navigate while action in progress

### Tests
- [ ] Navigation unit tests pass
- [ ] Window manager tests pass
- [ ] Integration tests pass

---

## Phase 3: Feature Pods

### Feature Isolation
- [ ] Each feature imports only from allowed packages
- [ ] No sideways imports between features
- [ ] Shared components remain accessible

### Comparator Feature
- [ ] Inherits from TestWindowBase
- [ ] Opens and displays correctly
- [ ] Sidebar renders
- [ ] Editor displays
- [ ] Console displays
- [ ] StatusView displays
- [ ] Run tests button works
- [ ] Results update correctly

### Validator Feature
- [ ] Inherits from TestWindowBase
- [ ] Opens and displays correctly
- [ ] Sidebar renders
- [ ] Editor displays
- [ ] Console displays
- [ ] StatusView displays
- [ ] Run validation works
- [ ] Results display correctly

### Benchmarker Feature
- [ ] Inherits from TestWindowBase
- [ ] Opens and displays correctly
- [ ] Sidebar renders
- [ ] Editor displays
- [ ] Console displays
- [ ] StatusView displays
- [ ] Run benchmarks works
- [ ] Performance metrics display

### Main Feature
- [ ] Opens and displays correctly
- [ ] Main content area renders
- [ ] Document widget works
- [ ] Navigation buttons functional

### Editor Feature
- [ ] Opens and displays correctly
- [ ] Code editor displays
- [ ] Syntax highlighting works
- [ ] Line numbers display
- [ ] Tab widget functions
- [ ] File operations work

### Results Feature
- [ ] Opens and displays correctly
- [ ] Results widget renders
- [ ] Test details display
- [ ] Export functions work

### Help Center Feature
- [ ] Opens and displays correctly
- [ ] Help content displays
- [ ] Document navigation works
- [ ] Search functions (if present)

### Shared Components Accessibility
- [ ] Editor components accessible from all features
- [ ] Console accessible from test features
- [ ] Sidebar accessible from test features
- [ ] StatusView accessible from test features
- [ ] Layout helpers accessible

### Import Rules Enforcement
```powershell
# Check for import violations
python scripts\check_import_rules.py --strict
```
- [ ] No import rule violations
- [ ] All imports follow allowed directions

### Tests
- [ ] All feature unit tests pass
- [ ] Integration tests pass
- [ ] No import errors

---

## Phase 4: Cleanup

### Legacy Code Removed
- [ ] `styles/` directory deleted
- [ ] `window_controller/` directory deleted
- [ ] `_deprecated/` directory deleted
- [ ] Legacy aliases removed

### Import Cleanup
- [ ] No references to old import paths
- [ ] All imports use new structure
- [ ] No unused imports

### Build & Test
- [ ] Full test suite passes
- [ ] No lint errors
- [ ] No dead code detected
- [ ] Type checking passes (if using mypy)

### Application Smoke Test
```powershell
python -m src.app
```
- [ ] App launches successfully
- [ ] Main window displays
- [ ] All menu items accessible
- [ ] All windows open correctly
- [ ] Navigation works end-to-end
- [ ] No console errors

---

## Cross-Phase Validation

### Functional Workflows

#### Comparator Workflow
1. [ ] Open Comparator window
2. [ ] Load or write test code
3. [ ] Set test count via slider
4. [ ] Click "Run Tests"
5. [ ] StatusView updates during execution
6. [ ] Results display in StatusView
7. [ ] Console shows output
8. [ ] Export results works

#### Validator Workflow
1. [ ] Open Validator window
2. [ ] Load or write validation code
3. [ ] Set test parameters
4. [ ] Click "Run Validation"
5. [ ] StatusView updates during execution
6. [ ] Results display correctly
7. [ ] Console shows validation output

#### Benchmarker Workflow
1. [ ] Open Benchmarker window
2. [ ] Load or write benchmark code
3. [ ] Configure benchmark parameters
4. [ ] Click "Run Benchmarks"
5. [ ] StatusView updates during execution
6. [ ] Performance metrics display
7. [ ] Console shows timing output

#### Editor Workflow
1. [ ] Open Editor window
2. [ ] Create new file
3. [ ] Write code with syntax highlighting
4. [ ] Save file
5. [ ] Load existing file
6. [ ] Edit and save changes
7. [ ] Close editor

### StatusView Signal/Slot Tests

#### Signals Emitted
- [ ] Runner started → StatusView updates to "Running"
- [ ] Test completed → StatusView updates counts
- [ ] All tests done → StatusView shows final state
- [ ] Error occurred → StatusView shows error

#### Slots Connected
- [ ] ViewModel receives runner signals
- [ ] View updates on ViewModel property changes
- [ ] Cards update on status change
- [ ] Colors apply based on test results

### Resource Path Validation
- [ ] Icons load correctly
- [ ] Fonts load correctly
- [ ] QSS files load (if present)
- [ ] No missing resource warnings

---

## Performance Validation

### Startup Time
```powershell
# Measure startup
Measure-Command { python -m src.app --no-gui }
```
- [ ] Startup time ≤ previous baseline
- [ ] No import time regressions

### Window Load Time
- [ ] Main window loads ≤ 500ms
- [ ] Editor window loads ≤ 500ms
- [ ] Test windows load ≤ 1s

### Memory Usage
```powershell
# Monitor memory during operation
```
- [ ] No memory leaks detected
- [ ] Memory usage ≤ previous baseline

---

## Regression Testing

### Run Full Test Suite
```powershell
pytest tests/ -v --cov=src.app.presentation
```
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All e2e tests pass
- [ ] Coverage ≥ previous baseline

### Manual Regression Tests
- [ ] All previously working features still work
- [ ] No new bugs introduced
- [ ] UI rendering unchanged
- [ ] Performance unchanged

---

## Final Sign-Off

### Code Quality
- [ ] No lint warnings
- [ ] No type errors
- [ ] No dead code
- [ ] Import rules enforced

### Documentation
- [ ] Architecture docs updated
- [ ] Developer guide updated
- [ ] Migration playbook complete
- [ ] Validation results documented

### Team Review
- [ ] Code review completed
- [ ] QA sign-off received
- [ ] Product owner approved

---

## Rollback Procedures

### If Phase 1 Fails
```powershell
git checkout src/app/presentation/styles/
git checkout src/app/presentation/design_system/styles/
git clean -fd src/app/presentation/
```

### If Phase 2 Fails
```powershell
git checkout src/app/presentation/window_controller/
git checkout src/app/presentation/navigation/
git clean -fd src/app/presentation/
```

### If Phase 3 Fails
```powershell
git checkout src/app/presentation/windows/
git clean -fd src/app/presentation/
```

### If Phase 4 Fails
```powershell
# Restore from Phase 3 completion
git reset --hard <phase3-commit-sha>
```

---

## Validation Results Template

```markdown
# Validation Results - Phase X

**Date:** YYYY-MM-DD
**Phase:** PX - <Phase Name>
**Validator:** <Name>

## Summary
- Total checks: X
- Passed: Y
- Failed: Z
- Warnings: W

## Issues Found
1. [Issue description]
   - Severity: High/Medium/Low
   - Fix: [Description]

## Recommendations
- [Recommendation 1]
- [Recommendation 2]

## Sign-Off
- [ ] Approved to proceed to next phase
- [ ] Requires fixes before proceeding
```

---

*Last Updated: 2025-10-21*  
*Generated by: Presentation Layer Migration Tool*
