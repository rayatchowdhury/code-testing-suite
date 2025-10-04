# Window Management Architecture Analysis
## Code Testing Suite - Presentation Layer Deep Dive

**Document Created:** October 3, 2025  
**Last Updated:** October 4, 2025  
**Analysis Focus:** `src/app/presentation/views/` and window management patterns

> **Note:** On October 4, 2025, the following refactoring was completed:
> - Moved `base_window.py`, `window_management.py`, `qt_doc_engine.py` to `presentation/window_controller/`
> - Moved `main_window.py` to `presentation/views/main_window/`
> - Renamed `main_window_doc.py` to `main_window_content.py` and moved to `presentation/views/main_window/`
> - All imports have been updated throughout the codebase

---

## Executive Summary

The Code Testing Suite uses a **hierarchical window management system** with:
- **1 Main Application Window** (QMainWindow)
- **7 Content Windows** managed by WindowManager (QStackedWidget)
- **Multiple Dialog Types** for configuration and details
- **Embedded Status Views** for test execution feedback

### Current State Assessment

**✅ Strengths:**
- Clear separation between window creation (Factory) and management (Manager)
- Consistent sidebar-based layout pattern across test windows
- Lazy loading to improve startup time
- Signal-based communication for navigation

**⚠️ Areas of Concern (Messiness Identified):**
1. **Mixed Responsibility:** Windows handle both UI and business logic
2. **Inconsistent State Management:** Status views stored differently across windows
3. **Duplicate Code:** Similar patterns repeated in comparator/validator/benchmarker
4. **Navigation History Issues:** Back button behavior inconsistent
5. **Dialog Creation:** Scattered across multiple files without centralization
6. **Memory Management:** Unclear cleanup patterns for embedded widgets

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     QApplication                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              MainWindow (QMainWindow)                  │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │        WindowManager (QStackedWidget)           │  │  │
│  │  │                                                  │  │  │
│  │  │  ┌────────────────────────────────────────┐    │  │  │
│  │  │  │   Current Window (QWidget)             │    │  │  │
│  │  │  │  ┌──────────┬──────────────────────┐  │    │  │  │
│  │  │  │  │ Sidebar  │   Display Area       │  │    │  │  │
│  │  │  │  │          │   (Content/Editor/   │  │    │  │  │
│  │  │  │  │          │    Status View)      │  │    │  │  │
│  │  │  │  └──────────┴──────────────────────┘  │    │  │  │
│  │  │  └────────────────────────────────────────┘    │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

           ┌──────────────────────────────────┐
           │     Dialogs (QDialog)            │
           │  - ConfigView                    │
           │  - TestDetailDialog              │
           │  - ErrorDialog                   │
           │  - QMessageBox (save prompts)    │
           └──────────────────────────────────┘
```

---

## Component Breakdown

### 1. Application Entry Point (`__main__.py`)

**Location:** `src/app/__main__.py`

**Responsibilities:**
- Sets up Python path and Qt API
- Creates QApplication with async event loop (qasync)
- Instantiates MainWindow
- Handles top-level error catching

**Key Code:**
```python
def create_main_window():
    from src.app.presentation.views.main_window import MainWindow
    return MainWindow()

def main():
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    window = create_main_window()
    window.show()
    loop.run_forever()
```

---

### 2. Main Application Container

#### 2.1 MainWindow (QMainWindow)
**Location:** `src/app/presentation/views/main_window.py` (lines 269-326)

**Type:** Top-level container  
**Parent:** None (root window)

**Key Responsibilities:**
1. Hosts WindowManager as central widget
2. Handles application-level close events
3. Checks for unsaved changes before exit
4. Manages cleanup on shutdown

**Architecture Pattern:** Container Pattern

**Key Methods:**
- `__init__()` - Sets up window properties and manager
- `closeEvent()` - Handles unsaved changes check
- `_perform_cleanup()` - Triggers cascade cleanup

**Issues Identified:**
- ❌ **Cleanup logic mixed with UI logic** - should be separated
- ❌ **UnsavedChangesHandler is a static class** - hard to test and extend

---

### 3. Window Management Layer

#### 3.1 WindowFactory
**Location:** `src/app/presentation/views/window_management.py` (lines 13-145)

**Type:** Static factory class  
**Pattern:** Factory Pattern with Lazy Loading

**Responsibilities:**
1. Register window creators (lazy import functions)
2. Create window instances on demand
3. Avoid circular imports through lazy loading

**Registered Windows:**
```python
{
    'main': MainWindowContent,
    'code_editor': CodeEditorWindow,
    'comparator': ComparatorWindow,
    'benchmarker': BenchmarkerWindow,
    'validator': ValidatorWindow,
    'help_center': HelpCenterWindow,
    'results': ResultsWindow
}
```

**Key Methods:**
- `register_window_creator(name, creator_func)` - Register new window type
- `create_window(name, parent)` - Instantiate window
- `get_window_class(name)` - Get class without instantiation

**Strengths:**
- ✅ Lazy imports prevent slow startup
- ✅ Easy to extend with new window types
- ✅ Avoids circular dependencies

**Issues:**
- ⚠️ No validation that creator returns QWidget
- ⚠️ Error messages printed instead of logged
- ⚠️ Thread-safety not considered (singleton pattern)

---

#### 3.2 WindowManager
**Location:** `src/app/presentation/views/window_management.py` (lines 148-239)

**Type:** QStackedWidget (manages multiple windows, shows one at a time)  
**Pattern:** Manager Pattern + Navigation Stack

**Responsibilities:**
1. Create windows using WindowFactory
2. Switch between windows
3. Maintain navigation history (back button)
4. Clean up window resources

**Key Data Structures:**
```python
self.windows = {}              # {name: widget_instance}
self.current_window = None     # Currently visible window name
self.window_history = []       # Navigation stack for back button
```

**Key Methods:**
- `show_window(name, **kwargs)` - Create/show window, manage history
- `go_back()` - Navigate to previous window
- `get_current_window()` - Get active window instance
- `cleanup_window(name)` - Remove and cleanup specific window
- `cleanup_all()` - Cleanup all windows (on app exit)

**Navigation Logic:**
```python
def show_window(self, window_name, **kwargs):
    # Create if doesn't exist
    if window_name not in self.windows:
        window = WindowFactory.create_window(window_name, self.parent())
        self.windows[window_name] = window
        self.addWidget(window)
    
    # Add current to history (if different)
    if self.current_window and self.current_window != window_name:
        if not self.window_history or self.window_history[-1] != self.current_window:
            self.window_history.append(self.current_window)
    
    # Switch to window
    window = self.windows[window_name]
    self.setCurrentWidget(window)
    self.current_window = window_name
