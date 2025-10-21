# Presentation Layer Migration - Complete Package

## 🎯 Overview

This package contains all the tools, documentation, and scripts needed to migrate the PySide6 presentation layer from a mixed structure to a clean "Feature-local MVVM" architecture with centralized design system.

**Status:** ✅ Discovery Complete - Ready for Execution

---

## 📊 Discovery Results

### Current State
- **Total files:** 296 (104 Python, 1 font, 191 other)
- **Python files by location:**
  - styles/: 36 files (→ moving to design_system)
  - window_controller/: 3 files (→ moving to navigation)
  - widgets/: 21 files
  - windows/: 24 files
  - base/: 5 files
  - design_system/: 6 files (existing partial structure)

### Import Analysis
- **Total imports:** 392
  - Internal: 177
  - External: 215
- **Top dependencies:** PySide6.QtWidgets (32), PySide6.QtCore (27), PySide6.QtGui (18)
- **Circular imports:** None detected ✅

### Widget Classification
- **Total widgets:** 48
- **Shared widgets:** 38 (editor, console, status_view, sidebar, layout)
- **Feature-local widgets:** 10 (results, main window components)

### Migration Scope
- **Total moves planned:** 50 files
  - Phase 1 (Styles): 36 moves
  - Phase 2 (Navigation): 3 moves
  - Phase 3 (Feature Pods): 9 moves
  - Phase 4 (Cleanup): 2 removals

---

## 📁 Package Structure

```
refactor/
├── rename_map.csv                      # All planned file moves (50 entries)
├── current_tree.json                   # Current structure analysis
├── import_graph.json                   # Complete import dependencies
├── styles_widgets_analysis.json        # Widget classification
├── codemods/
│   ├── import_rewrites.py              # AST-based import rewriting (libcst)
│   ├── qss_path_fixup.py               # Resource path updates
│   └── __init___exports_fixup.py       # Package export generation
└── aliases/
    └── presentation/
        └── legacy_aliases.py           # Temporary backward compatibility

docs/
├── migration_playbook.md               # Complete migration guide
├── validation_checklist.md             # Testing checklist per phase
└── todo_reading.md                     # Discovery checklist (COMPLETE)

scripts/win/
├── discover_tree.py                    # ✅ Executed - File structure analysis
├── build_import_graph.py               # ✅ Executed - Import dependency graph
├── scan_styles_and_widgets.py          # ✅ Executed - Widget classification
├── propose_moves.py                    # ✅ Executed - Move planning
├── 00_dry_run.py                       # Execution: Preview migration
├── 01_apply_moves.py                   # Execution: Physical file moves
├── 02_run_codemods.py                  # Execution: Import/path rewrites
└── 03_build_and_smoke.py               # Execution: Testing & validation
```

---

## 🚀 Quick Start

### Prerequisites
```powershell
# Install required dependency for import rewriting
pip install libcst
```

### Migration Workflow

#### 1. Review Current State
```powershell
# View discovery results
type refactor\current_tree.json
type refactor\import_graph.json
type refactor\rename_map.csv

# Read migration plan
type docs\migration_playbook.md
type docs\validation_checklist.md
```

#### 2. Dry Run (Preview Changes)
```powershell
# Preview all changes
python scripts\win\00_dry_run.py

# Preview specific phase
python scripts\win\00_dry_run.py --phase P1
```

#### 3. Execute Phase 1 (Style Consolidation)
```powershell
# Move style files to design_system
python scripts\win\01_apply_moves.py --phase P1

# Rewrite import statements
python scripts\win\02_run_codemods.py --phase P1

# Test and validate
python scripts\win\03_build_and_smoke.py --phase P1
```

