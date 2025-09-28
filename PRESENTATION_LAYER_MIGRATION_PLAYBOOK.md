# Presentation Layer Refactoring Migration Playbook
**Date**: September 28, 2025  
**Version**: 1.0  
**Scope**: Eliminate code duplication, remove dead code, and standardize presentation layer architecture

## 🎯 **OVERVIEW**

This playbook provides an atomic, step-by-step migration plan to refactor the presentation layer, eliminating massive code duplication and architectural inconsistencies while maintaining system stability.

## 📊 **CURRENT STATE ANALYSIS**

### Critical Issues Identified:
- **95%+ code duplication** across test windows (Validator, Comparator, Benchmarker)
- **90%+ code duplication** across display areas  
- **176 lines of dead code** in `comparator_display_area_old.py`
- **Inconsistent import patterns** for `MATERIAL_COLORS`
- **Duplicate dialog patterns** for save/discard operations
- **Fragmented status window implementations**

### Impact Metrics:
- **~2000+ lines** of duplicated code
- **3 identical window classes** with minor variations
- **3 identical display area classes** with minor variations  
- **Multiple duplicated dialog patterns**

## 🚦 **MIGRATION STRATEGY**

### Core Principles:
1. **Atomic Operations**: Each step is self-contained and reversible
2. **Zero Downtime**: System remains functional throughout migration
3. **Backward Compatibility**: Maintain existing API contracts
4. **Test Coverage**: Verify functionality at each step
5. **Incremental Progress**: Small, verifiable changes

## 📋 **MIGRATION PHASES**

---

## **PHASE 1: FOUNDATION SETUP** 
*Duration: 2-3 hours*  
*Risk: LOW*

### Step 1.1: Remove Dead Code
**Objective**: Clean up unused files immediately

**Actions**:
```bash
# 1. Verify no references to old file
git grep -r "comparator_display_area_old" src/
# Expected: No matches

# 2. Remove dead file
rm src/app/presentation/views/comparator/comparator_display_area_old.py

# 3. Commit atomic change
git add -A
git commit -m "refactor: remove dead code - comparator_display_area_old.py"
```

**Validation**: 
- [ ] Application starts successfully
- [ ] All test windows function normally
- [ ] No import errors

### Step 1.2: Standardize Import Patterns  
**Objective**: Fix inconsistent imports

**Actions**:
```python
# Strategy: Use single source for MATERIAL_COLORS
# All files should import from: src.app.presentation.styles.constants

# Files to update:
# - src/app/presentation/widgets/sidebar_widgets/test_count_slider.py
# - src/app/presentation/widgets/sidebar_widgets/limits_input_widget.py
# - src/app/presentation/views/validator/validator_status_window.py
# - src/app/presentation/views/validator/validator_display_area.py
# - src/app/presentation/views/results/results_widget.py
# - src/app/presentation/views/results/detailed_results_widget.py
# - src/app/presentation/views/comparator/compare_status_window.py
# - src/app/presentation/views/comparator/comparator_display_area.py
# - src/app/presentation/views/code_editor/code_editor_display_area.py
# - src/app/presentation/views/benchmarker/benchmark_status_window.py
# - src/app/presentation/views/benchmarker/benchmarker_display_area.py
# - src/app/presentation/styles/components/config_ui.py
# - src/app/presentation/styles/components/test_view_styles.py
```

**Change Pattern**:
```python
# FROM:
from src.app.presentation.styles.style import MATERIAL_COLORS

# TO:
from src.app.presentation.styles.constants import MATERIAL_COLORS
```

**Commit Strategy**: One commit per file for easy rollback

**Validation**:
- [ ] No import errors
- [ ] UI styling remains unchanged
- [ ] All windows load correctly

---

## **PHASE 2: BASE CLASS INFRASTRUCTURE**
*Duration: 4-6 hours*  
*Risk: MEDIUM*

### Step 2.1: Create Dialog Utilities
**Objective**: Eliminate duplicate dialog patterns

**File**: `src/app/presentation/utils/dialog_utils.py`

