# Presentation Layer MVVM Migration Playbook

**Version:** 1.0  
**Date:** October 21, 2025  
**Branch:** `refactor/presentation-incremental-extraction`  
**Status:** Phase 1 - Planning Complete

---

## Executive Summary

This playbook guides the incremental extraction and restructuring of the PySide6 presentation layer from a flat views-widgets structure to a per-window MVVM architecture with unified components, eliminating circular dependencies and reducing code duplication by ~40%.

**Key Objectives:**
- Replace singleton NavigationService with injectable Router
- Unify 3 duplicate Status View implementations into 1 configurable component
- Consolidate 2 duplicate detailed results dialogs
- Establish per-window packages with MVVM separation
- Enforce zero window→window imports via automated checks

**Estimated Impact:**
- **Lines removed:** ~2,000-2,500 lines
- **Files consolidated:** 15 → 8 files
- **Circular dependencies:** 12 → 0
- **Test coverage target:** 85%+ (currently ~70%)

---

## Goals & Non-Goals

### ✅ Goals

1. **Architectural Clarity**
   - Each window is a self-contained package (`windows/<name>/`)
   - Clear MVVM separation (View = Qt widgets, ViewModel = state + logic)
   - Zero inter-window dependencies

2. **Code Deduplication**
   - One Status View implementation with presets (not 3 per-tool forks)
   - One detailed results dialog (not 2 separate implementations)
   - Shared navigation via injectable router (not singleton)

3. **Testability**
   - ViewModels are pure Python (no Qt dependencies)
   - Router is injectable and mockable
   - All components have pytest-qt integration tests

4. **Maintainability**
   - Automated import-graph assertions (fail CI on violations)
   - Pre-commit hooks for ruff + isort
   - Clear ownership boundaries

### ❌ Non-Goals

1. **Not changing business logic** in `src/app/core/` (tools, AI, database)
2. **Not modifying APIs** outside presentation layer
3. **Not adding new features** (pure refactoring)
4. **Not changing UI behavior** visible to users
5. **Not introducing new dependencies** without explicit approval

---

## Current State Analysis

### Dependency Map & Circular Dependencies

**Critical Cycles Detected:**

```
Cycle 1: Navigation Singleton
views/benchmarker/benchmarker_window.py
  → services/navigation_service.py (singleton)
    → window_controller/window_management.py
      → views/benchmarker/benchmarker_window.py (import for factory)

Cycle 2: Results Cross-Reference
views/results/results_window.py
  → views/results/detailed_results_window.py
    → views/results/results_widget.py (data sharing)
      → views/results/results_window.py (parent reference)

Cycle 3: Window Manager
views/main_window/main_window.py
  → window_controller/window_management.py
    → views/main_window/main_window.py (lazy import)

Cycle 4: Status View Imports
views/benchmarker/benchmarker_window.py
  → views/benchmarker/benchmarker_status_view.py
    → widgets/status_view/presenter.py
      → widgets/status_view/widgets.py (circular)
```

**Import Hotspots (files importing from views/):**

| File | Imports From views/ | Risk Level |
|------|---------------------|------------|
| `window_controller/window_management.py` | 7 window classes | 🔴 HIGH |
| `views/__init__.py` | All windows | 🟡 MEDIUM |
| `views/results/results_window.py` | 2 internal views | 🟡 MEDIUM |
| `views/main_window/main_window.py` | 2 views (document, code_editor) | 🟡 MEDIUM |

**NavigationService Usage (19 call sites):**

- benchmarker_window.py: 1 usage
- comparator_window.py: 1 usage
- validator_window.py: 1 usage
- code_editor_window.py: 4 usages (close events)
- results_window.py: 2 usages
- main_window.py: 2 usages
- base_window.py: 1 usage
- test_window_base.py: 1 usage
- content_window_base.py: 1 usage
- detailed_results_window.py: 1 usage
- navigation_service.py: 4 self-references

**Status View Duplication:**

```
Implementation 1: widgets/status_view/
  - presenter.py (280 lines)
  - widgets.py (520 lines)
  - cards.py (180 lines)
  - models.py (150 lines)
  Total: ~1,130 lines

Implementation 2: views/benchmarker/benchmarker_status_view.py (170 lines)
Implementation 3: views/comparator/comparator_status_view.py (160 lines)
Implementation 4: views/validator/validator_status_view.py (155 lines)

Duplication: ~485 lines (43% of per-tool status views are duplicate patterns)
```

**Detailed Results Duplication:**

```
Implementation 1: views/results/detailed_results_window.py (620 lines)
Implementation 2: widgets/detailed_results_window.py (580 lines)

Common functionality: 
- 4-tab layout (Summary, Code, Passed, Failed)
- Test case rendering
- Export functionality
- Data loading from database

Estimated duplication: ~400 lines (65%)
```

---

## Target Structure

### Complete File Map