```

**Issues Identified:**
- ❌ **History management is fragile** - can accumulate duplicates
- ❌ **No max history size** - memory leak potential
- ❌ **No way to clear specific window from memory** - windows persist until app exit
- ❌ **Cleanup order hardcoded** - special case for 'main' window
- ⚠️ **RuntimeError catching too broad** - may hide real issues

---

### 4. Window Types

#### 4.1 Base Window Pattern

##### SidebarWindowBase
**Location:** `src/app/presentation/views/base_window.py`

**Type:** Abstract base class (QWidget)  
**Pattern:** Template Method Pattern

**Structure:**
```
┌──────────────────────────────────────────────┐
│           SidebarWindowBase (QWidget)        │
│  ┌──────────────────────────────────────┐   │
│  │  QHBoxLayout                         │   │
│  │  ┌────────────────────────────────┐  │   │
│  │  │  QSplitter (Horizontal)        │  │   │
│  │  │  ┌─────────┬────────────────┐  │  │   │
│  │  │  │ Sidebar │ Display Area   │  │  │   │
│  │  │  │         │                │  │  │   │
│  │  │  │ (250px) │ (expandable)   │  │  │   │
│  │  │  └─────────┴────────────────┘  │  │   │
│  │  └────────────────────────────────┘  │   │
│  └──────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
```

**Standard Sidebar Structure:**
```
┌───────────────────┐
│  Window Title     │  <- Header
├───────────────────┤
│ § Section 1       │  <- Collapsible sections
│   Button 1        │
│   Button 2        │
├───────────────────┤
│ § Section 2       │
│   Button 3        │
├───────────────────┤
│        ...        │
├───────────────────┤
│ Help Center       │  <- Help button
├───────────────────┤
│ Back  │  ⚙️       │  <- Footer buttons
└───────────────────┘
```

**Responsibilities:**
1. Provide consistent sidebar + display area layout
2. Handle Back button navigation
3. Handle Options (config) button
4. Provide test mode switching for status views
5. Manage display area content swapping

**Key Methods:**

**UI Setup:**
- `init_sidebar(title)` - Create sidebar with standard footer
- `setup_splitter(sidebar, content)` - Configure split view
- `update_splitter_sizes()` - Maintain 250/850 ratio

**Navigation:**
- `handle_button_click(button_text)` - Route button clicks
- `can_close()` - Check if window can be closed (unsaved changes)
- `cleanup()` - Override to clean up resources

**Test Execution Support:**
- `_switch_to_test_mode()` - Hide compile/run, show stop button
- `_restore_normal_mode()` - Show compile/run, hide stop button
- `_integrate_status_view(view)` - Replace display area with status view
- `_restore_display_area()` - Restore original display area content
- `_connect_worker_to_status_view(worker, view)` - Connect test signals

**Issues Identified:**
- ❌ **Test mode methods are empty stubs** - subclasses must override, no enforcement
- ❌ **Status view integration stores original content** - memory leak if not restored
- ❌ **No validation that display_area exists** - defensive checks scattered
- ⚠️ **Config reload logic embedded** - violates single responsibility
- ⚠️ **AI panel refresh mixed in** - should be event-driven

---

#### 4.2 Content Windows

##### A. MainWindowContent
**Location:** `src/app/presentation/views/main_window.py` (lines 58-198)

**Purpose:** Landing page / navigation hub  
**Parent Class:** SidebarWindowBase

**Unique Features:**
- Exit button instead of Back button
- Asynchronously loads Qt-rendered welcome content
- No display area swapping (static content)

**Sidebar Structure:**
```
Code Testing Suite
  § Editor
    Code Editor
  § Tests
    Compare
    Validate
    Benchmark
  § History
    Results
  ────────────────
  Help Center
  ────────────────
  Exit  │  ⚙️
```

**Navigation Mapping:**
```python
WINDOW_MAPPING = {
    'Compare': 'comparator',
    'Benchmark': 'benchmarker',
    'Validate': 'validator'
}
# Others use button_text.lower().replace(' ', '_')
```

**Display Area Content:**
- Loads `main_window_content.py` → `create_qt_main_window()`
- Custom Qt document widget with welcome text and feature overview
- Lazy loaded via QTimer to avoid blocking UI

**Issues:**
- ⚠️ **Module reload logic in production code** - should be dev-only
- ⚠️ **Magic timing constants** (CONTENT_INIT_DELAY = 0) - unclear purpose
- ❌ **Exit handling duplicated** in multiple methods

---

##### B. CodeEditorWindow
**Location:** `src/app/presentation/views/code_editor/code_editor_window.py`

**Purpose:** Multi-file code editing with syntax highlighting  
**Parent Class:** SidebarWindowBase

**Unique Features:**
- Tab-based multi-file editing
- Session persistence (saves open files to JSON + database)
- Unsaved changes tracking per tab
- AI panel integration per tab

**Sidebar Structure:**
```
Code Editor
  § File Operations
    New File
    Open File
    Save File
  ────────────────
  Help Center
  ────────────────
  Back  │  ⚙️
