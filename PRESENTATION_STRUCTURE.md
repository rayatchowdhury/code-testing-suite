# Presentation Layer Structure

## Overview
The presentation layer implements the GUI for the Code Testing Suite application using PySide6 (Qt). It follows a modular architecture with clear separation between views, widgets, services, and base classes.

## Directory Structure

```
src/app/presentation/
├── __init__.py                          # Module initialization
│
├── base/                                # Base classes and protocols
│   ├── __init__.py
│   ├── protocols.py                     # Protocol definitions for window interfaces
│   ├── window_base.py                   # Base window class with common functionality
│   ├── content_window_base.py           # Base for content windows with splitter support
│   └── test_window_base.py              # Base for test tool windows (shared test lifecycle)
│
├── services/                            # Business logic services
│   ├── __init__.py
│   ├── navigation_service.py            # Window navigation and routing
│   └── export_service.py                # Test results export functionality
│
├── views/                               # Application windows/views
│   ├── __init__.py
│   │
│   ├── main_window/                     # Main application window
│   │   ├── __init__.py
│   │   ├── main_window.py               # Main window with sidebar navigation
│   │   ├── content.py                   # Main content area widget
│   │   └── document.py                  # Document/info display widget
│   │
│   ├── code_editor/                     # Code editor window
│   │   ├── __init__.py
│   │   ├── code_editor_window.py        # Standalone code editor window
│   │   └── code_editor_display_area.py  # Editor display area with tabs
│   │
│   ├── benchmarker/                     # Benchmarker tool window
│   │   ├── __init__.py
│   │   ├── benchmarker_window.py        # Benchmark testing window
│   │   └── benchmarker_status_view.py   # Benchmark-specific status view
│   │
│   ├── comparator/                      # Comparator tool window
│   │   ├── __init__.py
│   │   ├── comparator_window.py         # Code comparison testing window
│   │   └── comparator_status_view.py    # Comparator-specific status view
│   │
│   ├── validator/                       # Validator tool window
│   │   ├── __init__.py
│   │   ├── validator_window.py          # Validation testing window
│   │   └── validator_status_view.py     # Validator-specific status view
│   │
│   ├── results/                         # Results viewing windows
│   │   ├── __init__.py
│   │   ├── results_window.py            # Main results browser window
│   │   ├── results_widget.py            # Results table and filtering
│   │   ├── detailed_results_window.py   # Detailed single result viewer
│   │   └── detailed_results_widget.py   # Detailed result display widgets
│   │
│   └── help_center/                     # Help/documentation window
│       ├── __init__.py
│       ├── help_center_window.py        # Help center main window
│       ├── content.py                   # Help content display
│       └── document.py                  # Help document widget
│
├── widgets/                             # Reusable UI components
│   ├── __init__.py
│   ├── sidebar.py                       # Navigation sidebar widget
│   ├── display_area.py                  # Content display area container
│   ├── testing_content_widget.py        # Testing tools content area
│   ├── test_detail_view.py              # Individual test result detail view
│   ├── detailed_results_window.py       # Detailed results popup window
│   │
│   ├── sidebar_widgets/                 # Sidebar-specific widgets
│   │   ├── __init__.py
│   │   ├── test_count_slider.py         # Test count selection slider
│   │   └── limits_input_widget.py       # Time/memory limit inputs
│   │
│   ├── display_area_widgets/            # Display area components
│   │   ├── __init__.py
│   │   ├── editor.py                    # Code editor widget
│   │   ├── editor_tab_widget.py         # Editor with tab support
│   │   ├── test_tab_widget.py           # Test file tabs (multi-language)
│   │   ├── console.py                   # Console output widget
│   │   └── ai_panel.py                  # AI assistance panel
│   │
│   └── status_view/                     # Status view components
│       ├── __init__.py
│       ├── presenter.py                 # Status view presenter/controller
│       ├── widgets.py                   # Status display widgets
│       ├── cards.py                     # Status info cards
│       └── models.py                    # Status data models
│
├── styles/                              # Styling and themes
│   ├── __init__.py
│   ├── constants.py                     # Style constants (colors, fonts)
│   │
│   ├── components/                      # Component-specific styles
│   │   ├── __init__.py
│   │   ├── button_styles.py             # Button styling
│   │   ├── sidebar_styles.py            # Sidebar styling
│   │   ├── editor_styles.py             # Editor styling
│   │   ├── console_styles.py            # Console styling
│   │   ├── ai_panel_styles.py           # AI panel styling
│   │   │
│   │   ├── dialogs/                     # Dialog-specific styles
│   │   │   ├── __init__.py
│   │   │   └── test_detail_styles.py    # Test detail dialog styles
│   │   │
│   │   └── status_view/                 # Status view styles
│   │       ├── __init__.py
│   │       ├── status_widgets_styles.py # Status widget styles
│   │       └── status_cards_styles.py   # Status card styles
│   │
│   └── helpers/                         # Style helper utilities
│       ├── __init__.py
│       └── colors.py                    # Color manipulation utilities
│
└── window_controller/                   # Window lifecycle management
    ├── __init__.py
    ├── window_management.py             # Window manager (creation, navigation)
    └── base_window.py                   # Base window controller (deprecated)
```

