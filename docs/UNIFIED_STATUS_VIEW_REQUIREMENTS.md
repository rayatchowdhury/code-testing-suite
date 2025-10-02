# Unified Status View - Comprehensive Requirements Document

**Date:** October 2, 2025  
**Version:** 1.0  
**Status:** Requirements Analysis & Feasibility Study

---

## 📋 Executive Summary

This document analyzes the requirement to **unify and redesign the status windows** for all three test types (Validator, Comparator, Benchmarker) into a **single, card-based, in-display-area view** with enhanced controls and consistent design.

**Key Changes:**
- Convert from **popup QDialog** → **embedded DisplayArea widget**
- Unify **3 separate status windows** → **1 base status widget** + specialized extensions
- Add **pause/resume/stop controls** for test execution
- Implement **card-based UI** with dynamic layout (1→2 columns)
- Add **time/memory metrics** to all test types (currently only Benchmarker has this)
- Implement **detailed test card expansion** within sections

---

## 🎯 Requirement Understanding

### Current Architecture

#### **Status Windows (3 Separate Implementations)**
```
ValidatorStatusWindow (QDialog)
├── Fixed 500x400 popup
├── 3-stage pipeline visualization
├── Results text area
└── Progress bar

CompareStatusWindow (QDialog)
├── Min 600x600 popup
├── Dual view (current test/history)
├── 3 text areas (input/correct/test output)
└── History list

BenchmarkStatusWindow (QDialog)
├── Min 600x600 popup
├── Performance metrics (time/memory)
├── 2 text areas (input/output)
└── History with performance data
```

**Issues with Current Design:**
- ❌ Inconsistent UI across test types
- ❌ Modal dialogs block main window interaction
- ❌ No pause/resume capability
- ❌ Different layouts/behaviors
- ❌ Limited time/memory tracking (only Benchmarker)
- ❌ Disconnected from main workflow

---

### Proposed Architecture

#### **Unified Status View (Embedded Widget)**
```
UnifiedStatusView (QWidget in DisplayArea)
├── Sidebar (modified)
│   ├── Back button → Returns to test window
│   ├── Pause button → Pause test execution
│   ├── Resume button → Continue paused tests
│   ├── Stop button → Cancel all tests
│   └── No compile button
│
├── Progress Section (Top - QHBoxLayout)
│   ├── Visual Progress (80% width)
│   │   └── Tick/Cross emoji progress bar
│   └── Stats Panel (20% width)
│       ├── Percentage complete
│       ├── Passed count
│       └── Failed count
│
└── Test Cards Section (Bottom - Dynamic Layout)
    ├── Initial: Single Column (all tests)
    ├── After First Failure: Two Columns
    │   ├── Left: Passed Tests (green tint)
    │   └── Right: Failed Tests (red tint)
    │
    └── Card Contents (All Test Types)
        ├── Test number
        ├── Time taken
        ├── Memory used
        └── Pass/Fail indicator
```

#### **Card Expansion Behavior**
```
When Card Clicked:
├── Replaces its section (passed/failed)
├── Shows BaseTestCardDetail widget
│   ├── Header: Test #, Time, Memory, Status
│   ├── Metrics panel
│   └── Text areas (type-specific)
│       ├── Validator: Input, Test Output, Validation Message
│       ├── Comparator: Input, Correct Output, Test Output
│       └── Benchmarker: Input, Output
│
└── Back button → Returns to card list view
```

---

## 🏗️ Architectural Changes Needed

### 1. **Base Widget Hierarchy**

```python
# New base class for unified status view
class BaseStatusView(QWidget):
    """Base status view for all test types"""
    
    def __init__(self, test_type: str, parent=None):
        self.test_type = test_type  # 'validator', 'comparator', 'benchmarker'
        self.sidebar = self._create_status_sidebar()
        self.progress_section = ProgressSection()
        self.cards_section = TestCardsSection()
        
    def _create_status_sidebar(self) -> Sidebar:
        """Create sidebar with pause/resume/stop controls"""
        
    def handle_test_started(self, test_num, total):
        """Handle test start signal"""
        
    def handle_test_completed(self, **kwargs):
        """Handle test completion - to be overridden"""
        
    def handle_all_tests_completed(self, all_passed):
        """Handle all tests completion"""

# Specialized implementations
class ValidatorStatusView(BaseStatusView):
    def __init__(self, parent=None):
        super().__init__('validator', parent)
        
    def handle_test_completed(self, test_number, passed, input_data, 
                              test_output, validation_message, 
                              error_details, validator_exit_code):
        # Create validator-specific test card
        card = ValidatorTestCard(...)
        self.cards_section.add_card(card, passed)

class ComparatorStatusView(BaseStatusView):
    def handle_test_completed(self, test_number, passed, input_text, 
                              correct_output, test_output):
        card = ComparatorTestCard(...)
        self.cards_section.add_card(card, passed)

class BenchmarkerStatusView(BaseStatusView):
    def handle_test_completed(self, test_name, test_number, passed, 
                              time_taken, memory_used, memory_passed):
        card = BenchmarkerTestCard(...)
        self.cards_section.add_card(card, passed)
```