```

**Display Area:** CodeEditorDisplay
- `EditorTabWidget` - Tab-based editor container
- `ConsoleOutput` - Compile and run output
- Split view (70% editor, 30% console)

**State Management:**
```python
# Saved to: EDITOR_STATE_FILE
{
    'open_files': [
        {'path': str, 'is_active': bool},
        ...
    ]
}
```

**Lifecycle:**
1. `__init__()` - Load previous session
2. `showEvent()` - Reload AI config, refresh AI panels
3. `closeEvent()` - Check unsaved changes, save state, cleanup
4. `cleanup()` - Stop compiler runner

**Issues Identified:**
- ❌ **Dual persistence** (JSON + database) - unnecessary complexity
- ❌ **Unsaved changes check in multiple places** - should be centralized
- ⚠️ **AI panel refresh on every show** - performance concern
- ⚠️ **Tab state tracking is fragile** - modified flag can get out of sync
- ❌ **save_editor_state() called too frequently** - throttling needed

---

##### C. Test Windows (Comparator/Validator/Benchmarker)
**Locations:**
- `src/app/presentation/views/comparator/comparator_window.py`
- `src/app/presentation/views/validator/validator_window.py`
- `src/app/presentation/views/benchmarker/benchmarker_window.py`

**Purpose:** Configure and run test suites with live feedback  
**Parent Class:** SidebarWindowBase

**Pattern:** 95% identical structure - **MAJOR CODE DUPLICATION**

**Common Structure:**

**Sidebar (Generic):**
```
{Test Type}
  § Number of Tests          ← Slider widget
    [======○==] 100
  § Resource Limits          ← Benchmarker only
    Time Limit: [____] ms
    Memory Limit: [____] MB
  § Actions
    Compile                  ← Initially visible
    Run                      ← Initially visible
    Stop                     ← Shows during test execution
    Run                      ← Shows after completion (rerun)
  § History
    Results
  ────────────────
  Help Center
  ────────────────
  Back  │  ⚙️
```

**Display Area (Generic):**
- `{Test}Display` - Contains file tabs, editor, console
- Test tabs widget (Solution/Generator/Validator files)
- Swapped with StatusView during execution

**Test Execution Flow:**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Compile Button Clicked                                   │
│    → Check unsaved changes                                   │
│    → tool.compile_all()                                      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Run Button Clicked                                        │
│    → Get test count from slider                              │
│    → tool.run_{comparison|validation|benchmark}_test(count)  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Tool Emits testingStarted Signal                          │
│    → _on_testing_started()                                   │
│    → Create StatusView                                       │
│    → _integrate_status_view() - swap display area            │
│    → _switch_to_test_mode() - hide Compile/Run, show Stop   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Tests Execute (Worker Thread)                             │
│    → Worker emits testStarted(n, total)                      │
│    → Worker emits testCompleted(n, passed, ...)              │
│    → StatusView updates cards and progress                   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Tool Emits testingCompleted Signal                        │
│    → _on_testing_completed()                                 │
│    → _switch_to_completed_mode() - hide Stop, show Rerun    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Back Button Clicked (During/After Tests)                  │
│    → If status_view_active: _on_back_requested()             │
│    → _restore_normal_mode() - show Compile/Run               │
│    → _restore_display_area() - restore original content      │
│    → status_view_active = False                              │
└─────────────────────────────────────────────────────────────┘
```

**Button State Management:**

| State | Compile | Run | Stop | Rerun |
|-------|---------|-----|------|-------|
| **Initial** | ✓ visible | ✓ visible | ✗ hidden | ✗ hidden |
| **Compiling** | ✓ visible | ✓ visible | ✗ hidden | ✗ hidden |
| **Tests Running** | ✗ hidden | ✗ hidden | ✓ visible | ✗ hidden |
| **Tests Completed** | ✗ hidden | ✗ hidden | ✗ hidden | ✓ visible |
| **After Back** | ✓ visible | ✓ visible | ✗ hidden | ✗ hidden |

**Key Differences:**

| Feature | Comparator | Validator | Benchmarker |
|---------|------------|-----------|-------------|
| **Tool Class** | `Comparator` | `ValidatorRunner` | `Benchmarker` |
| **Status View** | `ComparatorStatusView` | `ValidatorStatusView` | `BenchmarkerStatusView` |
| **Test Method** | `run_comparison_test()` | `run_validation_test()` | `run_benchmark_test()` |
| **Extra Inputs** | None | None | time_limit_ms, memory_limit_mb |
| **Display Area** | `ComparatorDisplay` | `ValidatorDisplay` | `BenchmarkerDisplay` |

**Shared Issues (All Three Windows):**
- ❌ **95% duplicate code** - should be extracted to base class
- ❌ **Button state management is complex** - state machine pattern needed
- ❌ **status_view_active flag is error-prone** - can get out of sync
- ❌ **_on_back_requested vs back button confusion** - two different flows
- ⚠️ **Worker connection logic duplicated** - should be in base class
- ⚠️ **No validation of status view creation** - can fail silently
- ❌ **Rerun button created dynamically** - memory leak if not cleaned up

---

##### D. HelpCenterWindow
**Location:** `src/app/presentation/views/help_center/help_center_window.py`

**Purpose:** Static documentation viewer  
**Parent Class:** SidebarWindowBase

**Unique Features:**
- Document-based content rendering
- Topic-based navigation (sidebar buttons)
- Uses custom `HelpDocument` widget

**Sidebar Structure:**
```
Help Center
  § Help Topics
    Introduction
    Code Editor Guide
    Comparison Guide
    Benchmarking Guide
    Validation Guide
    Configuration
    About
  ────────────────
  Back  │  ⚙️
```

**Display Area:**
- `DisplayArea` with custom `HelpDocument` widgets
- Content loaded from `help_content.py`
- Document replaced on topic change (previous deleted)

**Content Loading:**
```python
def load_help_content(self, topic):
    # Clear existing
    if self.current_document:
        self.display_area.layout.removeWidget(self.current_document)
        self.current_document.deleteLater()
    
    # Create new
    data = get_document_data(topic)
    self.current_document = HelpDocument(data['title'], data['sections'])
    self.display_area.layout.addWidget(self.current_document)
```

**Issues:**
- ⚠️ **Document replacement pattern is inefficient** - could use stacked widget
- ⚠️ **No caching of documents** - recreated every time
- ✓ Proper cleanup with `deleteLater()`

---

##### E. ResultsWindow
**Location:** `src/app/presentation/views/results/results_window.py`