```
src/app/presentation/
├── __init__.py                      # Module root, no window imports
│
├── base/                            # ✅ KEEP (already good)
│   ├── __init__.py
│   ├── protocols.py
│   ├── window_base.py
│   ├── content_window_base.py
│   └── test_window_base.py
│
├── navigation/                      # 🆕 NEW - Router replaces singleton
│   ├── __init__.py
│   └── router.py                    # NavigationRouter class
│
├── windows/                         # 🆕 NEW - Per-window packages
│   ├── __init__.py                  # Empty, no cross-window imports
│   │
│   ├── main/                        # MainWindow
│   │   ├── __init__.py
│   │   ├── view.py                  # MainWindow (renamed from main_window.py)
│   │   ├── viewmodel.py             # 🆕 MainViewModel (extracted logic)
│   │   └── widgets/
│   │       ├── __init__.py
│   │       ├── content.py           # Moved from views/main_window/
│   │       └── document.py          # Moved from views/main_window/
│   │
│   ├── editor/                      # CodeEditorWindow
│   │   ├── __init__.py
│   │   ├── view.py                  # CodeEditorWindow
│   │   ├── viewmodel.py             # 🆕 EditorViewModel
│   │   └── widgets/
│   │       ├── __init__.py
│   │       └── display_area.py      # Moved from code_editor_display_area.py
│   │
│   ├── benchmarker/                 # BenchmarkerWindow
│   │   ├── __init__.py
│   │   ├── view.py                  # BenchmarkerWindow
│   │   ├── viewmodel.py             # 🆕 BenchmarkerViewModel
│   │   └── widgets/                 # Local, tool-specific only
│   │       └── __init__.py
│   │
│   ├── comparator/                  # ComparatorWindow
│   │   ├── __init__.py
│   │   ├── view.py                  # ComparatorWindow
│   │   ├── viewmodel.py             # 🆕 ComparatorViewModel
│   │   └── widgets/
│   │       └── __init__.py
│   │
│   ├── validator/                   # ValidatorWindow
│   │   ├── __init__.py
│   │   ├── view.py                  # ValidatorWindow
│   │   ├── viewmodel.py             # 🆕 ValidatorViewModel
│   │   └── widgets/
│   │       └── __init__.py
│   │
│   ├── results/                     # ResultsWindow
│   │   ├── __init__.py
│   │   ├── view.py                  # ResultsWindow
│   │   ├── viewmodel.py             # 🆕 ResultsViewModel
│   │   └── widgets/
│   │       ├── __init__.py
│   │       └── table.py             # Renamed from results_widget.py
│   │
│   └── help_center/                 # HelpCenterWindow
│       ├── __init__.py
│       ├── view.py                  # HelpCenterWindow
│       ├── viewmodel.py             # 🆕 HelpViewModel
│       └── widgets/
│           ├── __init__.py
│           ├── content.py
│           └── document.py
│
├── dialogs/                         # 🆕 NEW - Shared dialogs
│   ├── __init__.py
│   └── result_detail/               # Unified detailed results
│       ├── __init__.py
│       ├── view.py                  # 🔀 MERGED from 2 implementations
│       └── viewmodel.py             # 🆕 DetailedResultViewModel
│
├── widgets/                         # ✅ REORGANIZED - Cross-window components
│   ├── __init__.py
│   │
│   ├── sidebar/                     # 📦 PACKAGED
│   │   ├── __init__.py
│   │   ├── sidebar.py               # Moved from widgets/sidebar.py
│   │   ├── test_count_slider.py     # Moved from sidebar_widgets/
│   │   └── limits_input.py          # Moved from sidebar_widgets/
│   │
│   ├── display_area/                # 📦 PACKAGED
│   │   ├── __init__.py
│   │   ├── display_area.py          # Moved from widgets/display_area.py
│   │   └── testing_content.py       # Moved from testing_content_widget.py
│   │
│   ├── editor/                      # 📦 PACKAGED
│   │   ├── __init__.py
│   │   ├── editor.py                # Moved from display_area_widgets/
│   │   ├── editor_tabs.py           # Moved from editor_tab_widget.py
│   │   └── test_tabs.py             # Moved from test_tab_widget.py
│   │
│   ├── console/                     # 📦 PACKAGED
│   │   ├── __init__.py
│   │   └── console.py               # Moved from display_area_widgets/
│   │
│   ├── ai_panel/                    # 📦 PACKAGED
│   │   ├── __init__.py
│   │   └── ai_panel.py              # Moved from display_area_widgets/
│   │
│   └── status_view/                 # ✅ UNIFIED (was 4 implementations)
│       ├── __init__.py
│       ├── models.py                # ✅ KEEP
│       ├── view.py                  # 🔀 MERGED from presenter.py + widgets.py
│       ├── viewmodel.py             # 🆕 StatusViewModel (extracted logic)
│       └── presets.py               # 🆕 Per-tool configurations
│
├── viewmodels/                      # 🆕 NEW - Shared ViewModel utilities
│   ├── __init__.py
│   └── test_tool_vm_base.py         # Optional: Common test tool behaviors
│
├── design_system/                   # 🆕 NEW - Design tokens
│   ├── __init__.py
│   ├── tokens.py                    # Moved from styles/constants.py
│   └── qss/                         # Optional: Theme files
│       └── __init__.py
│
├── styles/                          # ✅ SIMPLIFIED
│   ├── __init__.py
│   ├── components/                  # Component-specific QSS
│   │   ├── __init__.py
│   │   ├── button_styles.py
│   │   ├── sidebar_styles.py
│   │   ├── editor_styles.py
│   │   ├── console_styles.py
│   │   ├── ai_panel_styles.py
│   │   ├── dialogs/
│   │   │   ├── __init__.py
│   │   │   └── test_detail_styles.py
│   │   └── status_view/
│   │       ├── __init__.py
│   │       ├── status_widgets_styles.py
│   │       └── status_cards_styles.py
│   └── helpers/
│       ├── __init__.py
│       └── colors.py
│
└── services/                        # 🗑️ DELETE (only export_service remains)
    ├── __init__.py                  # Keep, update exports
    ├── export_service.py            # ✅ KEEP (utility, not navigation)
    └── navigation_service.py        # 🗑️ DELETE (replaced by router)
```

---

## Move Map

### Phase-by-Phase File Transformations