```python
# -*- coding: utf-8 -*-
"""
Dialog utility functions for consistent UI dialogs across the application.
"""
from PySide6.QtWidgets import QMessageBox
from typing import Optional, Union

class DialogResult:
    SAVE = "save"
    DISCARD = "discard" 
    CANCEL = "cancel"

def show_save_changes_dialog(parent, filename: str) -> str:
    """
    Show standardized save changes dialog.
    
    Args:
        parent: Parent widget
        filename: Name of file with unsaved changes
        
    Returns:
        DialogResult constant
    """
    reply = QMessageBox.question(
        parent, 
        'Save Changes?',
        f'Save changes to {filename}?',
        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
    )
    
    if reply == QMessageBox.Save:
        return DialogResult.SAVE
    elif reply == QMessageBox.Discard:
        return DialogResult.DISCARD
    else:
        return DialogResult.CANCEL

def show_error_dialog(parent, title: str, message: str):
    """Show standardized error dialog."""
    QMessageBox.critical(parent, title, message)
    
def show_info_dialog(parent, title: str, message: str):
    """Show standardized info dialog."""
    QMessageBox.information(parent, title, message)

def show_warning_dialog(parent, title: str, message: str):
    """Show standardized warning dialog."""
    QMessageBox.warning(parent, title, message)
```

### Step 2.2: Create Base Status Window
**Objective**: Common status dialog functionality

**File**: `src/app/presentation/views/base_status_window.py`

```python
# -*- coding: utf-8 -*-
"""
Base status window for test operations with common functionality.
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QProgressBar, QPushButton, QTextEdit)
from PySide6.QtCore import Qt, Signal
from src.app.presentation.styles.constants import MATERIAL_COLORS
from src.app.presentation.styles.components.test_view_styles import (
    TEST_VIEW_COMPILATION_STATUS_DIALOG_STYLE,
    TEST_VIEW_COMPILATION_STATUS_LABEL_STYLE,
    TEST_VIEW_COMPILATION_PROGRESS_BAR_STYLE,
)

class BaseStatusWindow(QDialog):
    """Base class for status windows with common layout and functionality."""
    
    # Signals
    cancelRequested = Signal()
    
    def __init__(self, parent=None, title="Status", size=(500, 400)):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(*size)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup common UI elements."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Main status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet(TEST_VIEW_COMPILATION_STATUS_LABEL_STYLE)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(TEST_VIEW_COMPILATION_PROGRESS_BAR_STYLE)
        layout.addWidget(self.progress_bar)
        
        # Custom content area (to be implemented by subclasses)
        self.content_widget = self._create_content_widget()
        if self.content_widget:
            layout.addWidget(self.content_widget)
        
        # Button area
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancelRequested.emit)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def _create_content_widget(self):
        """Override in subclasses to add custom content."""
        return None
        
    def update_status(self, message: str, progress: int = None):
        """Update status message and optional progress."""
        self.status_label.setText(message)
        if progress is not None:
            self.progress_bar.setValue(progress)
            
    def set_progress_range(self, min_val: int, max_val: int):
        """Set progress bar range."""
        self.progress_bar.setRange(min_val, max_val)
```

### Step 2.3: Create Base Test Display
**Objective**: Common display area functionality

**File**: `src/app/presentation/views/base_test_display.py`

