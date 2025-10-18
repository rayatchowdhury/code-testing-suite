# Status View Architecture Migration Playbook

**Version:** 1.0  
**Date:** October 19, 2025  
**Estimated Time:** 8-12 hours (split across phases)  
**Risk Level:** Medium (requires careful testing)

---

## Executive Summary

This playbook refactors the status view system to achieve:
1. **Clear separation of concerns** (Model → Presenter → View)
2. **Elimination of tight coupling** between BaseStatusView and widgets
3. **Consistent interfaces** using typed models instead of dicts
4. **Cleaner styles organization** (consolidate trivial files)

**Key Principle:** BaseStatusView coordinates, StatusViewPresenter translates, Widgets render.

---

## Phase 1: Prepare Foundation (2 hours)

### Step 1.1: Create Models Module

**File:** `src/app/presentation/models/test_result.py`

```python
"""
Test result models for unified status view system.
"""
from dataclasses import dataclass, field
from typing import Literal, Optional


@dataclass
class TestResult:
    """
    Unified test result model for all test types.
    
    Provides type-safe access to test data instead of raw dicts.
    """
    test_number: int
    passed: bool
    time: float  # seconds
    memory: float  # MB
    test_type: Literal['comparator', 'validator', 'benchmarker']
    
    # Optional common fields
    input_data: str = ""
    output_data: str = ""
    
    # Type-specific data (use dict for flexibility)
    extra_data: dict = field(default_factory=dict)
    
    @classmethod
    def for_comparator(cls, test_number: int, passed: bool, time: float, 
                       memory: float, input_text: str, correct_output: str, 
                       test_output: str) -> 'TestResult':
        """Factory method for comparator tests"""
        return cls(
            test_number=test_number,
            passed=passed,
            time=time,
            memory=memory,
            test_type='comparator',
            input_data=input_text,
            output_data=test_output,
            extra_data={
                'correct_output': correct_output,
                'test_output': test_output,
            }
        )
    
    @classmethod
    def for_validator(cls, test_number: int, passed: bool, time: float,
                      memory: float, input_data: str, test_output: str,
                      validation_message: str, error_details: str,
                      validator_exit_code: int) -> 'TestResult':
        """Factory method for validator tests"""
        return cls(
            test_number=test_number,
            passed=passed,
            time=time,
            memory=memory,
            test_type='validator',
            input_data=input_data,
            output_data=test_output,
            extra_data={
                'validation_message': validation_message,
                'error_details': error_details,
                'validator_exit_code': validator_exit_code,
            }
        )
    
    @classmethod
    def for_benchmarker(cls, test_number: int, passed: bool, time: float,
                        memory: float, test_name: str, memory_passed: bool,
                        input_data: str, output_data: str, 
                        test_size: int) -> 'TestResult':
        """Factory method for benchmarker tests"""
        return cls(
            test_number=test_number,
            passed=passed,
            time=time,
            memory=memory,
            test_type='benchmarker',
            input_data=input_data,
            output_data=output_data,
            extra_data={
                'test_name': test_name,
                'memory_passed': memory_passed,
                'test_size': test_size,
            }
        )


@dataclass
class TestStatistics:
    """Statistics calculated from test execution"""
    total_tests: int
    completed_tests: int
    passed_tests: int
    failed_tests: int
    progress_percentage: float
    current_speed: float  # tests/second
    elapsed_time: float  # seconds
    estimated_remaining: float  # seconds
    
    @property
    def pass_percentage(self) -> float:
        """Calculate pass percentage"""
        if self.completed_tests == 0:
            return 0.0
        return (self.passed_tests / self.completed_tests) * 100
    
    @property
    def fail_percentage(self) -> float:
        """Calculate fail percentage"""
        if self.completed_tests == 0:
            return 0.0
        return (self.failed_tests / self.completed_tests) * 100
```

**File:** `src/app/presentation/models/__init__.py`

```python
"""Presentation layer models"""
from .test_result import TestResult, TestStatistics

__all__ = ['TestResult', 'TestStatistics']
```

---

### Step 1.2: Create Test Execution State Manager

**File:** `src/app/presentation/models/test_execution_state.py`