| Old Path | New Path | Action | Phase | Notes |
|----------|----------|--------|-------|-------|
| **Navigation** |
| `services/navigation_service.py` | `navigation/router.py` | 🔄 REFACTOR | 2 | Singleton → Injectable router |
| **Windows** |
| `views/main_window/main_window.py` | `windows/main/view.py` | 🔄 RENAME + EXTRACT VM | 5 | Extract MainViewModel |
| `views/main_window/content.py` | `windows/main/widgets/content.py` | ➡️ MOVE | 5 | No changes |
| `views/main_window/document.py` | `windows/main/widgets/document.py` | ➡️ MOVE | 5 | No changes |
| `views/code_editor/code_editor_window.py` | `windows/editor/view.py` | 🔄 RENAME + EXTRACT VM | 5 | Extract EditorViewModel |
| `views/code_editor/code_editor_display_area.py` | `windows/editor/widgets/display_area.py` | ➡️ MOVE | 5 | No changes |
| `views/benchmarker/benchmarker_window.py` | `windows/benchmarker/view.py` | 🔄 RENAME + EXTRACT VM | 5 | Extract BenchmarkerViewModel |
| `views/benchmarker/benchmarker_status_view.py` | 🗑️ DELETE | 🗑️ DELETE | 3 | Replace with unified status view |
| `views/comparator/comparator_window.py` | `windows/comparator/view.py` | 🔄 RENAME + EXTRACT VM | 5 | Extract ComparatorViewModel |
| `views/comparator/comparator_status_view.py` | 🗑️ DELETE | 🗑️ DELETE | 3 | Replace with unified status view |
| `views/validator/validator_window.py` | `windows/validator/view.py` | 🔄 RENAME + EXTRACT VM | 5 | Extract ValidatorViewModel |
| `views/validator/validator_status_view.py` | 🗑️ DELETE | 🗑️ DELETE | 3 | Replace with unified status view |
| `views/results/results_window.py` | `windows/results/view.py` | 🔄 RENAME + EXTRACT VM | 5 | Extract ResultsViewModel |
| `views/results/results_widget.py` | `windows/results/widgets/table.py` | ➡️ MOVE + RENAME | 5 | No changes |
| `views/results/detailed_results_window.py` | `dialogs/result_detail/view.py` | 🔀 MERGE | 4 | Merge 2 implementations |
| `widgets/detailed_results_window.py` | 🗑️ DELETE | 🗑️ DELETE | 4 | Merged into dialogs/ |
| `views/help_center/help_center_window.py` | `windows/help_center/view.py` | 🔄 RENAME + EXTRACT VM | 5 | Extract HelpViewModel |
| `views/help_center/content.py` | `windows/help_center/widgets/content.py` | ➡️ MOVE | 5 | No changes |
| `views/help_center/document.py` | `windows/help_center/widgets/document.py` | ➡️ MOVE | 5 | No changes |
| **Widgets** |
| `widgets/sidebar.py` | `widgets/sidebar/sidebar.py` | ➡️ MOVE + PACKAGE | 6 | Package reorganization |
| `widgets/sidebar_widgets/test_count_slider.py` | `widgets/sidebar/test_count_slider.py` | ➡️ MOVE | 6 | Flatten into sidebar/ |
| `widgets/sidebar_widgets/limits_input_widget.py` | `widgets/sidebar/limits_input.py` | ➡️ MOVE + RENAME | 6 | Flatten into sidebar/ |
| `widgets/display_area.py` | `widgets/display_area/display_area.py` | ➡️ MOVE + PACKAGE | 6 | Package reorganization |
| `widgets/testing_content_widget.py` | `widgets/display_area/testing_content.py` | ➡️ MOVE + RENAME | 6 | Co-locate with display_area |
| `widgets/display_area_widgets/editor.py` | `widgets/editor/editor.py` | ➡️ MOVE | 6 | Package reorganization |
| `widgets/display_area_widgets/editor_tab_widget.py` | `widgets/editor/editor_tabs.py` | ➡️ MOVE + RENAME | 6 | Package reorganization |
| `widgets/display_area_widgets/test_tab_widget.py` | `widgets/editor/test_tabs.py` | ➡️ MOVE + RENAME | 6 | Package reorganization |
| `widgets/display_area_widgets/console.py` | `widgets/console/console.py` | ➡️ MOVE + PACKAGE | 6 | Package reorganization |
| `widgets/display_area_widgets/ai_panel.py` | `widgets/ai_panel/ai_panel.py` | ➡️ MOVE + PACKAGE | 6 | Package reorganization |
| **Status View** |
| `widgets/status_view/presenter.py` | `widgets/status_view/viewmodel.py` | 🔄 REFACTOR | 3 | Extract logic from presenter |
| `widgets/status_view/widgets.py` | `widgets/status_view/view.py` | 🔄 REFACTOR | 3 | Merge presenter + widgets |
| `widgets/status_view/cards.py` | 🗑️ DELETE | 🗑️ DELETE | 3 | Merge into view.py |
| `widgets/status_view/models.py` | ✅ KEEP | ✅ KEEP | 3 | No changes |
| 🆕 NEW | `widgets/status_view/presets.py` | 🆕 CREATE | 3 | Tool configurations |
| **Styles** |
| `styles/constants.py` | `design_system/tokens.py` | ➡️ MOVE | 6 | Design tokens |
| **Window Controller** |
| `window_controller/window_management.py` | 🔄 REFACTOR | 🔄 REFACTOR | 2 | Remove window imports, use router |
| `window_controller/base_window.py` | ✅ KEEP | ✅ KEEP | - | Already good |
| **Services** |
| `services/export_service.py` | ✅ KEEP | ✅ KEEP | - | Utility service, not navigation |

