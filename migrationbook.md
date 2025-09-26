# Widget System Migration Book
## Code Testing Suite - Presentation Layer Reorganization

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)  
3. [Target Architecture](#target-architecture)
4. [Migration Plan](#migration-plan)
5. [Implementation Steps](#implementation-steps)
6. [Testing Strategy](#testing-strategy)
7. [Rollback Plan](#rollback-plan)

---

## Executive Summary

This migration book outlines the comprehensive reorganization of the widget system in the Code Testing Suite presentation layer. The goal is to create a more modular, reusable widget architecture while consolidating duplicate status windows into embedded display area components.

### Key Objectives:
1. **Create `sidebar_widgets/` directory** - Centralize all sidebar-specific widgets (sliders, headers, footers)
2. **Reorganize `display_area_widgets/`** - Add status tracking and results widgets
3. **Eliminate popup status windows** - Convert status dialogs to embedded display area widgets
4. **Consolidate duplicated widgets** - Remove the 3 identical `TestCountSlider` classes
5. **Improve modularity** - Create reusable, configurable widget components

### Impact Assessment:
- **Files to be created:** 12+ new widget files
- **Files to be modified:** 25+ existing presentation files  
- **Files to be deleted:** 4 duplicate status window files
- **New directories:** 2 (`sidebar_widgets/`, updated `display_area_widgets/`)
- **Migration complexity:** High (affects core UI architecture)
- **Estimated timeline:** 2-3 weeks

---

## Current State Analysis

### 1. Current Widget Structure
```
src/app/presentation/widgets/
├── __init__.py
├── sidebar.py                    # Main sidebar component
├── display_area.py              # Generic display area
└── display_area_widgets/
    ├── __init__.py
    ├── ai_panel.py              # AI assistance panel
    ├── console.py               # Console output/input
    └── editor.py                # Code editor widget
```

### 2. Current Sidebar Widget Usage Patterns

#### 2.1 Duplicated TestCountSlider Classes
**Location:** Scattered across view-specific directories
- `src/app/presentation/views/validator/test_count_slider.py` (113 lines)
- `src/app/presentation/views/comparator/test_count_slider.py` (113 lines)  
- `src/app/presentation/views/benchmarker/test_count_slider.py` (110 lines)

**Analysis:**
```python
# Current duplicated pattern in each view:
class TestCountSlider(QWidget):
    valueChanged = Signal(int)
    
    def __init__(self, parent=None):
        # Nearly identical setup code
        # Only differences: max values and defaults
        # Validator: max=500, default=10
        # Comparator: max=500, default=10  
        # Benchmarker: max=100, default=5
```

**Issues:**
- 336+ lines of duplicated code
- Maintenance nightmare for bug fixes
- Inconsistent behavior potential
- Testing redundancy

#### 2.2 Sidebar Sections and Buttons
**Current Pattern:**
```python
# Repeated in every window:
options_section = self.sidebar.add_section("Number of Tests")
self.test_count_slider = TestCountSlider()
self.test_count_slider.valueChanged.connect(self.handle_test_count_changed)
options_section.layout().addWidget(self.test_count_slider)
```

**Reusable Components Identified:**
- Test count control section
- Action button groups (Compile, Run)
- History/Results sections
- Header titles with consistent styling
- Footer button layouts

### 3. Current Status Window Architecture

#### 3.1 Status Window Classes
**Popup Dialog Pattern:**
- `ValidatorStatusWindow` (242 lines) - Validation progress tracking
- `CompareStatusWindow` (163 lines) - Comparison test progress
- `BenchmarkStatusWindow` (262 lines) - Performance test tracking  
- `CompilationStatusWindow` (~150 lines) - Compilation progress

**Common Features Analysis:**
```python
# Shared patterns across all status windows:
class StatusWindow(QDialog):
    def __init__(self, parent=None):
        # Common setup:
        self.setWindowTitle("...")
        self.setMinimumSize(500, 400)
        
        # Common widgets:
        self.status_label = QLabel("...")
        self.progress_bar = QProgressBar()
        self.results_area = QTextEdit()
        self.close_button = QPushButton("Close")
        
    # Common methods:
    def show_test_running(self, current, total):
    def show_test_complete(self, ...):
    def show_all_complete(self, success):
```

#### 3.2 Status Window Usage Pattern
**Current Implementation:**
```python
# In core/tools/*.py:
def _create_test_status_window(self):
    return ValidatorStatusWindow()  # or CompareStatusWindow, etc.

# Usage:
self.status_window = self._create_test_status_window()
self.status_window.show()
```

**Problems:**
- Blocks main UI with modal dialogs
- Inconsistent UX across different test types
- Cannot see code/console while tests run
- Poor integration with main workflow

### 4. Current Display Area Structure

#### 4.1 Display Area Implementations
**View-Specific Display Areas:**
- `ValidatorDisplay` (271 lines) - File editing for validation tests
- `ComparatorDisplay` (209 lines) - File editing for comparison tests  
- `BenchmarkerDisplay` (estimated ~200 lines) - File editing for benchmark tests

**Common Pattern:**
```python
class *Display(QWidget):
    def __init__(self):
        # Common setup:
        self.splitter = QSplitter(Qt.Horizontal)
        self.editor = EditorWidget()
        self.console = ConsoleOutput()
        self.ai_panel = AIPanel()
        
        # File buttons (90% identical):
        self.file_buttons = {}
        for name in ['Generator', 'Test Code', 'Other Code']:
            btn = QPushButton(name)
            self.file_buttons[name] = btn
```

---

## Target Architecture

### 1. New Widget Structure

```
src/app/presentation/widgets/
├── __init__.py
├── sidebar.py                           # Main sidebar (updated)
├── display_area.py                     # Base display area (updated)
├── sidebar_widgets/                    # NEW - Sidebar-specific widgets
│   ├── __init__.py
│   ├── test_count_slider.py           # Consolidated slider widget
│   ├── sidebar_header.py              # Reusable header component  
│   ├── sidebar_section.py             # Enhanced section widget
│   ├── action_button_group.py         # Grouped action buttons
│   ├── footer_controls.py             # Footer button layouts
│   └── progress_indicator.py          # In-sidebar progress display
└── display_area_widgets/               # UPDATED - Enhanced with status widgets
    ├── __init__.py
    ├── ai_panel.py                    # AI assistance (unchanged)
    ├── console.py                     # Console (unchanged)  
    ├── editor.py                      # Code editor (unchanged)
    ├── test_status_widget.py          # NEW - Embedded test status
    ├── test_results_widget.py         # NEW - Test results display
    ├── progress_panel.py              # NEW - Progress tracking panel
    └── file_manager_panel.py          # NEW - File management widget
```

### 2. Consolidated Test Status Architecture

#### 2.1 Embedded Status Widget
**Replace popup dialogs with embedded widgets:**
```python
class TestStatusWidget(QWidget):
    """Unified test status widget for all test types"""
    
    def __init__(self, test_type="generic", parent=None):
        self.test_type = test_type  # 'validator', 'comparator', 'benchmarker'
        self._setup_ui_for_type()
        
    def _setup_ui_for_type(self):
        if self.test_type == "validator":
            self._setup_validator_ui()
        elif self.test_type == "comparator":  
            self._setup_comparator_ui()
        elif self.test_type == "benchmarker":
            self._setup_benchmarker_ui()
            
    # Unified interface:
    def show_test_running(self, current, total, **kwargs):
    def show_test_complete(self, **kwargs):
    def show_all_complete(self, success):
```

#### 2.2 Display Area Integration
**New Display Area Layout:**
```
Display Area Layout:
┌─────────────────┬─────────────────────┐
│                 │                     │
│                 │   Test Status       │
│   Editor        │   Widget            │
│   Panel         │   ┌───────────────┐ │
│                 │   │ Progress Bar  │ │
│                 │   │ Current Test  │ │
│                 │   │ Results       │ │
│                 │   └───────────────┘ │
├─────────────────┼─────────────────────┤
│                 │                     │
│   Console       │   Test Results      │
│   Output        │   History           │
│                 │                     │
└─────────────────┴─────────────────────┘
```

### 3. Sidebar Widget System

#### 3.1 Configurable Test Count Slider
```python
class TestCountSlider(QWidget):
    """Unified, configurable test count slider"""
    
    def __init__(self, min_value=1, max_value=500, default_value=10, parent=None):
        # Single implementation with configuration
        self.min_value = min_value
        self.max_value = max_value
        self.default_value = default_value
        
    @classmethod  
    def for_validator(cls, parent=None):
        return cls(min_value=1, max_value=500, default_value=10, parent=parent)
        
    @classmethod
    def for_comparator(cls, parent=None):
        return cls(min_value=1, max_value=500, default_value=10, parent=parent)
        
    @classmethod  
    def for_benchmarker(cls, parent=None):
        return cls(min_value=1, max_value=100, default_value=5, parent=parent)
```

#### 3.2 Reusable Sidebar Sections
```python
class SidebarSection(QFrame):
    """Enhanced sidebar section with built-in widgets"""
    
    @staticmethod
    def create_test_options_section(test_type, parent_sidebar):
        section = SidebarSection("Number of Tests")
        
        if test_type == "validator":
            slider = TestCountSlider.for_validator()
        elif test_type == "comparator":
            slider = TestCountSlider.for_comparator()  
        elif test_type == "benchmarker":
            slider = TestCountSlider.for_benchmarker()
            
        section.add_widget(slider)
        parent_sidebar.add_section_widget(section)
        return section, slider
        
    @staticmethod
    def create_action_section(actions, parent_sidebar):
        section = SidebarSection("Actions") 
        button_group = ActionButtonGroup(actions)
        section.add_widget(button_group)
        return section, button_group
```

---

## Migration Plan

### Phase 1: Foundation Setup (Days 1-3)
**Goal:** Create new directory structure and base classes

#### Day 1: Directory Structure & Base Classes
1. **Create new directories:**
   ```bash
   mkdir src/app/presentation/widgets/sidebar_widgets
   mkdir src/app/presentation/widgets/sidebar_widgets/__pycache__
   ```

2. **Create base widget classes:**
   - `sidebar_widgets/__init__.py` - Export definitions
   - `sidebar_widgets/base_sidebar_widget.py` - Base class for sidebar widgets
   - `display_area_widgets/base_status_widget.py` - Base class for status widgets

#### Day 2: Consolidated TestCountSlider  
1. **Create unified slider:**
   - Move and consolidate `TestCountSlider` to `sidebar_widgets/test_count_slider.py`
   - Add configuration parameters (min, max, default values)
   - Create factory methods for each test type
   - Add comprehensive unit tests

2. **Update imports temporarily:**
   - Keep old sliders in place temporarily
   - Add compatibility imports to prevent breaking changes

#### Day 3: Sidebar Enhancement Components
1. **Create sidebar widget components:**
   - `sidebar_widgets/sidebar_header.py` - Title headers with consistent styling
   - `sidebar_widgets/sidebar_section.py` - Enhanced section with built-in widgets  
   - `sidebar_widgets/action_button_group.py` - Grouped action buttons
   - `sidebar_widgets/footer_controls.py` - Footer layouts and buttons

### Phase 2: Status Widget Development (Days 4-8)

#### Day 4: Base Status Widget
1. **Create unified status widget base:**
   ```python
   # display_area_widgets/base_status_widget.py
   class BaseStatusWidget(QWidget):
       testStarted = Signal(int, int)      # current, total
       testCompleted = Signal(dict)        # test results
       allCompleted = Signal(bool)         # success/failure
       
       def __init__(self, test_type, parent=None):
           self.test_type = test_type
           self._setup_common_ui()
           self._setup_type_specific_ui()
   ```

2. **Design common interface:**
   - Progress tracking methods
   - Result display methods  
   - Configuration methods

#### Day 5-6: Type-Specific Status Widgets
1. **Validator Status Widget:**
   ```python
   # display_area_widgets/validator_status_widget.py  
   class ValidatorStatusWidget(BaseStatusWidget):
       def __init__(self, parent=None):
           super().__init__("validator", parent)
           
       def _setup_type_specific_ui(self):
           # Stage indicators (Generator → Test → Validator)
           # Validation-specific progress display
   ```

2. **Comparator Status Widget:**
   ```python
   # display_area_widgets/comparator_status_widget.py
   class ComparatorStatusWidget(BaseStatusWidget):
       def __init__(self, parent=None):
           super().__init__("comparator", parent) 
           
       def _setup_type_specific_ui(self):
           # Input/Output comparison display
           # Test history panel
   ```

3. **Benchmarker Status Widget:**
   ```python
   # display_area_widgets/benchmarker_status_widget.py
   class BenchmarkerStatusWidget(BaseStatusWidget):
       def __init__(self, parent=None):
           super().__init__("benchmarker", parent)
           
       def _setup_type_specific_ui(self):
           # Time/Memory usage display
           # Performance metrics panel
   ```

#### Day 7-8: Results and Progress Widgets
1. **Create supporting widgets:**
   - `display_area_widgets/test_results_widget.py` - Historical results display
   - `display_area_widgets/progress_panel.py` - Progress tracking panel
   - `display_area_widgets/file_manager_panel.py` - File management widget

### Phase 3: Display Area Integration (Days 9-12)

#### Day 9-10: Update Display Areas
1. **Create enhanced base display area:**
   ```python
   # widgets/display_area.py (updated)
   class DisplayArea(QWidget):
       def __init__(self, display_type="generic", parent=None):
           self.display_type = display_type
           self._setup_base_layout()
           self._add_status_widget()
           
       def _add_status_widget(self):
           if self.display_type == "validator":
               self.status_widget = ValidatorStatusWidget()
           elif self.display_type == "comparator":
               self.status_widget = ComparatorStatusWidget()
           elif self.display_type == "benchmarker":  
               self.status_widget = BenchmarkerStatusWidget()
   ```

2. **Update specific display areas:**
   - Modify `ValidatorDisplay` to use new status widget
   - Modify `ComparatorDisplay` to use new status widget  
   - Modify `BenchmarkerDisplay` to use new status widget

#### Day 11-12: Layout Integration
1. **Implement new layout system:**
   - 4-panel layout (Editor, Status, Console, Results)
   - Splitter configuration for optimal UX
   - Responsive design for different window sizes

2. **Update splitter logic:**
   - Configure collapsible panels
   - Set minimum/maximum sizes
   - Implement layout persistence

### Phase 4: Window Updates (Days 13-15)

#### Day 13-14: Update Window Classes
1. **Update all test windows:**
   ```python
   # views/validator/validator_window.py (updated)
   class ValidatorWindow(SidebarWindowBase):
       def __init__(self, parent=None):
           super().__init__(parent, title=None)
           
           # Use new sidebar widgets:
           self.sidebar = Sidebar("Validator")
           section, slider = SidebarSection.create_test_options_section(
               "validator", self.sidebar)
           self.test_count_slider = slider
           
           # Use enhanced display area:
           self.display_area = DisplayArea("validator")
   ```

2. **Remove old status window usage:**
   - Update `ValidatorWindow` to use embedded status
   - Update `ComparatorWindow` to use embedded status
   - Update `BenchmarkerWindow` to use embedded status

#### Day 15: Core Tools Integration  
1. **Update core tool classes:**
   ```python
   # core/tools/validator.py (updated) 
   class ValidatorRunner:
       def __init__(self, workspace_dir):
           # Remove status window creation
           # Connect to display area status widget instead
           
       def run_validation_test(self, test_count):
           # Emit signals to display area instead of popup
           self.display_area.status_widget.show_test_running(1, test_count)
   ```

### Phase 5: Testing & Cleanup (Days 16-18)

#### Day 16: Integration Testing
1. **Test all window types:**
   - Validator window functionality  
   - Comparator window functionality
   - Benchmarker window functionality

2. **Test status widget integration:**
   - Progress tracking accuracy
   - Result display correctness
   - Error handling robustness

#### Day 17: Cleanup Old Code
1. **Remove duplicate files:**
   - Delete `views/*/test_count_slider.py` files (3 files)
   - Delete old status window files (4 files)
   - Clean up unused imports

2. **Update documentation:**
   - Update widget usage documentation
   - Create migration notes for developers  
   - Update architecture diagrams

#### Day 18: Final Testing & Polish
1. **End-to-end testing:**
   - Complete test workflows in all windows
   - UI responsiveness testing
   - Performance regression testing

2. **Code quality checks:**
   - Run linting and formatting
   - Verify test coverage
   - Code review preparation

---

## Implementation Steps

### Step 1: Create Foundation Structure

```bash
# Create new directories
mkdir -p src/app/presentation/widgets/sidebar_widgets
mkdir -p src/app/presentation/widgets/display_area_widgets/status

# Create __init__.py files
touch src/app/presentation/widgets/sidebar_widgets/__init__.py
```

### Step 2: Implement Consolidated TestCountSlider

**File: `src/app/presentation/widgets/sidebar_widgets/test_count_slider.py`**
```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider, QHBoxLayout, QLineEdit
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator
from src.app.presentation.styles.style import MATERIAL_COLORS
from src.app.presentation.styles.components.test_view_styles import TEST_VIEW_SLIDER_STYLE

class TestCountSlider(QWidget):
    """Unified, configurable test count slider for all test types"""
    valueChanged = Signal(int)
    
    def __init__(self, min_value=1, max_value=500, default_value=10, parent=None):
        super().__init__(parent)
        self.min_value = min_value
        self.max_value = max_value
        self.default_value = default_value
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        
        # Slider and input container
        slider_container = QHBoxLayout()
        slider_container.setSpacing(0)
        slider_container.setContentsMargins(0, 0, 0, 0)
        
        # Create slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(self.min_value)
        self.slider.setMaximum(self.max_value)
        self.slider.setValue(self.default_value)
        self.slider.setStyleSheet(TEST_VIEW_SLIDER_STYLE)
        
        # Editable input field
        self.value_input = QLineEdit(str(self.default_value))
        self.value_input.setValidator(QIntValidator(self.min_value, self.max_value))
        self.value_input.setFixedWidth(50)
        self.value_input.setAlignment(Qt.AlignCenter)
        
        # Add widgets to layouts
        slider_container.addWidget(self.slider)
        slider_container.addWidget(self.value_input)
        layout.addLayout(slider_container)
        
        # Connect signals
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.value_input.textChanged.connect(self._on_input_changed)
        
        # Setup styling
        self._setup_input_styles()
    
    @classmethod
    def for_validator(cls, parent=None):
        """Create slider configured for validator tests"""
        return cls(min_value=1, max_value=500, default_value=10, parent=parent)
        
    @classmethod
    def for_comparator(cls, parent=None):
        """Create slider configured for comparison tests"""
        return cls(min_value=1, max_value=500, default_value=10, parent=parent)
        
    @classmethod
    def for_benchmarker(cls, parent=None):
        """Create slider configured for benchmark tests"""
        return cls(min_value=1, max_value=100, default_value=5, parent=parent)
    
    def _setup_input_styles(self):
        """Style the input field"""
        input_style = f"""
            QLineEdit {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                           stop:0 rgba(20, 24, 28, 0.8),
                           stop:1 rgba(14, 17, 20, 0.8));
                border: 1px solid {MATERIAL_COLORS['outline']};
                border-radius: 8px;
                color: {MATERIAL_COLORS['text_primary']};
                padding: 6px 8px;
                font-size: 12px;
                font-weight: 500;
                selection-background-color: {MATERIAL_COLORS['primary']}40;
                selection-color: {MATERIAL_COLORS['on_primary']};
            }}
            
            QLineEdit:hover {{
                border: 1px solid {MATERIAL_COLORS['primary']};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                           stop:0 {MATERIAL_COLORS['primary']}10,
                           stop:1 rgba(255, 255, 255, 0.08));
            }}
            
            QLineEdit:focus {{
                border: 2px solid {MATERIAL_COLORS['primary']};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                           stop:0 {MATERIAL_COLORS['primary']}15,
                           stop:1 rgba(255, 255, 255, 0.08));
                outline: none;
            }}
        """
        self.value_input.setStyleSheet(input_style)
    
    def _on_slider_changed(self, value):
        """Update input field when slider changes"""
        self.value_input.setText(str(value))
        self.valueChanged.emit(value)
    
    def _on_input_changed(self, text):
        """Update slider when input field changes"""
        try:
            if text and text.isdigit():
                value = int(text)
                if self.min_value <= value <= self.max_value:
                    self.slider.blockSignals(True)
                    self.slider.setValue(value)
                    self.slider.blockSignals(False)
                    self.valueChanged.emit(value)
        except ValueError:
            pass
    
    def value(self):
        return self.slider.value()
    
    def set_value(self, value):
        """Set the value programmatically"""
        if self.min_value <= value <= self.max_value:
            self.slider.setValue(value)
            self.value_input.setText(str(value))
```

### Step 3: Implement Base Status Widget

**File: `src/app/presentation/widgets/display_area_widgets/base_status_widget.py`**
```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QTextEdit, QFrame
from PySide6.QtCore import Qt, Signal
from abc import ABC, abstractmethod

class BaseStatusWidget(QWidget, ABC):
    """Base class for all test status widgets"""
    
    # Common signals
    testStarted = Signal(int, int)      # current_test, total_tests
    testCompleted = Signal(dict)        # test_result_data
    allCompleted = Signal(bool)         # success_status
    
    def __init__(self, test_type, parent=None):
        super().__init__(parent)
        self.test_type = test_type
        self.current_test = 0
        self.total_tests = 0
        self.test_results = []
        
        self.setObjectName("status_widget")
        self._setup_common_ui()
        self._setup_type_specific_ui()
        self._setup_styles()
    
    def _setup_common_ui(self):
        """Setup UI components common to all status widgets"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Status header
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status_label")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("status_progress")
        layout.addWidget(self.progress_bar)
        
        # Results area
        self.results_area = QTextEdit()
        self.results_area.setObjectName("status_results")
        self.results_area.setReadOnly(True)
        self.results_area.setMaximumHeight(150)
        layout.addWidget(self.results_area)
    
    @abstractmethod
    def _setup_type_specific_ui(self):
        """Setup UI components specific to test type"""
        pass
    
    @abstractmethod  
    def _setup_styles(self):
        """Apply styles specific to test type"""
        pass
    
    def show_test_running(self, current, total, **kwargs):
        """Show that a test is running"""
        self.current_test = current
        self.total_tests = total
        
        self.status_label.setText(f"Running Test {current}/{total}...")
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current - 1)
        
        self.testStarted.emit(current, total)
        self._handle_test_running(current, total, **kwargs)
    
    def show_test_complete(self, result_data):
        """Show that a test has completed"""
        self.test_results.append(result_data)
        self.progress_bar.setValue(self.current_test)
        
        self.testCompleted.emit(result_data)
        self._handle_test_complete(result_data)
    
    def show_all_complete(self, success):
        """Show that all tests have completed"""
        if success:
            self.status_label.setText("All Tests Completed Successfully ✓")
        else:
            self.status_label.setText("Tests Completed with Failures ✗")
            
        self.allCompleted.emit(success)
        self._handle_all_complete(success)
    
    @abstractmethod
    def _handle_test_running(self, current, total, **kwargs):
        """Handle test type specific running logic"""
        pass
    
    @abstractmethod
    def _handle_test_complete(self, result_data):
        """Handle test type specific completion logic"""
        pass
    
    @abstractmethod
    def _handle_all_complete(self, success):
        """Handle test type specific all complete logic"""
        pass
```

### Step 4: Update Window Classes

**Example: Update ValidatorWindow**
```python
# views/validator/validator_window.py (updated)
from src.app.presentation.widgets.sidebar_widgets.test_count_slider import TestCountSlider

class ValidatorWindow(SidebarWindowBase):
    def __init__(self, parent=None):
        super().__init__(parent, title=None)
        
        self.sidebar = Sidebar("Validator")
        
        # Use new consolidated slider
        options_section = self.sidebar.add_section("Number of Tests")
        self.test_count_slider = TestCountSlider.for_validator()
        self.test_count_slider.valueChanged.connect(self.handle_test_count_changed)
        options_section.layout().addWidget(self.test_count_slider)
        
        # Rest of setup...
        # Create display area with embedded status widget
        self.display_area = ValidatorDisplay()  # Will include embedded status widget
```

---

## Testing Strategy

### 1. Unit Testing
**New Test Files:**
- `tests/unit/widgets/test_sidebar_widgets/`
  - `test_test_count_slider.py` - Test consolidated slider functionality
  - `test_sidebar_components.py` - Test sidebar widget components
- `tests/unit/widgets/test_display_area_widgets/`
  - `test_status_widgets.py` - Test status widget functionality
  - `test_integration.py` - Test display area integration

**Test Coverage Requirements:**
- 90%+ coverage for all new widget classes
- Regression tests for existing functionality
- UI interaction tests using Qt Test Framework

### 2. Integration Testing
**Test Scenarios:**
1. **Complete test workflow** - Run tests from start to finish in each window
2. **Status widget updates** - Verify status updates correctly during tests
3. **Widget communication** - Test signal/slot connections between widgets
4. **Layout responsiveness** - Test UI with different window sizes

### 3. UI Testing
**Manual Test Checklist:**
- [ ] Validator window displays status inline (no popup)
- [ ] Comparator window displays status inline (no popup)  
- [ ] Benchmarker window displays status inline (no popup)
- [ ] Test count sliders work consistently across all windows
- [ ] Progress tracking shows correct information
- [ ] Results display properly in embedded widgets
- [ ] Window resizing works correctly with new layout
- [ ] All existing functionality preserved

---

## Rollback Plan

### Rollback Strategy
If critical issues arise during migration, the following rollback approach will be used:

#### Level 1: Partial Rollback (Recommended)
**Revert specific components while keeping others:**
1. **If status widgets fail:** Restore popup dialogs temporarily
2. **If sidebar widgets fail:** Restore original duplicate sliders temporarily  
3. **If display areas fail:** Restore original display area implementations

**Commands:**
```bash
# Revert specific files
git checkout HEAD~1 -- src/app/presentation/views/*/test_count_slider.py
git checkout HEAD~1 -- src/app/presentation/views/*/*status_window.py

# Remove new directories if needed
rm -rf src/app/presentation/widgets/sidebar_widgets
```

#### Level 2: Complete Rollback (Emergency)
**Revert entire migration:**
```bash
# Revert all presentation layer changes
git checkout HEAD~N -- src/app/presentation/

# Where N is the number of commits to roll back
```

### Rollback Testing
After rollback:
1. **Functionality verification** - All original features work
2. **UI verification** - All windows display correctly  
3. **Test execution** - All test types execute successfully
4. **Integration verification** - Core tools integrate properly

### Post-Rollback Actions
1. **Document issues** - Record what caused the rollback
2. **Plan fixes** - Address root causes before re-attempting
3. **Communication** - Notify team about rollback and next steps
4. **Data preservation** - Ensure no user data was lost

---

## Conclusion

This migration will significantly improve the Code Testing Suite's presentation layer by:

1. **Eliminating 300+ lines** of duplicated code
2. **Creating reusable widgets** that can be shared across windows  
3. **Improving user experience** with embedded status tracking
4. **Establishing patterns** for future widget development
5. **Reducing maintenance burden** through consolidation

The phased approach ensures minimal risk while delivering maximum value. Each phase builds upon the previous one, allowing for incremental testing and validation.

**Success Metrics:**
- Zero functionality regression
- Improved development velocity (less duplicate code to maintain)
- Better user experience (no modal dialogs blocking workflow)
- Increased code reusability across the application
- Simplified testing requirements

**Timeline:** 18 working days with proper testing and validation at each step.