# New Directory Structure - Visual Reference

## Presentation Layer Organization (After Refactor)

```
src/app/presentation/
│
├── window_controller/              ← NEW: Core window management
│   ├── __init__.py                 ← NEW: Package exports
│   ├── base_window.py              ← MOVED from views/
│   ├── window_management.py        ← MOVED from views/
│   └── qt_doc_engine.py            ← MOVED from views/
│
├── views/
│   ├── __init__.py                 ← UPDATED: Changed imports
│   │
│   ├── main_window/                ← NEW: Main window package
│   │   ├── __init__.py             ← NEW: Package exports
│   │   ├── main_window.py          ← MOVED from views/
│   │   └── main_window_content.py  ← MOVED & RENAMED from main_window_doc.py
│   │
│   ├── benchmarker/
│   │   ├── __init__.py
│   │   ├── benchmarker_window.py   ← UPDATED: Import from window_controller
│   │   ├── benchmarker_display_area.py
│   │   └── benchmarker_status_view.py
│   │
│   ├── code_editor/
│   │   ├── __init__.py
│   │   ├── code_editor_window.py   ← UPDATED: Import from window_controller
│   │   └── code_editor_display_area.py
│   │
│   ├── comparator/
│   │   ├── __init__.py
│   │   ├── comparator_window.py    ← UPDATED: Import from window_controller
│   │   ├── comparator_display_area.py
│   │   └── comparator_status_view.py
│   │
│   ├── help_center/
│   │   ├── __init__.py             ← UPDATED: Import from window_controller
│   │   ├── help_center_window.py   ← UPDATED: Import from window_controller
│   │   └── help_content.py         ← UPDATED: Import from window_controller
│   │
│   ├── results/
│   │   ├── __init__.py
│   │   ├── results_window.py       ← UPDATED: Import from window_controller
│   │   └── results_widget.py
│   │
│   ├── validator/
│   │   ├── __init__.py
│   │   ├── validator_window.py     ← UPDATED: Import from window_controller
│   │   ├── validator_display_area.py
│   │   └── validator_status_view.py
│   │
│   └── main_window.html            (unchanged location)
│
├── widgets/                        (unchanged)
│   ├── display_area.py
│   ├── sidebar.py
│   ├── test_cards.py
│   └── ...
│
└── styles/                         (unchanged)
    └── ...
```

## Import Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│              Application Entry                      │
│         src/app/__main__.py                         │
│    from ...main_window.main_window import MainWindow│
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│           Main Window Container                     │
│    views/main_window/main_window.py                │
│                                                     │
│  Imports:                                           │
│  - window_controller.base_window                    │
│  - window_controller.window_management              │
│  - .main_window_content                             │
└─────────────────────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        ▼                               ▼
┌──────────────────┐          ┌──────────────────────┐
│ Window Controller│          │  Main Content Widget  │
│                  │          │  main_window_content.py│
│ - base_window    │          │                       │
│ - window_mgmt    │          │  Imports:             │
│ - qt_doc_engine  │          │  - qt_doc_engine      │
└──────────────────┘          └──────────────────────┘
        │
        │ (inherited by all views)
        ▼
┌─────────────────────────────────────────────────────┐
│              View Windows                           │
│                                                     │
│  All inherit from:                                  │
│  window_controller.base_window.SidebarWindowBase    │
│                                                     │
│  - code_editor/code_editor_window.py                │
│  - comparator/comparator_window.py                  │
│  - validator/validator_window.py                    │
│  - benchmarker/benchmarker_window.py                │
│  - help_center/help_center_window.py                │
│  - results/results_window.py                        │
└─────────────────────────────────────────────────────┘
```

## Key Architectural Changes

### 1. Window Controller (New Module)

**Purpose:** Core window infrastructure used by all views

**Components:**
- `base_window.py` - Base class with sidebar layout
- `window_management.py` - Factory and manager for navigation
- `qt_doc_engine.py` - Document rendering for help/welcome

**Why Separate?**
- Reduces coupling between views
- Makes window management reusable
- Clear dependency hierarchy
- Easier to test in isolation

### 2. Main Window Package (New)

**Purpose:** Dedicated package for main window components

**Components:**
- `main_window.py` - Container and content widget
- `main_window_content.py` - Welcome screen document

**Why Package?**
- Groups related functionality
- Separates main window from other views
- Allows for future expansion (multiple content types)
- Better encapsulation

### 3. View Windows (Updated)

**Purpose:** Feature-specific windows (unchanged in structure)

**Change:**
- All now import from `window_controller` instead of `views`
- Clearer dependency: views depend on controller, not peers

## Dependency Graph

```
window_controller/
  ├── (depends on: PySide6, styles, widgets)
  └── (depended by: all views)

views/main_window/
  ├── (depends on: window_controller, widgets)
  └── (depended by: __main__.py, window_management)

views/{feature}/
  ├── (depends on: window_controller, widgets, tools)
  └── (depended by: window_management via factory)
```

## Module Responsibilities

| Module | Responsibility | Depends On | Used By |
|--------|---------------|------------|---------|
| `window_controller` | Window infrastructure | PySide6, styles | All views |
| `views/main_window` | Main application window | window_controller | __main__ |
| `views/{feature}` | Feature-specific UI | window_controller | WindowFactory |
| `widgets` | Reusable UI components | PySide6, styles | All views |
| `styles` | Visual styling | PySide6 | All presentation |

## Benefits of This Structure

1. **Clear Separation:** Infrastructure vs application views
2. **Reduced Coupling:** Views don't import from each other
3. **Better Navigation:** Related files grouped together
4. **Scalability:** Easy to add new window types
5. **Testability:** Can test controller independently
6. **Maintainability:** Clear ownership of responsibilities

## Future Considerations

1. **Consider moving main_window.html** into main_window/ package
2. **May create view_controller/** for view-specific logic
3. **Could extract dialog management** to separate module
4. **Status views** could be grouped in dedicated package