```python
"""
Test execution state management.
"""
import time
from typing import Dict, List, Optional

from .test_result import TestResult, TestStatistics


class TestExecutionState:
    """
    Manages test execution state and statistics.
    
    Responsible for:
    - Tracking test results
    - Calculating statistics
    - Managing execution timing
    """
    
    def __init__(self):
        self.results: Dict[int, TestResult] = {}
        self.total_tests: int = 0
        self.start_time: Optional[float] = None
        self.max_workers: int = 0
        
    def reset(self, total_tests: int, max_workers: int):
        """Reset state for new test run"""
        self.results.clear()
        self.total_tests = total_tests
        self.max_workers = max_workers
        self.start_time = time.time()
    
    def add_result(self, result: TestResult):
        """Record a test result"""
        self.results[result.test_number] = result
    
    def get_result(self, test_number: int) -> Optional[TestResult]:
        """Retrieve a specific test result"""
        return self.results.get(test_number)
    
    def get_all_results(self) -> List[TestResult]:
        """Get all results sorted by test number"""
        return [self.results[k] for k in sorted(self.results.keys())]
    
    def get_statistics(self) -> TestStatistics:
        """Calculate current statistics"""
        completed = len(self.results)
        passed = sum(1 for r in self.results.values() if r.passed)
        failed = completed - passed
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        speed = completed / elapsed if elapsed > 0 else 0
        remaining_tests = self.total_tests - completed
        estimated_remaining = remaining_tests / speed if speed > 0 else 0
        progress = (completed / self.total_tests * 100) if self.total_tests > 0 else 0
        
        return TestStatistics(
            total_tests=self.total_tests,
            completed_tests=completed,
            passed_tests=passed,
            failed_tests=failed,
            progress_percentage=progress,
            current_speed=speed,
            elapsed_time=elapsed,
            estimated_remaining=estimated_remaining,
        )
    
    @property
    def is_complete(self) -> bool:
        """Check if all tests are complete"""
        return len(self.results) == self.total_tests
    
    @property
    def all_passed(self) -> bool:
        """Check if all completed tests passed"""
        return all(r.passed for r in self.results.values())
```

---

## Phase 2: Create Presenter Layer (3 hours)

### Step 2.1: Status View Presenter

**File:** `src/app/presentation/presenters/status_view_presenter.py`

```python
"""
Status View Presenter - Translation layer between model and widgets.
"""
from typing import TYPE_CHECKING

from src.app.presentation.models.test_result import TestResult, TestStatistics

if TYPE_CHECKING:
    from src.app.presentation.widgets.status_view_widgets import (
        StatusHeaderSection,
        PerformancePanelSection,
        VisualProgressBarSection,
        TestResultsCardsSection,
    )


class StatusViewPresenter:
    """
    Presenter for status view widgets.
    
    Responsibilities:
    - Translate model state changes to widget updates
    - Format data for display
    - Coordinate widget updates in response to events
    
    Does NOT:
    - Store business logic
    - Make decisions about test execution
    - Know about test runners or workers
    """
    
    def __init__(
        self,
        header: 'StatusHeaderSection',
        performance: 'PerformancePanelSection',
        progress_bar: 'VisualProgressBarSection',
        cards_section: 'TestResultsCardsSection',
    ):
        self.header = header
        self.performance = performance
        self.progress_bar = progress_bar
        self.cards_section = cards_section
    
    def initialize_test_run(self, total_tests: int, max_workers: int):
        """Initialize widgets for new test run"""
        self.header.reset(total_tests)
        self.progress_bar.reset(total_tests)
        self.cards_section.clear()
        
        if max_workers > 0:
            self.performance.setup_workers(max_workers)
            self.performance.update_summary(max_workers, 0.0)
    
    def update_test_result(self, result: TestResult, stats: TestStatistics):
        """Update widgets when a test completes"""
        # Update progress bar
        self.progress_bar.add_result(result.test_number, result.passed)
        
        # Update header statistics
        self.header.update_stats(
            completed=stats.completed_tests,
            total=stats.total_tests,
            passed=stats.passed_tests,
            failed=stats.failed_tests,
        )
        
        # Update performance panel
        self.performance.update_summary(
            workers_active=stats.total_tests,  # Could be refined
            speed=stats.current_speed,
        )
    
    def mark_complete(self):
        """Mark test execution as complete"""
        self.header.mark_complete()
    
    def clear_all(self):
        """Clear all widget content"""
        self.cards_section.clear()
```