**Summary:**
- **Files to move:** 40
- **Files to delete:** 6
- **Files to create:** 15 (ViewModels + presets)
- **Files to merge:** 4
- **Net change:** +9 files, -2,200 lines

---

## Phased Execution Plan

### Phase 1: Prep and Guardrails (Est: 2-4 hours)

**Objective:** Set up automated checks and establish baseline metrics before any refactoring.

#### Tasks

- [x] **1.1** Generate current import graph visualization
  ```bash
  python scripts/analyze_imports.py src/app/presentation > import_graph.txt
  ```

- [ ] **1.2** Create import rule checker script
  ```python
  # scripts/check_import_rules.py
  # Rule: Forbid windows/** → windows/** imports
  # Rule: Allow windows/** → widgets/*, base/*, navigation/*
  ```

- [ ] **1.3** Configure ruff with strict rules
  ```toml
  # pyproject.toml
  [tool.ruff]
  line-length = 100
  target-version = "py310"
  select = ["E", "F", "I", "N", "W", "UP"]
  ignore = ["E501"]  # Line length handled by formatter
  
  [tool.ruff.per-file-ignores]
  "__init__.py" = ["F401"]  # Allow unused imports in __init__
  ```

- [ ] **1.4** Add pre-commit hooks
  ```yaml
  # .pre-commit-config.yaml
  repos:
    - repo: https://github.com/astral-sh/ruff-pre-commit
      rev: v0.1.6
      hooks:
        - id: ruff
          args: [--fix]
        - id: ruff-format
    - repo: local
      hooks:
        - id: import-rules
          name: Check import rules
          entry: python scripts/check_import_rules.py
          language: python
          pass_filenames: false
  ```

- [ ] **1.5** Add CI job for import checks
  ```yaml
  # .github/workflows/import-checks.yml
  name: Import Rules
  on: [push, pull_request]
  jobs:
    check-imports:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - uses: actions/setup-python@v4
        - run: python scripts/check_import_rules.py
        - run: pytest -q
        - run: ruff check .
  ```

#### Acceptance Criteria
- ✅ Import rule checker script exists and runs
- ✅ CI pipeline includes import-graph assertion
- ✅ Pre-commit hooks configured
- ✅ Baseline metrics documented (lines, files, cycles)
- ✅ All existing tests pass

#### Risks & Mitigation
- **Risk:** Existing code may already violate import rules
  - **Mitigation:** Document violations as "known issues" to fix in Phase 5
- **Risk:** CI setup may delay developer workflow
  - **Mitigation:** Make checks optional locally, enforce only on PR

#### Rollback Plan
- Delete scripts/check_import_rules.py
- Remove CI job
- Revert .pre-commit-config.yaml

---

### Phase 2: Navigation Singleton Removal (Est: 4-6 hours)

**Objective:** Replace NavigationService singleton with injectable NavigationRouter.

#### Tasks

- [ ] **2.1** Create navigation/router.py
  ```python
  # navigation/router.py
  class NavigationRouter:
      """Injectable navigation router with stack/history API."""
      
      def __init__(self, window_manager):
          self._window_manager = window_manager
          self._history: List[str] = []
      
      def navigate_to(self, window_name: str, **kwargs) -> bool:
          """Navigate to window, returns success."""
          # Implementation
      
      def go_back(self) -> bool:
          """Return to previous window."""
          # Implementation
      
      def can_go_back(self) -> bool:
          """Check if can navigate back."""
          return len(self._history) > 1
  ```

- [ ] **2.2** Update WindowManager to accept router
  ```python
  # window_controller/window_management.py
  class WindowManager:
      def __init__(self, stacked_widget, router: NavigationRouter):
          self.router = router
          # ...
  ```

- [ ] **2.3** Update MainWindow to inject router
  ```python
  # views/main_window/main_window.py
  class MainWindow:
      def __init__(self):
          self.router = NavigationRouter(self.window_manager)
          self.window_manager.router = self.router
  ```

- [ ] **2.4** Replace NavigationService calls (19 sites)
  - benchmarker_window.py: `NavigationService.instance()` → `self.router`
  - comparator_window.py: `NavigationService.instance()` → `self.router`
  - validator_window.py: `NavigationService.instance()` → `self.router`
  - code_editor_window.py: `NavigationService.instance()` → `self.router`
  - results_window.py: `NavigationService.instance()` → `self.router`
  - main_window.py: `NavigationService.instance()` → `self.router`
  - base_window.py: `NavigationService.instance()` → `self.router`
  - test_window_base.py: `NavigationService.instance()` → `self.router`
  - content_window_base.py: `NavigationService.instance()` → `self.router`
  - detailed_results_window.py: `NavigationService.instance()` → `self.router`

- [ ] **2.5** Add router property to base classes
  ```python
  # base/window_base.py
  class WindowBase:
      @property
      def router(self):
          if not hasattr(self, '_router') and self.parent():
              self._router = self.parent().router
          return getattr(self, '_router', None)
  ```

- [ ] **2.6** Write router unit tests
  ```python
  # tests/unit/navigation/test_router.py
  def test_navigate_to_success(mock_window_manager):
      router = NavigationRouter(mock_window_manager)
      assert router.navigate_to("benchmarker")
  
  def test_navigate_back():
      router = NavigationRouter(mock_window_manager)
      router.navigate_to("benchmarker")
      router.navigate_to("results")
      assert router.go_back()
      assert router._history[-1] == "benchmarker"
  ```

- [ ] **2.7** Delete services/navigation_service.py

- [ ] **2.8** Delete window_controller/window_management.py lazy imports