**Purpose:** View historical test results from database  
**Parent Class:** SidebarWindowBase

**Sidebar Structure:**
```
Results & Analytics
  § Actions
    Refresh Data
    Export Results        ← Planned feature
    Clear Old Data
  § View Options
    Show All
    Show Comparison Tests
    Show Benchmark Tests
  ────────────────
  Help Center
  ────────────────
  Back  │  ⚙️
```

**Display Area:** `TestResultsWidget`
- Database-backed results viewer
- Filters by test type
- Auto-cleanup of old data

**Issues:**
- ⚠️ **Export not implemented** - should be hidden or implemented
- ⚠️ **Database operations not async** - could block UI
- ⚠️ **No pagination** - could be slow with many results

---

### 5. Dialog Types

#### 5.1 Configuration Dialog
**Location:** `src/app/core/config/views/config_dialog.py`

**Type:** Modal dialog (QDialog)  
**Invocation:** Options button (⚙️) in any window footer

**Purpose:** 
- Configure compiler paths (C++, Java, Python)
- Configure AI settings (API keys, models)
- Manage database settings
- View system information

**Signals:**
```python
configSaved = Signal(dict)  # Emitted when config saved
```

**Connected in:** `SidebarWindowBase._on_config_changed()`
- Reloads AI configuration
- Refreshes AI panels in windows

**Architecture:**
- Tabbed interface (General, Compilers, AI, Database)
- Form-based inputs with validation
- Uses `ConfigManager` for persistence

**Issues:**
- ⚠️ **Validation errors not user-friendly** - uses ErrorDialog
- ⚠️ **No preview before save** - changes applied immediately
- ⚠️ **Large monolithic file (746 lines)** - should be split

---

#### 5.2 Test Detail Dialogs
**Location:** `src/app/presentation/widgets/test_detail_view.py`

**Type:** Modal dialog (QDialog)  
**Invocation:** Clicking test card in status view

**Hierarchy:**
```
TestDetailDialog (Base)
├── ComparatorDetailDialog
├── ValidatorDetailDialog
└── BenchmarkerDetailDialog
```

**Purpose:** Show detailed test information:
- Test number and pass/fail status
- Time and memory metrics
- Test-specific data (input, output, errors, etc.)

**Layout:**
```
┌─────────────────────────────────────┐
│  Test #5            ✓ Passed/✗ Failed │
├─────────────────────────────────────┤
│  Time: 0.123s    Memory: 4.5 MB     │
├─────────────────────────────────────┤
│                                     │
│  [Test-Specific Content]            │
│  - Input/Output (Comparator)        │
│  - Validation Results (Validator)   │
│  - Performance Metrics (Benchmarker)│
│                                     │
├─────────────────────────────────────┤
│                         [Close]      │
└─────────────────────────────────────┘
```

**Invocation Flow:**
```python
# In status view
card.clicked.connect(lambda: self.show_test_detail(test_number))

# In ComparatorStatusView
def show_test_detail(self, test_number):
    data = self.test_data[test_number]
    dialog = ComparatorDetailDialog(...)
    dialog.exec()
```

**Issues:**
- ⚠️ **Test data duplicated** - stored in status view and cards
- ⚠️ **No keyboard navigation** - should support arrow keys
- ✓ Proper modal behavior

---

#### 5.3 Error Dialog
**Location:** `src/app/core/config/views/config_dialog.py` (lines 18-100)

**Type:** Modal dialog (QDialog)  
**Purpose:** Display error messages with optional details

**Static Creation:**
```python
ErrorDialog.show_error(
    title="Configuration Error",
    message="Failed to save settings",
    details=traceback_string,
    parent=self
)
```

**Issues:**
- ⚠️ **Location is odd** - should be in presentation/widgets
- ⚠️ **Not consistently used** - some code uses QMessageBox instead

---

#### 5.4 System Message Boxes
**Type:** Built-in QMessageBox dialogs

**Common Uses:**

**Unsaved Changes:**
```python
reply = QMessageBox.question(
    self,
    "Save Changes?",
    "Do you want to save your changes?",
    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
)
```

**Confirmation:**
```python
reply = QMessageBox.question(
    self,
    "Clear Old Data",
    "This will delete test results older than 30 days. Continue?",
    QMessageBox.Yes | QMessageBox.No
)
```

**Issues:**
- ❌ **Inconsistent text** - save prompts vary across windows
- ❌ **No centralized dialog management** - scattered throughout code
- ⚠️ **Blocking calls** - could improve UX with async patterns

---

### 6. Embedded Views (Status Views)

#### 6.1 Base Status View Architecture
**Location:** `src/app/presentation/widgets/unified_status_view.py`

**Type:** QWidget (embedded, not dialog)  
**Purpose:** Real-time test execution feedback

**Hierarchy:**
```
BaseStatusView (QWidget)
├── ComparatorStatusView
├── ValidatorStatusView
└── BenchmarkerStatusView
```

**Integration Pattern:**
```python
# In test window (e.g., ComparatorWindow)
def _on_testing_started(self):
    # 1. Create status view
    status_view = ComparatorStatusView(parent=self)
    
    # 2. Store reference
    self.status_view = status_view
    
    # 3. Connect worker signals
    worker = self.comparator.get_current_worker()
    self._connect_worker_to_status_view(worker, status_view)
    
    # 4. Replace display area
    self._integrate_status_view(status_view)
    
    # 5. Update button states
    self._switch_to_test_mode()
```

**Structure:**
```
┌────────────────────────────────────────┐
│  ControlsPanel                         │
│  [Solution.cpp] [Generator.cpp] ...    │
├────────────────────────────────────────┤
│  ProgressSection                       │
│  Running Test 5/100                    │
│  [████████████░░░░░░░] 45%            │
│  Passed: 42  Failed: 3                 │
├────────────────────────────────────────┤
│  CardsSection (Scrollable)             │
│  ┌──────────────────────────────────┐ │
│  │ Test #1  ✓ Passed  0.123s  4.5MB│ │
│  ├──────────────────────────────────┤ │
│  │ Test #2  ✗ Failed  0.456s  5.2MB│ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
```

