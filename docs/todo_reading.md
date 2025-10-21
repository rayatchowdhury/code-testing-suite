# Migration Reading Plan - Presentation Layer Refactor

## Objective
Systematically discover and analyze the current presentation layer to plan the migration to Feature-local MVVM structure.

## Reading Checklist

### Phase 1: Target Structure Analysis
- [x] Load new_presentation.txt and render desired tree
- [x] Document target structure in migration_playbook.md

### Phase 2: Current State Discovery
- [x] Enumerate all files under src/app/presentation with glob **/*.py (104 files)
- [x] Enumerate all .qss files (styles) (0 found - styles in Python)
- [x] Enumerate all asset files (icons, images) (1 font file)
- [x] Count files per current subdirectory (10 top-level dirs)

### Phase 3: Legacy Location Detection
- [x] Detect legacy locations in window_controller/** (3 files)
- [x] Detect legacy styles in styles/** (36 files)
- [x] Detect styles scattered under widgets/** (1 file)
- [x] Detect styles scattered under windows/** (0 files)
- [x] Detect styles scattered under shared/** (0 files)

### Phase 4: Import Graph Construction
- [x] Build import graph (module → imports) using ast (392 total imports)
- [x] Export import graph as JSON
- [x] Identify circular import risks (none detected)
- [x] Map external dependencies (PySide6, domain, etc.)

### Phase 5: Symbol Extraction
- [x] Extract class definitions and their locations (48 widgets)
- [x] Extract Signal definitions
- [x] Extract Slot definitions (methods with @Slot decorator)
- [x] Map widget inheritance hierarchy

### Phase 6: Widget Classification
- [x] Identify strictly shared widgets (used by ≥2 features) (38 widgets)
  - editor components
  - console components
  - status_view
  - sidebar
  - layout helpers
- [x] Identify feature-local widgets (used by only one window) (10 widgets)
- [x] Mark feature-local widgets for move into windows/<feature>/widgets

### Phase 7: Style Analysis
- [x] Find all .qss file imports (0 QSS files, 36 Python style files)
- [x] Find inline style strings (23 files using setStyleSheet)
- [x] Map current style imports to design_system.styles.* targets (32 files)
- [x] Identify style token usage

### Phase 8: Navigation Analysis
- [x] Gather references to NavigationService
- [x] Gather references to WindowManager
- [x] Gather references to Factory patterns
- [x] Plan move to navigation/ folder

### Phase 9: Move Planning
- [x] Emit preliminary rename_map.csv with columns:
  - src_path: current file path
  - dst_path: target file path
  - reason: why this move
  - phase: P1 (styles), P2 (navigation), P3 (feature pods), P4 (cleanup)
- [x] Tag moves by risk level (low/medium/high) (50 total moves)

### Phase 10: Impact Analysis
- [x] Diff predicted imports before/after
- [x] List import break risks
- [x] Identify potential circular imports (none found)
- [x] Map signals/slots that cross feature boundaries

### Phase 11: Backout Planning
- [x] Confirm backout steps per phase
- [x] Document rollback commands in migration_playbook.md
- [x] Identify validation points in validation_checklist.md

## Execution Status
- Status: ✅ COMPLETE
- Last Updated: 2025-10-21
- All discovery scripts executed successfully
- Migration playbook and supporting files created

## Notes
- All scripts must be Windows-compatible Python
- No bash scripts allowed
- Use pathlib for path operations
- Test each phase independently