```python
# -*- coding: utf-8 -*-
"""
Base test display area with common functionality for test windows.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QHBoxLayout
from PySide6.QtCore import Qt, Signal
import os

from src.app.presentation.widgets.display_area_widgets.editor import EditorWidget
from src.app.presentation.widgets.display_area_widgets.console import ConsoleOutput
from src.app.presentation.widgets.display_area_widgets.test_tab_widget import TestTabWidget
from src.app.core.tools.compiler_runner import CompilerRunner
from src.app.presentation.styles.components.code_editor_display_area import SPLITTER_STYLE, OUTER_PANEL_STYLE
from src.app.shared.constants import WORKSPACE_DIR

class BaseTestDisplay(QWidget):
    """Base display area for test windows with common functionality."""
    
    # Common signals
    filePathChanged = Signal()
    
    def __init__(self, parent=None, tab_config=None, default_tab='Generator', 
                 ai_panel_type=None):
        super().__init__(parent)
        
        # Configuration
        self.workspace_dir = WORKSPACE_DIR  
        self.tab_config = tab_config or {}
        self.default_tab = default_tab
        self.ai_panel_type = ai_panel_type
        
        # Initialize
        os.makedirs(self.workspace_dir, exist_ok=True)
        self._setup_ui()
        self._connect_signals()
        
        # Initialize threaded compiler
        self.compiler_runner = CompilerRunner(self.console)
        
        # Activate default tab
        if hasattr(self.test_tabs, 'activate_default_tab'):
            self.test_tabs.activate_default_tab()

        # Add backward compatibility property
        self.file_buttons = getattr(self.test_tabs, 'file_buttons', {})

    def _setup_ui(self):
        """Setup the main UI layout."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet(SPLITTER_STYLE)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(0)

        # Create outer panel
        outer_panel = QWidget()
        outer_panel.setMinimumWidth(400)
        outer_panel.setStyleSheet(OUTER_PANEL_STYLE)
        outer_layout = QVBoxLayout(outer_panel)
        outer_layout.setContentsMargins(3, 3, 3, 3)
        outer_layout.setSpacing(0)

        # Create editor
        self.editor = EditorWidget()
        
        # Create test tabs widget
        self.test_tabs = TestTabWidget(
            parent=self,
            tab_config=self.tab_config,
            default_tab=self.default_tab,
            multi_language=True,
            default_language='cpp'
        )
        
        # Set editor as content widget for tabs
        self.test_tabs.set_content_widget(self.editor)

        # Initialize AI panel if specified
        if self.ai_panel_type:
            self.ai_panel = self.editor.get_ai_panel()
            self.ai_panel.set_panel_type(self.ai_panel_type)

        # Add test tabs to outer panel
        outer_layout.addWidget(self.test_tabs)

        # Setup console
        self.console = ConsoleOutput()
        self.console.setMinimumWidth(200)

        # Add panels to splitter
        self.splitter.addWidget(outer_panel)
        self.splitter.addWidget(self.console)

        # Configure splitter
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, True)
        self.splitter.setSizes([700, 300])

        # Add splitter to main layout
        main_layout.addWidget(self.splitter)

    def _connect_signals(self):
        """Connect internal signals."""
        self.test_tabs.fileChanged.connect(self.filePathChanged.emit)
        
    def get_current_file_path(self):
        """Get current file path from editor."""
        return getattr(self.editor, 'currentFilePath', None)
        
    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'compiler_runner'):
            self.compiler_runner.stop_execution()
```

### Step 2.4: Create Base Test Window  
**Objective**: Common window functionality

**File**: `src/app/presentation/views/base_test_window.py`

```python
# -*- coding: utf-8 -*-
"""
Base test window with common functionality for all test windows.
"""
from src.app.presentation.views.base_window import SidebarWindowBase
from src.app.presentation.widgets.sidebar import Sidebar
from src.app.presentation.widgets.sidebar_widgets import TestCountSlider
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QFont

class BaseTestWindow(SidebarWindowBase):
    """Base class for test windows with common sidebar and functionality."""
    
    def __init__(self, parent=None, window_title="Test Window", 
                 slider_mode="test", display_class=None, **display_kwargs):
        super().__init__(parent, title=None)
        
        self.window_title = window_title
        self.slider_mode = slider_mode
        self.display_class = display_class
        self.display_kwargs = display_kwargs
        
        self._setup_sidebar()
        self._setup_display()
        self._setup_splitter()
        self._connect_signals()
        
    def _setup_sidebar(self):
        """Setup common sidebar structure."""
        self.sidebar = Sidebar(self.window_title)
        
        # Test count slider section
        options_section = self.sidebar.add_section("Number of Tests")
        self.test_count_slider = TestCountSlider(mode=self.slider_mode)
        self.test_count_slider.valueChanged.connect(self.handle_test_count_changed)
        options_section.layout().addWidget(self.test_count_slider)
        
        # Additional sections (can be overridden)
        self._setup_additional_sections()
        
        # Actions section
        action_section = self.sidebar.add_section("Actions")
        for button_text in ['Compile', 'Run']:
            btn = self.sidebar.add_button(button_text, action_section)
            btn.clicked.connect(lambda checked, text=button_text: self.handle_action_button(text))
            
        # History section
        history_section = self.sidebar.add_section("History")
        results_btn = self.sidebar.add_button('Results', history_section)
        results_btn.clicked.connect(lambda checked: self.handle_action_button('Results'))
            
        # Footer
        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()

        back_btn, options_btn = self.create_footer_buttons()
        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)
        
    def _setup_additional_sections(self):
        """Override in subclasses to add additional sidebar sections."""
        pass
        
    def _setup_display(self):
        """Setup display area."""
        if self.display_class:
            self.display_area = self.display_class(**self.display_kwargs)
        else:
            raise NotImplementedError("Subclasses must provide display_class")
            
    def _setup_splitter(self):
        """Setup splitter with sidebar and display area."""
        self.setup_splitter(self.sidebar, self.display_area)
        
    def _connect_signals(self):
        """Connect common signals."""
        self.sidebar.button_clicked.connect(self.handle_button_click)
        
    def handle_test_count_changed(self, value):
        """Handle test count slider change. Override in subclasses."""
        pass
        
    def handle_action_button(self, action):
        """Handle action button clicks. Override in subclasses.""" 
        pass
        
    def can_close(self):
        """Check if window can be closed. Override in subclasses."""
        return True
        
    def cleanup(self):
        """Clean up resources."""
        if hasattr(self.display_area, 'cleanup'):
            self.display_area.cleanup()
```

