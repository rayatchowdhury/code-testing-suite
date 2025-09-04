# V2 Structure Proposal

## Structure Overview

A modular, layered package with clear boundaries between UI, services (business/process logic), and core (config/paths/models). This reduces circular imports, isolates Qt from headless logic, and simplifies testing.

```
app/
  __init__.py
  main.py                    # Qt + qasync bootstrap; minimal wiring only
  core/                      # App-wide foundations (no Qt imports)
    __init__.py
    paths.py                 # Project/user-data paths, resource locators
    config.py                # Config models + load/save/validation (moved from views/config)
    logging.py               # absl/Qt logging init & levels
    constants/
      __init__.py
      colors.py              # Theming constants (moved from styles.constants)
    models/
      __init__.py
      settings.py            # Dataclasses for config/editor/ai settings
  services/                  # Headless capabilities (no QWidget here)
    __init__.py
    files/
      ops.py                 # FileOperations (split UI dialogs into UI layer)
    compilers/
      __init__.py
      process.py             # QProcess/subprocess wrappers and safety
      languages/
        cpp.py               # Compile/run C++ (g++)
        python.py            # Run Python script
        java.py              # Run Java with class validation
      runner.py              # Orchestrates by file type; emits structured events
      stress.py              # Compile chain + stress execution worker
      tle.py                 # Compile chain + TLE worker
    ai/
      __init__.py
      editor_ai.py           # EditorAI, API config, prompts; async-safe
      config.py              # AI-specific config accessors
    workspace/
      __init__.py
      state.py               # Editor session persistence (open files, etc.)
  ui/                        # All Qt widgets, windows, styles, and web assets
    __init__.py
    app_window.py            # MainWindow (host WindowManager as central widget)
    base/
      window_base.py         # SidebarWindowBase
      window_manager.py      # Stacked manager + history
      window_factory.py      # Registry-based lazy window creation
    windows/
      main/
        __init__.py
        main_window.py       # MainWindowContent (webview landing)
        main_window.html
      code_editor/
        __init__.py
        window.py            # CodeEditorWindow
        display.py           # CodeEditorDisplay
        welcome.html
      stress_tester/
        __init__.py
        window.py            # StressTesterWindow
        display.py
        status_compilation.py
        status_progress.py
      tle_tester/
        __init__.py
        window.py            # TLETesterWindow
        display.py
        status_progress.py
      help_center/
        __init__.py
        window.py
        content/             # Static help files
    widgets/
      __init__.py
      sidebar/
        sidebar.py
      display/
        area.py
      editor/
        editor.py            # CodeEditor, LineNumberArea
        syntax.py            # Syntax highlighters
        ai_panel.py
        console.py
    styles/
      __init__.py
      global.py              # DISPLAY_AREA_STYLE, WEBVIEW_STYLE, shared
      components/            # Existing component styles (flatten duplicates)
      themes/
        material.py          # MATERIAL_COLORS
    assets/
      icons/
      html/
    web/
      html.css               # Shared webview CSS
  resources/                 # Static media kept for packaging (if needed)
  tests/
    unit/
    ui/                      # Optional Qt widget tests via CI screenshots
```

Rationales:
- Headless logic lives in services/ (compilers, stress/tle, files, AI) to avoid Qt coupling and enable testing.
- UI imports services, not vice versa. core/ is shared, stable, with no Qt.
- Flatten styles and widgets to remove duplication (styles/components vs styles/constants vs widgets/display_area_widgets).
- Windows under ui/windows/<feature> to group window + display + status UIs.
- One consistent entry in app/main.py; top-level main.py can import and call app.main.

## Module Organization

- core: paths, config, logging, models. Single source of truth for USER_DATA_DIR, WORKSPACE_DIR, and config schemas.
- services.files.ops: Pure file IO; UI dialogs (QFileDialog/QMessageBox) are moved to UI adapters.
- services.compilers: Language-specific compile/run adapters exposed via runner.py; shared process safety in process.py; stress.py and tle.py orchestrate multi-step workflows.
- services.ai: EditorAI and AI config split; async-only boundary with clear error strings; no Qt.
- services.workspace.state: Load/save editor session; JSON format and future migrations.
- ui.base: Window base, manager, and factory remain but import services instead of tools/utils.
- ui.widgets: Editor, console, ai_panel, sidebar, display area. Editor is split into editor.py (widget) and syntax.py (highlighters).
- ui.windows: Each feature is self-contained and uses services.*; only UI code here.
- ui.styles: Global + components; consolidate constants and remove duplicated modules.

## Dependency Strategy

- Allowed imports (arrows show dependency direction):
  - ui -> services -> core
  - ui -> core
  - services -> core
  - core: no imports from ui/services
- Avoid ui importing ui across features except via base/ and widgets/.
- Absolute imports from the app package: `from app.services.compilers import runner`.
- Signals/slots are the UI boundary; services surface Python callbacks or Qt-neutral events. UI layer adapts those to Qt signals.
- External deps:
  - PySide6 and qasync used only in ui and app/main.py.
  - google-generativeai isolated within services.ai.editor_ai.
  - subprocess/QProcess use wrappers in services.compilers.process.

## Benefits

- Testability: services are Qt-free; unit tests run without a QApplication.
- Maintainability: Clear layering removes circular import risks; WindowFactory remains but registry lives in ui.base.
- Reuse: compilers/stress/tle share a process layer and event types; less duplication.
- Performance: Lazy imports preserved (AI, syntax); faster startup.
- Portability: Centralized toolchain detection; Windows flags isolated; easier future Linux/macOS support.
- Developer Experience: Consistent absolute imports, predictable file locations, smaller modules.

## File Organization Rules

- Naming: modules are snake_case; classes in PascalCase; signals in past tense (finished, output_available).
- Locations:
  - Headless logic in services/ only. No QMessageBox/QFileDialog beyond ui/.
  - All widgets under ui/widgets; feature windows under ui/windows/<feature>/.
  - Styles in ui/styles; themes/colors in ui/styles/themes.
  - HTML/assets in ui/assets or ui/windows/<feature>/.
- Imports: use `from app...` absolute paths. No relative imports that jump folders.
- Config & State:
  - Define dataclasses in core.models; read/write via core.config and services.workspace.state.
  - Keep JSON schemas backward-compatible; version in file.
- Processes: use services.compilers.process for QProcess/subprocess; never start processes in widgets directly.
- AI:
  - All AI calls async; UI uses adapters to show progress and errors.
  - Safety settings and prompts live in services.ai; no duplication in widgets.
- Testing:
  - Unit tests for services; light UI tests for signal wiring.
- Lint/Type:
  - Enforce `ruff/black` and optional `mypy` later; keep runtime clean of type-only imports.