---

## Detailed File Descriptions

### 📁 base/
Core base classes and protocols that other components inherit from.

#### **protocols.py** (169 lines)
**Purpose**: Defines protocol interfaces for type-safe component interactions

**Key Protocols**:
- `TestRunner`: Protocol for test runner objects (Benchmarker, Validator, Comparator)
  - Defines required signals: `compilationOutput`, `compilationFinished`, `testingStarted`, `testingCompleted`, `testStarted`, `allTestsCompleted`
  - Enables dependency inversion - windows depend on protocol, not concrete implementations
  
- `WindowProtocol`: Base window interface
  - Methods: `show()`, `hide()`, `close()`, `can_close()`
  
- `ContentWindowProtocol`: Extended window with splitter support
  - Adds: `setup_splitter()`, `update_splitter_sizes()`
  
- `TestWindowProtocol`: Test tool window interface
  - Adds: `handle_action_button()`, `_initialize_tool()`, `_create_runner()`

**Usage**: Import protocols for type hints to ensure components implement required interfaces without circular dependencies.

#### **window_base.py** (~250 lines)
**Purpose**: Abstract base class for all application windows

**Key Features**:
- Common window initialization (title, size, parent references)
- Error handling and display (`show_error()`, `show_warning()`, `show_info()`)
- Window lifecycle management (`showEvent()`, `closeEvent()`)
- Unsaved changes checking (`can_close()`)
- Configuration loading/saving

**Methods**:
- `__init__(parent)`: Initialize window with parent reference
- `show_error(title, message)`: Display error dialog
- `can_close() -> bool`: Check if window can close safely
- `closeEvent(event)`: Handle window close with confirmation

**Inheritance Chain**: All windows inherit from this base class.

#### **content_window_base.py** (~200 lines)
**Purpose**: Base class for windows with sidebar + content area layout (uses QSplitter)

**Key Features**:
- QSplitter setup with sidebar and content area
- Splitter size persistence (saved to config)
- Automatic splitter configuration from settings
- Content widget swapping

**Methods**:
- `_create_splitter()`: Create and configure QSplitter
- `setup_splitter(sidebar, content)`: Add widgets to splitter
- `update_splitter_sizes(sizes)`: Update splitter proportions
- `_on_config_changed()`: Reload splitter sizes from config

**Used By**: MainWindow, HelpCenterWindow, and test tool windows.

#### **test_window_base.py** (~450 lines)
**Purpose**: Template base class for test tool windows (Benchmarker, Comparator, Validator)