**Commit Strategy**:
```bash
git add src/app/presentation/utils/dialog_utils.py
git commit -m "feat: add dialog utility functions"

git add src/app/presentation/views/base_status_window.py  
git commit -m "feat: add base status window class"

git add src/app/presentation/views/base_test_display.py
git commit -m "feat: add base test display class"

git add src/app/presentation/views/base_test_window.py
git commit -m "feat: add base test window class"
```

**Validation**:
- [ ] All files compile without errors
- [ ] Import paths are correct
- [ ] Base classes can be instantiated

---

## **PHASE 3: INCREMENTAL MIGRATION**
*Duration: 6-8 hours*  
*Risk: MEDIUM-HIGH*

### Step 3.1: Migrate Validator Window (Pilot)
**Objective**: Migrate one window as proof of concept

**Strategy**: Create new implementation alongside old, test thoroughly, then replace

**File**: `src/app/presentation/views/validator/validator_window_new.py`

```python
# -*- coding: utf-8 -*-
from src.app.presentation.views.base_test_window import BaseTestWindow
from src.app.presentation.views.validator.validator_display_area import ValidatorDisplay

class ValidatorWindow(BaseTestWindow):
    def __init__(self, parent=None):
        # Configure display for validator
        tab_config = {
            'Generator': {
                'cpp': 'generator.cpp',
                'py': 'generator.py', 
                'java': 'Generator.java'
            },
            'Test Code': {
                'cpp': 'test.cpp',
                'py': 'test.py',
                'java': 'Test.java'
            },
            'Validator Code': {
                'cpp': 'validator.cpp',
                'py': 'validator.py',
                'java': 'ValidatorCode.java'
            }
        }
        
        super().__init__(
            parent=parent,
            window_title="Validator",
            slider_mode="validator", 
            display_class=ValidatorDisplay,
            tab_config=tab_config,
            ai_panel_type="validator"
        )
        
        # Initialize validator runner
        self._init_validator_runner()
        
    def _init_validator_runner(self):
        """Initialize validator-specific functionality."""
        from src.app.core.tools.validator import ValidatorRunner
        self.validator_runner = ValidatorRunner(
            self.display_area.console,
            self.display_area.workspace_dir
        )
        
    def handle_test_count_changed(self, value):
        """Handle test count slider change."""
        # Validator-specific logic
        pass
        
    def handle_action_button(self, action):
        """Handle action button clicks.""" 
        if action == 'Compile':
            # Validator-specific compile logic
            pass
        elif action == 'Run':
            # Validator-specific run logic  
            pass
        elif action == 'Results':
            # Show validator results
            pass
```

**Testing Strategy**:
```python
# Test in isolation first
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = ValidatorWindow()
    window.show()
    sys.exit(app.exec())
```