#### Acceptance Criteria
- ✅ navigation/router.py exists with 100% test coverage
- ✅ All 19 NavigationService call sites replaced
- ✅ services/navigation_service.py deleted
- ✅ All tests pass (pytest -v)
- ✅ Import-graph checker passes (zero cycles)

#### Risks & Mitigation
- **Risk:** Router not accessible in deeply nested widgets
  - **Mitigation:** Add router property to all base classes with parent traversal
- **Risk:** Tests break due to missing router injection
  - **Mitigation:** Create mock_router fixture in conftest.py

#### Rollback Plan
- Restore services/navigation_service.py from git
- Revert all NavigationService → router changes
- Delete navigation/router.py

---

### Phase 3: Status View Unification (Est: 6-8 hours)

**Objective:** Consolidate 4 status view implementations into 1 configurable component.

#### Tasks

- [ ] **3.1** Create widgets/status_view/presets.py
  ```python
  # widgets/status_view/presets.py
  from dataclasses import dataclass
  from typing import List
  
  @dataclass
  class StatusViewPreset:
      stages: List[str]
      metrics: List[str]
      show_worker_status: bool
      show_performance_panel: bool
  
  BENCHMARKER_PRESET = StatusViewPreset(
      stages=["Compilation", "Test Generation", "Execution", "Analysis"],
      metrics=["Time Limit", "Memory Limit", "Pass Rate"],
      show_worker_status=True,
      show_performance_panel=True
  )
  
  COMPARATOR_PRESET = StatusViewPreset(
      stages=["Compilation", "Test Generation", "Comparison"],
      metrics=["Pass Rate", "Diff Count"],
      show_worker_status=False,
      show_performance_panel=False
  )
  
  VALIDATOR_PRESET = StatusViewPreset(
      stages=["Compilation", "Test Generation", "Validation"],
      metrics=["Pass Rate", "Validation Errors"],
      show_worker_status=False,
      show_performance_panel=False
  )
  ```

- [ ] **3.2** Refactor widgets/status_view/presenter.py → viewmodel.py
  ```python
  # widgets/status_view/viewmodel.py
  class StatusViewModel:
      def __init__(self, preset: StatusViewPreset):
          self.preset = preset
          self._state = {}  # Pure Python state
      
      def update_stage(self, stage: str, status: str):
          # Logic only, no Qt
      
      def update_metric(self, metric: str, value: Any):
          # Logic only, no Qt
  ```

- [ ] **3.3** Merge widgets/status_view/{presenter, widgets, cards}.py → view.py
  ```python
  # widgets/status_view/view.py
  class StatusView(QWidget):
      def __init__(self, viewmodel: StatusViewModel, parent=None):
          self.vm = viewmodel
          self._setup_ui_from_preset(self.vm.preset)
      
      def _setup_ui_from_preset(self, preset: StatusViewPreset):
          # Create pipeline stages from preset.stages
          # Create metric cards from preset.metrics
          # Conditionally show worker/performance panels
  ```

- [ ] **3.4** Delete per-tool status views
  - views/benchmarker/benchmarker_status_view.py
  - views/comparator/comparator_status_view.py
  - views/validator/validator_status_view.py

- [ ] **3.5** Update TestWindowBase to use unified status view
  ```python
  # base/test_window_base.py
  def _create_status_view(self):
      """Override in subclass to provide preset."""
      raise NotImplementedError
  
  def _integrate_status_view(self):
      preset = self._get_status_preset()
      vm = StatusViewModel(preset)
      self.status_view = StatusView(vm, parent=self)
  ```

- [ ] **3.6** Update each test window to provide preset
  ```python
  # windows/benchmarker/view.py
  def _get_status_preset(self):
      from src.app.presentation.widgets.status_view.presets import BENCHMARKER_PRESET
      return BENCHMARKER_PRESET
  ```

- [ ] **3.7** Write StatusView integration tests
  ```python
  # tests/integration/widgets/test_status_view.py
  def test_benchmarker_preset_renders_all_stages(qtbot):
      vm = StatusViewModel(BENCHMARKER_PRESET)
      view = StatusView(vm)
      qtbot.addWidget(view)
      assert len(view._stage_widgets) == 4
  ```

#### Acceptance Criteria
- ✅ widgets/status_view/ has 4 files (models, view, viewmodel, presets)
- ✅ 3 per-tool status views deleted (~485 lines removed)
- ✅ All 3 test tools render status view correctly
- ✅ Status view tests achieve 90%+ coverage
- ✅ Zero logic duplication between tools

#### Risks & Mitigation
- **Risk:** Per-tool status views have unique features
  - **Mitigation:** Identify unique features, make them preset-configurable or add extension points
- **Risk:** Test tools break during migration
  - **Mitigation:** Migrate one tool at a time, verify UI manually before next tool

#### Rollback Plan
- Restore deleted per-tool status views from git
- Revert TestWindowBase changes
- Delete presets.py and viewmodel.py

---

### Phase 4: Results Detail Consolidation (Est: 4-5 hours)

**Objective:** Merge 2 duplicate detailed results dialogs into 1.

#### Tasks

- [ ] **4.1** Create dialogs/result_detail/ structure
  ```
  dialogs/result_detail/
  ├── __init__.py
  ├── view.py
  └── viewmodel.py
  ```

- [ ] **4.2** Analyze differences between implementations
  ```bash
  diff views/results/detailed_results_window.py widgets/detailed_results_window.py > detail_diff.txt
  ```