**Template Methods** (subclasses must implement):
- `_create_runner()`: Create specific runner (Benchmarker/Comparator/Validator)
- `_create_status_view()`: Create tool-specific status view
- `_get_runner_attribute_name()`: Return runner attribute name ('benchmarker', 'comparator', 'validator_runner')
- `_get_run_method_name()`: Return run method name ('run_benchmark_test', 'run_comparison_test', etc.)
- `handle_action_button(button_text)`: Handle Compile/Run/Stop/Results buttons

**Key Features**:
- **Test Lifecycle Management**: Handles complete test execution flow
- **Mode Switching**: Normal → Testing → Completed modes with UI updates
- **Status View Integration**: Shows/hides status overlay during testing
- **Save Button Management**: Swaps Results ↔ Save button based on test state
- **Unsaved Changes**: Prompts before running tests with unsaved code
- **Signal Coordination**: Connects runner signals to status view updates

**UI Modes**:
1. **Normal Mode**: Shows editor, compile/run buttons visible
2. **Testing Mode**: Shows status view overlay, only Stop button visible
3. **Completed Mode**: Shows status view with results, Save button visible

**Methods**:
- `_switch_to_test_mode()`: Enter testing mode (hide editor, show status)
- `_switch_to_completed_mode()`: Enter completed mode (show Save button)
- `_restore_normal_mode()`: Return to normal mode (hide status view)
- `_on_testing_started()`: Handle test start signal
- `_on_testing_completed()`: Handle test completion signal
- `_integrate_status_view()`: Add status view to display area
- `enable_save_button()`: Make Save button available
- `mark_results_saved()`: Reset UI after saving results

**Reduces Code Duplication**: Eliminated ~150 lines per test window (450 lines total) by extracting common patterns.

### 📁 services/
Business logic services that can be used across the presentation layer.

#### **navigation_service.py** (~112 lines)
**Purpose**: Singleton service for centralized window navigation without parent coupling

**Key Features**:
- **Singleton Pattern**: One global instance accessible from anywhere
- **Decoupled Navigation**: Windows don't need parent.window_manager references
- **Testable**: Can mock navigation in tests
- **History Support**: Go back functionality

**Public API**:
```python
# Get singleton instance
nav = NavigationService.instance()

# Navigate to window
nav.navigate_to("benchmarker")          # Opens benchmarker window
nav.navigate_to("results", show=True)   # Opens and brings to front

# Navigation history
nav.go_back()                            # Return to previous window
nav.can_go_back() -> bool                # Check if can go back

# Setup (in MainWindow __init__)
nav.set_window_manager(self.window_manager)
```

**Signals**:
- `windowChangeRequested(str, dict)`: Emitted when navigation requested

**Methods**:
- `instance() -> NavigationService`: Get singleton instance (class method)
- `set_window_manager(manager)`: Register WindowManager
- `navigate_to(window_name, **kwargs) -> bool`: Navigate to window
- `go_back()`: Return to previous window
- `can_go_back() -> bool`: Check navigation history

**Usage Example**:
```python
from src.app.presentation.services.navigation_service import NavigationService

# From any window or widget
if NavigationService.instance().navigate_to("results"):
    print("Navigated to results window")
```

#### **export_service.py** (~150 lines)
**Purpose**: Export test results to organized ZIP archives

**Key Features**:
- Creates structured ZIP with folders: `code/`, `passed/`, `failed/`, `summary.txt`
- Handles all test types (benchmarker, comparator, validator)
- Generates human-readable summary files
- Error handling for file operations

**Public API**:
```python
ExportService.export_to_zip(
    result_data: dict,
    export_path: str
) -> bool
```

**ZIP Structure**:
```
result_export.zip
├── code/
│   ├── generator.cpp
│   ├── test.cpp
│   └── correct.cpp
├── passed/
│   ├── test_001.txt
│   └── test_002.txt
├── failed/
│   ├── test_003.txt (includes diff)
│   └── test_004.txt
└── summary.txt (metadata + statistics)
```