**Signal Flow:**
```
Worker Thread                Status View
─────────────                ────────────
testStarted(n, total) ──────> on_test_running()
                              └─> Update progress
                              
testCompleted(n, passed) ───> on_test_completed()
                              ├─> Update counters
                              ├─> Create test card
                              └─> Update progress bar
                              
allTestsCompleted() ─────────> on_tests_completed()
                              └─> Final summary
```

**Lifecycle:**
```
1. Creation:        _on_testing_started()
2. Display:         _integrate_status_view()
3. Execution:       Worker signals update view
4. Completion:      Tests finish, Rerun button shown
5. Restoration:     _on_back_requested()
6. Cleanup:         _restore_display_area()
```

**Issues Identified:**
- ❌ **No cleanup of status view** - remains in memory after restoration
- ❌ **Original display content stored indefinitely** - memory leak
- ⚠️ **Stop button removed from status view** - now in sidebar (confusing)
- ⚠️ **Back button behavior overloaded** - different meaning during tests
- ❌ **status_view_active flag duplicates state** - window has reference
- ⚠️ **Card data duplicated** - in view and in individual cards

---

#### 6.2 Test Cards
**Location:** `src/app/presentation/widgets/test_cards.py`

**Type:** Clickable card widgets  
**Purpose:** Compact test result display in status view

**Hierarchy:**
```
BaseTestCard (QFrame)
├── ComparatorTestCard
├── ValidatorTestCard
└── BenchmarkerTestCard
```

**Layout:**
```
┌─────────────────────────────────────────┐
│ Test #5               ✓ Passed/✗ Failed │
│ Time: 0.123s         Memory: 4.5 MB     │
│                                          │
│ [Preview of test-specific info]         │
│ Input: test_input.txt                    │
│ Output: Expected ✓                       │
└─────────────────────────────────────────┘
```

**Click Behavior:**
```python
card.clicked.connect(lambda: status_view.show_test_detail(test_number))
```

**Issues:**
- ⚠️ **Data duplicated** - card stores same data as status view
- ⚠️ **No hover effects** - unclear cards are clickable
- ⚠️ **Cards never removed** - accumulate in memory

---

### 7. Sidebar Components

#### 7.1 Sidebar Widget
**Location:** `src/app/presentation/widgets/sidebar.py`

**Structure:**
```
┌──────────────────────┐
│  Title Label         │
├──────────────────────┤
│  Section 1 (Header)  │  ← Collapsible
│    Button 1          │
│    Button 2          │
├──────────────────────┤
│  Section 2 (Header)  │
│    Widget            │  ← Can contain any widget
├──────────────────────┤
│  ...                 │
├──────────────────────┤
│  QSpacerItem         │  ← Pushes footer down
├──────────────────────┤
│  Help Center         │  ← Special button
├──────────────────────┤
│  Divider Line        │
├──────────────────────┤
│  Footer Container    │
│  [Back]  [⚙️]        │  ← Horizontal buttons
└──────────────────────┘
```

**Key Methods:**
- `add_section(title)` - Creates collapsible section
- `add_button(text, section)` - Adds button to section
- `add_help_button()` - Adds Help Center button
- `add_footer_divider()` - Adds separator line
- `setup_horizontal_footer_buttons(btn1, btn2)` - Arranges footer

**Signals:**
```python
button_clicked = Signal(str)  # Button text emitted on click
```

**Issues:**
- ⚠️ **Section collapse state not persisted** - resets on window change
- ⚠️ **No validation of button uniqueness** - can add duplicates
- ⚠️ **Help button behavior hardcoded** - emits 'Help Center' signal

---

#### 7.2 Sidebar Widgets
**Location:** `src/app/presentation/widgets/sidebar_widgets/`

**TestCountSlider:**
- Range: 1-1000 tests
- Modes: comparator, validator, benchmarker (different defaults)
- Signal: `valueChanged(int)`

**LimitsInputWidget:** (Benchmarker only)
- Time limit input (milliseconds)
- Memory limit input (megabytes)
- Signals: `timeLimitChanged(int)`, `memoryLimitChanged(int)`

**Issues:**
- ⚠️ **No input validation** - can enter invalid values
- ⚠️ **State not persisted** - resets to defaults on window reopen

---

### 8. Display Area Components

#### 8.1 Generic DisplayArea
**Location:** `src/app/presentation/widgets/display_area.py`

**Type:** Simple container widget  
**Purpose:** Generic content area for windows

**Structure:**
```python
class DisplayArea(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
```

**Used By:**
- MainWindowContent (welcome screen)
- HelpCenterWindow (documentation)

---

#### 8.2 Test Display Areas
**Locations:**
- `code_editor/code_editor_display_area.py` - CodeEditorDisplay
- `comparator/comparator_display_area.py` - ComparatorDisplay
- `validator/validator_display_area.py` - ValidatorDisplay
- `benchmarker/benchmarker_display_area.py` - BenchmarkerDisplay

**Common Structure:**
```
┌─────────────────────────────────────────┐
│  File Buttons Row                       │
│  [Solution] [Generator] [Validator]     │
├─────────────────────────────────────────┤
│  QSplitter (Horizontal)                 │
│  ┌──────────────────┬─────────────────┐│
│  │  Editor Area     │  Console        ││
│  │  (Code editor    │  (Compile/run   ││
│  │   with syntax    │   output)       ││
│  │   highlighting)  │                 ││
│  └──────────────────┴─────────────────┘│
└─────────────────────────────────────────┘
```

**Key Components:**
- File button row (tab-like switching)
- Code editor with syntax highlighting
- Console output panel
- AI panel (code editor only)

**File Management:**
- Each button represents a file (e.g., Solution, Generator)
- Click button to switch file
- Files auto-created with templates on first access
- Unsaved changes tracked per file

**Issues:**
- ❌ **File button state scattered** - in multiple data structures
- ❌ **Unsaved changes check duplicated** - should be in one place
- ⚠️ **No file rename capability** - buttons have fixed names
- ⚠️ **AI panel only in code editor** - inconsistent

---

### 9. Key Patterns and Anti-Patterns