**Deployment Strategy**:
```bash
# 1. Create new implementation
git add src/app/presentation/views/validator/validator_window_new.py
git commit -m "feat: new ValidatorWindow using base classes"

# 2. Test extensively
# 3. Backup old implementation
mv src/app/presentation/views/validator/validator_window.py \
   src/app/presentation/views/validator/validator_window_old.py

# 4. Replace with new implementation
mv src/app/presentation/views/validator/validator_window_new.py \
   src/app/presentation/views/validator/validator_window.py

git add -A
git commit -m "refactor: migrate ValidatorWindow to base classes"

# 5. Test thoroughly
# 6. Remove old backup if successful
rm src/app/presentation/views/validator/validator_window_old.py
git add -A
git commit -m "cleanup: remove old ValidatorWindow implementation"
```

### Step 3.2: Migrate Display Areas
**Objective**: Migrate display areas to base class

**Strategy**: Same as Step 3.1 but for display areas

### Step 3.3: Migrate Remaining Windows
**Objective**: Apply same pattern to ComparatorWindow and BenchmarkerWindow

---

## **PHASE 4: FINAL CLEANUP**
*Duration: 2-3 hours*  
*Risk: LOW*

### Step 4.1: Update Import Statements
**Objective**: Update all references to use new classes

### Step 4.2: Remove Unused Code
**Objective**: Clean up any remaining duplicated code

### Step 4.3: Update Tests
**Objective**: Ensure all tests pass with new architecture

---

## **🔍 VALIDATION CHECKLIST**

### After Each Phase:
- [ ] Application starts successfully
- [ ] All test windows open and function correctly
- [ ] File operations (save/load) work properly
- [ ] Compilation and execution work
- [ ] AI panels function correctly
- [ ] Status windows display properly
- [ ] No import errors or exceptions
- [ ] Memory usage remains stable

### Regression Testing:
- [ ] Create new project workflow
- [ ] Open existing project workflow  
- [ ] Validator window functionality
- [ ] Comparator window functionality
- [ ] Benchmarker window functionality
- [ ] Editor window functionality
- [ ] Results window functionality

### Performance Validation:
- [ ] Application startup time unchanged
- [ ] Window switching performance
- [ ] Memory footprint reduction

---

## **🚨 ROLLBACK PROCEDURES**

### Immediate Rollback (Per Phase):
```bash
# Rollback last commit
git reset --hard HEAD~1

# Or rollback to specific commit
git reset --hard <commit-hash>

# Force push if needed (use carefully)
git push --force-with-lease origin main
```

### Emergency Rollback:
```bash
# Create emergency branch with current state
git checkout -b emergency-rollback

# Reset main to before migration
git checkout main
git reset --hard <pre-migration-commit-hash>
git push --force-with-lease origin main
```

---

## **📈 SUCCESS METRICS**

### Code Reduction:
- **Target**: Reduce presentation layer by 1500+ lines
- **Measurement**: `git diff --stat` before/after

### Duplication Elimination:
- **Target**: Eliminate 90%+ of duplicated code  
- **Measurement**: Code analysis tools

### Maintainability:
- **Target**: Single source of truth for test window functionality
- **Measurement**: Number of files to modify for new features

### Consistency:
- **Target**: Uniform behavior across all test windows
- **Measurement**: Feature parity checklist

---

## **⏰ TIMELINE & RESOURCES**

### Estimated Duration: **14-20 hours**
- Phase 1: 2-3 hours
- Phase 2: 4-6 hours  
- Phase 3: 6-8 hours
- Phase 4: 2-3 hours

### Required Resources:
- **Developer**: 1 senior developer familiar with codebase
- **Testing**: Comprehensive manual testing of all workflows
- **Backup**: Complete git history and rollback procedures

### Risk Mitigation:
- **Frequent commits** for granular rollback capability
- **Isolated testing** before deployment
- **Gradual migration** rather than big-bang approach
- **Backup strategies** at each phase

---

## **📝 NOTES & CONSIDERATIONS**

### Breaking Changes:
- None expected if API contracts maintained
- Internal refactoring should be transparent

### Dependencies:
- No external dependency changes required
- Internal imports will be updated systematically

### Future Maintenance:
- New test windows can extend base classes
- Common functionality changes propagate automatically
- Reduced maintenance burden significantly

---

**End of Migration Playbook**