**File:** `src/app/presentation/presenters/__init__.py`

```python
"""Presentation layer presenters"""
from .status_view_presenter import StatusViewPresenter

__all__ = ['StatusViewPresenter']
```

---

## Phase 3: Refactor BaseStatusView (2 hours)

### Step 3.1: Slim Down BaseStatusView

**File:** `src/app/presentation/widgets/unified_status_view.py` (REPLACE ENTIRE on_tests_started and on_test_completed)

```python
# Add imports at top
from src.app.presentation.models.test_execution_state import TestExecutionState
from src.app.presentation.models.test_result import TestResult
from src.app.presentation.presenters.status_view_presenter import StatusViewPresenter

# In __init__, add:
    def __init__(self, test_type: str, parent=None):
        super().__init__(parent)
        self.test_type = test_type
        self.parent_window = parent
        
        # Use state manager instead of raw attributes
        self.state = TestExecutionState()
        self.tests_running = False  # Keep for backward compatibility
        
        # Presenter will be created after UI setup
        self.presenter = None
        
        self._setup_ui()
        self._setup_styles()
        self._create_presenter()
    
    def _create_presenter(self):
        """Create presenter after widgets are initialized"""
        self.presenter = StatusViewPresenter(
            header=self.status_header,
            performance=self.performance_panel,
            progress_bar=self.progress_bar,
            cards_section=self.cards_section,
        )

# REPLACE on_tests_started:
    def on_tests_started(self, total: int):
        """Called when tests start"""
        self.tests_running = True
        
        # Get worker count
        max_workers = self._determine_worker_count()
        
        # Reset state
        self.state.reset(total, max_workers)
        
        # Delegate to presenter
        self.presenter.initialize_test_run(total, max_workers)
    
    def _determine_worker_count(self) -> int:
        """Determine max worker count from various sources"""
        worker = None
        if hasattr(self, 'runner') and hasattr(self.runner, 'get_current_worker'):
            worker = self.runner.get_current_worker()
        elif self.parent_window and hasattr(self.parent_window, 'comparator'):
            if hasattr(self.parent_window.comparator, 'get_current_worker'):
                worker = self.parent_window.comparator.get_current_worker()
        
        if worker and hasattr(worker, 'max_workers'):
            return worker.max_workers
        
        # Fallback
        import multiprocessing
        return min(8, max(1, multiprocessing.cpu_count() - 1))

# REPLACE on_test_completed:
    def on_test_completed(self, test_number: int, passed: bool, **kwargs):
        """
        Called when a test completes.
        
        Subclasses should override to create TestResult and call this.
        
        Args:
            test_number: Test case number (1-indexed)
            passed: Whether test passed
            **kwargs: Additional test data (will be ignored, use create_result in subclass)
        """
        # This base implementation shouldn't be called directly
        # Subclasses should create TestResult and call _handle_test_result
        raise NotImplementedError(
            "Subclasses must override on_test_completed and create TestResult"
        )
    
    def _handle_test_result(self, result: TestResult):
        """
        Internal method to handle a test result.
        
        Called by subclasses after creating TestResult.
        """
        # Store result
        self.state.add_result(result)
        
        # Get current statistics
        stats = self.state.get_statistics()
        
        # Delegate to presenter
        self.presenter.update_test_result(result, stats)

# UPDATE on_all_tests_completed:
    def on_all_tests_completed(self, all_passed: bool):
        """Called when all tests complete"""
        self.tests_running = False
        self.presenter.mark_complete()
        
        # Notify parent window
        if self.parent_window and hasattr(self.parent_window, "enable_save_button"):
            self.parent_window.enable_save_button()

# ADD backward compatibility properties:
    @property
    def total_tests(self) -> int:
        """Backward compatibility"""
        return self.state.total_tests
    
    @property
    def completed_tests(self) -> int:
        """Backward compatibility"""
        return len(self.state.results)
    
    @property
    def passed_tests(self) -> int:
        """Backward compatibility"""
        return sum(1 for r in self.state.results.values() if r.passed)
    
    @property
    def failed_tests(self) -> int:
        """Backward compatibility"""
        return self.completed_tests - self.passed_tests
```

