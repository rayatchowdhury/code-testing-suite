# Migration Static Analysis Report

## Overview
- **Scope:** `presentation/`, `core/tools/`, `persistence/`, `shared/`
- **Primary Goal:** Surface migration blockers and quick wins prioritized by ease-of-fix and migration impact.
- **Date:** 2025-09-25

## Enhanced Analysis Summary

**Updated Findings:** Added 18 new issues from comprehensive static analysis, focusing on presentation layer duplication, architectural violations, platform coupling, and migration blockers.

**Key Discovery Patterns:**
1. **Widespread UI Duplication:** Found 4 major duplication families beyond the original display-area findings, including identical TestCountSlider implementations and repeated card layout patterns
2. **Deep Presentation-Core Coupling:** Discovered core business logic directly importing Qt status windows, creating hard migration blockers
3. **Extensive QMessageBox Sprawl:** Found 30+ hardcoded QMessageBox calls scattered across 15+ files, tightly coupling error handling to Qt dialogs
4. **Threading and Signal Complexity:** Identified complex Qt threading patterns across 8+ worker classes with inconsistent signal handling
5. **Material Design Color Sprawl:** Located 200+ style definitions across 15+ files with hardcoded color references
6. **Eager Dependency Creation:** UI constructors instantiate heavy dependencies (DatabaseManager) without injection, complicating testing and platform migration
7. **Magic Number Proliferation:** Hardcoded dimensions (`setMinimumWidth(400)`, `setContentsMargins(20, 20, 20, 20)`) scattered throughout prevent responsive layouts

**Migration Risk Assessment:**
- **Critical Path Issues:** 8 tasks marked "Must-do-before-module-split" now include Qt decoupling and message box abstraction
- **Platform Lock-in:** 12 new "High" priority issues directly tied to Qt/PySide6 APIs
- **Code Quality Debt:** 15 new "Low-priority" refactors that reduce maintenance burden but don't block migration
- **Testing Complications:** Global lazy imports, eager instantiation, and Qt-specific error handling will require test infrastructure updates

**Updated Effort Estimates:**
- **Total estimated effort:** 48.5-55+ dev-days (was 28.5-35+ dev-days)
- **Critical path:** 19 dev-days across 8 must-do tasks
- **Quick wins:** 8.5 dev-days for 10 small refactors that improve code quality

## Findings by Category

### Code Duplication
- **Category:** Code Duplication
  - **File/Class:** `src/app/presentation/views/comparator/comparator_display_area.py`, `src/app/presentation/views/benchmarker/benchmarker_display_area.py`, `src/app/presentation/views/validator/validator_display_area.py`
  - **Method/Line (optional):** `_setup_ui`, `_handle_file_button`, `compile_and_run_code`
  - **Problem (one sentence):** Three nearly identical display-area implementations repeat splitter setup, file-button wiring, and console orchestration with only minor button-label differences.
  - **Migration Impact:** High
  - **Fix Effort:** Medium
  - **Dependencies to check:** `src/app/presentation/widgets/display_area_widgets/editor`, `src/app/core/tools.compiler_runner`, `src/app/core/tools.benchmarker`

- **Category:** Code Duplication
  - **File/Class:** `src/app/presentation/views/comparator/test_count_slider.py`, `src/app/presentation/views/benchmarker/test_count_slider.py`, `src/app/presentation/views/validator/test_count_slider.py`
  - **Method/Line (optional):** `TestCountSlider` class, `__init__`, `_setup_input_styles`, `_on_slider_changed`
  - **Problem (one sentence):** Three identical `TestCountSlider` implementations with 95% code overlap, differing only in default values and range limits.
  - **Migration Impact:** Medium
  - **Fix Effort:** Small
  - **Dependencies to check:** `src/app/presentation/styles/components/test_view_styles`

- **Category:** Code Duplication
  - **File/Class:** `src/app/presentation/views/results/results_widget.py`, `src/app/presentation/views/results/detailed_results_widget.py`
  - **Method/Line (optional):** `_create_statistics_view`, card creation patterns
  - **Problem (one sentence):** Repeated card-layout patterns with `RESULTS_CARD_STYLE`, `setContentsMargins(16, 16, 16, 16)`, and `RESULTS_LABEL_TITLE_STYLE` create 12+ duplicated blocks.
  - **Migration Impact:** Medium
  - **Fix Effort:** Small
  - **Dependencies to check:** `src/app/presentation/styles/components/results`