- [ ] **4.3** Merge common functionality into view.py
  ```python
  # dialogs/result_detail/view.py
  class DetailedResultDialog(QDialog):
      def __init__(self, result_id: int, vm: DetailedResultViewModel, parent=None):
          self.vm = vm
          self._setup_tabs()  # 4 tabs: Summary, Code, Passed, Failed
      
      def _setup_tabs(self):
          self.tabs = QTabWidget()
          self.tabs.addTab(self._create_summary_tab(), "Summary")
          self.tabs.addTab(self._create_code_tab(), "Code Files")
          self.tabs.addTab(self._create_passed_tab(), "Passed Tests")
          self.tabs.addTab(self._create_failed_tab(), "Failed Tests")
  ```

- [ ] **4.4** Extract logic into viewmodel.py
  ```python
  # dialogs/result_detail/viewmodel.py
  class DetailedResultViewModel:
      def __init__(self, db_manager):
          self.db_manager = db_manager
      
      def load_result(self, result_id: int):
          # Pure Python data loading
          return self.db_manager.get_test_result_by_id(result_id)
      
      def format_summary(self, result) -> dict:
          # Format data for UI
  ```

- [ ] **4.5** Update windows/results/view.py to use new dialog
  ```python
  # windows/results/view.py
  def show_detailed_view(self, result_id: int):
      from src.app.presentation.dialogs.result_detail.view import DetailedResultDialog
      from src.app.presentation.dialogs.result_detail.viewmodel import DetailedResultViewModel
      
      vm = DetailedResultViewModel(self.db_manager)
      dialog = DetailedResultDialog(result_id, vm, parent=self)
      dialog.exec()
  ```

- [ ] **4.6** Delete duplicate implementations
  - views/results/detailed_results_window.py
  - widgets/detailed_results_window.py

- [ ] **4.7** Write dialog integration tests
  ```python
  # tests/integration/dialogs/test_result_detail.py
  def test_dialog_loads_all_tabs(qtbot, mock_db):
      vm = DetailedResultViewModel(mock_db)
      dialog = DetailedResultDialog(result_id=1, vm=vm)
      qtbot.addWidget(dialog)
      assert dialog.tabs.count() == 4
  ```

#### Acceptance Criteria
- ✅ dialogs/result_detail/ exists with view + viewmodel
- ✅ 2 duplicate implementations deleted (~400 lines removed)
- ✅ ResultsWindow uses new dialog
- ✅ Dialog tests achieve 85%+ coverage
- ✅ Export functionality preserved

#### Risks & Mitigation
- **Risk:** Subtle UI differences between implementations
  - **Mitigation:** Side-by-side manual testing before deletion
- **Risk:** Data loading breaks
  - **Mitigation:** Comprehensive unit tests for ViewModel

#### Rollback Plan
- Restore deleted detailed_results_window.py files
- Revert ResultsWindow changes
- Delete dialogs/result_detail/

---

### Phase 5: Per-Window Packaging (Est: 8-10 hours)

**Objective:** Move each window into `windows/<name>/` with MVVM separation.

#### Tasks

**Per Window (repeat for all 7 windows):**

- [ ] **5.1** Create windows/<name>/ structure
  ```bash
  mkdir -p windows/main windows/editor windows/benchmarker windows/comparator windows/validator windows/results windows/help_center
  ```

- [ ] **5.2** Move window file to view.py
  ```bash
  git mv views/main_window/main_window.py windows/main/view.py
  ```

- [ ] **5.3** Extract ViewModel from View
  ```python
  # windows/main/viewmodel.py
  class MainViewModel:
      """Pure Python ViewModel - no Qt dependencies."""
      
      def __init__(self):
          self._current_section = "home"
      
      def navigate_to_section(self, section: str):
          # Logic only, emit signal for view to handle
          self._current_section = section
  ```

- [ ] **5.4** Refactor View to use ViewModel
  ```python
  # windows/main/view.py
  class MainWindow(ContentWindowBase):
      def __init__(self, vm: MainViewModel, parent=None):
          self.vm = vm
          super().__init__(parent)
      
      def _on_section_clicked(self, section: str):
          self.vm.navigate_to_section(section)
          self._update_ui()  # Qt code only
  ```

- [ ] **5.5** Move local widgets to widgets/ subdirectory
  ```bash
  git mv views/main_window/content.py windows/main/widgets/
  git mv views/main_window/document.py windows/main/widgets/
  ```

- [ ] **5.6** Update all imports pointing to old paths
  ```bash
  # Use ruff to find and fix imports
  ruff check --fix --select I src/app/
  ```

- [ ] **5.7** Write ViewModel unit tests (pure Python)
  ```python
  # tests/unit/windows/main/test_viewmodel.py
  def test_navigate_to_section():
      vm = MainViewModel()
      vm.navigate_to_section("editor")
      assert vm._current_section == "editor"
  ```

- [ ] **5.8** Write View integration tests (pytest-qt)
  ```python
  # tests/integration/windows/main/test_view.py
  def test_main_window_opens(qtbot):
      vm = MainViewModel()
      window = MainWindow(vm)
      qtbot.addWidget(window)
      window.show()
      assert window.isVisible()
  ```

**Windows to migrate:**
1. Main (main_window)
2. Editor (code_editor)
3. Benchmarker
4. Comparator
5. Validator
6. Results
7. Help Center

#### Acceptance Criteria (per window)
- ✅ windows/<name>/{view, viewmodel}.py exist
- ✅ Local widgets moved to widgets/ subdirectory
- ✅ Old views/<name>/ directory deleted
- ✅ All imports updated and passing
- ✅ ViewModel has 100% pure Python test coverage
- ✅ View has pytest-qt smoke test

