# Styling System Documentation

## 📚 Table of Contents

1. [Core Principles](#core-principles)
2. [Folder Structure](#folder-structure)
3. [Color System](#color-system)
4. [Helper Functions](#helper-functions)
5. [Component Styles](#component-styles)
6. [Best Practices](#best-practices)
7. [Common Patterns](#common-patterns)
8. [File Size Guidelines](#file-size-guidelines)
9. [Testing Guidelines](#testing-guidelines)
10. [Contribution Guidelines](#contribution-guidelines)

---

## 🎯 Core Principles

### 1. Centralization Over Duplication
**DO:**
```python
from src.app.presentation.styles.components.dialogs import TEST_DETAIL_DIALOG_STYLE

dialog.setStyleSheet(TEST_DETAIL_DIALOG_STYLE)
```

**DON'T:**
```python
# ❌ Inline styles
dialog.setStyleSheet("""
    QDialog {
        background-color: #1a1a1c;
        border-radius: 8px;
    }
""")
```

### 2. Use Material Design Colors
**DO:**
```python
from src.app.presentation.styles.constants.colors import MATERIAL_COLORS

color = MATERIAL_COLORS['primary']  # #0096C7
```

**DON'T:**
```python
# ❌ Hardcoded hex colors
color = '#0096C7'
```

### 3. Modular Organization
- Keep style files **under 200 lines**
- Split large files into focused packages
- Use `__init__.py` for re-exports

### 4. Composable Helpers
**DO:**
```python
from src.app.presentation.styles.helpers.common_styles import bold_label

label.setStyleSheet(bold_label(16, MATERIAL_COLORS['primary']))
```

**DON'T:**
```python
# ❌ Repeating patterns
label.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {MATERIAL_COLORS['primary']};")
```

---

## 📁 Folder Structure

```
styles/
├── constants/
│   ├── colors.py              # MATERIAL_COLORS dictionary (single source of truth)
│   └── status_colors.py       # Status-specific color constants
│
├── helpers/
│   ├── common_styles.py       # Reusable style snippets (bold_label, error_text, etc.)
│   ├── gradients.py           # Gradient helper functions (12 gradient types)
│   └── inline_styles.py       # Legacy inline style helpers (to be migrated)
│
├── components/
│   ├── config/                # Config dialog styles (modular package)
│   │   ├── __init__.py        # Re-exports for backward compatibility
│   │   ├── dialog_styles.py   # Dialog container, scroll areas
│   │   ├── input_styles.py    # Input fields (combobox, lineedit, spinbox)
│   │   ├── button_styles.py   # Button variants (primary, secondary, danger)
│   │   └── label_styles.py    # Labels (standard, info, warning)
│   │
│   ├── status_view/           # Status view styles (modular package)
│   │   ├── __init__.py        # Re-exports all status styles
│   │   ├── status_containers.py  # Container, controls, headers
│   │   ├── status_progress.py    # Progress bars, segments, stats
│   │   └── status_cards.py       # Card sections and test cards
│   │
│   ├── test_view/             # Test view styles (modular package)
│   │   ├── __init__.py        # Re-exports test view styles
│   │   ├── test_editor_styles.py   # Editor UI (file buttons, panels)
│   │   └── test_control_styles.py  # Status dialogs, compilation
│   │
│   ├── dialogs/               # Dialog-specific styles
│   │   └── test_detail_styles.py   # Test detail dialog components
│   │
│   ├── inputs/                # Input widget styles
│   │   └── input_styles.py    # Centralized input component styles
│   │
│   ├── results.py             # Results window styles
│   ├── editor.py              # Code editor styles
│   ├── sidebar.py             # Sidebar styles
│   ├── console.py             # Console/terminal styles
│   └── ...                    # Other component styles
│
├── fonts/
│   └── emoji.py               # Emoji font loading utilities
│
└── style.py                   # Legacy style file (being phased out)
```

---

## 🎨 Color System

### Material Design Palette

All colors are defined in `styles/constants/colors.py`:

```python
MATERIAL_COLORS = {
    # Primary colors
    'primary': '#0096C7',              # Main brand color (cyan)
    'primary_variant': '#0077B6',      # Darker variant
    'on_primary': '#FFFFFF',           # Text on primary
    
    # Surface colors
    'surface': '#1C1B1F',              # Main background
    'surface_dim': '#141316',          # Dimmed surface
    'surface_bright': '#3B383E',       # Bright surface
    'surface_variant': '#49454F',      # Variant surface
    
    # Text colors
    'on_surface': '#E6E1E5',           # Primary text
    'text_primary': '#E0E0E0',         # Alternative primary text
    'text_secondary': '#B0B0B0',       # Secondary text
    'text_disabled': '#6E6E6E',        # Disabled text
    
    # Semantic colors
    'error': '#F72585',                # Error/failed states
    'success': '#2ECC71',              # Success/passed states
    'warning': '#F39C12',              # Warning states
    'info': '#3498DB',                 # Informational
    
    # Borders and outlines
    'outline': '#938F99',              # Standard border
    'outline_variant': '#49454F',      # Variant border
    'separator': '#3A3A3C',            # Dividers
}
```

### Usage Guidelines

1. **Never hardcode hex colors** in views/widgets
2. **Always import from MATERIAL_COLORS**
3. **Use semantic color names** (e.g., 'error' not 'red')
4. **Maintain color consistency** across the application

---

## 🔧 Helper Functions

### Common Style Helpers (`helpers/common_styles.py`)

#### Text Styling
```python
# Bold labels with custom size and color
bold_label(font_size=14, color=None) -> str

# Semantic text colors
error_text(font_size=14, bold=False) -> str
success_text(font_size=14, bold=False) -> str
warning_text(font_size=14, bold=False) -> str
info_text(font_size=14, bold=False) -> str
text_secondary() -> str
text_disabled() -> str
```

#### Backgrounds & Borders
```python
# Background colors
background_surface() -> str
background_variant() -> str

# Border styles
border_standard(width=1, radius=4) -> str
border_primary(width=1, radius=4) -> str
border_error(width=1, radius=4) -> str
rounded_corners(radius=4) -> str
```

#### Layout Helpers
```python
# Spacing
padding_standard(size=8) -> str
padding_custom(top, right, bottom, left) -> str
margin_standard(size=8) -> str

# Utility
no_border() -> str
transparent_background() -> str
```

### Gradient Helpers (`helpers/gradients.py`)

```python
# Surface gradients
surface_gradient() -> str        # Standard background gradient
input_gradient() -> str          # Input field gradient

# Button gradients
button_gradient() -> str         # Standard button
primary_button_gradient() -> str # Primary action button
hover_gradient() -> str          # Hover state gradient

# Component gradients
card_gradient() -> str           # Card backgrounds
sidebar_gradient() -> str        # Sidebar gradient
```

---

## 🧩 Component Styles

### Example: Config Dialog

**Modular package structure:**
```
config/
├── __init__.py           # Combines all styles
├── dialog_styles.py      # Container styles
├── input_styles.py       # Input widgets
├── button_styles.py      # All buttons
└── label_styles.py       # Labels and text
```

**Usage:**
```python
# Import the complete dialog style
from src.app.presentation.styles.components.config import CONFIG_DIALOG_STYLE

dialog.setStyleSheet(CONFIG_DIALOG_STYLE)

# Or import specific components
from src.app.presentation.styles.components.config.button_styles import (
    CONFIG_SAVE_BUTTON_STYLE,
    CONFIG_CANCEL_BUTTON_STYLE
)

save_btn.setStyleSheet(CONFIG_SAVE_BUTTON_STYLE)
cancel_btn.setStyleSheet(CONFIG_CANCEL_BUTTON_STYLE)
```

---

## ✅ Best Practices

### 1. Import Organization

```python
# Standard library
import json
from pathlib import Path

# Third-party (PySide6)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel

# Local - Constants first
from src.app.presentation.styles.constants.colors import MATERIAL_COLORS

# Local - Helpers second
from src.app.presentation.styles.helpers.common_styles import bold_label

# Local - Component styles last
from src.app.presentation.styles.components.dialogs import TEST_DETAIL_DIALOG_STYLE
```

### 2. Style Composition

**Good - Composable:**
```python
from src.app.presentation.styles.helpers.common_styles import bold_label, padding_standard

label.setStyleSheet(f"""
    {bold_label(16, MATERIAL_COLORS['primary'])}
    {padding_standard(12)}
""")
```

**Better - Dedicated constant:**
```python
# In styles/components/my_component.py
HEADER_LABEL_STYLE = f"""
    {bold_label(16, MATERIAL_COLORS['primary'])}
    {padding_standard(12)}
"""

# In your view
from src.app.presentation.styles.components.my_component import HEADER_LABEL_STYLE
label.setStyleSheet(HEADER_LABEL_STYLE)
```

### 3. Dynamic Styles

**Use functions for state-based styling:**
```python
# In styles/components/my_component.py
def get_status_style(passed: bool) -> str:
    """Get style based on pass/fail status"""
    color = MATERIAL_COLORS['success'] if passed else MATERIAL_COLORS['error']
    return bold_label(14, color)

# In your view
label.setStyleSheet(get_status_style(test_passed))
```

---

## 📋 Common Patterns

### Pattern 1: Card with Header

```python
from src.app.presentation.styles.helpers.common_styles import (
    bold_label,
    border_standard,
    padding_standard,
    background_surface
)

CARD_STYLE = f"""
    QWidget {{
        {background_surface()}
        {border_standard(1, 8)}
        {padding_standard(16)}
    }}
"""

CARD_HEADER_STYLE = f"""
    QLabel {{
        {bold_label(18, MATERIAL_COLORS['primary'])}
        padding-bottom: 8px;
    }}
"""
```

### Pattern 2: Status Label

```python
from src.app.presentation.styles.helpers.common_styles import error_text, success_text

def get_test_result_style(passed: bool) -> str:
    return success_text(14, bold=True) if passed else error_text(14, bold=True)
```

### Pattern 3: Hover Effects

```python
BUTTON_STYLE = f"""
    QPushButton {{
        background: {MATERIAL_COLORS['primary']};
        color: {MATERIAL_COLORS['on_primary']};
        border-radius: 4px;
        padding: 8px 16px;
    }}
    QPushButton:hover {{
        background: {MATERIAL_COLORS['primary_variant']};
    }}
"""
```

---

## 📏 File Size Guidelines

### Limits
- **Component style files**: Maximum 200 lines
- **Helper files**: Maximum 300 lines
- **Package `__init__.py`**: Maximum 100 lines

### When to Split

**Split a file when:**
1. It exceeds 200 lines
2. It contains multiple logical sections
3. Components could be reused independently

**Example - Before split:**
```
config_styles.py (404 lines)  ❌
```

**After split:**
```
config/
├── dialog_styles.py (80 lines)   ✅
├── input_styles.py (150 lines)   ✅
├── button_styles.py (155 lines)  ✅
└── label_styles.py (40 lines)    ✅
```

---

## 🧪 Testing Guidelines

### 1. Visual Testing

After style changes, manually verify:
- ✅ Main window renders correctly
- ✅ All dialogs open without errors
- ✅ Colors match Material Design palette
- ✅ Hover states work
- ✅ Focus states are visible
- ✅ Text is readable

### 2. Code Testing

```bash
# Run the application
py -m src.app

# Run style linter
python scripts/lint_styles.py

# Run unit tests
pytest tests/ -v
```

### 3. Linter Checks

The style linter checks for:
- **Inline styles** in views/widgets
- **Hardcoded hex colors** (should use MATERIAL_COLORS)
- **Oversized files** (>200 lines)

---

## 🤝 Contribution Guidelines

### Adding New Styles

1. **Choose the right location:**
   - Component-specific → `styles/components/`
   - Reusable helper → `styles/helpers/common_styles.py`
   - Color constant → `styles/constants/colors.py`

2. **Follow naming conventions:**
   - Constants: `UPPER_SNAKE_CASE`
   - Functions: `lower_snake_case`
   - Use descriptive names (e.g., `PRIMARY_BUTTON_STYLE` not `BTN_1`)

3. **Add documentation:**
   ```python
   def get_card_style(highlighted: bool = False) -> str:
       """
       Get card style with optional highlight.
       
       Args:
           highlighted: Whether to apply highlight styling
           
       Returns:
           CSS style string for card widget
           
       Example:
           >>> card.setStyleSheet(get_card_style(highlighted=True))
       """
   ```

4. **Test your changes:**
   - Run the application
   - Run the linter
   - Verify no regressions

### Modifying Existing Styles

1. **Check for usage:**
   ```python
   # Search for all usages before changing
   # Use VS Code search or grep
   ```

2. **Consider backward compatibility:**
   - If removing a style, ensure no files use it
   - If renaming, update all imports

3. **Update documentation:**
   - Add comments explaining changes
   - Update this README if patterns change

### Code Review Checklist

Before submitting style changes:
- [ ] No hardcoded hex colors
- [ ] No inline styles in views/widgets
- [ ] File size under 200 lines
- [ ] Style linter passes
- [ ] Application runs without errors
- [ ] Imports organized correctly
- [ ] Documentation updated

---

## 🔍 Migration Notes

This styling system was migrated in October 2024 to improve:
- **Maintainability**: Eliminated 104 lines of duplicate Theme classes
- **Consistency**: Single source of truth for colors
- **Modularity**: Split 3 oversized files into 9 focused modules
- **Reusability**: Created 30+ helper functions

### Legacy Code

Some files still contain legacy patterns:
- `views/main_window/document.py` - Inline styles (acceptable for markdown)
- `views/help_center/document.py` - Inline styles (acceptable for markdown)
- `styles/components/editor.py` - Custom theme colors for syntax highlighting
- `styles/components/console.py` - Terminal-specific colors

These are **intentional exceptions** and should not be modified without careful consideration.

---

## 📚 Additional Resources

- **Material Design 3**: https://m3.material.io/
- **Qt Style Sheets**: https://doc.qt.io/qt-6/stylesheet-reference.html
- **PySide6 Docs**: https://doc.qt.io/qtforpython-6/

---

## 📝 Changelog

### Week 4 (October 2024)
- Added `common_styles.py` helper functions (18 functions)
- Created style linter (`scripts/lint_styles.py`)
- Reduced style violations by 70%+

### Week 3 (October 2024)
- Split `status_view_styles.py` into 3-file package
- Split `config_styles.py` into 4-file package
- Split `test_view_styles.py` into 2-file package

### Week 2 (October 2024)
- Created `inputs/input_styles.py` (7 input styles)
- Added error label helpers to `results.py`
- Centralized 127+ inline style references

### Week 1 (October 2024)
- Expanded MATERIAL_COLORS palette (8 new colors)
- Removed duplicate Theme classes
- Created `helpers/gradients.py` (12 gradient functions)
- Created `dialogs/test_detail_styles.py`

---

**Last Updated**: October 18, 2024  
**Maintainer**: Code Testing Suite Development Team  
**Version**: 2.0 (Post-Migration)