---

### Step 3.2: Update Subclasses to Use TestResult

**File:** `src/app/presentation/views/comparator/comparator_status_view.py` (REPLACE on_test_completed)

```python
# Add import
from src.app.presentation.models.test_result import TestResult

# REPLACE on_test_completed method:
    def on_test_completed(
        self,
        test_number: int,
        passed: bool,
        input_text: str,
        correct_output: str,
        test_output: str,
        time: float = 0.0,
        memory: float = 0.0,
    ):
        """Handle comparator test completion"""
        # Create typed result
        result = TestResult.for_comparator(
            test_number=test_number,
            passed=passed,
            time=time,
            memory=memory,
            input_text=input_text,
            correct_output=correct_output,
            test_output=test_output,
        )
        
        # Store for detail view
        self.test_data[test_number] = {
            "passed": passed,
            "input_text": input_text,
            "correct_output": correct_output,
            "test_output": test_output,
            "time": time,
            "memory": memory,
        }
        
        # Call base class with typed result
        self._handle_test_result(result)
        
        # Create and add card
        card = ComparatorTestCard(
            test_number=test_number,
            passed=passed,
            time=time,
            memory=memory,
            input_text=input_text,
            correct_output=correct_output,
            test_output=test_output,
        )
        self.add_test_card(card)
```

**Apply similar changes to:**
- `validator_status_view.py` (use `TestResult.for_validator`)
- `benchmarker_status_view.py` (use `TestResult.for_benchmarker`)

---

## Phase 4: Consolidate Styles (1 hour)

### Step 4.1: Merge status_containers.py

**Action:** Delete `src/app/presentation/styles/components/status_view/status_containers.py`

**File:** `src/app/presentation/styles/components/status_view/status_widgets_styles.py` (ADD at bottom)

```python
# ============================================================================
# CONTAINER STYLES (merged from status_containers.py)
# ============================================================================

STATUS_VIEW_CONTAINER_STYLE = f"""
QWidget {{
    background: {MATERIAL_COLORS['background']};
    border: none;
}}
"""

# Update __all__ to include STATUS_VIEW_CONTAINER_STYLE
```

**File:** `src/app/presentation/styles/components/status_view/__init__.py` (UPDATE imports)

```python
# REMOVE:
# from .status_containers import STATUS_VIEW_CONTAINER_STYLE

# ADD:
from .status_widgets_styles import (
    # ... existing imports ...
    STATUS_VIEW_CONTAINER_STYLE,  # Add this
)

# Update __all__ accordingly
```

---

### Step 4.2: Optimize Style Files Structure

**OPTIONAL:** Split `status_widgets_styles.py` by component if it gets too large:

```
status_view/
├── __init__.py (exports)
├── status_cards.py (existing)
└── widgets/
    ├── __init__.py
    ├── header_styles.py (STATUS_HEADER_* styles)
    ├── performance_styles.py (PERFORMANCE_PANEL_*, WORKER_* styles)
    ├── progress_styles.py (PROGRESS_BAR_*, VISUAL_PROGRESS_* styles)
    └── cards_section_styles.py (CARDS_SECTION_* styles)
```

**Decision:** Keep as-is for now (430 lines is manageable). Only split if crosses 600+ lines.

---

## Phase 5: Testing & Validation (2 hours)

### Step 5.1: Update Unit Tests

**File:** `tests/unit/presentation/widgets/test_status_view.py` (UPDATE tests)

```python
# Add import
from src.app.presentation.models.test_result import TestResult

# UPDATE fixture to use new architecture
@pytest.fixture
def status_view(qtbot):
    """Create BaseStatusView widget for testing."""
    # Use concrete subclass for testing since BaseStatusView.on_test_completed 
    # now raises NotImplementedError
    from src.app.presentation.views.comparator.comparator_status_view import ComparatorStatusView
    widget = ComparatorStatusView()
    qtbot.addWidget(widget)
    return widget

# UPDATE test methods to use proper interface:
class TestStatusViewTestLifecycle:
    def test_on_test_completed_updates_counters(self, status_view):
        """Should update counters when test completes."""
        status_view.on_tests_started(10)
        
        # Use proper comparator interface
        status_view.on_test_completed(
            test_number=1,
            passed=True,
            input_text="test",
            correct_output="output",
            test_output="output",
            time=0.5,
            memory=10.0
        )
        
        assert status_view.completed_tests == 1
        assert status_view.passed_tests == 1
        assert status_view.failed_tests == 0
```

