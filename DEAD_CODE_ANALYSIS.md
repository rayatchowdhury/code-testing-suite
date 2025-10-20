# Dead Code Analysis - Presentation Layer

## Summary
Found **207 potentially unused items** across the presentation layer. Many are legitimate (Qt callbacks, template methods, protocols), but some are clearly dead code.

## 🔴 HIGH PRIORITY - Definitely Unused (Safe to Remove)

### 1. Unused Helper Functions in `styles/helpers/common_styles.py`
**Impact:** 15 unused functions, ~150 lines
```python
- success_text() - never used
- warning_text() - never used
- info_text() - never used
- background_surface() - never used
- background_variant() - never used
- border_standard() - never used
- border_primary() - never used
- border_error() - never used
- rounded_corners() - never used
- padding_standard() - never used
- padding_custom() - never used
- margin_standard() - never used
- text_secondary() - never used
- text_disabled() - never used
- no_border() - never used
- transparent_background() - never used
```

### 2. Unused Gradient Functions in `styles/helpers/gradients.py`
**Impact:** 12 unused functions, ~150 lines
```python
- surface_gradient() - never used
- input_gradient() - never used
- button_gradient() - never used
- primary_button_gradient() - never used
- hover_gradient() - never used
- pressed_gradient() - never used
- progress_gradient() - never used
- success_gradient() - never used
- error_gradient() - never used
- warning_gradient() - never used
- header_gradient() - never used
- dialog_gradient() - never used
```

### 3. Unused Style Functions in Test View
**Files:** `styles/components/test_view/test_control_styles.py`
**Impact:** 7 unused functions, ~50 lines
```python
- get_history_label_style() - never used
- get_running_status_style() - never used
- get_test_view_error_status_style() - never used
- get_test_view_success_status_style() - never used
- get_compilation_status_style() - never used
- get_passed_status_style() - never used
- get_failed_status_style() - never used
```

### 4. Unused Config UI Styles
**File:** `styles/components/config_ui.py`
**Impact:** 3 unused functions, ~30 lines
```python
- get_error_status_style() - never used
- get_neutral_status_style() - never used
- get_success_status_style() - never used
```

### 5. Unused Widget Helper Functions
**File:** `utils/widget_helpers.py`
**Impact:** 2 unused functions, ~20 lines
```python
- find_widgets_by_type() - never used
- clear_layout() - never used
```

### 6. Unused Signal Helpers
**File:** `utils/signal_helpers.py`
**Impact:** 2 unused functions, ~20 lines
```python
- safe_disconnect() - never used
- connect_once() - never used
```

### 7. Unused Inline Style Functions
**File:** `styles/helpers/inline_styles.py`
**Impact:** 2 unused functions
```python
- build_error_style() - never used
- build_status_style() - only in detailed_results_widget import but not used
```

### 8. Unused Results Styles
**File:** `styles/components/results.py`
```python
- create_error_label() - never used
```

### 9. Unused Tab Style
**File:** `styles/components/test_view/test_tab_styles.py`
```python
- get_file_button_style() - never used
```

### 10. Unused Status Widget Style
**File:** `styles/components/status_view/status_widgets_styles.py`
```python
- get_worker_progress_container_style() - never used
```

### 11. Unused Emoji Helper
**File:** `styles/fonts/emoji.py`
```python
- create_emoji_label() - never used
```

### 12. Unused Help Center Function
**File:** `views/help_center/content.py`
```python
- get_available_topics() - never used
```

## 🟡 MEDIUM PRIORITY - Likely Unused (Review Before Removing)

### 1. EditorTabWidget Unused Public Methods
**File:** `widgets/display_area_widgets/editor_tab_widget.py`
**Impact:** 9 unused public methods
```python
- close_current_tab() - public API but never called
- close_all_tabs() - public API but never called
- current_tab() - property never accessed
- tab_count() - property never accessed
- get_tab_at_index() - public API but never called
- get_current_index() - public API but never called
- set_current_index() - public API but never called
- get_all_file_paths() - public API but never called
- save_current_file() - public API but never called
- save_all_files() - public API but never called
```
**Note:** These look like they were meant to be used but aren't. Either use them or remove them.

### 2. TestTabWidget Unused Public Methods
**File:** `widgets/display_area_widgets/test_tab_widget.py`
**Impact:** 5 unused public methods
```python
- get_content_widget() - never called
- get_current_file_path() - never called
- get_current_language() - never called
- set_tab_config() - never called
- get_files_for_tool() - never called
```

### 3. ConsoleOutput Unused Methods
**File:** `widgets/display_area_widgets/console.py`
```python
- requestInput() - never called
- setInputEnabled() - never called
```

### 4. AIPanel Unused Methods
**File:** `widgets/display_area_widgets/ai_panel.py`
```python
- _initialize_ai_background() - defined but never called
- update_code_context() - public method never called
- refresh_from_config() - public method never called
```