### 2. **Card System**

```python
class BaseTestCard(QFrame):
    """Base test card widget"""
    clicked = Signal(int)  # Emits test number
    
    def __init__(self, test_number, passed, time, memory):
        self.test_number = test_number
        self.passed = passed
        self.time = time
        self.memory = memory
        self._setup_ui()
        self._apply_tint()  # Green/red based on passed
        
class ValidatorTestCard(BaseTestCard):
    """Validator-specific card"""
    def __init__(self, test_number, passed, time, memory, 
                 validation_message, error_details):
        super().__init__(test_number, passed, time, memory)
        self.validation_message = validation_message
        self.error_details = error_details

class BaseTestCardDetail(QWidget):
    """Detailed view when card is clicked"""
    back_requested = Signal()
    
    def __init__(self, test_data):
        self._setup_header()  # Test #, time, memory, status
        self._setup_metrics()
        self._setup_text_areas()  # Type-specific
```

### 3. **Dynamic Layout Manager**

```python
class TestCardsSection(QWidget):
    """Manages dynamic 1→2 column layout"""
    
    def __init__(self):
        self.layout_mode = 'single'  # 'single' or 'split'
        self.passed_cards = []
        self.failed_cards = []
        self._setup_layouts()
        
    def add_card(self, card: BaseTestCard, passed: bool):
        if passed:
            self.passed_cards.append(card)
            self._add_to_passed_column(card)
        else:
            self.failed_cards.append(card)
            if self.layout_mode == 'single':
                self._switch_to_split_layout()
            self._add_to_failed_column(card)
            
    def _switch_to_split_layout(self):
        """Convert from 1 column to 2 columns"""
        # Move existing passed cards to left column
        # Create right column for failed cards
        self.layout_mode = 'split'
        
    def show_card_detail(self, card: BaseTestCard):
        """Replace section with detail view"""
        section = 'passed' if card.passed else 'failed'
        # Use QStackedWidget to switch views
```

### 4. **Progress Section**

```python
class ProgressSection(QWidget):
    """Progress bar with emoji indicators + stats"""
    
    def __init__(self):
        self.progress_bar = EmojiProgressBar()  # ✓ / ✗ indicators
        self.stats_panel = StatsPanel()
        
class EmojiProgressBar(QWidget):
    """Custom progress bar showing ✓/✗ for each test"""
    
    def add_test_result(self, passed: bool):
        # Add ✓ or ✗ to visual progress
        
class StatsPanel(QWidget):
    """Statistics display"""
    
    def update_stats(self, completed, total, passed, failed):
        percentage = (completed / total) * 100
        self.percentage_label.setText(f"{percentage:.1f}%")
        self.passed_label.setText(f"Passed: {passed}")
        self.failed_label.setText(f"Failed: {failed}")
```

---

## 🔧 Integration with Existing System

### 1. **Runner Changes**

```python
# In BaseRunner
def _create_test_status_window(self):
    """CHANGED: Create status view instead of dialog"""
    # Old: return ValidatorStatusWindow()  # QDialog
    # New: 
    status_view = self._create_status_view()  # QWidget
    return status_view
    
def run_tests(self, test_count, **kwargs):
    self.status_view = self._create_test_status_window()
    
    # CHANGED: Don't call .show(), instead integrate with display area
    # Old: self.status_window.show()
    # New: self._integrate_status_view()
    
    # Rest remains the same...
    
def _integrate_status_view(self):
    """Integrate status view into display area"""
    # Get the current window's display area
    if hasattr(self, 'parent_window'):
        display_area = self.parent_window.display_area
        display_area.set_content(self.status_view)
```

### 2. **Window Integration**

```python
# In ComparatorWindow (and similar)
class ComparatorWindow(SidebarWindowBase):
    def handle_action_button(self, button_text):
        if button_text == 'Run':
            # Store reference to window in comparator
            self.comparator.parent_window = self
            
            test_count = self.test_count_slider.value()
            self.comparator.run_comparison_test(test_count)
            # Status view will automatically integrate into display_area
```

### 3. **Pause/Resume/Stop Implementation**