#### 4. Execute Remaining Phases
```powershell
# Phase 2: Navigation
python scripts\win\01_apply_moves.py --phase P2
python scripts\win\02_run_codemods.py --phase P2
python scripts\win\03_build_and_smoke.py --phase P2

# Phase 3: Feature Pods
python scripts\win\01_apply_moves.py --phase P3
python scripts\win\02_run_codemods.py --phase P3
python scripts\win\03_build_and_smoke.py --phase P3

# Phase 4: Cleanup
python scripts\win\01_apply_moves.py --phase P4
python scripts\win\03_build_and_smoke.py --phase P4
```

#### 5. Advanced: All Phases at Once (Use with caution)
```powershell
python scripts\win\01_apply_moves.py
python scripts\win\02_run_codemods.py
python scripts\win\03_build_and_smoke.py
```

---

## 📋 Phase Details

### Phase 1: Design System Consolidation
**Goal:** Move all styles to `design_system/styles/`  
**Files:** 36 Python files  
**Risk:** Medium  
**Duration:** 2-3 hours

**Key moves:**
- `styles/style.py` → `design_system/styles/style.py`
- `styles/helpers/*.py` → `design_system/styles/*.py`
- `styles/components/**` → `design_system/styles/components/**`

**Validation:**
- All style imports resolve
- Windows render with correct styles
- StatusView displays properly

### Phase 2: Navigation Unification
**Goal:** Move `window_controller/` to `navigation/`  
**Files:** 3 Python files  
**Risk:** High (central component)  
**Duration:** 1-2 hours

**Key moves:**
- `window_controller/window_management.py` → `navigation/window_manager.py`
- Create `navigation/factory.py` for window registry

**Validation:**
- All windows open correctly
- Navigation history works
- Back button functions
- No circular imports

### Phase 3: Feature Pods
**Goal:** Organize windows into MVVM feature pods  
**Files:** 9 feature-local widgets  
**Risk:** Low  
**Duration:** 1 hour

**Actions:**
- Move feature-local widgets into `windows/<feature>/widgets/`
- Ensure no sideways imports between features
- Validate feature isolation

**Validation:**
- Each feature works independently
- Import rules enforced
- Test windows inherit TestWindowBase

### Phase 4: Cleanup
**Goal:** Remove legacy code and aliases  
**Files:** Remove empty directories  
**Risk:** Low  
**Duration:** 30 minutes

**Actions:**
- Remove `_deprecated/` folder
- Remove empty `styles/` directory
- Remove empty `window_controller/` directory
- Remove `legacy_aliases.py`

**Validation:**
- No import errors
- All tests pass
- App launches successfully

---

## 🎯 Import Rules (Post-Migration)

### Allowed Directions
```
windows/<feature>/ → {shared/, base/, design_system/, services/, navigation/}
shared/ → {base/, design_system/}
navigation/ → {base/, windows/ via factory}
services/ → {design_system/, base/, domain}
design_system/ → {PySide6 only}
base/ → {PySide6 only}
```

### Forbidden
- ❌ Sideways imports: `windows/<feature>/ → windows/<other>/`
- ❌ Upward imports: `base/ → windows/`
- ❌ Circular imports at any level

---

## ✅ Validation Strategy

### Per-Phase Testing
Each phase includes:
1. Import resolution check
2. Syntax validation
3. Unit tests
4. Manual smoke test

### Windows to Validate
- [ ] Main Window
- [ ] Editor Window
- [ ] Results Window
- [ ] Help Center Window
- [ ] Comparator Window (TestWindowBase)
- [ ] Validator Window (TestWindowBase)
- [ ] Benchmarker Window (TestWindowBase)

### StatusView Critical Checks
- [ ] Displays in test windows
- [ ] Updates on runner progress
- [ ] Correct status colors
- [ ] Card rendering

See `docs/validation_checklist.md` for complete checklist.

---

## 🔧 Troubleshooting

### Import Errors
**Symptom:** `ModuleNotFoundError`

**Solution:**
1. Check `refactor/aliases/presentation/legacy_aliases.py`
2. Rerun codemods: `python scripts\win\02_run_codemods.py`
3. Verify `__init__.py` exports

