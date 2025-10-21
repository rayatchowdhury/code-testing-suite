# Migration Execution Tracker

## Pre-Migration Setup

- [ ] Read `docs/MIGRATION_SUMMARY.md`
- [ ] Read `refactor/README.md`
- [ ] Skim `docs/migration_playbook.md`
- [ ] Install dependencies: `pip install libcst`
- [ ] Create git branch: `git checkout -b presentation-migration`
- [ ] Commit current state: `git commit -am "Pre-migration snapshot"`
- [ ] Notify team of migration start
- [ ] Ensure no conflicting PRs

---

## Phase 1: Design System Consolidation

### Execution
- [ ] **Dry run:** `python scripts\win\00_dry_run.py --phase P1`
  - Review output, confirm 36 moves planned
- [ ] **Apply moves:** `python scripts\win\01_apply_moves.py --phase P1`
  - Verify: 36 files moved to `design_system/styles/`
- [ ] **Run codemods:** `python scripts\win\02_run_codemods.py --phase P1`
  - Verify: Import paths rewritten
- [ ] **Test:** `python scripts\win\03_build_and_smoke.py --phase P1`
  - Verify: All imports resolve, app launches

### Validation (from validation_checklist.md)
- [ ] All style imports resolve
- [ ] Main window renders with styles
- [ ] Editor syntax highlighting works
- [ ] Console displays with colors
- [ ] Sidebar styled correctly
- [ ] StatusView displays in test windows
- [ ] All 7 windows open successfully

### Sign-off
- [ ] All validation checks pass
- [ ] Commit: `git commit -am "Phase 1 complete: Style consolidation"`
- [ ] Push: `git push origin presentation-migration`

**Notes:**
```
[Add any issues encountered or deviations from plan]
```

---

## Phase 2: Navigation Unification

### Execution
- [ ] **Dry run:** `python scripts\win\00_dry_run.py --phase P2`
  - Review output, confirm 3 moves planned
- [ ] **Apply moves:** `python scripts\win\01_apply_moves.py --phase P2`
  - Verify: `window_controller/` → `navigation/`
- [ ] **Run codemods:** `python scripts\win\02_run_codemods.py --phase P2`
  - Verify: WindowManager imports updated
- [ ] **Test:** `python scripts\win\03_build_and_smoke.py --phase P2`
  - Verify: Navigation works, no circular imports

### Validation
- [ ] WindowManager imports correctly
- [ ] All windows open via navigation
- [ ] Back button works (all windows)
- [ ] Window stack managed correctly
- [ ] Navigation history functions
- [ ] No circular imports detected

### Navigation Tests (Critical)
- [ ] Main → Editor → Back
- [ ] Main → Results → Back
- [ ] Main → Help Center → Back
- [ ] Main → Comparator → Back
- [ ] Main → Validator → Back
- [ ] Main → Benchmarker → Back

### Sign-off
- [ ] All validation checks pass
- [ ] Commit: `git commit -am "Phase 2 complete: Navigation unification"`
- [ ] Push: `git push origin presentation-migration`

**Notes:**
```
[Add any issues encountered or deviations from plan]
```

---

## Phase 3: Feature Pods

### Execution
- [ ] **Dry run:** `python scripts\win\00_dry_run.py --phase P3`
  - Review output, confirm 9 moves planned
- [ ] **Apply moves:** `python scripts\win\01_apply_moves.py --phase P3`
  - Verify: Feature-local widgets moved to pods
- [ ] **Run codemods:** `python scripts\win\02_run_codemods.py --phase P3`
  - Verify: Widget imports updated
- [ ] **Test:** `python scripts\win\03_build_and_smoke.py --phase P3`
  - Verify: Features isolated, no sideways imports

### Validation
- [ ] No sideways imports between features
- [ ] Shared widgets still accessible
- [ ] Each feature window works independently

### Feature Tests
- [ ] **Comparator:** Opens, runs tests, displays results
- [ ] **Validator:** Opens, runs validation, displays results
- [ ] **Benchmarker:** Opens, runs benchmarks, displays results
- [ ] **Main:** Opens, navigation works
- [ ] **Editor:** Opens, code editing works
- [ ] **Results:** Opens, results display
- [ ] **Help Center:** Opens, help content displays

### Import Rules Check
```powershell
python scripts\check_import_rules.py --strict
```
- [ ] No import rule violations