#### ✅ Good Patterns

**1. Factory + Manager Separation**
```python
# Good: Clear separation of concerns
window = WindowFactory.create_window('comparator', parent)
window_manager.show_window('comparator')
```

**2. Lazy Loading**
```python
# Good: Avoid circular imports and slow startup
def _create_comparator():
    from src.app.presentation.views.comparator import ComparatorWindow
    return ComparatorWindow
```

**3. Signal-Based Communication**
```python
# Good: Loose coupling between components
self.sidebar.button_clicked.connect(self.handle_button_click)
worker.testCompleted.connect(status_view.on_test_completed)
```

**4. Template Method Pattern**
```python
# Good: Base class provides structure, subclasses implement details
class SidebarWindowBase:
    def handle_button_click(self, button_text):
        if button_text == 'Back':
            # Common behavior
        elif button_text == 'Options':
            # Common behavior
```

---

#### ❌ Anti-Patterns

**1. Code Duplication (The Worst Offender)**
```python
# BAD: Comparator, Validator, Benchmarker windows are 95% identical
# Should have TestWindowBase with test-specific subclasses
```

**Lines of duplicate code:** ~200 lines per window × 3 windows = **600+ lines**

**What should be shared:**
- Sidebar structure (test count slider, actions, history)
- Button state management (compile/run/stop/rerun)
- Status view integration logic
- Worker signal connection
- Display area swapping

**What should differ:**
- Tool class type
- Status view type
- Test method name
- Extra parameters (benchmarker limits)

**2. Mixed Responsibilities**
```python
# BAD: Window classes doing too much
class ComparatorWindow(SidebarWindowBase):
    def _initialize_tool(self):        # Tool creation
        self.comparator = Comparator(...)
    
    def handle_action_button(self):    # UI logic
        if button_text == 'Compile':
    
    def _on_testing_started(self):     # Status view management
        status_view = ComparatorStatusView()
    
    def _switch_to_test_mode(self):    # Button visibility
        self.compile_btn.hide()
```

**Should be separated into:**
- Window (UI only)
- Controller (coordination)
- Tool (business logic)

**3. Fragile State Management**
```python
# BAD: Multiple sources of truth
self.status_view_active = False    # Flag in window
self.status_view = None            # Reference in window
self.current_status_view = None    # Another reference
self._original_display_content     # Stored in base class

# If any get out of sync, bugs occur
```

**Should use:** State machine pattern with single source of truth

**4. Memory Leaks**
```python
# BAD: Status view never cleaned up
def _integrate_status_view(self, status_view):
    # Store original content
    if not hasattr(self, '_original_display_content'):
        self._original_display_content = layout.itemAt(0).widget()
    # But if called multiple times, old content is lost!

# BAD: Rerun button created but never deleted
if not hasattr(self, 'rerun_btn'):
    self.rerun_btn = self.sidebar.add_button('Run', self.action_section)
```

**Should:** Use explicit cleanup methods

**5. Error Handling by Print**
```python
# BAD: Errors printed instead of logged or handled
def create_window(cls, window_name, parent):
    try:
        ...
    except Exception as e:
        print(f"Error creating window '{window_name}': {e}")
        return None
```

**Should:** Use logging module and propagate errors

**6. Static Utility Classes**
```python
# BAD: Can't be tested or extended
class UnsavedChangesHandler:
    @staticmethod
    def check_and_handle_unsaved_changes(window_manager):
        ...
```

**Should:** Use dependency injection or instance methods

---

### 10. Critical Issues Summary

#### Priority 1: High Impact, High Frequency

| Issue | Impact | Location | Effort |
|-------|--------|----------|--------|
| **Code Duplication in Test Windows** | Very High | All test windows | High |
| **Memory Leaks in Status View Integration** | High | Base window | Medium |
| **Button State Management Complexity** | High | All test windows | Medium |
| **Unsaved Changes Check Scattered** | Medium | Multiple windows | Medium |

#### Priority 2: Medium Impact

| Issue | Impact | Location | Effort |
|-------|--------|----------|--------|
| **History Management Fragility** | Medium | WindowManager | Low |
| **No Window Cleanup Strategy** | Medium | WindowManager | Medium |
| **Error Handling Inconsistency** | Low | Throughout | High |
| **Static Handler Classes** | Low | Main window | Low |

#### Priority 3: Code Quality

| Issue | Impact | Location | Effort |
|-------|--------|----------|--------|
| **Missing Input Validation** | Low | Sidebar widgets | Low |
| **No State Persistence** | Low | Sliders, sections | Medium |
| **Dialog Management Scattered** | Low | Throughout | Medium |
| **Inefficient Document Reload** | Low | Help center | Low |

---

### 11. Recommendations

#### Phase 1: Extract Common Test Window Base Class

**Create:** `src/app/presentation/views/test_window_base.py`

```python
class TestWindowBase(SidebarWindowBase):
    """
    Base class for Comparator, Validator, Benchmarker windows.
    
    Provides:
    - Common sidebar structure
    - Button state machine
    - Status view lifecycle management
    - Tool initialization pattern
    """
    
    # Abstract properties (subclasses must define)
    @property
    @abstractmethod
    def tool_class(self): pass
    
    @property
    @abstractmethod
    def status_view_class(self): pass
    
    @property
    @abstractmethod
    def display_area_class(self): pass
    
    # Common implementation
    def __init__(self, parent=None, window_title=None):
        super().__init__(parent, title=None)
        self._setup_sidebar(window_title)
        self._setup_display_area()
        self._initialize_tool()
        self._state_machine = TestButtonStateMachine()
    
    def _setup_sidebar(self, title):
        # Common to all three
        ...
    
    def handle_action_button(self, button_text):
        # Common to all three
        ...
```

**Benefits:**
- Eliminate 600+ lines of duplication
- Centralize button state management
- Easier to add new test window types
- Single place to fix bugs

**Estimated effort:** 2-3 days

---

#### Phase 2: Implement Button State Machine

**Create:** `src/app/presentation/state/button_state_machine.py`