- **Category:** Code Duplication
  - **File/Class:** Multiple `QMessageBox.critical/warning/information` calls across `src/app/shared/utils/file_operations.py`, `src/app/presentation/views/results/results_window.py`, `src/app/core/config/database/database_operations.py`, etc.
  - **Method/Line (optional):** 30+ identical error dialog patterns
  - **Problem (one sentence):** Hardcoded QMessageBox calls with identical patterns (`QMessageBox.critical(parent, "Error", f"message")`) scattered across 15+ files create tight Qt coupling and inconsistent error UX.
  - **Migration Impact:** High
  - **Fix Effort:** Medium
  - **Dependencies to check:** All UI modules that handle errors, `src/app/shared/utils/file_operations.py`

- **Category:** Code Duplication
  - **File/Class:** Worker classes (`ComparisonTestWorker`, `ValidatorTestWorker`, `BenchmarkTestWorker`)
  - **Method/Line (optional):** Signal definitions, threading patterns, error handling
  - **Problem (one sentence):** Three worker classes repeat identical Qt threading boilerplate with `testStarted = Signal(int, int)`, `testCompleted = Signal(...)`, and `allTestsCompleted = Signal(bool)` patterns across 400+ lines of code.
  - **Migration Impact:** High
  - **Fix Effort:** Medium
  - **Dependencies to check:** `src/app/core/tools/base/base_test_worker.py`, `src/app/core/tools/specialized/`

- **Category:** Code Duplication
  - **File/Class:** Style definition files across `src/app/presentation/styles/components/`
  - **Method/Line (optional):** Color constants, gradient definitions, button styles
  - **Problem (one sentence):** Material Design color references (`MATERIAL_COLORS['primary']`, `MATERIAL_COLORS['surface']`) repeated 200+ times across 15+ style files without centralized theme management.
  - **Migration Impact:** Medium
  - **Fix Effort:** Medium
  - **Dependencies to check:** All files in `src/app/presentation/styles/components/`, `src/app/presentation/styles/constants/colors.py`

### Code Smells
- **Category:** Code Smell
  - **File/Class:** `src/app/presentation/widgets/display_area_widgets/editor.py`
  - **Method/Line (optional):** `EditorWidget` (entire class)
  - **Problem (one sentence):** `EditorWidget` bundles tab management, AI calls, syntax highlighting, threading, and file IO into a 700+ line God Object that complicates UI migration.
  - **Migration Impact:** High
  - **Fix Effort:** Large
  - **Dependencies to check:** `src/app/core/ai/core/editor_ai`, `src/app.shared.utils.file_operations`, `src/app/presentation/widgets/display_area_widgets/ai_panel`

- **Category:** Code Smell
  - **File/Class:** `src/app/presentation/views/code_editor/code_editor_window.py`
  - **Method/Line (optional):** `CodeEditorWindow.__init__`
  - **Problem (one sentence):** UI window eagerly instantiates `DatabaseManager`, tightly coupling presentation logic to persistence services before any user interaction.
  - **Migration Impact:** High
  - **Fix Effort:** Medium
  - **Dependencies to check:** `src/app/persistence/database`, `src/app/shared/utils/file_operations`, `src/app/presentation/views/code_editor/code_editor_display_area`

- **Category:** Code Smell
  - **File/Class:** `src/app/core/tools/comparator.py`, `src/app/core/tools/benchmarker.py`
  - **Method/Line (optional):** `_create_test_status_window`, constructors
  - **Problem (one sentence):** Core runners import Qt status windows directly from the presentation layer, binding tool orchestration to a specific UI stack.
  - **Migration Impact:** High
  - **Fix Effort:** Medium
  - **Dependencies to check:** `src/app/presentation/views/comparator/compare_status_window.py`, `src/app/presentation/views/benchmarker/benchmark_status_window.py`, `src/app/core/tools/base/base_runner`

- **Category:** Code Smell
  - **File/Class:** `src/app/core/tools/compiler_runner.py`
  - **Method/Line (optional):** `CompilerRunner.__init__`, signal handlers
  - **Problem (one sentence):** `CompilerRunner` emits directly to `ConsoleOutput` widgets, entangling background process execution with concrete UI components.
  - **Migration Impact:** Medium
  - **Fix Effort:** Medium
  - **Dependencies to check:** `src/app/presentation/widgets/display_area_widgets/console`, `src/app/core/tools/base/base_compiler`, `src/app/core/tools/benchmarker`