### 5. LimitsInputWidget Setters
**File:** `widgets/sidebar_widgets/limits_input_widget.py`
```python
- set_time_limit() - setter never used
- set_memory_limit() - setter never used
```

### 6. TestCountSlider Methods
**File:** `widgets/sidebar_widgets/test_count_slider.py`
```python
- get_range() - getter never used
- set_range() - setter never used
```

### 7. Sidebar Unused Methods
**File:** `widgets/sidebar.py`
```python
- add_spacer() - public method never called
- add_back_button() - public method never called
```

### 8. TestingContentWidget Methods
**File:** `widgets/testing_content_widget.py`
```python
- on_complete() - callback never triggered
- refresh_ai_panel() - public method never called
```

### 9. CodeEditorDisplay Method
**File:** `views/code_editor/code_editor_display_area.py`
```python
- on_complete() - callback never triggered
```

### 10. MainWindow Methods
**File:** `views/main_window/main_window.py`
```python
- MainWindowContent.handle_exit() - never called
- MainWindow.return_to_main() - never called
```

### 11. DetailedResultsWidget Method
**File:** `views/results/detailed_results_window.py`
```python
- _detect_language() - helper never used
```

### 12. Comparator/Validator Window Methods
```python
- ComparatorWindow.handle_compare_options() - never called
- ValidatorWindow.handle_validate_options() - never called
```

### 13. StatusViewPresenter Method
**File:** `widgets/status_view/presenter.py`
```python
- get_statistics() - public method never called
```

## 🟢 LOW PRIORITY - Legitimate (Keep)

### 1. Template Methods (Abstract/Override Pattern)
- `TestWindowBase._get_run_method_name()` - overridden by subclasses
- `StatusViewBase._get_card_class()` - overridden by subclasses
- All `_get_card_class()` and `_get_detail_dialog_class()` in status views

### 2. Qt Framework Callbacks
- `paintEvent()` methods - called by Qt
- `sizeHint()` methods - called by Qt
- `highlightBlock()` methods - called by Qt syntax highlighter
- All signal handler methods (`_on_*`, `_handle_*`)

### 3. Protocol Definitions (Type Hints Only)
- All classes in `base/protocols.py` - used for type checking
- `TestRunner`, `TestCard`, `TestDetailDialog`, `NavigationManager`

### 4. Base Classes (Inheritance Only)
- `WindowBase`, `ContentWindowBase`, `TestWindowBase`, `StatusViewBase`
- These are never instantiated directly but used via inheritance

### 5. Service Singletons
- `NavigationService` - accessed via `.instance()`
- `ErrorHandlerService` - accessed via `.instance()`

### 6. Window Classes
- All window classes (MainWindow, BenchmarkerWindow, etc.) - created via factory

## 📊 Estimated Cleanup Impact

| Category | Files | Lines | Priority |
|----------|-------|-------|----------|
| Unused style helpers | 8 | ~500 | HIGH |
| Unused widget methods | 5 | ~200 | MEDIUM |
| Unused helper functions | 3 | ~100 | HIGH |
| Unused imports | 20+ | ~20 | HIGH |
| **TOTAL REMOVABLE** | **16+** | **~820 lines** | |

## 🎯 Recommended Action Plan

### Phase 1: Clean Unused Style Functions (High Priority)
1. Remove all unused gradient functions from `styles/helpers/gradients.py`
2. Remove unused common style functions from `styles/helpers/common_styles.py`
3. Remove unused test view styles
4. Remove unused inline styles

**Estimated Removal:** ~400-500 lines

### Phase 2: Clean Unused Helper Functions (High Priority)
1. Remove unused widget helpers
2. Remove unused signal helpers
3. Remove unused style utility functions

**Estimated Removal:** ~100 lines

### Phase 3: Review Public APIs (Medium Priority)
1. Review EditorTabWidget unused methods - either use or remove
2. Review TestTabWidget unused methods - either use or remove
3. Review AIPanel unused methods
4. Review widget setter/getter methods

**Estimated Removal:** ~200 lines

### Phase 4: Clean Unused Imports (High Priority)
1. Remove all unused imports flagged by vulture
2. This is safe and has zero risk

**Estimated Removal:** ~20 lines

## ⚠️ Important Notes

1. **Don't Remove:**
   - Template methods (abstract methods overridden by subclasses)
   - Qt framework callbacks (paintEvent, etc.)
   - Protocol definitions (type hints)
   - Base classes used for inheritance
   - Service singletons accessed via .instance()

2. **Test After Each Phase:**
   - Run the application
   - Test each major feature
   - Ensure no import errors

3. **Git Commits:**
   - Commit after each phase
   - Makes it easy to roll back if needed

## 🔍 How to Verify

Before removing any code, verify it's truly unused:

```bash
# Search for usage across entire codebase
grep -r "function_name" src/

# Check for dynamic usage (getattr, etc.)
grep -r "getattr.*function_name" src/
grep -r '"function_name"' src/
```