**Summary File Contains**:
- Test metadata (type, timestamp, language)
- Pass/fail statistics
- Configuration (test count, limits)
- Overall result status

**Methods**:
- `export_to_zip(result_data, export_path) -> bool`: Main export function
- `_create_summary(result_data) -> str`: Generate summary text
- `_write_test_cases(zip_file, tests, folder)`: Write test case files
- `_write_code_files(zip_file, files)`: Write source code files

### 📁 views/
Main application windows and views.

#### main_window/
- **main_window.py**: The main application window with sidebar navigation to different tools (Benchmarker, Comparator, Validator, Results, Editor, Help). Entry point window
- **content.py**: Main content area widget displayed in the main window, shows welcome information and quick actions
- **document.py**: Document/info display widget for showing formatted text content in the main window

#### code_editor/
- **code_editor_window.py**: Standalone code editor window with multi-file tab support, syntax highlighting, AI panel, and file management
- **code_editor_display_area.py**: Display area for the code editor with editor tabs and optional AI panel

#### benchmarker/
- **benchmarker_window.py**: Benchmark testing window (extends TestWindowBase), allows running performance benchmarks with time/memory limits
- **benchmarker_status_view.py**: Benchmarker-specific status view showing benchmark progress, resource usage, and results

#### comparator/
- **comparator_window.py**: Code comparison testing window (extends TestWindowBase), compares test code output against correct code
- **comparator_status_view.py**: Comparator-specific status view showing comparison progress and pass/fail status

#### validator/
- **validator_window.py**: Validation testing window (extends TestWindowBase), runs validator against test outputs
- **validator_status_view.py**: Validator-specific status view showing validation progress and results

#### results/
- **results_window.py**: Main results browser window, displays table of all test results with filtering, searching, export, and "Load to Test" functionality
- **results_widget.py**: Results table widget with filtering controls, search, and result management (view, export, delete)
- **detailed_results_window.py**: Popup window showing detailed view of a single test result with 4 tabs: Summary, Code Files, Passed Tests, Failed Tests
- **detailed_results_widget.py**: Widget for displaying detailed test result information with multiple tabs and test case details

#### help_center/
- **help_center_window.py**: Help center main window providing application documentation and guides
- **content.py**: Help content display widget showing topics and information
- **document.py**: Help document viewer widget for formatted help text

### 📁 widgets/
Reusable UI components used across different windows.

**Top-level widgets:**
- **sidebar.py**: Navigation/action sidebar widget with sections, buttons, and two-button layout support (Compile/Run)
- **display_area.py**: Content display area container that can hold different content widgets (editor, testing content, etc.)
- **testing_content_widget.py**: Complete testing content area with test tabs, editor, console, and AI panel. Used by all test tool windows
- **test_detail_view.py**: Dialog for displaying individual test case details (input, expected output, actual output, errors)
- **detailed_results_window.py**: Popup window for detailed result viewing (duplicate, consider consolidating with views/results/)

#### sidebar_widgets/
Specialized widgets for the sidebar.

- **test_count_slider.py**: Slider + input widget for selecting number of tests (1-1000), mode-specific configurations
- **limits_input_widget.py**: Input widgets for time limit (ms) and memory limit (MB) in benchmarker

#### display_area_widgets/
Widgets for the content display area.

- **editor.py**: Basic code editor widget with syntax highlighting (uses QPlainTextEdit)
- **editor_tab_widget.py**: Multi-file editor with tab support for code editor window
- **test_tab_widget.py**: Multi-language test file tabs (Generator, Test Code, Correct Code, Validator), handles language switching and file management
- **console.py**: Console output widget for displaying compilation and execution output with syntax highlighting
- **ai_panel.py**: AI assistance panel with action buttons (Analysis, Issues, Tips, Document/Generate) and custom command input

#### status_view/
Status view system for displaying test progress and results.