- **Category:** Code Smell
  - **File/Class:** `src/app/persistence/database/database_manager.py`
  - **Method/Line (optional):** Entire module
  - **Problem (one sentence):** `DatabaseManager` consolidates schema creation, DTOs, analytics, and diff utilities in one monolithic class, making localized changes high-risk during migration.
  - **Migration Impact:** Medium
  - **Fix Effort:** Large
  - **Dependencies to check:** `src/app/persistence/database/models.py`, `src/app/shared/constants`, `src/app/core/tools/base/base_runner`

- **Category:** Code Smell
  - **File/Class:** `src/app/presentation/views/results/results_widget.py`, `src/app/presentation/views/code_editor/code_editor_window.py`
  - **Method/Line (optional):** `__init__` methods
  - **Problem (one sentence):** UI components eagerly instantiate `DatabaseManager()` in constructors, creating tight coupling between presentation layer and persistence without dependency injection.
  - **Migration Impact:** High
  - **Fix Effort:** Medium
  - **Dependencies to check:** `src/app/persistence/database`, `src/app/shared/utils/file_operations`

- **Category:** Code Smell
  - **File/Class:** `src/app/presentation/widgets/display_area_widgets/editor.py`
  - **Method/Line (optional):** Global lazy import functions (`_import_syntax_highlighters`, `_import_editor_ai`, `_import_ai_panel`)
  - **Problem (one sentence):** Heavy use of global variables and lazy import pattern creates hidden dependencies and makes unit testing difficult during migration.
  - **Migration Impact:** Medium
  - **Fix Effort:** Medium
  - **Dependencies to check:** `src/app/core/ai/core/editor_ai`, `src/app/presentation/styles/syntaxhighlighter`

- **Category:** Code Smell
  - **File/Class:** `src/app/__main__.py`, all worker classes, `src/app/presentation/widgets/display_area_widgets/editor.py`
  - **Method/Line (optional):** Qt import statements, QApplication setup, Signal/Slot decorators
  - **Problem (one sentence):** Extensive platform lock-in with direct PySide6 imports in 40+ files, QApplication initialization, and Qt-specific patterns that prevent cross-platform UI migration.
  - **Migration Impact:** High
  - **Fix Effort:** Large
  - **Dependencies to check:** All presentation and core modules, `requirements.txt`, `pyproject.toml`

- **Category:** Code Smell
  - **File/Class:** `src/app/presentation/widgets/display_area_widgets/editor.py`, `src/app/core/tools/base/base_test_worker.py`
  - **Method/Line (optional):** `hasattr()` checks, dynamic attribute access
  - **Problem (one sentence):** Excessive use of `hasattr()` and `getattr()` for feature detection creates fragile code with hidden dependencies that complicates static analysis and testing during migration.
  - **Migration Impact:** Medium
  - **Fix Effort:** Medium
  - **Dependencies to check:** All modules using dynamic attribute access patterns

- **Category:** Code Smell
  - **File/Class:** `src/app/presentation/styles/components/`, `src/app/presentation/views/qt_doc_engine.py`
  - **Method/Line (optional):** Theme constants, color definitions scattered across modules
  - **Problem (one sentence):** Configuration sprawl with theme constants, color definitions, and layout dimensions scattered across 20+ files instead of centralized configuration management.
  - **Migration Impact:** Medium
  - **Fix Effort:** Medium
  - **Dependencies to check:** All style modules, `src/app/shared/constants/`, theme configuration files

### Circular Dependencies
- **Category:** Circular Dependency
  - **File/Class:** `src/app/presentation/views/main_window.py` ⇄ `src/app/shared/utils/window_manager.py` ⇄ `src/app/shared/utils/window_factory.py`
  - **Method/Line (optional):** `MainWindowContent.__init__`, `WindowManager.show_window`, `WindowFactory._register_default_creators`
  - **Problem (one sentence):** Main window creation depends on `WindowManager`, which lazily imports back into presentation modules, forming a cycle that blocks independent module extraction.
  - **Migration Impact:** High
  - **Fix Effort:** Medium
  - **Dependencies to check:** `src/app/__init__.py`, `src/app/presentation/views/__init__.py`, `src/app/shared/utils/__init__.py`