### Sign-off
- [ ] All validation checks pass
- [ ] Commit: `git commit -am "Phase 3 complete: Feature pods"`
- [ ] Push: `git push origin presentation-migration`

**Notes:**
```
[Add any issues encountered or deviations from plan]
```

---

## Phase 4: Cleanup

### Execution
- [ ] **Remove legacy aliases:**
  - Delete `refactor/aliases/presentation/legacy_aliases.py`
- [ ] **Remove empty directories:**
  - Verify `styles/` removed
  - Verify `window_controller/` removed
  - Verify `_deprecated/` removed (if exists)
- [ ] **Test:** `python scripts\win\03_build_and_smoke.py --phase P4`
  - Verify: No import errors, all tests pass

### Final Validation
- [ ] Full test suite: `pytest tests/`
- [ ] App launches successfully
- [ ] All windows accessible
- [ ] No dead code remains
- [ ] No lint errors
- [ ] Import rules enforced

### Final Smoke Tests
- [ ] Main window displays
- [ ] Navigate to all 7 windows
- [ ] Run test workflow (Comparator)
- [ ] Run validation workflow (Validator)
- [ ] Run benchmark workflow (Benchmarker)
- [ ] Edit code (Editor)
- [ ] View results (Results)
- [ ] Read help (Help Center)

### Sign-off
- [ ] All validation checks pass
- [ ] Commit: `git commit -am "Phase 4 complete: Cleanup"`
- [ ] Push: `git push origin presentation-migration`

**Notes:**
```
[Add any issues encountered or deviations from plan]
```

---

## Post-Migration Tasks

### Documentation
- [ ] Update architecture documentation
- [ ] Update developer onboarding guide
- [ ] Document new import rules
- [ ] Update code style guide

### Code Quality
- [ ] Enable import linting in CI
- [ ] Add import-linter config
- [ ] Update pre-commit hooks (if any)

### Team Communication
- [ ] Demo new structure to team
- [ ] Share migration results
- [ ] Update team wiki/confluence
- [ ] Conduct retrospective

### Future Improvements
- [ ] Extract common patterns
- [ ] Reduce widget duplication
- [ ] Improve MVVM separation
- [ ] Profile performance

---

## Migration Results

### Metrics
```
Files moved:        _____ / 50
Imports rewritten:  _____
Time taken:         _____ hours
Tests passing:      _____ / _____
```

### Issues Encountered
```
[List any problems and how they were resolved]

1. 
2. 
3. 
```

### Deviations from Plan
```
[List any changes made to the original plan]

1. 
2. 
3. 
```

### Lessons Learned
```
[What worked well, what could be improved]

1. 
2. 
3. 
```

---

## Rollback Log

### Phase 1 Rollback (if needed)
```powershell
git checkout src/app/presentation/styles/
git checkout src/app/presentation/design_system/styles/
git clean -fd src/app/presentation/
```
- [ ] Executed: Yes / No
- [ ] Reason: _______________

### Phase 2 Rollback (if needed)
```powershell
git checkout src/app/presentation/window_controller/
git checkout src/app/presentation/navigation/
git clean -fd src/app/presentation/
```
- [ ] Executed: Yes / No
- [ ] Reason: _______________

### Phase 3 Rollback (if needed)
```powershell
git checkout src/app/presentation/windows/
git clean -fd src/app/presentation/
```
- [ ] Executed: Yes / No
- [ ] Reason: _______________

### Complete Rollback (if needed)
```powershell
git reset --hard <pre-migration-commit-sha>
```
- [ ] Executed: Yes / No
- [ ] Reason: _______________

---

## Final Sign-Off

### Technical Lead
- [ ] Code review completed
- [ ] Architecture approved
- [ ] Import rules verified
- Name: _______________
- Date: _______________

### QA
- [ ] All tests pass
- [ ] Manual testing complete
- [ ] No regressions found
- Name: _______________
- Date: _______________

### Product Owner
- [ ] Functionality verified
- [ ] No user-facing changes
- [ ] Ready for deployment
- Name: _______________
- Date: _______________

---

**Migration Status:** ⬜ Not Started | 🟡 In Progress | ✅ Complete  
**Last Updated:** _______________  
**Next Action:** _______________

---

*Track your progress through the migration using this checklist.*  
*Update after each phase completion.*