- **presenter.py**: Status view presenter/controller, coordinates between models and view widgets
- **widgets.py**: Core status display widgets (pipeline stages, progress bars, worker status)
- **cards.py**: Information cards for displaying status details and metrics
- **models.py**: Data models for status information (TestStatus, WorkerStatus, etc.)

### 📁 styles/
Application styling and theming.

- **constants.py**: Global style constants including colors, fonts, dimensions
- **components/**: Component-specific stylesheets

**Component styles:**
- **button_styles.py**: Button styling (action buttons, sidebar buttons, etc.)
- **sidebar_styles.py**: Sidebar and section styling
- **editor_styles.py**: Code editor styling (syntax highlighting, line numbers)
- **console_styles.py**: Console output styling
- **ai_panel_styles.py**: AI panel and button styling

**Dialogs:**
- **test_detail_styles.py**: Test detail dialog styling

**Status view:**
- **status_widgets_styles.py**: Status widget styling (pipelines, progress bars)
- **status_cards_styles.py**: Status card styling

**Helpers:**
- **colors.py**: Color manipulation utilities (lighten, darken, adjust alpha)

### 📁 window_controller/
Window lifecycle and management.

- **window_management.py**: WindowManager class that creates, manages, and navigates between windows. Maintains window registry and history
- **base_window.py**: Deprecated base window controller (functionality moved to base/window_base.py)

---

## Architecture Patterns

### 🏗️ Base Class Hierarchy
```
WindowProtocol (protocol)
    ↓
WindowBase
    ↓
ContentWindowBase (adds splitter support)
    ↓
TestWindowBase (adds test lifecycle)
        ↓
        ├── BenchmarkerWindow
        ├── ComparatorWindow
        └── ValidatorWindow
```

### 🔄 Key Design Patterns

1. **Template Method Pattern**: TestWindowBase defines test lifecycle template with hooks for subclasses
2. **Singleton Pattern**: NavigationService uses singleton for global navigation coordination
3. **Observer Pattern**: Extensive use of Qt signals/slots for component communication
4. **Protocol Pattern**: Type-safe interfaces via Protocol classes
5. **Service Layer**: Separation of business logic (services/) from UI (views/, widgets/)

### 🔌 Signal/Slot Architecture

Major signal flows:
- **Navigation**: User clicks → Sidebar → NavigationService → WindowManager → Window display
- **Testing**: User clicks Run → TestWindow → Runner → StatusView updates
- **AI Actions**: User clicks AI button → AIPanel signal → Window handler → AI service
- **Results**: Test complete → Save to DB → ResultsWidget refresh → User views

### 📦 Component Composition

Test tool windows compose:
- Sidebar (with action buttons)
- DisplayArea
  - TestingContentWidget
    - TestTabWidget (multi-language code tabs)
    - Editor
    - Console
    - AIPanel
  - StatusView (overlayed during testing)

---

## File Statistics

- **Total Python files**: ~100
- **Total directories**: 20
- **Lines of code**: ~15,000+ (after cleanup)
- **Main windows**: 7 (Main, Editor, Benchmarker, Comparator, Validator, Results, Help)
- **Reusable widgets**: 20+
- **Base classes**: 4
- **Services**: 2

---

## Recent Refactoring (refactor/presentation-layer branch)

### ✅ Completed Cleanup:
1. ✅ Removed ~90 DEBUG print statements from results_window.py
2. ✅ Removed 6 debug prints from test windows
3. ✅ Replaced 21 error prints with proper logging
4. ✅ Simplified 80 verbose docstrings (~206 lines saved)
5. ✅ Removed 19 phase/issue tracking comments
6. ✅ Removed 50+ obvious inline comments
7. ✅ Removed ~120-150 excessive blank lines

### 📊 Total Impact:
- **~570-600 lines removed**
- **186+ print statements** eliminated or upgraded to logging
- **Improved maintainability** with standardized code style
- **PEP 8 compliance** across presentation layer