```python
# In BaseRunner
def pause_tests(self):
    """Pause test execution"""
    if self.worker and hasattr(self.worker, 'pause'):
        self.worker.pause()
        
def resume_tests(self):
    """Resume paused tests"""
    if self.worker and hasattr(self.worker, 'resume'):
        self.worker.resume()
        
def stop_tests(self):
    """Stop tests and return to test window"""
    self.stop()  # Existing method
    # Navigate back
    if hasattr(self, 'parent_window'):
        # Restore original display area content
        self.parent_window.display_area.set_content(
            self.parent_window.original_content
        )

# In Workers (ValidatorTestWorker, etc.)
class BaseTestWorker(QObject):
    def __init__(self):
        self.is_running = True
        self.is_paused = False
        self._pause_lock = threading.Lock()
        self._pause_event = threading.Event()
        self._pause_event.set()  # Initially not paused
        
    def pause(self):
        self.is_paused = True
        self._pause_event.clear()
        
    def resume(self):
        self.is_paused = False
        self._pause_event.set()
        
    def run_tests(self):
        # In test loop:
        for test_num in range(1, self.test_count + 1):
            # Check pause state
            self._pause_event.wait()  # Blocks if paused
            
            if not self.is_running:
                break
                
            # Run test...
```

---

## 📊 Time/Memory Tracking for All Test Types

Currently only **Benchmarker** tracks time and memory. Need to add this to **Validator** and **Comparator**.

### Implementation Strategy:

```python
# Add to ValidatorTestWorker and ComparisonTestWorker

def _run_single_test_with_metrics(self, test_number):
    """Run test with time and memory tracking"""
    
    # Track memory for each stage
    def monitor_process(process):
        try:
            proc = psutil.Process(process.pid)
            peak_memory = 0
            while process.poll() is None:
                mem = proc.memory_info().rss / (1024 * 1024)  # MB
                peak_memory = max(peak_memory, mem)
                time.sleep(0.01)
            return peak_memory
        except:
            return 0
    
    # Generator stage
    gen_start = time.time()
    gen_process = subprocess.Popen(...)
    gen_memory = monitor_process(gen_process)
    gen_time = time.time() - gen_start
    
    # Test stage
    test_start = time.time()
    test_process = subprocess.Popen(...)
    test_memory = monitor_process(test_process)
    test_time = time.time() - test_start
    
    # Validator stage (for validator)
    val_start = time.time()
    val_process = subprocess.Popen(...)
    val_memory = monitor_process(val_process)
    val_time = time.time() - val_start
    
    # Store metrics
    total_time = gen_time + test_time + val_time
    total_memory = max(gen_memory, test_memory, val_memory)
    
    return {
        'time': total_time,
        'memory': total_memory,
        # ... other test data
    }
```

### Signal Updates:

```python
# Change signal signatures to include metrics

# ValidatorTestWorker
testCompleted = Signal(int, bool, str, str, str, str, int, float, float)
# Added: time (float), memory (float)

# ComparisonTestWorker  
testCompleted = Signal(int, bool, str, str, str, float, float)
# Added: time (float), memory (float)
```

---

## 🎨 Styling & Design System

### Color Scheme (Material Design)

```python
# Success/Pass colors
PASS_BACKGROUND = "#e8f5e9"  # Light green
PASS_BORDER = "#4caf50"      # Green
PASS_TEXT = "#2e7d32"        # Dark green

# Failure colors
FAIL_BACKGROUND = "#ffebee"  # Light red
FAIL_BORDER = "#f44336"      # Red
FAIL_TEXT = "#c62828"        # Dark red

# Card styles
TEST_CARD_STYLE = """
QFrame {
    background: %s;
    border: 2px solid %s;
    border-radius: 8px;
    padding: 12px;
}
QFrame:hover {
    border-width: 3px;
    background: %s;
}
"""

# Progress bar with emojis
EMOJI_PROGRESS_STYLE = """
QWidget {
    background: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 4px;
}
"""
```

### Layout Specifications:

```
╔════════════════════════════════════════════════╗
║ Sidebar        ║  Display Area                 ║
║ (200px)        ║  (Remaining width)            ║
║                ║                                ║
║ Back           ║  Progress Section (80px)      ║
║ ───────        ║  ┌──────────────────────────┐ ║
║ Pause          ║  │ ✓✗✓✓✗✓ │ 60% │ P:4 F:2 │ ║
║ Resume         ║  └──────────────────────────┘ ║
║ Stop           ║                                ║
║                ║  Cards Section (Remaining)    ║
║                ║  ┌─────────┬─────────┐        ║
║                ║  │ Passed  │ Failed  │        ║
║                ║  │ [Card1] │ [Card6] │        ║
║                ║  │ [Card2] │ [Card8] │        ║
║                ║  │ [Card3] │         │        ║
║                ║  │ [Card4] │         │        ║
║                ║  │ [Card5] │         │        ║
║                ║  │ [Card7] │         │        ║
║                ║  └─────────┴─────────┘        ║
╚════════════════════════════════════════════════╝
```