### Style Not Applied
**Symptom:** UI elements without styles

**Solution:**
1. Check import path in view file
2. Verify style file in `design_system/`
3. Check `design_system/styles/__init__.py` exports

### Circular Import
**Symptom:** Partially initialized module error

**Solution:**
1. Move import inside function (late import)
2. Use factory pattern for window creation
3. Refactor to protocols/interfaces

---

## 📊 Key Metrics

### Before Migration
- Presentation files: 104
- Legacy locations: 3 (styles, window_controller, scattered)
- Import complexity: Mixed
- Feature coupling: High

### After Migration
- Presentation files: 104 (same, reorganized)
- Legacy locations: 0
- Import complexity: Clean, enforced rules
- Feature coupling: Low (pod isolation)

### Performance Targets
- Startup time: ≤ baseline
- Window load: ≤ 1s per window
- Memory: ≤ baseline
- Test coverage: ≥ baseline

---

## 🎓 Documentation

### Primary Documents
1. **migration_playbook.md** - Complete migration guide with phases, commands, validation
2. **validation_checklist.md** - Testing checklist for each phase
3. **todo_reading.md** - Discovery checklist (completed)

### Discovery Artifacts
- `refactor/current_tree.json` - Current structure analysis
- `refactor/import_graph.json` - Import dependencies (392 total)
- `refactor/styles_widgets_analysis.json` - Widget classification (48 widgets)
- `refactor/rename_map.csv` - All 50 planned moves

---

## ⚠️ Important Notes

### Before Starting
- [ ] Create git branch: `git checkout -b presentation-migration`
- [ ] Backup current state: `git commit -am "Pre-migration snapshot"`
- [ ] Notify team of migration start
- [ ] Ensure no conflicting PRs

### During Migration
- [ ] Execute phases sequentially (P1 → P2 → P3 → P4)
- [ ] Test after each phase
- [ ] Push after successful phase completion
- [ ] Keep `legacy_aliases.py` until Phase 4

### After Migration
- [ ] Remove `legacy_aliases.py`
- [ ] Run full test suite
- [ ] Update architecture documentation
- [ ] Demo new structure to team

---

## 🔄 Rollback Procedures

### Phase 1 Rollback
```powershell
git checkout src/app/presentation/styles/
git checkout src/app/presentation/design_system/styles/
git clean -fd src/app/presentation/
```

### Phase 2 Rollback
```powershell
git checkout src/app/presentation/window_controller/
git checkout src/app/presentation/navigation/
git clean -fd src/app/presentation/
```

### Phase 3 Rollback
```powershell
git checkout src/app/presentation/windows/
git clean -fd src/app/presentation/
```

### Complete Rollback
```powershell
git reset --hard <pre-migration-commit-sha>
```

---

## 📞 Support

### Questions?
- Review `docs/migration_playbook.md` for detailed guidance
- Check `docs/validation_checklist.md` for testing procedures
- Review discovery artifacts in `refactor/*.json`

### Issues?
- Check troubleshooting section above
- Review error output from scripts
- Use dry-run mode to preview changes

---

## ✨ Success Criteria

- ✅ All 104 Python files compile without errors
- ✅ All imports resolve correctly
- ✅ Zero circular imports
- ✅ All windows open and render correctly
- ✅ StatusView displays in test windows
- ✅ Navigation works (forward/back)
- ✅ All existing tests pass
- ✅ Import rules enforced
- ✅ No performance degradation

---

## 📈 Timeline Estimate

- **Phase 1:** 2-3 hours (36 files, many imports)
- **Phase 2:** 1-2 hours (critical component, careful testing)
- **Phase 3:** 1 hour (straightforward isolation)
- **Phase 4:** 30 minutes (cleanup only)

**Total:** 5-7 hours including testing

---

*Generated by Presentation Layer Migration Tool*  
*Last Updated: 2025-10-21*  
*Repo: code-testing-suite*  
*Branch: main*