#### Risks & Mitigation
- **Risk:** Massive import churn breaks tests
  - **Mitigation:** Use ruff --fix for automated updates, verify after each window
- **Risk:** ViewModel extraction introduces bugs
  - **Mitigation:** Extract incrementally, run tests after each extraction

#### Rollback Plan
- Restore views/<name>/ from git
- Delete windows/<name>/
- Revert import changes

---

### Phase 6: Styles and Tokens (Est: 3-4 hours)

**Objective:** Move styles/constants.py to design_system/tokens.py and organize widget packages.

#### Tasks

- [ ] **6.1** Create design_system/ structure
  ```bash
  mkdir -p design_system/qss
  ```

- [ ] **6.2** Move styles/constants.py → design_system/tokens.py
  ```bash
  git mv styles/constants.py design_system/tokens.py
  ```

- [ ] **6.3** Package widgets
  ```bash
  # Example: sidebar
  mkdir -p widgets/sidebar
  git mv widgets/sidebar.py widgets/sidebar/sidebar.py
  git mv widgets/sidebar_widgets/test_count_slider.py widgets/sidebar/
  git mv widgets/sidebar_widgets/limits_input_widget.py widgets/sidebar/limits_input.py
  ```

- [ ] **6.4** Update style imports
  ```python
  # Old: from src.app.presentation.styles.constants import COLORS
  # New: from src.app.presentation.design_system.tokens import COLORS
  ```

- [ ] **6.5** Verify all QSS still applies correctly
  ```bash
  pytest tests/integration/widgets/ -v
  ```

#### Acceptance Criteria
- ✅ design_system/tokens.py exists
- ✅ All widget packages organized (sidebar/, display_area/, editor/, console/, ai_panel/, status_view/)
- ✅ All style imports updated
- ✅ UI renders identically (manual spot-check)

#### Risks & Mitigation
- **Risk:** QSS breaks due to import changes
  - **Mitigation:** Import tokens at top of style files, use automated find/replace

#### Rollback Plan
- Restore styles/constants.py
- Revert widget package structure

---

### Phase 7: Cleanup and Docs (Est: 2-3 hours)

**Objective:** Delete dead code, update documentation, finalize release.

#### Tasks

- [ ] **7.1** Delete deprecated files
  ```bash
  rm -rf services/navigation_service.py
  rm -rf views/
  rm -rf window_controller/window_management.py
  rm -rf widgets/sidebar_widgets/
  rm -rf widgets/display_area_widgets/
  ```

- [ ] **7.2** Run dead code scanner
  ```bash
  vulture src/app/presentation/ --min-confidence 80
  ```

- [ ] **7.3** Update PRESENTATION_STRUCTURE.md
  - Document new architecture
  - Update file tree
  - Add MVVM examples

- [ ] **7.4** Update README.md
  - Add architecture section
  - Document import rules
  - Add contribution guidelines

- [ ] **7.5** Final import-graph scan
  ```bash
  python scripts/check_import_rules.py --strict
  ```

- [ ] **7.6** Final duplicate symbol check
  ```bash
  pylint --disable=all --enable=duplicate-code src/app/presentation/
  ```

- [ ] **7.7** Tag release
  ```bash
  git tag -a v2.0.0-presentation-mvvm -m "MVVM presentation layer refactor"
  git push origin v2.0.0-presentation-mvvm
  ```

#### Acceptance Criteria
- ✅ Zero dead code reported (or documented as intentional)
- ✅ Import-graph checker passes with zero violations
- ✅ Documentation updated
- ✅ Release tagged

---

## Test Plan

### Unit Tests (Pure Python)

**Target Coverage:** 95%+

**Focus Areas:**
- ViewModels (all business logic)
- NavigationRouter
- StatusViewModel with presets
- DetailedResultViewModel

**Example:**
```python
# tests/unit/windows/benchmarker/test_viewmodel.py
def test_benchmarker_vm_updates_limits():
    vm = BenchmarkerViewModel()
    vm.set_time_limit(5000)
    assert vm.time_limit == 5000
```

### Integration Tests (pytest-qt)

**Target Coverage:** 80%+

**Focus Areas:**
- Window open/close
- Signal/slot connections
- Router navigation flow
- Status view rendering

**Example:**
```python
# tests/integration/windows/benchmarker/test_view.py
def test_benchmarker_window_opens(qtbot):
    vm = BenchmarkerViewModel()
    window = BenchmarkerWindow(vm)
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    assert window.isVisible()
```

### Import Graph Tests

**Automated Check:**
```python
# tests/unit/test_import_rules.py
def test_no_windows_to_windows_imports():
    """Ensure windows never import other windows."""
    violations = check_import_rules("src/app/presentation/windows")
    assert len(violations) == 0, f"Found violations: {violations}"
```

### Smoke Tests

**Manual Checklist:**
- [ ] Open each window from main window
- [ ] Run a benchmark test end-to-end
- [ ] Run a comparison test end-to-end
- [ ] Run a validation test end-to-end
- [ ] Export results to ZIP
- [ ] Open detailed results dialog
- [ ] Navigate back and forth between windows
- [ ] Open help center

---

## Tooling

### Import Analysis

```bash
# Generate import graph
python scripts/analyze_imports.py src/app/presentation > import_graph.txt

# Check for cycles
python scripts/check_import_rules.py --cycles

# Check specific rule violations
python scripts/check_import_rules.py --rule no-windows-to-windows
```

### Refactoring Scripts

```bash
# Bulk rename/move with git history preservation
python scripts/bulk_move.py --map move_map.json

# Extract ViewModel from View
python scripts/extract_viewmodel.py --view windows/main/view.py --output windows/main/viewmodel.py
```

### Code Quality