---

## ✅ Feasibility Analysis

### **HIGHLY FEASIBLE** ✓

**Reasons:**
1. ✅ Qt provides all necessary widgets (QStackedWidget, QScrollArea, QFrame)
2. ✅ Signal/slot system already in place for communication
3. ✅ Material Design styling system already implemented
4. ✅ BaseRunner/Worker architecture supports extension
5. ✅ DisplayArea integration mechanism exists
6. ✅ psutil already used in Benchmarker for memory tracking

### Technical Capabilities:

| Feature | Feasibility | Notes |
|---------|-------------|-------|
| Embed in DisplayArea | ✅ Easy | DisplayArea.set_content() already exists |
| Dynamic 1→2 columns | ✅ Easy | QHBoxLayout + show/hide |
| Card-based UI | ✅ Easy | QFrame + custom painting |
| Pause/Resume | ✅ Medium | Need threading.Event in workers |
| Time/Memory tracking | ✅ Medium | Extend existing Benchmarker code |
| Card expansion | ✅ Easy | QStackedWidget pattern |
| Emoji progress bar | ✅ Easy | Custom QWidget with paintEvent |
| Back button navigation | ✅ Easy | Store previous content reference |

---

## 🔴 Complexity Assessment

### Overall Complexity: **MEDIUM-HIGH** ⚠️

### Breakdown by Component:

#### **1. Base Status View (Medium)** 🟡
- **Effort:** 2-3 days
- **Risk:** Low
- **Reason:** Standard Qt widget composition

#### **2. Card System (Low-Medium)** 🟢
- **Effort:** 2 days
- **Risk:** Low
- **Reason:** Simple QFrame subclassing

#### **3. Dynamic Layout (Medium)** 🟡
- **Effort:** 2-3 days
- **Risk:** Medium
- **Reason:** Layout switching can be tricky, need proper widget cleanup

#### **4. Pause/Resume (High)** 🔴
- **Effort:** 3-4 days
- **Risk:** High
- **Reason:** Threading complexity, state management, process control
- **Challenges:**
  - Worker is in separate QThread
  - Processes already spawned may not pause gracefully
  - Need to handle pause during subprocess execution
  - State synchronization between threads

#### **5. Time/Memory Tracking (Medium-High)** 🟡
- **Effort:** 2-3 days per test type
- **Risk:** Medium
- **Reason:** Process monitoring is non-trivial
- **Challenges:**
  - Accurate memory measurement
  - Cross-platform differences (Windows/Linux)
  - Memory tracking for short-lived processes

#### **6. Signal Refactoring (Medium)** 🟡
- **Effort:** 2 days
- **Risk:** Low-Medium
- **Reason:** Need to update signal signatures, could break compatibility

#### **7. Integration & Testing (High)** 🔴
- **Effort:** 3-5 days
- **Risk:** High
- **Reason:** Integration with existing code, edge cases, regression testing

### **Total Estimated Effort: 18-26 days** (3.6-5.2 weeks)

---

## ⚠️ Risks & Challenges

### 1. **Pause/Resume Complexity** 🔴 **HIGH RISK**

**Problem:** 
- Tests run in separate processes via `subprocess.Popen()`
- Once started, processes don't have built-in pause mechanism
- QThread workers coordinate multiple process executions

**Solutions:**
- **Option A (Simple):** "Pause" only prevents starting NEW tests, current test completes
  ```python
  if self.is_paused:
      continue  # Skip to next iteration
  ```
  - ✅ Easy to implement
  - ❌ Not true pause (current test finishes)
  
- **Option B (Complex):** Use process signals (SIGSTOP/SIGCONT on Unix, harder on Windows)
  ```python
  if os.name != 'nt':
      os.kill(process.pid, signal.SIGSTOP)  # Pause
      os.kill(process.pid, signal.SIGCONT)  # Resume
  ```
  - ✅ True pause
  - ❌ Platform-dependent, complex
  - ❌ May not work with all programs

**Recommendation:** Start with **Option A** (pseudo-pause), upgrade to Option B if needed.

### 2. **Memory Tracking Accuracy** 🟡 **MEDIUM RISK**

**Problem:**
- `psutil.Process().memory_info()` samples memory periodically
- Short-lived processes may peak between samples
- Overhead of monitoring affects performance

