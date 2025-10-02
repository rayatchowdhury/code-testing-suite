# Architecture Fix: Duplicate Sidebar Issue

## Problem Description

**Critical Issue**: Two sidebars were appearing simultaneously when running tests - one from the window and one from the status view.

### Root Cause
The `BaseStatusView` was incorrectly creating its own sidebar with back/options buttons, treating itself as a standalone window. When embedded in the display area, this created a second sidebar alongside the window's existing sidebar.

**Incorrect Architecture** (Before):
```
Window
├── Sidebar (window's sidebar)
│   ├── Actions (Compile, Run)
│   └── Footer (Back, Options)
└── Display Area
    └── Status View
        ├── Sidebar (duplicate sidebar!) ❌
        │   ├── "Status" header
        │   └── Footer (Back, Options)
        └── Content (controls, progress, cards)
```

**Correct Architecture** (After):
```
Window
├── Sidebar (single sidebar)
│   ├── Actions (Compile → Stop during tests)
│   └── Footer (Back, Options)
└── Display Area (switches content)
    ├── Editor/Console (normal mode)
    └── Status View (test mode - content only)
        ├── Controls Panel
        ├── Progress Section
        └── Cards Section
```

## Solution Implementation

### 1. Refactored BaseStatusView (unified_status_view.py)

**Changes:**
- ✅ Removed sidebar creation (`_create_sidebar()` method deleted)
- ✅ Removed QSplitter for sidebar/content layout
- ✅ Removed back/options button handling (moved to window level)
- ✅ Made status view content-only with simple QVBoxLayout
- ✅ Kept only: ControlsPanel, ProgressSection, CardsSection

**Result**: Status view is now a simple widget that can be embedded in display area.

### 2. Added Sidebar Button State Management

**Window Classes** (ComparatorWindow, ValidatorWindow, BenchmarkerWindow):

Added two methods to each window class:

```python
def _switch_to_test_mode(self):
    """Hide Compile button, show Stop button when tests start"""
    - Hide compile_btn
    - Show stop_btn (create if needed)

def _restore_normal_mode(self):
    """Show Compile button, hide Stop button when tests finish"""
    - Show compile_btn
    - Hide stop_btn
```

**Key Changes:**
- Store references to `action_section`, `compile_btn`, `run_btn`, `stop_btn`
- Dynamically show/hide buttons during test execution
- Stop button created on-demand and reused

### 3. Updated BaseRunner Integration

**Modified Methods:**

**`_integrate_status_view()`:**
- Switches display area content to status view
- **NEW**: Calls `parent_window._switch_to_test_mode()` to update sidebar buttons
- Now manages both display AND sidebar state

**`_handle_back_request()`:**
- Restores display area to original content
- **NEW**: Calls `parent_window._restore_normal_mode()` to restore sidebar buttons
- Properly coordinates both restorations

### 4. Updated Unit Tests

**test_base_status_view.py:**
- ✅ Removed tests expecting `sidebar` attribute
- ✅ Removed tests expecting `splitter` attribute
- ✅ Updated tests to verify content-only structure
- ✅ Added test: `test_content_only_no_sidebar_or_splitter()`

## Files Modified

### Core Architecture Changes
1. **src/app/presentation/widgets/unified_status_view.py**
   - Removed: sidebar, splitter, back/options buttons
   - Made: content-only QWidget with vertical layout

2. **src/app/core/tools/base/base_runner.py**
   - Enhanced: `_integrate_status_view()` to call `_switch_to_test_mode()`
   - Enhanced: `_handle_back_request()` to call `_restore_normal_mode()`

### Window Updates
3. **src/app/presentation/views/comparator/comparator_window.py**
   - Added: `_switch_to_test_mode()` method
   - Added: `_restore_normal_mode()` method
   - Stored: button references for dynamic management

4. **src/app/presentation/views/validator/validator_window.py**
   - Added: `_switch_to_test_mode()` method
   - Added: `_restore_normal_mode()` method
   - Stored: button references for dynamic management

5. **src/app/presentation/views/benchmarker/benchmarker_window.py**
   - Added: `_switch_to_test_mode()` method
   - Added: `_restore_normal_mode()` method
   - Stored: button references for dynamic management

### Test Updates
6. **tests/unit/test_base_status_view.py**
   - Fixed: 4 tests updated for content-only architecture
   - Removed: expectations of `sidebar` and `splitter` attributes
   - Added: test verifying no sidebar/splitter present

## Test Results

### Before Fix
- ❌ 4 failed tests (expecting sidebar/splitter)
- ❌ Duplicate sidebars in production
- Total: 374 passed, 4 failed

### After Fix
- ✅ All tests passing
- ✅ Single sidebar with proper button transitions
- Total: **377 passed, 5 skipped, 56 warnings**

### Test Coverage
- ✅ Status view creation (content-only)
- ✅ No sidebar/splitter attributes
- ✅ Signal handling (stop, back)
- ✅ Test state tracking
- ✅ Display area integration (existing tests)

## Architecture Benefits

### Before (Incorrect)
- ❌ Two sidebars visible simultaneously
- ❌ Confusing UX with duplicate navigation
- ❌ Status view trying to be standalone window
- ❌ Inconsistent with display area pattern

### After (Correct)
- ✅ Single sidebar with dynamic button state
- ✅ Clean embedding in display area
- ✅ Status view is pure content widget
- ✅ Proper separation of concerns:
  - Window: manages sidebar and navigation
  - Display area: switches content
  - Status view: displays test execution state

## User Experience Flow

### Starting Tests
1. User clicks "Run" button
2. Runner compiles code
3. **Display area switches** to status view
4. **Sidebar updates**: Compile button hidden, Stop button shown
5. Tests execute with live updates in status view

### During Tests
- Single sidebar with Stop button visible
- Status view shows progress, cards, controls
- Back button available in window footer

### Back Button Pressed
1. **Display area restores** to editor/console
2. **Sidebar restores**: Stop button hidden, Compile button shown
3. User back to normal editing mode

## Technical Notes

### Why This Architecture?
1. **Display Area Pattern**: Content switching is display area's responsibility
2. **Single Sidebar**: Window owns navigation, not embedded widgets
3. **State Coordination**: Runner coordinates both display and sidebar changes
4. **Separation of Concerns**: Each component has clear responsibility

### Migration Impact
- ✅ No breaking changes to test execution logic
- ✅ All 377 tests still passing
- ✅ Display area integration tests validate proper embedding
- ✅ Status view still receives same signals and updates

## Conclusion

The duplicate sidebar issue was caused by a fundamental architecture misunderstanding where the status view tried to be a standalone window instead of embedded content. The fix properly separates concerns:

- **Window**: Owns the single sidebar and manages button state
- **Display Area**: Switches between editor/console and status view
- **Status View**: Pure content widget without navigation chrome

This results in a clean, intuitive UX with a single sidebar that dynamically adapts during test execution.
