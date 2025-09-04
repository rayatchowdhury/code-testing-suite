# Migration Strategy

## Migration Approach

Incremental, in-place refactor with adapter shims. We keep main features working at all times by:
- Creating new app/ package alongside current modules
- Moving headless logic first (easy wins), keeping thin compatibility wrappers
- Redirecting UI imports to new services/core in small PRs
- Deleting old modules once mapped and covered by smoke tests

## Phase Breakdown

1) Bootstrap (0.5 day)
- Add `app/` package skeleton (dirs only) and `app/main.py` that bootstraps Qt and loads current MainWindow.
- Add core.paths with current constants; add core.logging to standardize absl init.
- Wire top-level `main.py` to import `app.main:main()`; keep behavior identical.

2) Core consolidation (1 day)
- Move `constants/paths.py` -> `app/core/paths.py` and update imports via a temporary `constants/__init__.py` shim that re-exports from `app.core.paths`.
- Create `app/core/models/settings.py` dataclasses for config/editor/ai; add `app/core/config.py` to own load/save/validate logic (move from `views/config/config_manager.py`).
- Keep `views/config/config_manager.py` as a UI-only adapter that calls into `app.core.config` (thin wrapper), then remove after callers are updated.

3) Services extraction (2 days)
- Create `app/services/files/ops.py` with pure IO from `utils/file_operations.py` (no dialogs). Update UI to use a new adapter `ui/widgets/file_dialogs.py` for dialogs.
- Move compiler logic:
  - `tools/compiler_runner.py` -> `app/services/compilers/runner.py` (+ split languages into cpp.py, python.py, java.py, process.py)
  - `tools/stress_compiler_runner.py` -> folded into process + runner (threaded orchestration)
  - `tools/stresser.py` -> `app/services/compilers/stress.py`
  - `tools/tle_compiler_runner.py`, `tools/tle_runner.py` -> `app/services/compilers/tle.py`
- Extract AI: `tools/editor_ai.py` -> `app/services/ai/editor_ai.py`; use `app/core/config.py` for API key.

4) UI rewire (1.5 days)
- Move `utils/window_manager.py` -> `app/ui/base/window_manager.py` and `utils/window_factory.py` -> `app/ui/base/window_factory.py`.
- Move windows and displays under `app/ui/windows/...` preserving names. Adjust imports to new absolute paths (`from app.services...`).
- Consolidate widgets under `app/ui/widgets/...` and update imports.
- Consolidate styles under `app/ui/styles/...`; replace scattered constants with a single `themes/material.py` + `global.py`.

5) State & workspace (0.5 day)
- Move editor session persistence into `app/services/workspace/state.py`. Replace direct file writes in `CodeEditorWindow` with calls to this service.

6) Cleanup and removal (0.5 day)
- Remove old `tools/`, `utils/`, and redundant `styles/` subpackages once all imports point to `app/...`.
- Delete re-export shims.

## File Mapping (examples)

- constants/paths.py → app/core/paths.py
- utils/file_operations.py (IO-only parts) → app/services/files/ops.py
- tools/compiler_runner.py → app/services/compilers/runner.py (+ languages/cpp.py, python.py, java.py)
- tools/stress_compiler_runner.py → app/services/compilers/runner.py (threaded path) or services/compilers/stress.py
- tools/stresser.py → app/services/compilers/stress.py
- tools/tle_compiler_runner.py → app/services/compilers/tle.py
- tools/tle_runner.py → app/services/compilers/tle.py
- views/config/config_manager.py → app/core/config.py (logic) and ui adapter
- views/base_window.py → app/ui/base/window_base.py
- utils/window_manager.py → app/ui/base/window_manager.py
- utils/window_factory.py → app/ui/base/window_factory.py
- views/main_window.py → app/ui/windows/main/main_window.py
- views/code_editor/code_editor_window.py → app/ui/windows/code_editor/window.py
- views/code_editor/code_editor_display_area.py → app/ui/windows/code_editor/display.py
- widgets/display_area_widgets/editor.py → app/ui/widgets/editor/editor.py
- widgets/display_area_widgets/ai_panel.py → app/ui/widgets/editor/ai_panel.py
- widgets/display_area_widgets/console.py → app/ui/widgets/editor/console.py

## Risk Mitigation

- Shims: keep old module paths that re-export new implementations while refactoring incrementally.
- Tests: add lightweight unit tests for services (compilers, file ops, config) and a smoke test that instantiates `MainWindow`.
- Backups: preserve user config/state; version config schema, migrate on load with fallback defaults.
- Tooling detection: centralize g++/java/python detection; show actionable error messages if missing.
- Rollback: because changes are staged by package, we can revert a phase without breaking others; keep PRs small.

## Timeline Estimation

- Week 1: Phases 1–3 (core + services extraction). 3–4 dev-days.
- Week 2: Phases 4–6 (UI rewire, state, cleanup), 3–4 dev-days, including review and fixes.
- Total: ~6–8 dev-days for a single dev; parallelizable by area (services vs UI).

## Team Coordination

- Branching: feature branches per phase; CI runs unit tests + flake8/black; optional Qt smoke test on Windows runner.
- Ownership: assign one owner for services, one for UI migration; agree on public service APIs first.
- Review gates: no UI imports inside services/core; absolute imports only (`from app...`).
- Communication: maintain a living checklist mapping old → new modules and current status; update daily.
- Freeze windows: avoid new features during migration; bug fixes forward-ported to V2 paths.
