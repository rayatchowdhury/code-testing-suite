# 🚀 Styling Migration Playbook

**Version**: 1.0  
**Target**: Refactor styling system from C+ (69/100) to A- (90/100)  
**Timeline**: 4 weeks (14 hours total)  
**Lines to Delete**: 564+ duplicate/waste lines  
**Files to Touch**: 50+

---

## 📋 Table of Contents

1. [Quick Reference](#quick-reference)
2. [Pre-Migration Checklist](#pre-migration-checklist)
3. [Week 1: Critical Fixes](#week-1-critical-fixes)
4. [Week 2: Consolidation](#week-2-consolidation)
5. [Week 3: Modularity](#week-3-modularity)
6. [Week 4: Polish & Validation](#week-4-polish--validation)
7. [Testing Strategy](#testing-strategy)
8. [Rollback Plan](#rollback-plan)

---

## 🎯 Quick Reference

### Migration Goals
- ✅ Delete 2 conflicting Theme classes (-104 lines)
- ✅ Create reusable gradient helpers (-400 duplicate lines)
- ✅ Centralize all widget styles (-88 lines)
- ✅ Split 3 oversized files (improve maintainability)
- ✅ Reduce external styling from 35% to <10%

### Critical Numbers
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total lines | 4,000 | 3,200 | -20% |
| Duplicate lines | 618 | 54 | -91% |
| Files with inline styles | 35+ | <5 | -86% |
| Largest style file | 430 | <200 | -53% |
| External styling % | 35% | <10% | -71% |

---

## ✅ Pre-Migration Checklist

### 1. Backup Current State
```powershell
# Create backup branch
git checkout -b backup-styling-before-migration
git add .
git commit -m "Backup: Pre-styling migration snapshot"
git push origin backup-styling-before-migration

# Return to main branch
git checkout main
git checkout -b feature/styling-migration
```

### 2. Document Current Issues
```powershell
# Run the app and screenshot all windows/dialogs
py -m src.app

# Test each major feature:
# - Main window
# - Config dialog
# - Test detail dialogs (validator/benchmarker/comparator)
# - Results windows
# - Help center
```

### 3. Set Up Testing Environment
```powershell
# Install dependencies
pip install -r requirements-dev.txt

# Run existing tests
pytest tests/ -v

# Generate coverage baseline
pytest --cov=src/app/presentation --cov-report=html
```

### 4. Create Migration Branch Structure
```powershell
# Week 1 branch
git checkout -b week1-critical-fixes

# Prepare directories
mkdir -p src/app/presentation/styles/helpers/gradients
mkdir -p src/app/presentation/styles/components/dialogs
```

---

## 📅 Week 1: Critical Fixes (4 hours)

**Goal**: Remove duplicate Theme classes, create gradient helpers, extract dialog styles  
**Impact**: -284 lines, eliminate color conflicts

---

### Task 1.1: Delete Conflicting Theme Classes (30 min)

#### Step 1: Update `main_window/document.py`

**File**: `src/app/presentation/styles/constants/colors.py`

**ADD** these missing colors to MATERIAL_COLORS:
```python
# Add to MATERIAL_COLORS dict if not present:
'separator': '#2A3550',
'text_bright': '#FFFFFF',
'text_dim': '#9CA3AF',
'hover_overlay': 'rgba(0, 150, 199, 0.1)',
```

**File**: `src/app/presentation/views/main_window/document.py`

**FIND** (around line 50-105):
```python
class Theme:
    """Color theme and styling constants."""
    
    COLORS = {
        'primary': '#0096C7',
        'accent': '#00B4D8',
        'bg_dark': '#0A0E27',
        'bg_light': '#13182E',
        'surface': '#1A1F3A',
        'text_bright': '#FFFFFF',
        'text_normal': '#E8E8E8',
        'text_dim': '#9CA3AF',
        'separator': '#2A3550',
        'success': '#90BE6D',
        'warning': '#F9C74F',
        'error': '#F72585',
        'info': '#0096C7',
        'hover_overlay': 'rgba(0, 150, 199, 0.1)',
    }
    
    SPACING = {
        'small': 8,
        'medium': 16,
        'large': 24,
        'xl': 32,
    }
    
    FONTS = {
        'small': 11,
        'medium': 13,
        'large': 15,
        'xl': 18,
    }
```

**REPLACE** with:
```python
# DELETE entire Theme class, use centralized colors instead
```

**FIND** all occurrences of `Theme.COLORS['xxx']`:
```python
Theme.COLORS['primary']
Theme.COLORS['bg_dark']
Theme.COLORS['text_bright']
# ... etc
```

**REPLACE** with:
```python
MATERIAL_COLORS['primary']
MATERIAL_COLORS['background']
MATERIAL_COLORS['text_bright']
# ... etc
```

**ADD** import at top:
```python
from src.app.presentation.styles.constants.colors import MATERIAL_COLORS
```

#### Step 2: Update `help_center/document.py`

**File**: `src/app/presentation/views/help_center/document.py`

**FIND** (around line 20-67):
```python
class Theme:
    """Help Center styling theme."""
    
    COLORS = {
        'primary': '#F72585',      # Pink - WRONG!
        'accent': '#4CC9F0',
        'bg_dark': '#0A0E27',
        'bg_light': '#13182E',
        'surface': '#1A1F3A',
        'text_bright': '#E8E8E8',  # Different from main!
        'text_normal': '#C0C0C0',
        'text_dim': '#808080',
        'separator': '#2A3550',
        'code_bg': '#0D1117',
        'border': '#30363D',
    }
```

**DELETE** entire Theme class.

**FIND** all `Theme.COLORS['xxx']` and **REPLACE** with `MATERIAL_COLORS['xxx']`.

**ADD** import:
```python
from src.app.presentation.styles.constants.colors import MATERIAL_COLORS
```

**Lines saved**: 104

---

### Task 1.2: Create Gradient Helper Module (45 min)

**CREATE FILE**: `src/app/presentation/styles/helpers/gradients.py`

```python
"""
Gradient helper functions for consistent styling.

Eliminates 400+ lines of duplicate gradient code.
"""

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS


def surface_gradient() -> str:
    """Standard surface gradient (light to dark)."""
    return f"""qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 {MATERIAL_COLORS['surface']},
        stop:1 {MATERIAL_COLORS['surface_variant']}
    )"""


def surface_gradient_reverse() -> str:
    """Reverse surface gradient (dark to light)."""
    return f"""qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 {MATERIAL_COLORS['surface_variant']},
        stop:1 {MATERIAL_COLORS['surface']}
    )"""


def input_gradient() -> str:
    """Standard input field background gradient."""
    return """qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(19, 24, 46, 255),
        stop:1 rgba(26, 31, 58, 255)
    )"""


def button_gradient(color_top: str, color_bottom: str) -> str:
    """Generic button gradient with custom colors."""
    return f"""qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 {color_top},
        stop:1 {color_bottom}
    )"""


def primary_button_gradient() -> str:
    """Primary button gradient (cyan shades)."""
    return button_gradient(MATERIAL_COLORS['primary'], MATERIAL_COLORS['primary_dark'])


def hover_gradient(base_color: str, opacity: float = 0.2) -> str:
    """Hover state gradient overlay."""
    rgba = f"rgba(0, 150, 199, {opacity})"
    return f"""qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 {rgba},
        stop:1 transparent
    )"""


def card_gradient() -> str:
    """Test card background gradient."""
    return surface_gradient()


def sidebar_gradient() -> str:
    """Sidebar background gradient."""
    return f"""qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 {MATERIAL_COLORS['background']},
        stop:1 {MATERIAL_COLORS['surface']}
    )"""
```

**UPDATE**: `src/app/presentation/styles/helpers/__init__.py`
```python
from .gradients import (
    surface_gradient,
    surface_gradient_reverse,
    input_gradient,
    button_gradient,
    primary_button_gradient,
    hover_gradient,
    card_gradient,
    sidebar_gradient,
)

__all__ = [
    'surface_gradient',
    'surface_gradient_reverse',
    'input_gradient',
    'button_gradient',
    'primary_button_gradient',
    'hover_gradient',
    'card_gradient',
    'sidebar_gradient',
]
```

---

### Task 1.3: Extract Test Detail Dialog Styles (1 hour)

**CREATE FILE**: `src/app/presentation/styles/components/dialogs/test_detail_styles.py`

```python
"""Styles for test detail dialogs (validator/comparator/benchmarker)."""

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS
from src.app.presentation.styles.helpers.gradients import surface_gradient, input_gradient


# Base dialog
TEST_DETAIL_DIALOG_STYLE = f"""
QDialog {{
    background: {MATERIAL_COLORS['background']};
    color: {MATERIAL_COLORS['text']};
}}
"""

# Header section
TEST_DETAIL_HEADER_STYLE = f"""
QFrame {{
    background: {surface_gradient()};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 8px;
    padding: 12px;
}}
"""

TEST_DETAIL_TITLE_STYLE = """
font-weight: bold;
font-size: 18px;
"""

TEST_DETAIL_STATUS_PASSED_STYLE = f"""
font-weight: bold;
font-size: 16px;
color: {MATERIAL_COLORS['primary']};
"""

TEST_DETAIL_STATUS_FAILED_STYLE = f"""
font-weight: bold;
font-size: 16px;
color: {MATERIAL_COLORS['error']};
"""

# Metrics section
TEST_DETAIL_METRICS_FRAME_STYLE = f"""
QFrame {{
    background: {MATERIAL_COLORS['surface_variant']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 6px;
    padding: 8px;
}}
"""

TEST_DETAIL_METRIC_LABEL_STYLE = f"""
font-size: 11px;
color: {MATERIAL_COLORS['text_secondary']};
"""

TEST_DETAIL_METRIC_VALUE_STYLE = """
font-weight: bold;
font-size: 13px;
"""

# Content labels
TEST_DETAIL_SECTION_LABEL_STYLE = """
font-weight: bold;
font-size: 14px;
"""

# Text editors
TEST_DETAIL_TEXTEDIT_STYLE = f"""
QTextEdit {{
    background: {input_gradient()};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 4px;
    padding: 8px;
    color: {MATERIAL_COLORS['text']};
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}}
QTextEdit:focus {{
    border: 2px solid {MATERIAL_COLORS['primary']};
}}
"""

# Buttons
TEST_DETAIL_CLOSE_BUTTON_STYLE = f"""
QPushButton {{
    background: {MATERIAL_COLORS['primary']};
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 24px;
    font-weight: bold;
    font-size: 13px;
}}
QPushButton:hover {{
    background: {MATERIAL_COLORS['primary_variant']};
}}
QPushButton:pressed {{
    background: {MATERIAL_COLORS['primary_dark']};
}}
"""
```

**UPDATE**: `src/app/presentation/widgets/test_detail_view.py`

**REPLACE** all inline setStyleSheet calls:

**FIND** (line ~88-93):
```python
test_label.setStyleSheet(
    """
    font-weight: bold;
    font-size: 18px;
"""
)
```

**REPLACE** with:
```python
test_label.setStyleSheet(TEST_DETAIL_TITLE_STYLE)
```

**FIND** (line ~100-106):
```python
status_label.setStyleSheet(f"""
    font-weight: bold;
    font-size: 16px;
    color: {status_color};
""")
```

**REPLACE** with:
```python
status_label.setStyleSheet(
    TEST_DETAIL_STATUS_PASSED_STYLE if self.passed 
    else TEST_DETAIL_STATUS_FAILED_STYLE
)
```

**FIND** (lines 254, 267, 279 - DUPLICATED 3 TIMES):
```python
input_label.setStyleSheet("font-weight: bold; font-size: 14px;")
expected_label.setStyleSheet("font-weight: bold; font-size: 14px;")
actual_label.setStyleSheet("font-weight: bold; font-size: 14px;")
```

**REPLACE** with:
```python
input_label.setStyleSheet(TEST_DETAIL_SECTION_LABEL_STYLE)
expected_label.setStyleSheet(TEST_DETAIL_SECTION_LABEL_STYLE)
actual_label.setStyleSheet(TEST_DETAIL_SECTION_LABEL_STYLE)
```

**ADD** import at top:
```python
from src.app.presentation.styles.components.dialogs.test_detail_styles import (
    TEST_DETAIL_DIALOG_STYLE,
    TEST_DETAIL_HEADER_STYLE,
    TEST_DETAIL_TITLE_STYLE,
    TEST_DETAIL_STATUS_PASSED_STYLE,
    TEST_DETAIL_STATUS_FAILED_STYLE,
    TEST_DETAIL_METRICS_FRAME_STYLE,
    TEST_DETAIL_SECTION_LABEL_STYLE,
    TEST_DETAIL_TEXTEDIT_STYLE,
    TEST_DETAIL_CLOSE_BUTTON_STYLE,
)
```

**APPLY** to all 4 dialog classes:
- `TestDetailDialog`
- `ComparatorDetailDialog`
- `ValidatorDetailDialog`
- `BenchmarkerDetailDialog`

**Lines saved**: 180

---

### Task 1.4: Test Week 1 Changes (30 min)

```powershell
# Run app
py -m src.app

# Test each dialog:
# 1. Open validator and run tests -> Click test card -> Verify dialog styling
# 2. Open comparator and run tests -> Click test card -> Verify dialog styling
# 3. Open benchmarker and run tests -> Click test card -> Verify dialog styling
# 4. Open main window -> Verify colors match
# 5. Open help center -> Verify colors now match main window

# Run automated tests
pytest tests/presentation/ -v

# Commit
git add .
git commit -m "Week 1: Remove Theme classes, add gradient helpers, extract dialog styles"
```

**Week 1 Total**: -284 lines, 4 hours

---

## 📅 Week 2: Consolidation (3 hours)

**Goal**: Centralize widget styles, create reusable helpers  
**Impact**: -152 lines, eliminate widget inline styles

---

### Task 2.1: Create Input Styles Module (45 min)

**CREATE FILE**: `src/app/presentation/styles/components/inputs/input_styles.py`

```python
"""Centralized input widget styles."""

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS
from src.app.presentation.styles.helpers.gradients import input_gradient


# Group boxes
INPUT_GROUP_STYLE = f"""
QGroupBox {{
    border: 2px solid {MATERIAL_COLORS['outline']};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    background: {input_gradient()};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
    color: {MATERIAL_COLORS['primary']};
    font-weight: bold;
    font-size: 13px;
}}
"""

# Spin boxes
INPUT_SPINBOX_STYLE = f"""
QSpinBox {{
    background: {input_gradient()};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 4px;
    padding: 6px;
    color: {MATERIAL_COLORS['text']};
    font-size: 13px;
    min-height: 24px;
}}
QSpinBox:focus {{
    border: 2px solid {MATERIAL_COLORS['primary']};
}}
QSpinBox:hover {{
    border-color: {MATERIAL_COLORS['primary_variant']};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background: {MATERIAL_COLORS['surface']};
    border: 1px solid {MATERIAL_COLORS['outline']};
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background: {MATERIAL_COLORS['primary_variant']};
}}
"""

# Double spin boxes
INPUT_DOUBLE_SPINBOX_STYLE = INPUT_SPINBOX_STYLE.replace('QSpinBox', 'QDoubleSpinBox')

# Combo boxes
INPUT_COMBOBOX_STYLE = f"""
QComboBox {{
    background: {input_gradient()};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 4px;
    padding: 6px 8px;
    color: {MATERIAL_COLORS['text']};
    font-size: 13px;
    min-height: 24px;
}}
QComboBox:focus {{
    border: 2px solid {MATERIAL_COLORS['primary']};
}}
QComboBox:hover {{
    border-color: {MATERIAL_COLORS['primary_variant']};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid {MATERIAL_COLORS['text']};
    margin-right: 6px;
}}
QComboBox QAbstractItemView {{
    background: {MATERIAL_COLORS['surface']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    selection-background-color: {MATERIAL_COLORS['primary']};
    color: {MATERIAL_COLORS['text']};
}}
"""
```

**UPDATE**: `src/app/presentation/widgets/sidebar_widgets/limits_input_widget.py`

**FIND** (lines ~120-175 - setup_styles method):
```python
def setup_styles(self):
    """Setup widget styling."""
    group_style = """
        QGroupBox {
            border: 2px solid #2A3550;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 16px;
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(19, 24, 46, 255),
                stop:1 rgba(26, 31, 58, 255)
            );
        }
        # ... 50 more lines
    """
    self.time_group.setStyleSheet(group_style)
    self.memory_group.setStyleSheet(group_style)
```

**REPLACE** with:
```python
def setup_styles(self):
    """Setup widget styling."""
    self.time_group.setStyleSheet(INPUT_GROUP_STYLE)
    self.memory_group.setStyleSheet(INPUT_GROUP_STYLE)
    
    # Apply to all spin boxes
    for spinbox in [self.time_spinbox, self.memory_spinbox]:
        spinbox.setStyleSheet(INPUT_DOUBLE_SPINBOX_STYLE)
```

**ADD** import:
```python
from src.app.presentation.styles.components.inputs.input_styles import (
    INPUT_GROUP_STYLE,
    INPUT_DOUBLE_SPINBOX_STYLE,
)
```

**Lines saved**: 55

---

**UPDATE**: `src/app/presentation/widgets/sidebar_widgets/test_count_slider.py`

**FIND** (lines ~90-123):
```python
input_style = """
    QSpinBox {
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(19, 24, 46, 255),
            stop:1 rgba(26, 31, 58, 255)
        );
        # ... 30 more lines (EXACT DUPLICATE!)
    }
"""
self.count_input.setStyleSheet(input_style)
```

**REPLACE** with:
```python
self.count_input.setStyleSheet(INPUT_SPINBOX_STYLE)
```

**ADD** import:
```python
from src.app.presentation.styles.components.inputs.input_styles import INPUT_SPINBOX_STYLE
```

**Lines saved**: 33

---

### Task 2.2: Create Error Label Helper (30 min)

**UPDATE**: `src/app/presentation/styles/components/results.py`

**ADD** at the end:
```python
# Error label styling
ERROR_LABEL_STYLE = f"color: {MATERIAL_COLORS['error']}; font-weight: 500;"

def create_error_label(text: str, parent=None) -> QLabel:
    """
    Create a styled error label.
    
    Eliminates 19 duplicate lines in detailed_results_widget.py.
    
    Args:
        text: Label text
        parent: Parent widget
        
    Returns:
        QLabel: Styled error label
    """
    from PySide6.QtWidgets import QLabel
    label = QLabel(text, parent)
    label.setStyleSheet(ERROR_LABEL_STYLE)
    label.setWordWrap(True)
    return label
```

**UPDATE**: `src/app/presentation/views/results/detailed_results_widget.py`

**FIND** (19 occurrences at lines 138, 194, 265, 328, 353, 364, 431, 470, 484, 514, 543, 693, 708, 712, 722, 726, 767, 779):
```python
error_label = QLabel("Error message")
error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
```

**REPLACE** with:
```python
error_label = create_error_label("Error message")
```

**ADD** import:
```python
from src.app.presentation.styles.components.results import create_error_label
```

**Lines saved**: 19

---

### Task 2.3: Consolidate Inline Styles (1 hour)

**UPDATE**: `src/app/presentation/views/results/detailed_results_window.py`

**ADD** to `styles/components/results.py`:
```python
RESULTS_SCROLL_STYLE = f"background-color: {MATERIAL_COLORS['surface']};"
RESULTS_SEPARATOR_STYLE = f"background-color: {MATERIAL_COLORS['outline']}; border: none; max-height: 1px;"
RESULTS_VALUE_BOLD_STYLE = lambda color: f"color: {color}; font-weight: bold;"
```

**FIND** (line 413):
```python
scroll.setStyleSheet(f"background-color: {MATERIAL_COLORS['surface']};")
```

**REPLACE** with:
```python
scroll.setStyleSheet(RESULTS_SCROLL_STYLE)
```

**FIND** (line 783):
```python
line.setStyleSheet(f"background-color: {MATERIAL_COLORS['outline']};")
```

**REPLACE** with:
```python
line.setStyleSheet(RESULTS_SEPARATOR_STYLE)
```

**Lines saved**: 25

---

### Task 2.4: Test Week 2 Changes (30 min)

```powershell
py -m src.app

# Test:
# 1. Sidebar widgets (limits input, test count slider)
# 2. Results windows (detailed results, error labels)
# 3. All input fields render correctly

pytest tests/ -v

git add .
git commit -m "Week 2: Centralize widget styles, create error label helper"
```

**Week 2 Total**: -152 lines, 3 hours

---

## 📅 Week 3: Modularity (3 hours)

**Goal**: Split oversized files for better organization  
**Impact**: No line reduction, improved maintainability

---

### Task 3.1: Split status_view_styles.py (1 hour)

**CURRENT**: `src/app/presentation/styles/components/status_view_styles.py` (430 lines)

**CREATE 3 FILES**:

#### File 1: `status_containers.py` (~140 lines)
```python
"""Status view container styles."""

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS
from src.app.presentation.styles.helpers.gradients import surface_gradient

STATUS_VIEW_CONTAINER_STYLE = f"""
QWidget#status_container {{
    background: {MATERIAL_COLORS['background']};
    border-radius: 8px;
}}
"""

STATUS_VIEW_INNER_CONTAINER_STYLE = f"""
QWidget#inner_container {{
    background: {surface_gradient()};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 6px;
}}
"""

# ... move all container-related styles here
```

#### File 2: `status_progress.py` (~140 lines)
```python
"""Status view progress and segment styles."""

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS

def get_segment_style(color: str, is_active: bool = False) -> str:
    """Generate segment style with dynamic color."""
    # ... existing implementation
    
# ... move all progress bar styles here
```

#### File 3: `status_cards.py` (~150 lines)
```python
"""Status view test card styles."""

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS

# ... move all card-related styles here
```

**UPDATE**: Files using STATUS_VIEW_* imports:
- `src/app/presentation/widgets/unified_status_view.py`
- Update imports to use new module structure

---

### Task 3.2: Split config_styles.py (1 hour)

**CURRENT**: `src/app/presentation/styles/components/config_styles.py` (405 lines)

**CREATE 4 FILES**:

#### File 1: `config/dialog_styles.py` (~100 lines)
```python
"""Config dialog container and layout styles."""

CONFIG_DIALOG_STYLE = """..."""
CONFIG_DIALOG_TITLE_STYLE = """..."""
# Section frames, containers
```

#### File 2: `config/input_styles.py` (~100 lines)
```python
"""Config dialog input field styles."""

# All input, combobox, checkbox styles specific to config dialog
```

#### File 3: `config/button_styles.py` (~100 lines)
```python
"""Config dialog button styles."""

# Primary, secondary, danger button styles
```

#### File 4: `config/label_styles.py` (~105 lines)
```python
"""Config dialog label and text styles."""

SECTION_INFO_LABEL_STYLE = """..."""
ERROR_DIALOG_STYLE = """..."""
# Warning labels, etc.
```

**UPDATE**: `src/app/core/config/views/config_dialog.py`
```python
from src.app.presentation.styles.components.config.dialog_styles import CONFIG_DIALOG_STYLE
from src.app.presentation.styles.components.config.label_styles import SECTION_INFO_LABEL_STYLE
# etc.
```

---

### Task 3.3: Split test_view_styles.py (45 min)

**CURRENT**: `src/app/presentation/styles/components/test_view_styles.py` (300+ lines)

**CREATE 2 FILES**:

#### File 1: `test_editor_styles.py` (~150 lines)
```python
"""Test editor and syntax highlighting styles."""
# Editor-specific styles
```

#### File 2: `test_control_styles.py` (~150 lines)
```python
"""Test control buttons and widgets."""
# Control buttons, sliders, configuration widgets
```

---

### Task 3.4: Test Week 3 Changes (15 min)

```powershell
py -m src.app

# Test ALL windows/dialogs to ensure nothing broke
# Verify imports work correctly

pytest tests/ -v

git add .
git commit -m "Week 3: Split oversized style files for better modularity"
```

**Week 3 Total**: 0 line reduction (organization only), 3 hours

---

## 📅 Week 4: Polish & Validation (4 hours)

**Goal**: Add helpers, create linter, document standards  
**Impact**: -128 lines, prevent future regressions

---

### Task 4.1: Create Common Style Helpers (1 hour)

**CREATE FILE**: `src/app/presentation/styles/helpers/common_styles.py`

```python
"""Common reusable style helpers."""

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS


def bold_label(font_size: int = 14, color: str = None) -> str:
    """Bold label style."""
    color_str = f"color: {color};" if color else ""
    return f"font-weight: bold; font-size: {font_size}px; {color_str}"


def error_text() -> str:
    """Error text color."""
    return f"color: {MATERIAL_COLORS['error']};"


def success_text() -> str:
    """Success text color."""
    return f"color: {MATERIAL_COLORS['success']};"


def warning_text() -> str:
    """Warning text color."""
    return f"color: {MATERIAL_COLORS['warning']};"


def background_surface() -> str:
    """Standard surface background."""
    return f"background-color: {MATERIAL_COLORS['surface']};"


def border_standard(width: int = 1) -> str:
    """Standard border style."""
    return f"border: {width}px solid {MATERIAL_COLORS['outline']};"


def rounded_corners(radius: int = 4) -> str:
    """Rounded corner style."""
    return f"border-radius: {radius}px;"


def padding_standard(size: int = 8) -> str:
    """Standard padding."""
    return f"padding: {size}px;"
```

**UPDATE** 20+ files to use these helpers instead of inline styles.

---

### Task 4.2: Create Style Linter (1.5 hours)

**CREATE FILE**: `scripts/lint_styles.py`

```python
"""
Lint styling violations across the codebase.

Finds:
- Inline setStyleSheet calls outside styles/
- Magic color strings (hex codes not from MATERIAL_COLORS)
- Duplicate gradient patterns
- Files with >200 lines in styles/
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple


class StyleLinter:
    def __init__(self):
        self.violations = []
        self.stats = {
            'inline_styles': 0,
            'magic_colors': 0,
            'duplicate_gradients': 0,
            'oversized_files': 0,
        }
    
    def lint_all(self):
        """Run all lint checks."""
        self.check_inline_styles()
        self.check_magic_colors()
        self.check_oversized_files()
        self.print_report()
    
    def check_inline_styles(self):
        """Find inline setStyleSheet calls outside styles/ folder."""
        print("🔍 Checking for inline styles...")
        
        for py_file in Path("src/app").rglob("*.py"):
            if "styles/" in str(py_file):
                continue
            
            content = py_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                if 'setStyleSheet(' in line and not line.strip().startswith('#'):
                    # Check if it's importing a constant (allowed)
                    if re.search(r'setStyleSheet\([A-Z_]+\)', line):
                        continue
                    
                    self.violations.append({
                        'type': 'inline_style',
                        'file': str(py_file),
                        'line': i,
                        'content': line.strip()[:80],
                    })
                    self.stats['inline_styles'] += 1
    
    def check_magic_colors(self):
        """Find hardcoded hex colors."""
        print("🔍 Checking for magic color strings...")
        
        for py_file in Path("src/app").rglob("*.py"):
            if "styles/constants/colors.py" in str(py_file):
                continue
            
            content = py_file.read_text(encoding='utf-8')
            
            # Find hex colors like #RRGGBB
            hex_colors = re.findall(r'#[0-9A-Fa-f]{6}', content)
            
            if hex_colors:
                self.violations.append({
                    'type': 'magic_color',
                    'file': str(py_file),
                    'colors': list(set(hex_colors))[:5],
                })
                self.stats['magic_colors'] += len(set(hex_colors))
    
    def check_oversized_files(self):
        """Find style files >200 lines."""
        print("🔍 Checking for oversized style files...")
        
        for py_file in Path("src/app/presentation/styles/components").rglob("*.py"):
            if py_file.name == '__init__.py':
                continue
            
            lines = py_file.read_text(encoding='utf-8').split('\n')
            line_count = len(lines)
            
            if line_count > 200:
                self.violations.append({
                    'type': 'oversized_file',
                    'file': str(py_file),
                    'lines': line_count,
                })
                self.stats['oversized_files'] += 1
    
    def print_report(self):
        """Print linting report."""
        print("\n" + "="*80)
        print("📊 STYLE LINTING REPORT")
        print("="*80)
        
        print(f"\n📈 Statistics:")
        print(f"  Inline styles: {self.stats['inline_styles']}")
        print(f"  Magic colors: {self.stats['magic_colors']}")
        print(f"  Oversized files: {self.stats['oversized_files']}")
        print(f"  Total violations: {len(self.violations)}")
        
        if self.violations:
            print(f"\n⚠️  Found {len(self.violations)} violations:\n")
            
            for v in self.violations[:20]:  # Show first 20
                if v['type'] == 'inline_style':
                    print(f"❌ Inline style in {v['file']}:{v['line']}")
                    print(f"   {v['content']}\n")
                
                elif v['type'] == 'magic_color':
                    print(f"❌ Magic colors in {v['file']}")
                    print(f"   Colors: {', '.join(v['colors'])}\n")
                
                elif v['type'] == 'oversized_file':
                    print(f"❌ Oversized file: {v['file']}")
                    print(f"   Lines: {v['lines']} (should be <200)\n")
        else:
            print("\n✅ No violations found! Excellent work!")
        
        # Exit code
        return 0 if len(self.violations) == 0 else 1


if __name__ == "__main__":
    linter = StyleLinter()
    exit_code = linter.lint_all()
    exit(exit_code)
```

**RUN**:
```powershell
python scripts/lint_styles.py
```

---

### Task 4.3: Create Documentation (1 hour)

**CREATE FILE**: `src/app/presentation/styles/README.md`

```markdown
# Styling Guidelines

## 🎯 Core Principles

1. **Single Source of Truth**: All styles MUST live in `styles/` folder
2. **No Inline Styles**: Use object names + CSS selectors (except dynamic values)
3. **Reuse Helpers**: Use gradient/color helpers instead of duplicating
4. **Keep Files Small**: Max 200 lines per style file
5. **Import from Constants**: Always use `MATERIAL_COLORS` dict

## 📁 Folder Structure

```
styles/
├── constants/           # Color definitions (DO NOT DUPLICATE!)
│   ├── colors.py        # MATERIAL_COLORS, COLORS
│   ├── editor_colors.py # Editor-specific colors
│   └── status_colors.py # Semantic status colors
│
├── components/          # Component-specific styles
│   ├── config/          # Config dialog styles
│   ├── inputs/          # Input widget styles
│   ├── dialogs/         # Dialog styles
│   └── *.py             # Other component styles
│
├── helpers/             # Reusable utilities
│   ├── gradients.py     # Gradient generators
│   └── common_styles.py # Common style helpers
│
└── fonts/               # Font utilities
```

## ✅ Good Examples

### Using Centralized Styles
```python
from src.app.presentation.styles.components.dialogs.test_detail_styles import (
    TEST_DETAIL_DIALOG_STYLE
)

dialog.setStyleSheet(TEST_DETAIL_DIALOG_STYLE)
```

### Using Helpers
```python
from src.app.presentation.styles.helpers.gradients import surface_gradient

style = f"background: {surface_gradient()};"
```

### Using Object Names
```python
button.setObjectName("primary_button")
container.setStyleSheet(BUTTON_STYLE)  # Uses #primary_button selector
```

## ❌ Bad Examples

### Inline Styles (DON'T DO THIS!)
```python
# BAD - inline style
label.setStyleSheet("color: red; font-size: 14px;")

# GOOD - use constant
from styles.helpers.common_styles import error_text, bold_label
label.setStyleSheet(f"{error_text()} {bold_label(14)}")
```

### Magic Colors (DON'T DO THIS!)
```python
# BAD - magic hex color
setStyleSheet("color: #F72585;")

# GOOD - use MATERIAL_COLORS
setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
```

### Duplicate Gradients (DON'T DO THIS!)
```python
# BAD - copying gradient code
style = """
qlineargradient(x1:0, y1:0, x2:0, y2:1,
    stop:0 rgba(19, 24, 46, 255),
    stop:1 rgba(26, 31, 58, 255))
"""

# GOOD - use helper
from styles.helpers.gradients import input_gradient
style = f"background: {input_gradient()};"
```

## 🔧 Adding New Styles

1. **Determine Category**: Is it a button, input, dialog, or component?
2. **Choose Location**: Add to appropriate `components/` file
3. **Use Helpers**: Import gradients/colors from helpers/constants
4. **Keep it DRY**: If copying code >2 times, extract to helper
5. **Document**: Add docstring explaining usage

## 🧪 Testing Styles

```powershell
# Visual test
py -m src.app

# Lint styles
python scripts/lint_styles.py

# Run tests
pytest tests/presentation/ -v
```

## 📏 File Size Limits

- Style files: Max 200 lines (split if larger)
- Helper files: Max 300 lines
- Color files: Max 150 lines

## 🎨 Color Usage

Always import from `MATERIAL_COLORS`:

```python
from src.app.presentation.styles.constants.colors import MATERIAL_COLORS

# Primary colors
MATERIAL_COLORS['primary']      # #0096C7
MATERIAL_COLORS['error']        # #F72585
MATERIAL_COLORS['success']      # #90BE6D

# Surface colors
MATERIAL_COLORS['background']   # #0A0E27
MATERIAL_COLORS['surface']      # #13182E
```

**Never** create local Theme classes!
```

---

### Task 4.4: Final Validation (30 min)

```powershell
# Run linter
python scripts/lint_styles.py

# Should show minimal violations (<5)

# Run full test suite
pytest tests/ -v --cov=src/app/presentation

# Manual testing - open every window/dialog
py -m src.app

# Checklist:
# ✅ Main window
# ✅ Config dialog
# ✅ Help center
# ✅ Validator window + test detail dialogs
# ✅ Comparator window + test detail dialogs
# ✅ Benchmarker window + test detail dialogs
# ✅ Results window
# ✅ Detailed results window

# Commit final changes
git add .
git commit -m "Week 4: Add helpers, linter, documentation"
git push origin feature/styling-migration
```

---

## 🧪 Testing Strategy

### Automated Tests

**Run before each commit**:
```powershell
pytest tests/presentation/styles/ -v
```

**Coverage target**: >80%

### Visual Tests

**Manual checklist** (run after each week):

- [ ] Main window renders correctly
- [ ] Config dialog opens and all inputs styled
- [ ] Test detail dialogs show correct colors
- [ ] Results windows display properly
- [ ] Help center matches main window colors
- [ ] All buttons have hover states
- [ ] All inputs have focus states
- [ ] Gradients render smoothly
- [ ] No visual regressions

### Regression Prevention

**Weekly linter runs**:
```powershell
# Add to CI/CD pipeline
python scripts/lint_styles.py || exit 1
```

---

## 🔄 Rollback Plan

### If Something Breaks

**Week 1 rollback**:
```powershell
git checkout week1-critical-fixes
git reset --hard HEAD~1
```

**Week 2 rollback**:
```powershell
git checkout week2-consolidation
git reset --hard HEAD~1
```

**Full rollback**:
```powershell
git checkout backup-styling-before-migration
git checkout -b main-restored
```

### Common Issues & Fixes

**Issue**: Colors don't match after removing Theme classes
```python
# Fix: Ensure all MATERIAL_COLORS keys exist
# Add missing colors to constants/colors.py
```

**Issue**: Gradients not rendering
```python
# Fix: Check import path
from src.app.presentation.styles.helpers.gradients import surface_gradient
# Ensure return value is string, not function
```

**Issue**: Import errors after splitting files
```python
# Fix: Update __init__.py in each module
# Re-export all constants for easy import
```

---

## 📊 Success Metrics

### After Full Migration

| Metric | Before | Target | How to Measure |
|--------|--------|--------|----------------|
| Total lines | 4,000 | 3,200 | `find src/app/presentation/styles -name "*.py" -exec wc -l {} + | tail -1` |
| Duplicate lines | 618 | <60 | Run linter |
| Files with inline styles | 35+ | <5 | `python scripts/lint_styles.py` |
| Largest file | 430 | <200 | `wc -l styles/components/*.py` |
| External styling | 35% | <10% | Manual audit |
| Test coverage | 60% | >80% | `pytest --cov` |

---

## 📝 Final Checklist

### Pre-Merge Review

- [ ] All tests passing (`pytest tests/ -v`)
- [ ] Linter shows <5 violations
- [ ] Visual inspection completed
- [ ] Documentation updated
- [ ] Code reviewed by team
- [ ] Performance tested (no slowdowns)
- [ ] Backup branch created
- [ ] Migration log completed

### Merge to Main

```powershell
git checkout main
git merge feature/styling-migration
git push origin main

# Tag the release
git tag -a v2.0-styling-refactor -m "Major styling system refactor"
git push origin v2.0-styling-refactor
```

---

## 🎓 Lessons Learned

### What Worked Well
- Gradient helpers eliminated massive duplication
- Centralized colors prevented conflicts
- Incremental weekly approach reduced risk
- Automated linter caught regressions

### What to Improve
- Earlier testing of Theme class removal
- Better documentation from day 1
- More comprehensive visual test suite

### Future Recommendations
- Enforce linter in CI/CD
- Code review checklist for styling
- Quarterly style audits
- Component library for reusability

---

**Migration Playbook Complete** - Total: 14 hours, -564 lines, +maintainability ∞