```python
class TestButtonState(Enum):
    INITIAL = "initial"
    COMPILING = "compiling"
    RUNNING = "running"
    COMPLETED = "completed"
    VIEWING_RESULTS = "viewing_results"

class TestButtonStateMachine:
    """
    Manages button visibility for test windows.
    
    States:
        INITIAL: Compile, Run visible
        COMPILING: Compile, Run visible
        RUNNING: Stop visible
        COMPLETED: Rerun visible
        VIEWING_RESULTS: Run visible (after back)
    """
    
    def __init__(self, buttons):
        self.state = TestButtonState.INITIAL
        self.buttons = buttons  # {name: button_widget}
        self._apply_state()
    
    def transition_to(self, new_state):
        self.state = new_state
        self._apply_state()
    
    def _apply_state(self):
        visibility = STATE_VISIBILITY_MAP[self.state]
        for button_name, visible in visibility.items():
            if button_name in self.buttons:
                self.buttons[button_name].setVisible(visible)
```

**Benefits:**
- Single source of truth for button states
- Prevent invalid state transitions
- Easy to visualize and test
- Eliminate state_view_active flag

**Estimated effort:** 1-2 days

---

#### Phase 3: Fix Memory Leaks in Status View Integration

**Changes needed:**

1. **Proper cleanup in base class:**
```python
def _integrate_status_view(self, status_view):
    # Clean up previous status view if exists
    if hasattr(self, '_active_status_view') and self._active_status_view:
        self._cleanup_status_view(self._active_status_view)
    
    # Store new status view
    self._active_status_view = status_view
    
    # Rest of implementation...

def _cleanup_status_view(self, status_view):
    """Properly cleanup status view resources."""
    if status_view:
        self.display_area.layout().removeWidget(status_view)
        status_view.deleteLater()
        status_view.setParent(None)
```

2. **Cleanup on window close:**
```python
def closeEvent(self, event):
    # Cleanup active status view
    if hasattr(self, '_active_status_view'):
        self._cleanup_status_view(self._active_status_view)
    
    # Cleanup display area
    if hasattr(self, '_original_display_content'):
        # Only cleanup if we actually swapped it out
        ...
    
    super().closeEvent(event)
```

**Benefits:**
- No memory leaks
- Clearer ownership of widgets
- Easier to track resources

**Estimated effort:** 1 day

---

#### Phase 4: Centralize Dialog Management

**Create:** `src/app/presentation/dialogs/`

Structure:
```
dialogs/
├── __init__.py
├── base_dialog.py           # Base dialog with common styling
├── message_boxes.py         # Unsaved changes, confirmations
├── config_dialog.py         # Move from core/config
├── test_detail_dialogs.py   # Move from widgets
└── error_dialog.py          # Move from config
```

**Benefits:**
- Single place to find all dialogs
- Consistent styling and behavior
- Reusable message box templates
- Better organization

**Estimated effort:** 2 days

---

#### Phase 5: Add Logging Infrastructure

**Create:** `src/app/shared/logging/`

Replace all `print()` statements with proper logging:

```python
from src.app.shared.logging import get_logger

logger = get_logger(__name__)

# Instead of:
print(f"Error creating window '{window_name}': {e}")

# Use:
logger.error(f"Failed to create window '{window_name}'", exc_info=e)
```

**Benefits:**
- Better debugging
- Log rotation and management
- Configurable log levels
- Easier to trace issues

**Estimated effort:** 2-3 days

---

#### Phase 6: Improve WindowManager

**Changes:**

1. **Add window lifecycle hooks:**
```python
class WindowManager(QStackedWidget):
    def show_window(self, window_name, **kwargs):
        window = self._get_or_create_window(window_name)
        
        # Call lifecycle hooks
        if hasattr(window, 'on_show'):
            window.on_show()
        
        # Existing show logic...
    
    def hide_window(self, window_name):
        window = self.windows.get(window_name)
        if window and hasattr(window, 'on_hide'):
            window.on_hide()
```

2. **Add max history size:**
```python
MAX_HISTORY_SIZE = 10

def show_window(self, window_name, **kwargs):
    # Existing logic...
    
    # Trim history if too long
    if len(self.window_history) > self.MAX_HISTORY_SIZE:
        self.window_history = self.window_history[-self.MAX_HISTORY_SIZE:]
```

3. **Add window caching strategy:**
```python
def cleanup_unused_windows(self):
    """Clean up windows not in history and not current."""
    unused = set(self.windows.keys()) - {self.current_window} - set(self.window_history)
    for window_name in unused:
        self.cleanup_window(window_name)
```

**Benefits:**
- Better memory management
- Clearer lifecycle
- Prevent history bloat
- More control over window persistence

**Estimated effort:** 2 days

---

### 12. Architectural Diagram (Proposed Future State)

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│  ┌────────────┬──────────────┬───────────────────────────┐  │
│  │ __main__.py│ MainWindow   │ WindowManager             │  │
│  │            │ (Container)  │ (Navigation & Lifecycle)  │  │
│  └────────────┴──────────────┴───────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ creates via factory
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Window Factory                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Lazy Import Registry                               │    │
│  │  main → MainWindowContent                           │    │
│  │  code_editor → CodeEditorWindow                     │    │
│  │  test_windows → ComparatorWindow, etc.              │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ instantiates
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Window Hierarchy                           │
│                                                              │
│  SidebarWindowBase                                           │
│  ├── MainWindowContent                                       │
│  ├── CodeEditorWindow                                        │
│  ├── TestWindowBase (NEW)                                    │
│  │   ├── ComparatorWindow                                    │
│  │   ├── ValidatorWindow                                     │
│  │   └── BenchmarkerWindow                                   │
│  ├── HelpCenterWindow                                        │
│  └── ResultsWindow                                           │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ uses
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 Shared Components                            │
│                                                              │
│  Widgets                  Dialogs                State       │
│  ├── Sidebar              ├── ConfigDialog       ├── Button │
│  ├── DisplayArea          ├── MessageBoxes       │   State  │
│  ├── StatusView           └── TestDetailDialogs  │   Machine│
│  ├── TestCards                                   └──────────│
│  └── Console                                                 │
└─────────────────────────────────────────────────────────────┘
```

---

### 13. Testing Strategy

#### Current State
- ❌ **No dedicated window tests** - only integration tests
- ❌ **Navigation not tested** - manual testing only
- ❌ **State transitions not tested** - button states unchecked

#### Recommended Tests

**Unit Tests:**
```python
# tests/unit/test_window_factory.py
def test_factory_creates_window():
    window = WindowFactory.create_window('comparator', parent=None)
    assert isinstance(window, ComparatorWindow)