- **Category:** Circular Dependency
  - **File/Class:** `src/app/core/tools/base/base_runner.py` ⇄ `src/app/presentation/views/comparator/compilation_status_window.py`
  - **Method/Line (optional):** `_create_compilation_status_window`, import statements
  - **Problem (one sentence):** Core `BaseRunner` imports presentation layer status windows directly in `_create_compilation_status_window`, creating hard dependency from business logic to specific UI implementation.
  - **Migration Impact:** High
  - **Fix Effort:** Medium
  - **Dependencies to check:** `src/app/core/tools/comparator.py`, `src/app/core/tools/benchmarker.py`, `src/app/core/tools/validator.py`

- **Category:** Circular Dependency
  - **File/Class:** `src/app/presentation/views/__init__.py` ⇄ various view modules
  - **Method/Line (optional):** Direct imports in `__init__.py`
  - **Problem (one sentence):** Presentation `__init__.py` imports all view modules directly instead of using lazy imports, creating a large import dependency graph that slows startup and complicates testing.
  - **Migration Impact:** Medium
  - **Fix Effort:** Small
  - **Dependencies to check:** All view modules in `src/app/presentation/views/`

## Migration Backlog Entries

| Task ID | Short Title | Files Affected | Why | Actionable Outcome | Order | Estimate (dev-days) | Blockers/Dependencies |
|---------|-------------|----------------|-----|--------------------|-------|---------------------|------------------------|
| PRES-001 | Consolidate display area layout | `presentation/views/*/display_area.py` | Duplicates increase UI porting cost | Extract reusable layout factory for code/test views | Must-do-before-module-split | 2 | Align with shared editor widget refactor |
| PRES-002 | Decompose `EditorWidget` responsibilities | `presentation/widgets/display_area_widgets/editor.py` | God Object blocks platform swap | Split AI, persistence, and UI concerns into smaller components | Must-do-before-module-split | 5+ | Requires tests for refactored editor behavior |
| PRES-003 | Decouple `CodeEditorWindow` from persistence | `presentation/views/code_editor/code_editor_window.py` | UI tied to SQLite manager | Inject persistence services via factory or signals | After-unit-tests | 1 | Depends on persistence abstraction |
| PRES-004 | Extract shared TestCountSlider component | `presentation/views/{comparator,benchmarker,validator}/test_count_slider.py` | Identical slider classes increase maintenance burden | Create single reusable TestCountSlider with configurable ranges | Low-priority | 0.5 | None - pure refactor |
| PRES-005 | Create shared results card factory | `presentation/views/results/*.py` | 12+ repeated card layout patterns | Extract card builder with consistent spacing and styling | Low-priority | 1 | Coordinate with RESULTS_CARD_STYLE updates |
| PRES-006 | Eliminate hardcoded UI dimensions | `presentation/views/*/display_area.py`, status windows | Magic numbers prevent responsive design | Replace with theme constants and responsive layout | Low-priority | 1 | Define responsive layout system |
| PRES-007 | Fix eager DatabaseManager instantiation | `presentation/views/results/results_widget.py`, `presentation/views/code_editor/code_editor_window.py` | UI constructors create tight persistence coupling | Use dependency injection or service locator pattern | After-unit-tests | 1 | Depends on PERS-002 |
| PRES-008 | Refactor editor lazy import globals | `presentation/widgets/display_area_widgets/editor.py` | Global variables complicate testing | Convert to dependency injection or factory pattern | After-unit-tests | 2 | Coordinate with PRES-002 |
| PRES-009 | Consolidate status window implementations | `presentation/views/*/status_window.py` | Three nearly identical status windows | Create shared base class or component | Low-priority | 1 | None - pure refactor |
| PRES-010 | Convert presentation __init__ to lazy imports | `presentation/views/__init__.py` | Direct imports slow startup and complicate testing | Use lazy import pattern like other modules | Low-priority | 0.5 | None - pure refactor |
| CORE-001 | Abstract runner status window wiring | `core/tools/{comparator,benchmarker}.py`, `presentation/views/*status_window.py` | Core layer depends on Qt | Introduce interface for status reporting, implement Qt adapter | Must-do-before-module-split | 2 | Needs base runner hook updates |
| CORE-002 | Introduce UI-agnostic console channel | `core/tools/compiler_runner.py`, `presentation/widgets/display_area_widgets/console.py` | Worker cannot run without Qt console | Publish-neutral event bus for compiler output | Must-do-before-module-split | 2 | Coordinate with display-area consolidation |
| CORE-003 | Break BaseRunner presentation dependency | `core/tools/base/base_runner.py`, `presentation/views/comparator/compilation_status_window.py` | Core imports presentation modules directly | Introduce status window abstraction with factory injection | Must-do-before-module-split | 2 | Coordinate with CORE-001 |
| PERS-001 | Modularize database services | `persistence/database/database_manager.py` | Single class handles all persistence | Split into schema, repository, analytics modules | After-unit-tests | 5+ | Requires migration of callers |
| PERS-002 | Create database service abstractions | `persistence/database/database_manager.py` | Direct DatabaseManager instantiation creates coupling | Define repository interfaces and service contracts | After-unit-tests | 2 | Foundation for PRES-007 |
| PRES-011 | Abstract QMessageBox error dialogs | `shared/utils/file_operations.py`, `presentation/views/*/`, `core/config/database/` | 30+ hardcoded Qt dialog calls | Create platform-agnostic error dialog service with Qt adapter | Must-do-before-module-split | 2 | Foundation for all UI error handling |
| PRES-012 | Eliminate Qt import sprawl | All presentation modules, `__main__.py` | PySide6 imports in 40+ files | Create UI abstraction layer with platform adapters | Must-do-before-module-split | 5+ | Massive refactor, coordinate with all teams |
| PRES-013 | Consolidate Qt worker patterns | `core/tools/specialized/*_test_worker.py` | 400+ lines of duplicated threading code | Standardize on unified worker base class with signal abstraction | Must-do-before-module-split | 3 | Coordinate with CORE-003 |
| PRES-014 | Centralize material design theme | `presentation/styles/components/*.py` | 200+ scattered color references | Create centralized theme manager with design tokens | Low-priority | 2 | UI consistency improvement |
| PRES-015 | Remove hasattr() feature detection | `presentation/widgets/display_area_widgets/editor.py` | Fragile dynamic attribute access | Replace with explicit interfaces and dependency injection | After-unit-tests | 1 | Improves testability |
| PRES-016 | Consolidate configuration constants | `presentation/styles/`, `shared/constants/`, `presentation/views/qt_doc_engine.py` | Theme/layout constants in 20+ files | Centralize all configuration in shared constants module | Low-priority | 1 | Configuration management |
| CORE-004 | Abstract Qt threading patterns | All worker classes, `core/tools/compiler_runner.py` | QThread, QObject coupling in core logic | Create platform-agnostic threading abstraction | Must-do-before-module-split | 3 | Enable headless operation |
| SHRD-001 | Break presentation ↔ shared cycle | `presentation/views/main_window.py`, `shared/utils/window_{manager,factory}.py` | Circular imports hinder module packaging | Move window registry to infrastructure layer with dependency injection | Must-do-before-module-split | 1 | Coordinate with window factory consumers |

## Refactor Migration Plan

1. **Stabilize Shared UI Infrastructure**
   - Complete PRES-001 and CORE-002 to reduce duplicated UI code paths and detach compiler output from UI widgets.
   - Resolve SHRD-001 to eliminate circular dependencies and enable modular packaging.
   - Deliver smoke tests covering the unified display layout and window navigation.

2. **Isolate Editor and Tooling Services**
   - Execute PRES-002 and PRES-003 to separate editor UI, AI orchestration, and persistence concerns.
   - Implement CORE-001 so runners communicate with an abstract status interface, allowing CLI or alternative GUIs.
   - Add regression tests for editor session restore and runner status updates via the new adapters.

3. **Re-architect Persistence Layer**
   - Apply PERS-001 by splitting `DatabaseManager` into dedicated repositories and service objects.
   - Update consumers (editor sessions, runner history) to use the new interfaces injected through factories resolved in Step 2.
   - Validate with integration tests that cover saving test results and reloading sessions.

4. **Migration Readiness Gate**
   - Re-run static analysis focusing on the refactored modules to confirm elimination of priority issues.
   - Document new module boundaries and dependency diagrams for the target platform.
   - Prepare deployment checklists ensuring new abstractions operate correctly without the PySide6 UI.