---

### Step 5.2: Create New Tests for Models

**File:** `tests/unit/presentation/models/test_test_result.py`

```python
"""Unit tests for TestResult model"""
import pytest
from src.app.presentation.models.test_result import TestResult, TestStatistics


class TestTestResultModel:
    def test_comparator_factory(self):
        """Should create comparator test result"""
        result = TestResult.for_comparator(
            test_number=1,
            passed=True,
            time=0.5,
            memory=10.0,
            input_text="input",
            correct_output="expected",
            test_output="actual",
        )
        
        assert result.test_number == 1
        assert result.passed is True
        assert result.test_type == 'comparator'
        assert result.extra_data['correct_output'] == "expected"
    
    def test_validator_factory(self):
        """Should create validator test result"""
        result = TestResult.for_validator(
            test_number=2,
            passed=False,
            time=1.0,
            memory=20.0,
            input_data="input",
            test_output="output",
            validation_message="Wrong Answer",
            error_details="Details",
            validator_exit_code=1,
        )
        
        assert result.test_number == 2
        assert result.passed is False
        assert result.test_type == 'validator'


class TestTestStatistics:
    def test_calculates_percentages(self):
        """Should calculate pass/fail percentages"""
        stats = TestStatistics(
            total_tests=10,
            completed_tests=5,
            passed_tests=4,
            failed_tests=1,
            progress_percentage=50.0,
            current_speed=2.0,
            elapsed_time=2.5,
            estimated_remaining=2.5,
        )
        
        assert stats.pass_percentage == 80.0
        assert stats.fail_percentage == 20.0
```

---

### Step 5.3: Integration Testing

Run existing integration tests to ensure nothing broke:

```bash
pytest tests/integration/test_comparator_workflow.py -v
pytest tests/integration/test_validator_workflow.py -v
pytest tests/integration/test_benchmarker_workflow.py -v
```

---

## Phase 6: Documentation & Cleanup (1 hour)

### Step 6.1: Update Architecture Docs

**File:** `docs/architecture/STATUS_VIEW_ARCHITECTURE.md` (CREATE)

```markdown
# Status View Architecture

## Overview

The status view system follows the Model-View-Presenter (MVP) pattern:

```
┌─────────────────────────────────────────┐
│          Test Execution                  │
│    (Worker signals test events)         │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│     ComparatorStatusView                 │
│     ValidatorStatusView                  │
│     BenchmarkerStatusView                │
│  (Convert events to TestResult)         │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│      BaseStatusView (Controller)        │
│  - Manages TestExecutionState           │
│  - Coordinates Presenter                │
│  - Handles user signals                 │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│   StatusViewPresenter (Translator)      │
│  - Translates state to widget updates   │
│  - Formats data for display             │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│    Status View Widgets (Pure UI)        │
│  - StatusHeaderSection                  │
│  - PerformancePanelSection              │
│  - VisualProgressBarSection             │
│  - TestResultsCardsSection              │
└─────────────────────────────────────────┘
```

## Key Components

### TestExecutionState (Model)
- Stores test results using `TestResult` models
- Calculates statistics
- Manages timing information
- **Does NOT** know about UI

### StatusViewPresenter (Presenter)
- Receives state updates from controller
- Calls appropriate widget update methods
- Formats data for display
- **Does NOT** contain business logic

### BaseStatusView (Controller)
- Coordinates between model and presenter
- Handles Qt signals (stop, back, run)
- Manages lifecycle events
- **Does NOT** directly manipulate widgets

### Status Widgets (View)
- Pure UI components
- Expose clean update APIs
- Handle animations and styling
- **Does NOT** know about test execution logic

## Data Flow

1. Worker emits signal → Window catches it
2. Window calls StatusView.on_test_completed()
3. StatusView creates TestResult model
4. StatusView updates TestExecutionState
5. StatusView calls Presenter with result + stats
6. Presenter updates individual widgets
7. Widgets render the changes

## Benefits

- **Testability:** Each layer can be tested independently
- **Maintainability:** Clear responsibilities
- **Flexibility:** Easy to swap widget implementations
- **Type Safety:** TestResult provides compile-time checks
```