# tests/unit/test_button_state_machine.py
def test_state_transition_running_to_completed():
    machine = TestButtonStateMachine(...)
    machine.transition_to(TestButtonState.COMPLETED)
    assert machine.state == TestButtonState.COMPLETED
    assert buttons['stop'].isVisible() == False
    assert buttons['rerun'].isVisible() == True
```

**Integration Tests:**
```python
# tests/integration/test_window_navigation.py
def test_navigate_from_main_to_comparator():
    manager = WindowManager()
    manager.show_window('main')
    manager.show_window('comparator')
    assert manager.current_window == 'comparator'
    assert 'main' in manager.window_history

def test_back_button_navigation():
    manager.show_window('main')
    manager.show_window('comparator')
    manager.go_back()
    assert manager.current_window == 'main'
```

**UI Tests:**
```python
# tests/ui/test_status_view_lifecycle.py
def test_status_view_integration():
    window = ComparatorWindow()
    window._on_testing_started()
    
    # Check status view is displayed
    assert hasattr(window, 'status_view')
    assert window.status_view.isVisible()
    
    # Check buttons switched
    assert window.compile_btn.isVisible() == False
    assert window.stop_btn.isVisible() == True
```

---

### 14. Migration Path

**Step-by-step refactoring without breaking existing functionality:**

#### Week 1: Foundation
1. Add logging infrastructure
2. Create TestWindowBase skeleton (coexist with current windows)
3. Add button state machine
4. Write unit tests for new components

#### Week 2: Test Window Migration
5. Migrate ComparatorWindow to use TestWindowBase
6. Run full test suite, fix issues
7. Migrate ValidatorWindow
8. Run full test suite, fix issues
9. Migrate BenchmarkerWindow
10. Run full test suite, fix issues

#### Week 3: Cleanup
11. Fix memory leaks in status view integration
12. Centralize dialog management
13. Improve WindowManager with lifecycle hooks
14. Add history size limit

#### Week 4: Polish
15. Add comprehensive tests
16. Update documentation
17. Remove dead code
18. Performance profiling and optimization

---

### 15. Conclusion

**Current State:**
The window management system is **functional but messy**, with significant code duplication and fragile state management.

**Root Causes:**
1. **Rapid development without refactoring** - features added without abstracting common patterns
2. **Copy-paste inheritance** - test windows copied from comparator
3. **No clear separation of concerns** - windows do too much

**Impact:**
- **High maintenance cost** - bug fixes must be applied 3× times
- **Difficult to extend** - adding new test type requires copying 200+ lines
- **Memory leaks** - status views and buttons not properly cleaned up
- **Fragile navigation** - history management can break

**Priority Actions:**
1. **Extract TestWindowBase** - eliminate 600+ lines of duplication
2. **Implement state machine** - fix button state management
3. **Fix memory leaks** - proper cleanup of status views
4. **Add logging** - replace print statements

**Estimated Effort:**
- Critical fixes: 1-2 weeks
- Full refactor: 3-4 weeks
- Testing and polish: 1 week

**Long-term Benefits:**
- **50% less code to maintain** in test windows
- **Easier to add features** - change in one place
- **More reliable** - state machine prevents invalid states
- **Better performance** - no memory leaks
- **Easier to test** - clearer separation of concerns

---

### Appendix A: File Map

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `__main__.py` | Entry point | 138 | ✓ Clean |
| `main_window.py` | Main window + content | 326 | ⚠️ Needs cleanup |
| `window_management.py` | Factory + manager | 239 | ⚠️ Needs improvements |
| `base_window.py` | Base for sidebar windows | 252 | ❌ Memory leaks |
| `code_editor_window.py` | Code editor | 315 | ⚠️ Complexity high |
| `comparator_window.py` | Comparator tests | 294 | ❌ Duplicate code |
| `validator_window.py` | Validator tests | 294 | ❌ Duplicate code |
| `benchmarker_window.py` | Benchmarker tests | 305 | ❌ Duplicate code |
| `help_center_window.py` | Help docs | 67 | ✓ Clean |
| `results_window.py` | Results viewer | 90 | ✓ Clean |

**Total Lines in views/**: ~2,620  
**Duplicate Lines**: ~600 (23%)  
**Reduction Potential**: ~400 lines (15%)

---

### Appendix B: Signal Flow Diagram

```
User Click                  Window                  WindowManager
──────────                  ──────                  ─────────────
    │                          │                          │
    │  Click "Compare"         │                          │
    ├─────────────────────────>│                          │
    │                          │                          │
    │                          │  button_clicked("Compare")
    │                          │                          │
    │                          │  show_window('comparator')│
    │                          ├─────────────────────────>│
    │                          │                          │
    │                          │                          │ Create/get window
    │                          │                          │ setCurrentWidget
    │                          │                          │
    │                          │<─────────────────────────┤
    │                          │                          │
    │                     Window shown                    │
    │<─────────────────────────┤                          │
    │                          │                          │
    │  Click "Run"             │                          │
    ├─────────────────────────>│                          │
    │                          │                          │
    │                          │  run_comparison_test()   │
    │                          │                          │
    │                          │  Tool creates worker     │
    │                          │  Signals connected       │
    │                          │                          │
    │                          │  testingStarted          │
    │                          ├──────────┐               │
    │                          │          │               │
    │                          │<─────────┘               │
    │                          │                          │
    │                          │  _on_testing_started()   │
    │                          │  Create StatusView       │
    │                          │  Integrate into display  │
    │                          │  Switch button state     │
    │                          │                          │
    │                   Status view shown                 │
    │<─────────────────────────┤                          │
```

---

**Document End**