```bash
# Format all code
ruff format src/app/presentation/

# Check for violations
ruff check src/app/presentation/

# Sort imports
isort src/app/presentation/

# Check for duplicate code
pylint --disable=all --enable=duplicate-code src/app/presentation/

# Run all tests
pytest -v --cov=src/app/presentation --cov-report=html
```

### Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Architectural Rules

### Enforced by Automated Checks

1. **No window→window imports**
   ```python
   # ❌ FORBIDDEN
   from src.app.presentation.windows.main.view import MainWindow
   
   # ✅ ALLOWED
   from src.app.presentation.base.window_base import WindowBase
   from src.app.presentation.widgets.sidebar import Sidebar
   ```

2. **Windows may import:**
   - `widgets/*` ✅
   - `design_system/*` ✅
   - `base/*` ✅
   - `navigation/router` ✅
   - `dialogs/*` ✅
   - Domain services via constructor injection ✅

3. **Widgets may NOT import:**
   - `windows/*` ❌

4. **View = Qt widgets only, ViewModel = state + signals/slots + service calls, no UI code in VMs**
   ```python
   # ❌ FORBIDDEN in ViewModel
   class BadViewModel:
       def update_ui(self):
           self.label.setText("foo")  # Qt widget access
   
   # ✅ ALLOWED in ViewModel
   class GoodViewModel:
       def update_data(self):
           self._data = "foo"
           self.dataChanged.emit()  # Pure signal
   ```

5. **Status View is one implementation with presets; zero per-tool forks**

---

## Risk Register

| Risk | Probability | Impact | Mitigation | Owner |
|------|-------------|--------|------------|-------|
| **Import churn breaks tests** | HIGH | HIGH | Automated ruff --fix, incremental migration | Phase 5 Lead |
| **ViewModel extraction introduces bugs** | MEDIUM | HIGH | Extract incrementally, 100% unit test coverage | All phases |
| **Status View unification missing features** | MEDIUM | MEDIUM | Document unique features first, make presets extensible | Phase 3 Lead |
| **Router not accessible deep in widget tree** | LOW | MEDIUM | Add router property to all base classes | Phase 2 Lead |
| **CI fails due to import violations** | LOW | LOW | Make checks pass before merging | Phase 1 Lead |
| **Manual testing misses regression** | MEDIUM | MEDIUM | Comprehensive smoke test checklist | All phases |
| **Git history lost in moves** | LOW | HIGH | Use `git mv` exclusively, never copy/paste | All phases |

---

## Acceptance Criteria

### Phase 1: Prep and Guardrails
- [x] Import rule checker script exists
- [ ] CI pipeline includes import-graph assertion
- [ ] Pre-commit hooks configured
- [ ] Baseline metrics documented

### Phase 2: Navigation Singleton Removal
- [ ] navigation/router.py exists with 100% test coverage
- [ ] All 19 NavigationService call sites replaced
- [ ] services/navigation_service.py deleted
- [ ] Zero circular dependencies

### Phase 3: Status View Unification
- [ ] widgets/status_view/ has 4 files (models, view, viewmodel, presets)
- [ ] 3 per-tool status views deleted
- [ ] All 3 test tools render status view correctly
- [ ] 90%+ test coverage

### Phase 4: Results Detail Consolidation
- [ ] dialogs/result_detail/ exists
- [ ] 2 duplicate implementations deleted
- [ ] 85%+ test coverage

### Phase 5: Per-Window Packaging
- [ ] All 7 windows in windows/<name>/
- [ ] ViewModels have 100% pure Python test coverage
- [ ] Views have pytest-qt smoke tests

### Phase 6: Styles and Tokens
- [ ] design_system/tokens.py exists
- [ ] All widget packages organized

### Phase 7: Cleanup and Docs
- [ ] Zero dead code reported
- [ ] Import-graph checker passes with zero violations
- [ ] Documentation updated
- [ ] Release tagged

---

## Rollout Plan

### Branching Strategy
```
main
  └── refactor/presentation-incremental-extraction
        ├── phase-1-prep
        ├── phase-2-navigation
        ├── phase-3-status-view
        ├── phase-4-results-detail
        ├── phase-5-per-window
        ├── phase-6-styles
        └── phase-7-cleanup
```

### PR Strategy
- **One PR per phase**
- Each PR must:
  - Pass all tests
  - Pass import-graph check
  - Have code review approval
  - Include updated documentation

### Merge Criteria
- ✅ All tests pass
- ✅ Import rules pass
- ✅ Code review approved
- ✅ No merge conflicts
- ✅ Documentation updated

### Deployment
- Merge each phase to main after approval
- Tag milestones: `v2.0.0-alpha.1`, `v2.0.0-alpha.2`, etc.
- Final release: `v2.0.0-presentation-mvvm`

---

## Appendix

### Glossary

- **MVVM:** Model-View-ViewModel architectural pattern
- **Router:** Injectable navigation coordinator replacing singleton
- **Preset:** Configuration object for Status View per tool
- **Import Graph:** Directed graph of module dependencies
- **Circular Dependency:** Cycle in import graph (A→B→A)

### References

- [MVVM Pattern](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93viewmodel)
- [Dependency Injection](https://en.wikipedia.org/wiki/Dependency_injection)
- [Qt Signal/Slot](https://doc.qt.io/qt-6/signalsandslots.html)
- [pytest-qt](https://pytest-qt.readthedocs.io/)

### Contact

- **Project Lead:** @rayatchowdhury
- **Architecture Review:** TBD
- **Questions:** Open GitHub issue with `[presentation-refactor]` tag

---

**END OF PLAYBOOK**