---

### Step 6.2: Add Code Comments

Add docstring clarifications to key files explaining the new architecture.

---

## Phase 7: Rollout Strategy

### Option A: Big Bang (Riskier, Faster)
1. Complete all phases in feature branch
2. Comprehensive testing
3. Merge to main in single PR

### Option B: Incremental (Safer, Slower)
1. **PR 1:** Add models (TestResult, TestExecutionState)
2. **PR 2:** Add presenter layer (StatusViewPresenter)
3. **PR 3:** Refactor BaseStatusView to use presenter
4. **PR 4:** Update subclasses to use TestResult
5. **PR 5:** Consolidate styles
6. **PR 6:** Update tests and docs

**Recommendation:** **Option B** - Incremental rollout with thorough testing at each step.

---

## Rollback Plan

If issues arise after migration:

1. **Revert commits** in reverse order
2. **Key commit messages** should clearly mark each phase
3. **Tag pre-migration state** with `pre-status-view-refactor`

```bash
# Tag current state before starting
git tag -a pre-status-view-refactor -m "Before status view architecture refactor"
git push origin pre-status-view-refactor

# If rollback needed
git revert <commit-hash>
# or
git reset --hard pre-status-view-refactor
```

---

## Success Criteria

✅ All existing tests pass  
✅ No regression in UI behavior  
✅ Code coverage maintained or improved  
✅ Manual testing of all three status views (comparator, validator, benchmarker)  
✅ No circular imports  
✅ Clean separation verified via dependency graph  

---

## Common Pitfalls & Solutions

### Pitfall 1: "Property object has no attribute..."
**Cause:** Using `@property` for backward compatibility but something tries to set it  
**Solution:** Add `@property.setter` or refactor calling code

### Pitfall 2: "NotImplementedError in base class"
**Cause:** Code still calling `BaseStatusView.on_test_completed()` directly  
**Solution:** Ensure all calls go through subclass implementations

### Pitfall 3: Tests fail with "module not found"
**Cause:** New module structure not in Python path  
**Solution:** Ensure `__init__.py` files exist in all new directories

### Pitfall 4: Widgets not updating
**Cause:** Presenter not wired up correctly  
**Solution:** Verify `_create_presenter()` is called after `_setup_ui()`

---

## Estimated Lines of Code Impact

| Action | LOC Before | LOC After | Change |
|--------|------------|-----------|--------|
| Create models | 0 | 180 | +180 |
| Create presenter | 0 | 100 | +100 |
| Refactor BaseStatusView | 280 | 240 | -40 |
| Update subclasses | 360 | 360 | 0 |
| Consolidate styles | 30 | 15 | -15 |
| Tests | 400 | 450 | +50 |
| **Total** | **1,070** | **1,345** | **+275** |

**Note:** Net increase is due to proper separation of concerns, not bloat.

---

## Timeline

| Phase | Duration | Blocking | Can Start After |
|-------|----------|----------|-----------------|
| Phase 1 | 2h | No | Immediately |
| Phase 2 | 3h | No | Phase 1 |
| Phase 3 | 2h | Yes | Phase 2 |
| Phase 4 | 1h | No | Anytime |
| Phase 5 | 2h | Yes | Phase 3 |
| Phase 6 | 1h | No | Phase 5 |
| **Total** | **11h** | | |

---

## Final Checklist

Before merging to main:

- [ ] All phases completed
- [ ] Unit tests pass (`pytest tests/unit/`)
- [ ] Integration tests pass (`pytest tests/integration/`)
- [ ] Manual testing completed (run app, test all 3 modes)
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Pre-migration tag created
- [ ] Migration playbook reviewed by team
- [ ] Performance testing done (1000+ test run)
- [ ] Memory profiling done (check for leaks)

---

## Contact

Questions? Issues during migration?  
→ Open an issue or ping the team

**Good luck!** 🚀