**Solutions:**
- Increase sampling frequency (10ms → 5ms)
- Use peak RSS (Resident Set Size) instead of current
- Accept ±5% margin of error

### 3. **Backward Compatibility** 🟡 **MEDIUM RISK**

**Problem:**
- Existing code may depend on status windows being QDialog
- Signal signatures changing breaks external listeners
- Database schema may need updates for time/memory

**Solutions:**
- Keep old status windows for migration period
- Add new signals without removing old ones (deprecate gradually)
- Add time/memory columns to database as nullable

### 4. **UI Performance** 🟢 **LOW RISK**

**Problem:**
- Large number of test cards (100+) may slow down UI
- Frequent updates during test execution

**Solutions:**
- Use QScrollArea with viewport optimization
- Update cards in batches
- Lazy loading for off-screen cards

---

## 📦 Implementation Strategy

### Phase 1: Foundation (Week 1)
- [ ] Create `BaseStatusView` widget
- [ ] Create `BaseTestCard` and card variants
- [ ] Implement `ProgressSection` and `StatsPanel`
- [ ] Basic styling and Material Design integration

### Phase 2: Layout & Cards (Week 2)
- [ ] Implement `TestCardsSection` with dynamic layout
- [ ] Card click → detail view expansion
- [ ] Emoji progress bar
- [ ] Test with mock data

### Phase 3: Integration (Week 3)
- [ ] Modify `BaseRunner` to use status view instead of dialog
- [ ] Update `DisplayArea` integration
- [ ] Implement back button navigation
- [ ] Connect existing signals to new views

### Phase 4: Metrics (Week 4)
- [ ] Add time/memory tracking to ValidatorTestWorker
- [ ] Add time/memory tracking to ComparisonTestWorker
- [ ] Update signal signatures
- [ ] Test accuracy of measurements

### Phase 5: Controls (Week 5)
- [ ] Implement pseudo-pause (Option A)
- [ ] Implement resume functionality
- [ ] Implement stop with cleanup
- [ ] State management and synchronization

### Phase 6: Polish & Testing (Week 6)
- [ ] Comprehensive testing (unit, integration, UI)
- [ ] Performance optimization
- [ ] Documentation
- [ ] Migration guide
- [ ] Bug fixes

---

## 🎯 Recommendations

### Priority Order:

1. **HIGH PRIORITY** 🔴
   - Base status view foundation
   - Card system
   - Display area integration
   - Stop button (already exists)

2. **MEDIUM PRIORITY** 🟡
   - Dynamic layout switching
   - Time/memory tracking for all types
   - Card expansion/detail view
   - Progress section with stats

3. **LOW PRIORITY** 🟢
   - Pause/Resume (complex, optional feature)
   - Emoji progress bar (nice-to-have)
   - Advanced animations

### Alternative Approach: **Incremental Migration**

Instead of big-bang replacement:

1. Keep existing status windows
2. Add new unified view as **opt-in** feature
3. Add toggle in config: `"use_unified_status_view": false`
4. Migrate one test type at a time
5. Gather feedback and iterate
6. Remove old windows when stable

**Benefits:**
- ✅ Lower risk
- ✅ Easier to rollback
- ✅ Gradual adoption
- ✅ Parallel testing

**Drawbacks:**
- ❌ More maintenance overhead
- ❌ Longer migration period
- ❌ Code duplication

---

## 📝 Conclusion

### Summary:

The proposed unified status view redesign is **technically feasible** and represents a **significant UX improvement**. The main challenges are:

1. **Pause/Resume implementation** (high complexity)
2. **Time/memory tracking extension** (medium complexity)
3. **Integration testing** (high effort)

### Estimated Timeline:

- **Optimistic:** 4 weeks (with pseudo-pause, basic features)
- **Realistic:** 5-6 weeks (with full features, testing)
- **Conservative:** 7-8 weeks (with true pause, polish, comprehensive testing)

### Go/No-Go Decision Factors:

**GO ✅ if:**
- Willing to accept pseudo-pause initially
- Can allocate 5-6 weeks development time
- Team agrees on incremental migration approach
- UI/UX improvement is high priority

**NO-GO ❌ if:**
- True pause/resume is mandatory requirement
- Need completion in < 3 weeks
- High risk aversion (keep current system)
- Limited testing resources

### Final Recommendation: **GO with Incremental Approach** ✅

Implement in phases, starting with one test type (Comparator recommended as it's simplest), validate the design, then extend to others. Accept pseudo-pause for first version, enhance later if needed.

---

**Document Status:** Ready for Review  
**Next Steps:** Team review → Design approval → Implementation kickoff
