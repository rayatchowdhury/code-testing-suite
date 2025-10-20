# Presentation Layer Refactoring Playbook
**Project**: Code Testing Suite  
**Date Started**: October 21, 2025  
**Status**: 🚧 In Progress  
**Version**: 1.0

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Phase 0: Scaffolding - Create Barebones Structure](#phase-0-scaffolding)
4. [Phase 1A: Protocols Definition](#phase-1a-protocols-definition)
5. [Phase 1B: Base Window Classes](#phase-1b-base-window-classes)
6. [Phase 1C: Service Layer Foundation](#phase-1c-service-layer-foundation)
7. [Phase 2A: TestWindowBase Implementation](#phase-2a-testwindowbase-implementation)
8. [Phase 2B: StatusViewBase Implementation](#phase-2b-statusviewbase-implementation)
9. [Phase 3A: Migrate BenchmarkerWindow](#phase-3a-migrate-benchmarkerwindow)
10. [Phase 3B: Migrate ValidatorWindow](#phase-3b-migrate-validatorwindow)
11. [Phase 3C: Migrate ComparatorWindow](#phase-3c-migrate-comparatorwindow)
12. [Phase 4A: Navigation Service Integration](#phase-4a-navigation-service-integration)
13. [Phase 4B: Error Handler Service Integration](#phase-4b-error-handler-service-integration)
14. [Phase 4C: Window Registry Implementation](#phase-4c-window-registry-implementation)
15. [Phase 5A: Directory Restructuring](#phase-5a-directory-restructuring)
16. [Phase 5B: Cleanup Legacy Code](#phase-5b-cleanup-legacy-code)
17. [Phase 6A: Testing & Validation](#phase-6a-testing-validation)
18. [Phase 6B: Documentation](#phase-6b-documentation)
19. [Phase 7: Final Review & Metrics](#phase-7-final-review-metrics)

---

## Overview

### Goals
This playbook guides the complete refactoring of the presentation layer to:
- **Eliminate 1,200+ lines** of duplicated code (73% reduction)
- **Introduce clean architecture** with base classes and services
- **Improve testability** through dependency injection
- **Standardize patterns** across all windows and components
- **Enable type-safe navigation** with enum-based routing

### Architecture Summary
```
Current State:
- 813 lines duplicated across test windows
- 450 lines duplicated across status views  
- Tight coupling (parent.window_manager)
- Inconsistent error handling
- String-based navigation

Target State:
- TestWindowBase (588 lines → 60 lines across 3 windows)
- StatusViewBase (450 lines → 90 lines across 3 views)
- Service layer (NavigationService, ErrorHandlerService)
- Type-safe navigation (WindowType enum)
- Consistent patterns throughout
```

### Key Documents
- **analysis.md**: Complete analysis of current issues
- **structure.md**: Proposed architecture and examples
- **PLAYBOOK.md**: This migration guide (atomic steps)

---

## Prerequisites

### Required Reading
Before starting, read these documents completely:
- ✅ `analysis.md` - Understanding current problems
- ✅ `structure.md` - Understanding target architecture

### Development Environment
- Python 3.10+
- PySide6 installed
- Git for version control
- IDE with Python support (VS Code recommended)
- Test framework (pytest) configured

### Backup Strategy
```bash
# Create migration branch
git checkout -b refactor/presentation-layer

# Create backup of current state
git tag backup-before-refactor

# Commit frequently (after each phase)
git commit -m "Phase X: [description]"
```

---

## Phase 0: Scaffolding

**Status**: ⏳ Not Started  
**Estimated Time**: 2-3 hours  
**Risk Level**: 🟢 Low

### Objective
Create all new directories and barebones files with docstrings only. No implementation. This establishes the structure and validates imports resolve correctly.

### Files to Read
None (pure scaffolding phase)

### Directories to Create
```bash
src/app/presentation/base/
src/app/presentation/services/
src/app/presentation/models/
src/app/presentation/utils/
src/app/presentation/components/status/
```

### Files to Create

#### 1. Base Classes (7 files)

**`src/app/presentation/base/__init__.py`**
```python
"""
Base classes and protocols for presentation layer.

This module provides the foundation for all windows, widgets, and components
in the presentation layer.
"""

__all__ = [
    "WindowBase",
    "ContentWindowBase", 
    "TestWindowBase",
    "StatusViewBase",
    "WidgetBase",
]
```

**`src/app/presentation/base/protocols.py`**
```python
"""
Protocol definitions for presentation layer components.

Protocols define interfaces that components must implement, enabling
type checking and dependency inversion.
"""

from typing import Protocol, runtime_checkable
from PySide6.QtCore import Signal


@runtime_checkable
class TestRunner(Protocol):
    """
    Protocol for test runner objects (Benchmarker, Validator, Comparator).
    
    All test runners must emit these signals and provide these methods
    to work with TestWindowBase.
    """
    
    # Signals
    compilationOutput: Signal
    testingStarted: Signal
    testingCompleted: Signal
    allTestsCompleted: Signal
    workerBusy: Signal
    workerIdle: Signal
    
    def save_test_results(self) -> bool:
        """Save test results to database. Returns True if successful."""
        ...
    
    def stop_testing(self) -> None:
        """Stop all running tests."""
        ...


@runtime_checkable  
class TestCard(Protocol):
    """
    Protocol for test result card widgets.
    
    Cards display individual test results in status views.
    """
    
    def update_status(self, status: str) -> None:
        """Update the test status (e.g., 'Running', 'Passed', 'Failed')."""
        ...
    
    def update_time(self, time: float) -> None:
        """Update the execution time display."""
        ...
    
    def set_result(self, result: object) -> None:
        """Set the complete test result object."""
        ...


@runtime_checkable
class TestDetailDialog(Protocol):
    """
    Protocol for test detail dialog windows.
    
    Dialogs show detailed information when a test card is clicked.
    """
    
    @staticmethod
    def show(test_result: object, parent=None) -> None:
        """Display the dialog with test result details."""
        ...


@runtime_checkable
class NavigationManager(Protocol):
    """
    Protocol for window navigation managers.
    
    Manages window lifecycle and navigation history.
    """
    
    def show_window(self, window_name: str, **kwargs) -> bool:
        """Show a window by name. Returns True if successful."""
        ...
    
    def go_back(self) -> bool:
        """Navigate to previous window. Returns True if successful."""
        ...
    
    def current_window_name(self) -> str:
        """Get the name of the currently displayed window."""
        ...
```

**`src/app/presentation/base/window_base.py`**
```python
"""
Root base class for all presentation windows.

WindowBase provides fundamental lifecycle management, error handling
integration, and signal management for all windows.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal


class WindowBase(QWidget):
    """
    Base class for all windows in the presentation layer.
    
    Responsibilities:
    - Window lifecycle management (show, close events)
    - Error handling service integration
    - Signal management utilities
    - Common window behaviors
    
    Subclasses:
    - ContentWindowBase: Windows with sidebar layout
    
    Usage:
        class MyWindow(WindowBase):
            def __init__(self, parent=None):
                super().__init__(parent)
                # Initialize window-specific logic
    """
    
    # Signals
    windowShown = Signal()
    windowClosed = Signal()
    
    def __init__(self, parent=None):
        """
        Initialize WindowBase.
        
        Args:
            parent: Parent widget (typically MainWindow)
        """
        super().__init__(parent)
        # TODO: Implementation in Phase 1B
    
    def showEvent(self, event):
        """
        Handle window show event.
        
        Emits windowShown signal and performs initialization.
        
        Args:
            event: QShowEvent
        """
        # TODO: Implementation in Phase 1B
        pass
    
    def closeEvent(self, event):
        """
        Handle window close event.
        
        Emits windowClosed signal and performs cleanup.
        
        Args:
            event: QCloseEvent
        """
        # TODO: Implementation in Phase 1B
        pass
    
    def handle_error(self, error: Exception, title: str = "Error"):
        """
        Handle an error using the error handler service.
        
        Args:
            error: The exception that occurred
            title: Error dialog title
        """
        # TODO: Implementation in Phase 1C (after ErrorHandlerService)
        pass
```

**`src/app/presentation/base/content_window_base.py`**
```python
"""
Base class for windows with sidebar layout.

ContentWindowBase extends WindowBase to provide sidebar integration,
splitter management, and layout creation for content-focused windows.
"""

from PySide6.QtWidgets import QSplitter
from PySide6.QtCore import Qt
from .window_base import WindowBase


class ContentWindowBase(WindowBase):
    """
    Base class for windows with sidebar + content layout.
    
    Responsibilities:
    - Sidebar widget integration
    - Splitter creation and management
    - Layout organization (sidebar | content)
    - Footer button creation
    
    Subclasses:
    - TestWindowBase: Test tool windows
    - EditorWindowBase: File editing windows
    - DocumentWindowBase: Static content windows
    - ResultsWindowBase: Results display windows
    
    Usage:
        class MyContentWindow(ContentWindowBase):
            def __init__(self, parent=None):
                super().__init__(parent)
                self._setup_sidebar()
                self._setup_content()
    """
    
    def __init__(self, parent=None):
        """
        Initialize ContentWindowBase.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.sidebar = None
        self.display_area = None
        self.splitter = None
        # TODO: Implementation in Phase 1B
    
    def _create_splitter(self) -> QSplitter:
        """
        Create the horizontal splitter for sidebar and content.
        
        Returns:
            Configured QSplitter widget
        """
        # TODO: Implementation in Phase 1B
        pass
    
    def _setup_layout(self):
        """
        Set up the window layout with sidebar and content area.
        
        Creates splitter, adds sidebar and display area, configures sizes.
        """
        # TODO: Implementation in Phase 1B
        pass
    
    def create_footer_buttons(self):
        """
        Create standard footer buttons (Back, Options).
        
        Returns:
            Tuple of (back_button, options_button)
        """
        # TODO: Implementation in Phase 1B
        pass
```

**`src/app/presentation/base/test_window_base.py`**
```python
"""
Base class for test tool windows (Benchmarker, Validator, Comparator).

TestWindowBase consolidates 588 lines of duplicated code from test windows,
providing template methods for subclasses to customize behavior.
"""

from abc import abstractmethod
from typing import Optional
from .content_window_base import ContentWindowBase
from .protocols import TestRunner


class TestWindowBase(ContentWindowBase):
    """
    Base class for all test tool windows.
    
    This class eliminates 588 lines of duplication by providing shared
    implementations of test lifecycle management, status view integration,
    and UI mode switching.
    
    Responsibilities:
    - Test runner initialization and signal connection
    - Status view integration
    - Test execution lifecycle (start, complete, stop)
    - UI mode switching (normal, testing, completed)
    - AI panel coordination
    - Sidebar state management
    
    Template Methods (must override):
    - _create_runner(): Return specific runner instance
    - _create_status_view(): Return specific status view
    - _get_testing_content_config(): Return tab configuration
    - _get_sidebar_config(): Return sidebar configuration
    
    Subclasses:
    - BenchmarkerWindow: Performance benchmarking
    - ValidatorWindow: Code validation
    - ComparatorWindow: Performance comparison
    
    Usage:
        class BenchmarkerWindow(TestWindowBase):
            def _create_runner(self):
                return Benchmarker()
            
            def _create_status_view(self):
                return BenchmarkerStatusView()
    
    Before Refactoring:
        - BenchmarkerWindow: 271 lines
        - ValidatorWindow: 271 lines
        - ComparatorWindow: 271 lines
        - Total: 813 lines
    
    After Refactoring:
        - TestWindowBase: 300 lines (shared)
        - BenchmarkerWindow: 25 lines (config only)
        - ValidatorWindow: 25 lines (config only)
        - ComparatorWindow: 25 lines (config only)
        - Total: 375 lines (54% reduction)
    """
    
    def __init__(self, parent=None):
        """
        Initialize TestWindowBase.
        
        Args:
            parent: Parent widget (typically MainWindow)
        """
        super().__init__(parent)
        self._runner: Optional[TestRunner] = None
        self._status_view = None
        # TODO: Implementation in Phase 2A
    
    @abstractmethod
    def _create_runner(self) -> TestRunner:
        """
        Create the test runner instance (Benchmarker, Validator, Comparator).
        
        Returns:
            Configured test runner instance
        
        Example:
            def _create_runner(self):
                return Benchmarker()
        """
        pass
    
    @abstractmethod
    def _create_status_view(self):
        """
        Create the status view instance.
        
        Returns:
            Configured status view widget
        
        Example:
            def _create_status_view(self):
                return BenchmarkerStatusView()
        """
        pass
    
    @abstractmethod
    def _get_testing_content_config(self) -> dict:
        """
        Get configuration for testing content widget tabs.
        
        Returns:
            Dictionary with 'tabs' key containing tab configurations
        
        Example:
            def _get_testing_content_config(self):
                return {
                    "tabs": [
                        {"name": "Source Code", "placeholder": "Enter code..."},
                        {"name": "Test Cases", "placeholder": "Enter tests..."}
                    ]
                }
        """
        pass
    
    @abstractmethod
    def _get_sidebar_config(self) -> dict:
        """
        Get configuration for sidebar sections and buttons.
        
        Returns:
            Dictionary with 'title' and 'sections' keys
        
        Example:
            def _get_sidebar_config(self):
                return {
                    "title": "Benchmarker",
                    "sections": [
                        {"name": "Actions", "buttons": ["Run", "Stop"]},
                        {"name": "Export", "buttons": ["Export CSV"]}
                    ]
                }
        """
        pass
    
    def _initialize_tool(self):
        """
        Initialize runner, status view, and connect signals.
        
        Called during window setup. Creates runner and status view using
        template methods, then connects all signals.
        """
        # TODO: Implementation in Phase 2A
        pass
    
    def _connect_runner_signals(self):
        """
        Connect all runner signals to status view and window methods.
        
        Connects:
        - testingStarted -> on_tests_started
        - testCompleted -> on_test_completed
        - allTestsCompleted -> on_all_tests_completed
        - workerBusy -> on_worker_busy
        - workerIdle -> on_worker_idle
        - compilationOutput -> console updates
        """
        # TODO: Implementation in Phase 2A
        pass
    
    def _switch_to_test_mode(self):
        """
        Switch UI to testing mode.
        
        - Disable status view widgets
        - Disable sidebar action buttons
        - Show "Stop Tests" button
        - Hide other controls
        """
        # TODO: Implementation in Phase 2A
        pass
    
    def _switch_to_completed_mode(self):
        """
        Switch UI to completed mode (after tests finish).
        
        - Enable status view widgets
        - Enable sidebar buttons
        - Replace "Results" with "Save" button
        - Show export options
        """
        # TODO: Implementation in Phase 2A
        pass
    
    def _restore_normal_mode(self):
        """
        Restore UI to normal mode (before tests or after save).
        
        - Reset status view
        - Restore "Results" button
        - Hide "Stop Tests" button
        - Re-enable all controls
        """
        # TODO: Implementation in Phase 2A
        pass
    
    def enable_save_button(self):
        """Enable the save button in sidebar."""
        # TODO: Implementation in Phase 2A
        pass
    
    def mark_results_saved(self):
        """Mark results as saved (change button to "✓ Saved")."""
        # TODO: Implementation in Phase 2A
        pass
    
    def refresh_ai_panels(self):
        """Refresh all AI panel contexts with current test data."""
        # TODO: Implementation in Phase 2A
        pass
```

**`src/app/presentation/base/status_view_base.py`**
```python
"""
Base class for status views (Benchmarker, Validator, Comparator).

StatusViewBase consolidates 450 lines of duplicated code from status views,
using configuration-driven design for customization.
"""

from abc import abstractmethod
from typing import Type
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal
from .protocols import TestCard, TestDetailDialog


class StatusViewBase(QWidget):
    """
    Base class for all test status views.
    
    This class eliminates 450 lines of duplication by providing shared
    implementations of UI setup, test lifecycle events, and database operations.
    
    Responsibilities:
    - UI layout (top controls, scroll area, test card grid)
    - Test lifecycle events (started, running, completed)
    - Worker coordination (busy/idle tracking)
    - Database save operations
    - Status presenter integration
    
    Configuration:
    - test_type: "benchmark", "validation", "comparison"
    - card_class: BenchmarkerTestCard, ValidatorTestCard, etc.
    - dialog_class: BenchmarkerDetailDialog, etc.
    - runner_attribute: "benchmarker", "validator_runner", etc.
    
    Template Methods (must override):
    - _create_test_card(): Create test-specific card widget
    - _get_detail_dialog_class(): Return dialog class
    - _get_runner_from_window(): Access runner from parent
    
    Subclasses:
    - BenchmarkerStatusView: Benchmark result display
    - ValidatorStatusView: Validation result display  
    - ComparatorStatusView: Comparison result display
    
    Usage:
        class BenchmarkerStatusView(StatusViewBase):
            def __init__(self, parent=None):
                config = StatusViewConfig(
                    test_type="benchmark",
                    card_class=BenchmarkerTestCard,
                    dialog_class=BenchmarkerDetailDialog,
                    runner_attribute="benchmarker"
                )
                super().__init__(config, parent)
    
    Before Refactoring:
        - BenchmarkerStatusView: 220 lines
        - ValidatorStatusView: 215 lines
        - ComparatorStatusView: 215 lines
        - Total: 650 lines
    
    After Refactoring:
        - StatusViewBase: 280 lines (shared)
        - BenchmarkerStatusView: 30 lines (config only)
        - ValidatorStatusView: 30 lines (config only)
        - ComparatorStatusView: 30 lines (config only)
        - Total: 370 lines (43% reduction)
    """
    
    # Signals
    stopRequested = Signal()
    backRequested = Signal()
    runRequested = Signal()
    
    def __init__(self, config, parent=None):
        """
        Initialize StatusViewBase.
        
        Args:
            config: StatusViewConfig with test-specific settings
            parent: Parent widget (test window)
        """
        super().__init__(parent)
        self._config = config
        self._presenter = None
        # TODO: Implementation in Phase 2B
    
    @abstractmethod
    def _create_test_card(self, test_name: str) -> TestCard:
        """
        Create a test card widget for displaying test results.
        
        Args:
            test_name: Name of the test
        
        Returns:
            Test card widget (protocol-compliant)
        
        Example:
            def _create_test_card(self, test_name: str):
                return BenchmarkerTestCard(test_name)
        """
        pass
    
    @abstractmethod
    def _get_detail_dialog_class(self) -> Type[TestDetailDialog]:
        """
        Get the dialog class for showing test details.
        
        Returns:
            Dialog class (protocol-compliant)
        
        Example:
            def _get_detail_dialog_class(self):
                return BenchmarkerDetailDialog
        """
        pass
    
    @abstractmethod
    def _get_runner_from_window(self):
        """
        Get the test runner from parent window.
        
        Returns:
            Test runner instance
        
        Example:
            def _get_runner_from_window(self):
                if self.parent():
                    return self.parent().benchmarker
                return None
        """
        pass
    
    def _setup_ui(self):
        """
        Set up the status view UI layout.
        
        Creates:
        - Top control panel (Run, Stop, Back buttons)
        - Scroll area for test cards
        - Grid layout for card organization
        - Bottom info panel (worker count, progress)
        """
        # TODO: Implementation in Phase 2B
        pass
    
    def on_tests_started(self, total: int):
        """
        Handle test execution started event.
        
        Args:
            total: Total number of tests to run
        """
        # TODO: Implementation in Phase 2B
        pass
    
    def on_test_completed(self, test_name: str, **kwargs):
        """
        Handle individual test completion.
        
        Args:
            test_name: Name of completed test
            **kwargs: Test-specific result data
        """
        # TODO: Implementation in Phase 2B
        pass
    
    def on_all_tests_completed(self):
        """Handle all tests completed event."""
        # TODO: Implementation in Phase 2B
        pass
    
    def on_worker_busy(self, worker_id: int):
        """
        Handle worker busy event.
        
        Args:
            worker_id: ID of busy worker
        """
        # TODO: Implementation in Phase 2B
        pass
    
    def on_worker_idle(self, worker_id: int):
        """
        Handle worker idle event.
        
        Args:
            worker_id: ID of idle worker
        """
        # TODO: Implementation in Phase 2B
        pass
    
    def save_to_database(self):
        """
        Save test results to database.
        
        Calls runner's save_test_results() and updates UI on success.
        """
        # TODO: Implementation in Phase 2B
        pass
    
    def _get_worker_count(self) -> int:
        """
        Get number of workers from runner.
        
        Returns:
            Worker count
        """
        # TODO: Implementation in Phase 2B
        pass
```

**`src/app/presentation/base/widget_base.py`**
```python
"""
Base class for common widget behaviors.

WidgetBase provides utilities and common patterns for reusable widgets.
"""

from PySide6.QtWidgets import QWidget


class WidgetBase(QWidget):
    """
    Base class for reusable widgets.
    
    Provides common widget utilities and patterns.
    
    Usage:
        class MyWidget(WidgetBase):
            def __init__(self, parent=None):
                super().__init__(parent)
    """
    
    def __init__(self, parent=None):
        """
        Initialize WidgetBase.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        # TODO: Implementation if needed
```

#### 2. Services (5 files)

**`src/app/presentation/services/__init__.py`**
```python
"""
Application services for presentation layer.

Services provide centralized functionality that windows and widgets
can consume without tight coupling.
"""

__all__ = [
    "NavigationService",
    "ErrorHandlerService",
    "ConfigService",
    "StateService",
    "TestExecutionService",
]
```

**`src/app/presentation/services/navigation_service.py`**
```python
"""
Navigation service for window management.

Provides centralized navigation without parent.window_manager coupling.
"""

from typing import Optional
from PySide6.QtCore import QObject, Signal


class NavigationService(QObject):
    """
    Singleton service for window navigation.
    
    Decouples windows from direct WindowManager access, enabling:
    - Testable navigation
    - No parent coupling
    - Centralized navigation logic
    
    Usage:
        # In any window or widget
        from src.app.presentation.services.navigation_service import NavigationService
        
        NavigationService.instance().navigate_to("benchmarker")
        NavigationService.instance().go_back()
    
    Setup (in MainWindow):
        nav_service = NavigationService.instance()
        nav_service.set_window_manager(self.window_manager)
    """
    
    # Singleton instance
    _instance: Optional['NavigationService'] = None
    
    # Signals
    windowChangeRequested = Signal(str, dict)  # window_name, kwargs
    
    @classmethod
    def instance(cls) -> 'NavigationService':
        """
        Get singleton instance.
        
        Returns:
            NavigationService singleton
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """
        Initialize NavigationService.
        
        Raises:
            RuntimeError: If called directly (use instance() instead)
        """
        if NavigationService._instance is not None:
            raise RuntimeError("Use NavigationService.instance()")
        super().__init__()
        self._window_manager = None
        # TODO: Implementation in Phase 1C
    
    def set_window_manager(self, manager):
        """
        Register the WindowManager.
        
        Called by MainWindow during initialization.
        
        Args:
            manager: WindowManager instance
        """
        # TODO: Implementation in Phase 1C
        pass
    
    def navigate_to(self, window_name: str, **kwargs):
        """
        Navigate to a window.
        
        Args:
            window_name: Name of window to show
            **kwargs: Window initialization arguments
        """
        # TODO: Implementation in Phase 1C
        pass
    
    def go_back(self):
        """Navigate to previous window in history."""
        # TODO: Implementation in Phase 1C
        pass
    
    def current_window(self) -> Optional[str]:
        """
        Get name of currently displayed window.
        
        Returns:
            Window name or None
        """
        # TODO: Implementation in Phase 1C
        pass
```

**`src/app/presentation/services/error_handler_service.py`**
```python
"""
Error handler service for centralized error management.

Replaces scattered print statements and QMessageBox calls with
consistent error handling, logging, and user feedback.
"""

from enum import Enum
from typing import Optional
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject, Signal
import logging


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "information"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorHandlerService(QObject):
    """
    Singleton service for error handling.
    
    Provides:
    - Consistent error logging
    - User-facing error dialogs
    - Severity-based handling
    - Error event notifications
    
    Usage:
        from src.app.presentation.services.error_handler_service import (
            ErrorHandlerService, ErrorSeverity
        )
        
        try:
            risky_operation()
        except Exception as e:
            ErrorHandlerService.instance().handle_error(
                e,
                title="Operation Failed",
                severity=ErrorSeverity.ERROR,
                parent=self
            )
    """
    
    # Singleton instance
    _instance: Optional['ErrorHandlerService'] = None
    
    # Signals
    errorOccurred = Signal(str, str, ErrorSeverity)  # title, message, severity
    
    @classmethod
    def instance(cls) -> 'ErrorHandlerService':
        """
        Get singleton instance.
        
        Returns:
            ErrorHandlerService singleton
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """
        Initialize ErrorHandlerService.
        
        Raises:
            RuntimeError: If called directly (use instance() instead)
        """
        if ErrorHandlerService._instance is not None:
            raise RuntimeError("Use ErrorHandlerService.instance()")
        super().__init__()
        # TODO: Implementation in Phase 1C
    
    def handle_error(
        self,
        error: Exception,
        title: str = "Error",
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        parent: Optional[QWidget] = None,
        log: bool = True
    ):
        """
        Handle an error with logging and user notification.
        
        Args:
            error: The exception that occurred
            title: Dialog title
            severity: Error severity level
            parent: Parent widget for dialog
            log: Whether to log the error
        """
        # TODO: Implementation in Phase 1C
        pass
```

**`src/app/presentation/services/config_service.py`**
```python
"""
Configuration service for centralized config access.

Wraps core.config to provide consistent configuration access
without lazy imports.
"""

from typing import Any, Optional
from PySide6.QtCore import QObject, Signal


class ConfigService(QObject):
    """
    Singleton service for configuration management.
    
    Centralizes access to application configuration, eliminating
    lazy imports and providing change notifications.
    
    Usage:
        from src.app.presentation.services.config_service import ConfigService
        
        config = ConfigService.instance()
        theme = config.get("theme", "dark")
        config.set("theme", "light")
    """
    
    # Singleton instance
    _instance: Optional['ConfigService'] = None
    
    # Signals
    configChanged = Signal(str, object)  # key, value
    
    @classmethod
    def instance(cls) -> 'ConfigService':
        """
        Get singleton instance.
        
        Returns:
            ConfigService singleton
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """
        Initialize ConfigService.
        
        Raises:
            RuntimeError: If called directly (use instance() instead)
        """
        if ConfigService._instance is not None:
            raise RuntimeError("Use ConfigService.instance()")
        super().__init__()
        # TODO: Implementation in Phase 1C
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        # TODO: Implementation in Phase 1C
        pass
    
    def set(self, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: New value
        """
        # TODO: Implementation in Phase 1C
        pass
```

**`src/app/presentation/services/state_service.py`**
```python
"""
State service for application-wide state management.

Manages global UI state that multiple windows need to access.
"""

from typing import Any, Dict
from PySide6.QtCore import QObject, Signal


class StateService(QObject):
    """
    Singleton service for application state.
    
    Manages shared state across windows and widgets.
    
    Usage:
        from src.app.presentation.services.state_service import StateService
        
        state = StateService.instance()
        state.set("last_test_run", datetime.now())
        last_run = state.get("last_test_run")
    """
    
    # Singleton instance
    _instance: Optional['StateService'] = None
    
    # Signals
    stateChanged = Signal(str, object)  # key, value
    
    @classmethod
    def instance(cls) -> 'StateService':
        """
        Get singleton instance.
        
        Returns:
            StateService singleton
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """
        Initialize StateService.
        
        Raises:
            RuntimeError: If called directly (use instance() instead)
        """
        if StateService._instance is not None:
            raise RuntimeError("Use StateService.instance()")
        super().__init__()
        self._state: Dict[str, Any] = {}
        # TODO: Implementation if needed
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get state value.
        
        Args:
            key: State key
            default: Default value if key not found
        
        Returns:
            State value
        """
        return self._state.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Set state value.
        
        Args:
            key: State key
            value: New value
        """
        self._state[key] = value
        self.stateChanged.emit(key, value)
```

**`src/app/presentation/services/test_execution_service.py`**
```python
"""
Test execution service for coordinating test runs.

Coordinates test execution across multiple windows and tools.
"""

from typing import Optional
from PySide6.QtCore import QObject, Signal


class TestExecutionService(QObject):
    """
    Singleton service for test execution coordination.
    
    Coordinates test runs, manages execution state, and provides
    cross-window test management.
    
    Usage:
        from src.app.presentation.services.test_execution_service import (
            TestExecutionService
        )
        
        service = TestExecutionService.instance()
        service.register_runner("benchmarker", runner)
    """
    
    # Singleton instance
    _instance: Optional['TestExecutionService'] = None
    
    # Signals
    testingStarted = Signal(str)  # tool_name
    testingCompleted = Signal(str)  # tool_name
    
    @classmethod
    def instance(cls) -> 'TestExecutionService':
        """
        Get singleton instance.
        
        Returns:
            TestExecutionService singleton
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """
        Initialize TestExecutionService.
        
        Raises:
            RuntimeError: If called directly (use instance() instead)
        """
        if TestExecutionService._instance is not None:
            raise RuntimeError("Use TestExecutionService.instance()")
        super().__init__()
        # TODO: Implementation if needed
```

#### 3. Models (3 files)

**`src/app/presentation/models/__init__.py`**
```python
"""
UI models for presentation layer.

Models represent UI state and configuration separately from business logic.
"""

__all__ = [
    "WindowConfig",
    "TestExecutionState",
    "UIState",
]
```

**`src/app/presentation/models/window_config.py`**
```python
"""
Window configuration models.

Defines configuration structures for windows.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class WindowConfig:
    """
    Configuration for a window.
    
    Attributes:
        title: Window title
        sidebar_config: Sidebar configuration
        content_config: Content area configuration
        metadata: Additional metadata
    """
    title: str
    sidebar_config: Dict[str, Any]
    content_config: Dict[str, Any]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize defaults."""
        if self.metadata is None:
            self.metadata = {}
```

**`src/app/presentation/models/test_execution_state.py`**
```python
"""
Test execution state model.

Tracks state of test execution (running, completed, failed, etc.).
This will be moved from core/ in Phase 5A.
"""

# TODO: Move from src/app/core/test_execution_state.py in Phase 5A
# For now, this is a placeholder
```

**`src/app/presentation/models/ui_state.py`**
```python
"""
UI state model.

Represents global UI state.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class UIState:
    """
    Global UI state.
    
    Attributes:
        current_window: Name of current window
        is_testing: Whether tests are running
        unsaved_changes: Whether there are unsaved changes
    """
    current_window: Optional[str] = None
    is_testing: bool = False
    unsaved_changes: bool = False
```

#### 4. Utils (2 files)

**`src/app/presentation/utils/__init__.py`**
```python
"""
Presentation layer utilities.

Helper functions and utilities for widgets and windows.
"""

__all__ = [
    "signal_helpers",
    "widget_helpers",
]
```

**`src/app/presentation/utils/signal_helpers.py`**
```python
"""
Signal connection utilities.

Helpers for managing Qt signals and slots.
"""

from typing import Callable, Any
from PySide6.QtCore import Signal, QObject


def safe_disconnect(signal: Signal, slot: Callable = None):
    """
    Safely disconnect a signal.
    
    Args:
        signal: Signal to disconnect
        slot: Specific slot to disconnect (None for all)
    """
    # TODO: Implementation if needed
    pass


def connect_once(signal: Signal, slot: Callable):
    """
    Connect signal to slot, ensuring single connection.
    
    Args:
        signal: Signal to connect
        slot: Slot to connect to
    """
    # TODO: Implementation if needed
    pass
```

**`src/app/presentation/utils/widget_helpers.py`**
```python
"""
Widget manipulation utilities.

Helper functions for common widget operations.
"""

from typing import List, Type
from PySide6.QtWidgets import QWidget


def find_widgets_by_type(parent: QWidget, widget_type: Type) -> List[QWidget]:
    """
    Find all child widgets of a specific type.
    
    Args:
        parent: Parent widget to search
        widget_type: Type of widget to find
    
    Returns:
        List of matching widgets
    """
    # TODO: Implementation if needed
    pass


def clear_layout(layout):
    """
    Clear all widgets from a layout.
    
    Args:
        layout: Layout to clear
    """
    # TODO: Implementation if needed
    pass
```

#### 5. Status Components

**`src/app/presentation/components/status/__init__.py`**
```python
"""
Status view components.

Status views and related components for test execution display.
"""

__all__ = [
    "StatusViewBase",
    "StatusViewConfig",
    "StatusViewPresenter",
]
```

**`src/app/presentation/components/status/status_config.py`**
```python
"""
Status view configuration model.

Configuration for customizing status views.
"""

from dataclasses import dataclass
from typing import Type, Dict


@dataclass
class StatusViewConfig:
    """
    Configuration for status views.
    
    Enables configuration-driven customization of status views
    instead of inheritance.
    
    Attributes:
        test_type: Type of test ("benchmark", "validation", "comparison")
        card_class: Test card widget class
        dialog_class: Test detail dialog class
        runner_attribute: Attribute name on parent window for runner
        runner_worker_attribute: Attribute name on runner for workers
        result_signature: Signature of on_test_completed kwargs
    
    Example:
        config = StatusViewConfig(
            test_type="benchmark",
            card_class=BenchmarkerTestCard,
            dialog_class=BenchmarkerDetailDialog,
            runner_attribute="benchmarker",
            runner_worker_attribute="workers",
            result_signature={"test_name": str, "result": "BenchmarkResult"}
        )
    """
    test_type: str
    card_class: Type
    dialog_class: Type
    runner_attribute: str
    runner_worker_attribute: str = "workers"
    result_signature: Dict = None
    
    def __post_init__(self):
        """Initialize defaults."""
        if self.result_signature is None:
            self.result_signature = {}
```

### Commands to Execute

```powershell
# Create directory structure
New-Item -ItemType Directory -Force -Path "src\app\presentation\base"
New-Item -ItemType Directory -Force -Path "src\app\presentation\services"
New-Item -ItemType Directory -Force -Path "src\app\presentation\models"
New-Item -ItemType Directory -Force -Path "src\app\presentation\utils"
New-Item -ItemType Directory -Force -Path "src\app\presentation\components\status"

# Verify structure
Get-ChildItem -Path "src\app\presentation" -Directory -Recurse
```

### Validation Checks

After creating all files, verify:

1. **Directory Structure**
```powershell
# Should show new directories
Get-ChildItem -Path "src\app\presentation" -Directory
```

2. **File Existence**
```powershell
# Count Python files in new directories
(Get-ChildItem -Path "src\app\presentation\base" -Filter "*.py").Count  # Should be 7
(Get-ChildItem -Path "src\app\presentation\services" -Filter "*.py").Count  # Should be 6
(Get-ChildItem -Path "src\app\presentation\models" -Filter "*.py").Count  # Should be 4
```

3. **Import Resolution**
```powershell
# Test imports (should not error)
python -c "from src.app.presentation.base import protocols"
python -c "from src.app.presentation.services import navigation_service"
```

4. **Syntax Check**
```powershell
# Run syntax check on all new files
python -m py_compile src\app\presentation\base\*.py
python -m py_compile src\app\presentation\services\*.py
python -m py_compile src\app\presentation\models\*.py
```

### Success Criteria

✅ All directories created  
✅ All 20 files created with docstrings  
✅ No syntax errors  
✅ All imports resolve  
✅ Git shows new files (not committed yet)

### Expected Output

```
src/app/presentation/
├── base/ (7 files)
│   ├── __init__.py ✓
│   ├── protocols.py ✓
│   ├── window_base.py ✓
│   ├── content_window_base.py ✓
│   ├── test_window_base.py ✓
│   ├── status_view_base.py ✓
│   └── widget_base.py ✓
├── services/ (6 files)
│   ├── __init__.py ✓
│   ├── navigation_service.py ✓
│   ├── error_handler_service.py ✓
│   ├── config_service.py ✓
│   ├── state_service.py ✓
│   └── test_execution_service.py ✓
├── models/ (4 files)
│   ├── __init__.py ✓
│   ├── window_config.py ✓
│   ├── test_execution_state.py ✓
│   └── ui_state.py ✓
├── utils/ (3 files)
│   ├── __init__.py ✓
│   ├── signal_helpers.py ✓
│   └── widget_helpers.py ✓
└── components/status/ (2 files)
    ├── __init__.py ✓
    └── status_config.py ✓
```

### Next Phase
After Phase 0 completes, proceed to **Phase 1A: Protocols Definition**.

---

## Phase 1A: Protocols Definition

**Status**: ⏳ Not Started  
**Estimated Time**: 3-4 hours  
**Risk Level**: 🟢 Low

### Objective
Implement complete protocol definitions by analyzing existing test runner, card, and dialog interfaces. Protocols enable type checking and dependency inversion.

### Files to Read (Full Analysis)

1. **`src/app/presentation/views/benchmarker/benchmarker_window.py`** (271 lines)
   - Analyze `self.benchmarker` usage
   - Identify all signals used from runner
   - Document methods called on runner

2. **`src/app/presentation/views/validator/validator_window.py`** (271 lines)
   - Compare with benchmarker for consistency
   - Note differences in runner interface

3. **`src/app/presentation/views/comparator/comparator_window.py`** (271 lines)
   - Complete runner interface analysis
   - Identify common signal patterns

4. **`src/app/presentation/views/benchmarker/benchmarker_status_view.py`** (220 lines)
   - Analyze test card creation
   - Analyze detail dialog usage
   - Document on_test_completed signature

### Files to Implement

**`src/app/presentation/base/protocols.py`** (already has skeleton)

Add complete implementations based on analysis:

```python
from typing import Protocol, runtime_checkable, Optional
from PySide6.QtCore import Signal

@runtime_checkable
class TestRunner(Protocol):
    """
    Protocol for test runners (Benchmarker, Validator, Comparator).
    
    Analyzed from:
    - src/app/core/benchmarker.py
    - src/app/core/validator.py  
    - src/app/core/comparator.py
    """
    
    # Required Signals (found in all 3 runners)
    compilationOutput: Signal  # Signal(str, str) - stdout, stderr
    testingStarted: Signal     # Signal(int) - total tests
    testingCompleted: Signal   # Signal()
    allTestsCompleted: Signal  # Signal()
    workerBusy: Signal        # Signal(int) - worker_id
    workerIdle: Signal        # Signal(int) - worker_id
    testCompleted: Signal     # Signal varies by runner!
    
    # Required Methods (called from windows)
    def save_test_results(self) -> bool: ...
    def stop_testing(self) -> None: ...
    def run_tests(self, source_code: str, test_cases: str) -> None: ...
    
    # Required Attributes (accessed from status views)
    workers: list  # Or validator_workers, comparator_workers

@runtime_checkable
class TestCard(Protocol):
    """Protocol for test result card widgets."""
    
    def update_status(self, status: str) -> None:
        """Update status label (Running/Passed/Failed)."""
        ...
    
    def update_time(self, time: float) -> None:
        """Update execution time display."""
        ...
    
    def set_clickable(self, clickable: bool) -> None:
        """Enable/disable click interaction."""
        ...
    
    def mousePressEvent(self, event) -> None:
        """Handle click to show details."""
        ...

@runtime_checkable
class TestDetailDialog(Protocol):
    """Protocol for test detail dialogs."""
    
    @staticmethod
    def show(test_result, parent=None) -> None:
        """Show dialog with test details."""
        ...

@runtime_checkable
class NavigationManager(Protocol):
    """Protocol for window managers."""
    
    def show_window(self, window_name: str, **kwargs) -> bool: ...
    def go_back(self) -> bool: ...
    def current_window_name(self) -> Optional[str]: ...
```

### Implementation Steps

1. **Analyze Runner Interfaces** (1 hour)
   ```powershell
   # Read all three test windows
   code src\app\presentation\views\benchmarker\benchmarker_window.py
   code src\app\presentation\views\validator\validator_window.py  
   code src\app\presentation\views\comparator\comparator_window.py
   
   # Take notes on:
   # - All signals connected from runner
   # - All methods called on runner
   # - All attributes accessed on runner
   ```

2. **Implement TestRunner Protocol** (1 hour)
   - Add all signals with correct signatures
   - Add all methods with type hints
   - Document which runners implement this

3. **Implement TestCard Protocol** (30 min)
   - Analyze benchmarker_test_card.py
   - Extract interface methods
   - Add to protocols.py

4. **Implement TestDetailDialog Protocol** (30 min)
   - Analyze benchmarker_detail_dialog.py
   - Extract static show() method signature
   - Add to protocols.py

5. **Type Check with mypy** (1 hour)
   ```powershell
   # Install mypy if needed
   pip install mypy
   
   # Run type checking
   mypy src\app\presentation\base\protocols.py
   
   # Fix any issues
   ```

### Code Examples

**Using Protocols in TestWindowBase**:
```python
from .protocols import TestRunner

class TestWindowBase(ContentWindowBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._runner: Optional[TestRunner] = None
    
    def _initialize_tool(self):
        # IDE knows _runner has these signals
        self._runner.testingStarted.connect(...)
        self._runner.testCompleted.connect(...)
```

**Using Protocols in StatusViewBase**:
```python
from .protocols import TestCard, TestDetailDialog

class StatusViewBase(QWidget):
    def _create_test_card(self, test_name: str) -> TestCard:
        # Subclasses must return TestCard-compliant widget
        ...
    
    def _get_detail_dialog_class(self) -> Type[TestDetailDialog]:
        # Subclasses must return TestDetailDialog-compliant class
        ...
```

### Validation & Testing

```powershell
# 1. Syntax check
python -m py_compile src\app\presentation\base\protocols.py

# 2. Import test
python -c "from src.app.presentation.base.protocols import TestRunner, TestCard"

# 3. Runtime checkable test
python -c "
from src.app.presentation.base.protocols import TestRunner
from src.app.core.benchmarker import Benchmarker
bench = Benchmarker()
print(f'Is TestRunner: {isinstance(bench, TestRunner)}')
"

# 4. Type checking (if mypy installed)
mypy --strict src\app\presentation\base\protocols.py
```

### Success Criteria

✅ All protocols defined with complete signatures  
✅ Mypy validation passes (no type errors)  
✅ All protocol members documented  
✅ Runtime checkable decorators work  
✅ Existing runners satisfy TestRunner protocol  
✅ Ready for use in Phase 1B/1C

### Troubleshooting

**Issue**: "Signal not defined in protocol"  
**Solution**: Check actual runner implementation, signals vary slightly

**Issue**: "mypy errors on Signal types"  
**Solution**: Signals are special - use `Signal` without parameters in protocol

### Next Phase
After Phase 1A completes, proceed to **Phase 1B: Base Window Classes**.

---

## Phase 1B: Base Window Classes

**Status**: ⏳ Not Started  
**Estimated Time**: 6-8 hours  
**Risk Level**: 🟡 Medium

### Objective
Implement WindowBase and ContentWindowBase by extracting common code from current SidebarWindowBase. These classes provide the foundation for all windows.

### Files to Read

1. **`src/app/presentation/window_controller/base_window.py`** (Full read - ~400 lines)
   - Extract common initialization
   - Extract splitter setup logic
   - Extract sidebar integration
   - Extract footer button creation
   - Identify what belongs in base vs. subclasses

### Files to Implement

**1. `src/app/presentation/base/window_base.py`**

Implement lifecycle management:
```python
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal

class WindowBase(QWidget):
    """Root base class for all windows."""
    
    windowShown = Signal()
    windowClosed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_initialized = False
    
    def showEvent(self, event):
        """Handle window show."""
        super().showEvent(event)
        if not self._is_initialized:
            self._on_first_show()
            self._is_initialized = True
        self.windowShown.emit()
    
    def closeEvent(self, event):
        """Handle window close."""
        self.windowClosed.emit()
        super().closeEvent(event)
    
    def _on_first_show(self):
        """Called once when window first shown."""
        pass  # Subclasses can override
```

**2. `src/app/presentation/base/content_window_base.py`**

Implement sidebar layout (extract from base_window.py lines 50-150):
```python
from PySide6.QtWidgets import QSplitter, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt
from .window_base import WindowBase

class ContentWindowBase(WindowBase):
    """Base for windows with sidebar layout."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sidebar = None
        self.display_area = None
        self.splitter = None
        
    def _setup_sidebar_layout(self):
        """Create sidebar + content splitter layout."""
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Add sidebar (created by subclass)
        if self.sidebar:
            self.splitter.addWidget(self.sidebar)
        
        # Add display area (created by subclass)
        if self.display_area:
            self.splitter.addWidget(self.display_area)
        
        # Set initial sizes (30% sidebar, 70% content)
        self.splitter.setSizes([300, 700])
        
        layout.addWidget(self.splitter)
    
    def create_footer_buttons(self):
        """Create standard Back and Options buttons."""
        back_btn = QPushButton("← Back")
        options_btn = QPushButton("⚙ Options")
        
        # Apply styles
        # ... (extract from base_window.py)
        
        return back_btn, options_btn
```

### Implementation Steps

1. **Extract WindowBase Logic** (2 hours)
   - Copy showEvent/closeEvent from base_window.py
   - Add signal definitions
   - Test lifecycle in isolation

2. **Extract ContentWindowBase Logic** (3 hours)
   - Copy splitter setup from base_window.py
   - Copy footer button creation
   - Remove test-specific code
   - Ensure generic for all content windows

3. **Create Unit Tests** (2 hours)
   ```python
   # tests/presentation/base/test_window_base.py
   def test_window_shown_signal():
       window = WindowBase()
       signal_emitted = False
       window.windowShown.connect(lambda: signal_emitted = True)
       window.show()
       assert signal_emitted
   ```

4. **Verify Existing Windows Still Work** (1 hour)
   ```powershell
   # Run app and test each window
   python main.py
   # Navigate to each window, verify no regressions
   ```

### Success Criteria

✅ WindowBase provides lifecycle management  
✅ ContentWindowBase provides sidebar layout  
✅ All tests pass  
✅ Existing windows (SidebarWindowBase subclasses) still work  
✅ Code is well-documented  
✅ No regressions in functionality

### Next Phase
After Phase 1B completes, proceed to **Phase 1C: Service Layer Foundation**.

---

## Phase 1C: Service Layer Foundation

**Status**: ⏳ Not Started  
**Estimated Time**: 8-10 hours  
**Risk Level**: 🟡 Medium

### Objective
Implement NavigationService, ErrorHandlerService, and ConfigService to decouple windows from direct manager access and standardize error handling.

### Files to Read

1. **`src/app/presentation/window_controller/window_management.py`** (253 lines)
   - Understand WindowManager.show_window()
   - Understand navigation history
   - Extract interface for NavigationService

2. **`src/app/presentation/views/main/main_window.py`** (350 lines)
   - Understand how WindowManager is created
   - Find where to register with NavigationService

3. **`src/app/core/config.py`** (analyze configuration structure)
   - Understand Config/ConfigView classes
   - Prepare for wrapping in ConfigService

### Files to Implement

**1. `src/app/presentation/services/navigation_service.py`**

Complete implementation:
```python
from typing import Optional
from PySide6.QtCore import QObject, Signal

class NavigationService(QObject):
    """Singleton for window navigation."""
    
    _instance = None
    windowChangeRequested = Signal(str, dict)
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        if NavigationService._instance is not None:
            raise RuntimeError("Use NavigationService.instance()")
        super().__init__()
        self._window_manager = None
        NavigationService._instance = self
    
    def set_window_manager(self, manager):
        """Register WindowManager (called from MainWindow)."""
        self._window_manager = manager
    
    def navigate_to(self, window_name: str, **kwargs):
        """Navigate to window."""
        if self._window_manager:
            return self._window_manager.show_window(window_name, **kwargs)
        else:
            self.windowChangeRequested.emit(window_name, kwargs)
            return False
    
    def go_back(self):
        """Go to previous window."""
        if self._window_manager:
            return self._window_manager.go_back()
        return False
    
    def current_window(self) -> Optional[str]:
        """Get current window name."""
        if self._window_manager:
            return self._window_manager.current_window_name()
        return None
```

**2. `src/app/presentation/services/error_handler_service.py`**

Complete implementation:
```python
from enum import Enum
from typing import Optional
from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtCore import QObject, Signal
import logging

class ErrorSeverity(Enum):
    INFO = "information"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ErrorHandlerService(QObject):
    """Singleton for error handling."""
    
    _instance = None
    errorOccurred = Signal(str, str, ErrorSeverity)
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        if ErrorHandlerService._instance is not None:
            raise RuntimeError("Use ErrorHandlerService.instance()")
        super().__init__()
        ErrorHandlerService._instance = self
    
    def handle_error(
        self,
        error: Exception,
        title: str = "Error",
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        parent: Optional[QWidget] = None,
        log: bool = True
    ):
        """Handle error with logging and dialog."""
        message = str(error)
        
        # Log
        if log:
            if severity == ErrorSeverity.CRITICAL:
                logging.critical(f"{title}: {message}", exc_info=error)
            elif severity == ErrorSeverity.ERROR:
                logging.error(f"{title}: {message}", exc_info=error)
            elif severity == ErrorSeverity.WARNING:
                logging.warning(f"{title}: {message}")
            else:
                logging.info(f"{title}: {message}")
        
        # Emit signal
        self.errorOccurred.emit(title, message, severity)
        
        # Show dialog
        if parent:
            if severity in (ErrorSeverity.CRITICAL, ErrorSeverity.ERROR):
                QMessageBox.critical(parent, title, message)
            elif severity == ErrorSeverity.WARNING:
                QMessageBox.warning(parent, title, message)
            else:
                QMessageBox.information(parent, title, message)
```

**3. `src/app/presentation/services/config_service.py`**

```python
from typing import Any, Optional
from PySide6.QtCore import QObject, Signal
from src.app.core.config import Config, ConfigView

class ConfigService(QObject):
    """Singleton for config access."""
    
    _instance = None
    configChanged = Signal(str, object)
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        if ConfigService._instance is not None:
            raise RuntimeError("Use ConfigService.instance()")
        super().__init__()
        self._config = Config()
        self._config_view = ConfigView()
        ConfigService._instance = self
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set config value."""
        self._config.set(key, value)
        self.configChanged.emit(key, value)
    
    def show_config_dialog(self, parent=None):
        """Show config dialog."""
        self._config_view.show(parent)
```

### Integration Steps

1. **Implement Services** (4 hours)
   - Implement NavigationService
   - Implement ErrorHandlerService
   - Implement ConfigService
   - Add __init__.py exports

2. **Register in MainWindow** (1 hour)
   ```python
   # In main_window.py __init__
   from src.app.presentation.services.navigation_service import NavigationService
   
   # After creating window_manager
   NavigationService.instance().set_window_manager(self.window_manager)
   ```

3. **Test Services** (2 hours)
   ```python
   # Test navigation
   NavigationService.instance().navigate_to("benchmarker")
   
   # Test error handling
   try:
       raise ValueError("Test error")
   except Exception as e:
       ErrorHandlerService.instance().handle_error(e, parent=self)
   ```

4. **Update main.py** (1 hour)
   ```python
   # Initialize services before app starts
   from src.app.presentation.services import (
       NavigationService,
       ErrorHandlerService,
       ConfigService
   )
   
   # Services auto-initialize on first instance() call
   ```

### Success Criteria

✅ All services implement singleton pattern correctly  
✅ NavigationService registered with WindowManager  
✅ Navigation works through service  
✅ Error handling shows dialogs and logs  
✅ Config service wraps core.config  
✅ No circular import issues  
✅ Services ready for use in windows

### Next Phase
After Phase 1C completes, proceed to **Phase 2A: TestWindowBase Implementation**.

---

## Phase 2A: TestWindowBase Implementation

**Status**: ⏳ Not Started  
**Estimated Time**: 10-12 hours  
**Risk Level**: 🔴 High (Core refactoring)

### Objective
Implement TestWindowBase with ALL 588 lines of shared code from benchmarker/validator/comparator windows. This is the critical phase that eliminates massive duplication.

### Files to Read (Complete Analysis)

1. **`src/app/presentation/views/benchmarker/benchmarker_window.py`** (271 lines - FULL READ)
   - Extract ALL shared methods
   - Note method signatures
   - Document dependencies

2. **`src/app/presentation/views/validator/validator_window.py`** (271 lines - FULL READ)
   - Compare with benchmarker
   - Identify differences
   - Note what can be parameterized

3. **`src/app/presentation/views/comparator/comparator_window.py`** (271 lines - FULL READ)
   - Complete comparison
   - Final list of shared methods
   - Document abstract method requirements

### Shared Methods to Extract (588 lines total)

**Identical Methods (324 lines)**:
1. `_switch_to_test_mode()` - 25 lines
2. `_switch_to_completed_mode()` - 14 lines  
3. `_handle_rerun_tests()` - 8 lines
4. `_on_testing_completed()` - 5 lines
5. `_restore_normal_mode()` - 23 lines
6. `enable_save_button()` - 3 lines
7. `mark_results_saved()` - 3 lines
8. `refresh_ai_panels()` - 4 lines
9. `showEvent()` - 10 lines
10. `_load_config()` - 10 lines
11. `_on_files_changed()` - 3 lines

**Near-Identical Methods (264 lines)**:
12. `_on_testing_started()` - 45 lines (status view class name differs)
13. `_initialize_tool()` - 20 lines (runner creation differs)
14. `handle_button_click()` - 20 lines (identical actually!)
15. `_get_runner()` - 3 lines (attribute name differs)

### Complete TestWindowBase Implementation

**`src/app/presentation/base/test_window_base.py`** (Implement fully)

```python
from abc import abstractmethod
from typing import Optional
from PySide6.QtWidgets import QWidget
from .content_window_base import ContentWindowBase
from .protocols import TestRunner
from ..services.navigation_service import NavigationService
from ..services.error_handler_service import ErrorHandlerService

class TestWindowBase(ContentWindowBase):
    """Base for Benchmarker, Validator, Comparator windows.
    
    Eliminates 588 lines of duplication.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._runner: Optional[TestRunner] = None
        self._status_view = None
        self._testing_content_widget = None
    
    # ===== TEMPLATE METHODS (must override) =====
    
    @abstractmethod
    def _create_runner(self) -> TestRunner:
        """Create specific runner (Benchmarker, Validator, Comparator)."""
        pass
    
    @abstractmethod
    def _create_status_view(self):
        """Create specific status view."""
        pass
    
    @abstractmethod
    def _get_testing_content_config(self) -> dict:
        """Get tab configuration for testing content."""
        pass
    
    @abstractmethod
    def _get_sidebar_config(self) -> dict:
        """Get sidebar configuration."""
        pass
    
    # ===== SHARED IMPLEMENTATION (588 lines) =====
    
    def _initialize_tool(self):
        """Initialize runner and connect signals."""
        # Create runner (template method)
        self._runner = self._create_runner()
        
        # Create status view (template method)
        self._status_view = self._create_status_view()
        
        # Connect signals
        self._connect_runner_signals()
        
        # Integrate into layout
        self._integrate_status_view()
    
    def _connect_runner_signals(self):
        """Connect ALL runner signals to status view."""
        if not self._runner or not self._status_view:
            return
        
        # Connect compilation output
        if hasattr(self._runner, 'compilationOutput'):
            self._runner.compilationOutput.connect(
                self._on_compilation_output
            )
        
        # Connect testing signals
        self._runner.testingStarted.connect(
            self._status_view.on_tests_started
        )
        self._runner.testCompleted.connect(
            self._status_view.on_test_completed
        )
        self._runner.allTestsCompleted.connect(
            self._status_view.on_all_tests_completed
        )
        
        # Connect worker signals
        self._runner.workerBusy.connect(
            self._status_view.on_worker_busy
        )
        self._runner.workerIdle.connect(
            self._status_view.on_worker_idle
        )
        
        # Connect to window methods
        self._runner.testingStarted.connect(self._on_testing_started)
        self._runner.allTestsCompleted.connect(self._on_testing_completed)
    
    def _switch_to_test_mode(self):
        """Switch to testing mode (disable controls)."""
        # Disable status view widgets
        if self._status_view:
            if hasattr(self._status_view, 'set_widgets_enabled'):
                self._status_view.set_widgets_enabled(False)
        
        # Update sidebar
        if self.sidebar:
            # Disable action buttons
            for section_name in ["Actions", "Export"]:
                section = self.sidebar.get_section(section_name)
                if section:
                    for button in section.findChildren(QPushButton):
                        if "Stop" not in button.text():
                            button.setEnabled(False)
            
            # Show Stop button
            stop_btn = self.sidebar.find_button("Stop Tests")
            if stop_btn:
                stop_btn.setVisible(True)
    
    def _switch_to_completed_mode(self):
        """Switch to completed mode (enable save)."""
        # Enable status view
        if self._status_view:
            if hasattr(self._status_view, 'set_widgets_enabled'):
                self._status_view.set_widgets_enabled(True)
        
        # Update sidebar
        if self.sidebar:
            # Re-enable buttons
            for section_name in ["Actions", "Export"]:
                section = self.sidebar.get_section(section_name)
                if section:
                    for button in section.findChildren(QPushButton):
                        button.setEnabled(True)
            
            # Replace Results with Save button
            self.sidebar.replace_results_with_save_button()
    
    def _restore_normal_mode(self):
        """Restore to normal mode."""
        # Reset status view
        if self._status_view:
            if hasattr(self._status_view, 'reset'):
                self._status_view.reset()
        
        # Restore sidebar
        if self.sidebar:
            self.sidebar.restore_results_button()
            
            # Hide Stop button
            stop_btn = self.sidebar.find_button("Stop Tests")
            if stop_btn:
                stop_btn.setVisible(False)
    
    def enable_save_button(self):
        """Enable save button after successful save."""
        if self.sidebar and hasattr(self.sidebar, 'save_button'):
            self.sidebar.save_button.setEnabled(True)
    
    def mark_results_saved(self):
        """Mark results as saved in UI."""
        if self.sidebar and hasattr(self.sidebar, 'save_button'):
            self.sidebar.save_button.setText("✓ Saved")
            self.sidebar.save_button.setEnabled(False)
    
    def refresh_ai_panels(self):
        """Refresh all AI panels with new context."""
        # Find all AI panels in widget tree
        from ..widgets.display_area_widgets.ai_panel import AIPanel
        for widget in self.findChildren(AIPanel):
            if hasattr(widget, 'refresh_context'):
                try:
                    widget.refresh_context()
                except Exception as e:
                    ErrorHandlerService.instance().handle_error(
                        e, "AI Panel Refresh Failed"
                    )
    
    def _on_testing_started(self, total: int):
        """Handle testing started."""
        self._switch_to_test_mode()
    
    def _on_testing_completed(self):
        """Handle testing completed."""
        self._switch_to_completed_mode()
    
    def _on_compilation_output(self, stdout: str, stderr: str):
        """Handle compilation output."""
        # Forward to console if exists
        if self._testing_content_widget:
            if hasattr(self._testing_content_widget, 'console'):
                self._testing_content_widget.console.append_output(
                    stdout, stderr
                )
    
    def handle_button_click(self, button_text: str):
        """Handle sidebar button clicks."""
        if button_text == "Run Tests":
            self._run_tests()
        elif button_text == "Stop Tests":
            self._stop_tests()
        elif button_text == "Clear Results":
            self._clear_results()
        elif button_text == "Export CSV":
            self._export_csv()
        elif button_text == "View Results":
            NavigationService.instance().navigate_to("results")
        elif button_text == "Back":
            NavigationService.instance().go_back()
        elif button_text == "Options":
            self._show_options()
    
    def _get_runner(self) -> Optional[TestRunner]:
        """Get the test runner instance."""
        return self._runner
    
    # Subclasses override these for specific behavior
    def _run_tests(self):
        """Run tests (subclasses can customize)."""
        if self._runner:
            # Get source and test code
            # ... implementation
            pass
    
    def _stop_tests(self):
        """Stop running tests."""
        if self._runner:
            self._runner.stop_testing()
    
    def _clear_results(self):
        """Clear test results."""
        if self._status_view:
            if hasattr(self._status_view, 'clear_results'):
                self._status_view.clear_results()
```

### Implementation Steps

1. **Extract Methods from Windows** (4 hours)
   - Copy all 11 identical methods
   - Copy all 4 near-identical methods
   - Adapt for template pattern

2. **Implement Template Methods** (2 hours)
   - Define abstract methods
   - Document what subclasses provide

3. **Handle Variations** (2 hours)
   - Parameterize differences
   - Use template methods for customization

4. **Create Unit Tests** (3 hours)
   ```python
   # tests/presentation/base/test_test_window_base.py
   class MockTestWindow(TestWindowBase):
       def _create_runner(self):
           return MockRunner()
       def _create_status_view(self):
           return MockStatusView()
   
   def test_switch_to_test_mode():
       window = MockTestWindow()
       window._switch_to_test_mode()
       # Assert buttons disabled
   ```

### Success Criteria

✅ All 588 lines of shared code extracted  
✅ Template methods clearly defined  
✅ Unit tests pass  
✅ Ready for subclass migration  
✅ No circular dependencies  
✅ Well documented

### Next Phase
After Phase 2A completes, proceed to **Phase 2B: StatusViewBase Implementation**.

---

## Phase 2B: StatusViewBase Implementation

**Status**: ⏳ Not Started  
**Estimated Time**: 8-10 hours  
**Risk Level**: 🔴 High (Core refactoring)

### Objective
Implement StatusViewBase with ALL 450 lines of shared code from benchmarker/validator/comparator status views. Uses configuration-driven design.

### Files to Read (Complete Analysis)

1. **`src/app/presentation/views/benchmarker/benchmarker_status_view.py`** (220 lines - FULL READ)
2. **`src/app/presentation/views/validator/validator_status_view.py`** (215 lines - FULL READ)  
3. **`src/app/presentation/views/comparator/comparator_status_view.py`** (215 lines - FULL READ)
4. **`src/app/core/test_execution_state.py`** (StatusViewPresenter location)

### Shared Code Analysis

**100% Identical Methods** (~300 lines):
- `_setup_ui()` - UI layout creation
- `on_tests_started()` - Test start handler
- `on_worker_busy()` - Worker busy handler
- `on_worker_idle()` - Worker idle handler  
- `_create_top_controls()` - Button creation
- `_setup_scroll_area()` - Scroll area setup
- `_update_worker_count()` - Worker count display

**95% Identical Methods** (~150 lines):
- `save_to_database()` - Only runner attribute differs
- `_get_worker_count()` - Only parent attribute differs
- `on_test_completed()` - Signature differs slightly
- `show_test_detail()` - Dialog class differs

### Implementation

**1. Create `src/app/presentation/components/status/status_config.py`**

```python
from dataclasses import dataclass
from typing import Type, Dict

@dataclass
class StatusViewConfig:
    """Configuration for status views."""
    test_type: str  # "benchmark", "validation", "comparison"
    card_class: Type
    dialog_class: Type
    runner_attribute: str  # "benchmarker", "validator_runner", "comparator"
    runner_worker_attribute: str = "workers"
    result_signature: Dict = None
    
    def __post_init__(self):
        if self.result_signature is None:
            self.result_signature = {}
```

**2. Copy presenter to new location**

```powershell
# Copy presenter.py to components/status/
Copy-Item "src\app\core\test_execution_state.py" `
          "src\app\presentation\components\status\status_presenter.py"

# Update imports in copied file
```

**3. Implement `src/app/presentation/components/status/status_view_base.py`**

```python
from abc import abstractmethod
from typing import Type
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QPushButton, QLabel, QGridLayout
)
from PySide6.QtCore import Signal, Qt
from .status_config import StatusViewConfig
from .status_presenter import StatusViewPresenter
from ...base.protocols import TestCard, TestDetailDialog

class StatusViewBase(QWidget):
    """Base for all status views.
    
    Eliminates 450 lines of duplication.
    """
    
    # Signals
    stopRequested = Signal()
    backRequested = Signal()
    runRequested = Signal()
    
    def __init__(self, config: StatusViewConfig, parent=None):
        super().__init__(parent)
        self._config = config
        self._presenter = StatusViewPresenter()
        self._test_cards = {}  # test_name -> card widget
        
        self._setup_ui()
        self._connect_signals()
    
    # ===== TEMPLATE METHODS =====
    
    @abstractmethod
    def _create_test_card(self, test_name: str) -> TestCard:
        """Create test-specific card."""
        pass
    
    @abstractmethod
    def _get_detail_dialog_class(self) -> Type[TestDetailDialog]:
        """Get dialog class for details."""
        pass
    
    @abstractmethod
    def _get_runner_from_window(self):
        """Get runner from parent window."""
        pass
    
    # ===== SHARED IMPLEMENTATION (450 lines) =====
    
    def _setup_ui(self):
        """Setup complete UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Top controls
        top_controls = self._create_top_controls()
        layout.addLayout(top_controls)
        
        # Scroll area for test cards
        scroll_area = self._setup_scroll_area()
        layout.addWidget(scroll_area)
        
        # Bottom info panel
        info_panel = self._create_info_panel()
        layout.addWidget(info_panel)
    
    def _create_top_controls(self) -> QHBoxLayout:
        """Create top control buttons."""
        layout = QHBoxLayout()
        
        # Run button
        self.run_btn = QPushButton("▶ Run Tests")
        self.run_btn.clicked.connect(self.runRequested.emit)
        layout.addWidget(self.run_btn)
        
        # Stop button (hidden initially)
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.clicked.connect(self.stopRequested.emit)
        self.stop_btn.setVisible(False)
        layout.addWidget(self.stop_btn)
        
        # Spacer
        layout.addStretch()
        
        # Back button
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(self.backRequested.emit)
        layout.addWidget(back_btn)
        
        return layout
    
    def _setup_scroll_area(self) -> QScrollArea:
        """Setup scrollable area for test cards."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container widget
        container = QWidget()
        self.grid_layout = QGridLayout(container)
        self.grid_layout.setSpacing(10)
        
        scroll.setWidget(container)
        return scroll
    
    def _create_info_panel(self) -> QWidget:
        """Create bottom info panel."""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        self.worker_count_label = QLabel("Workers: 0")
        layout.addWidget(self.worker_count_label)
        
        layout.addStretch()
        
        self.progress_label = QLabel("Ready")
        layout.addWidget(self.progress_label)
        
        return panel
    
    def on_tests_started(self, total: int):
        """Handle test execution start."""
        self._presenter.on_tests_started(total)
        
        # Update UI
        self.run_btn.setEnabled(False)
        self.stop_btn.setVisible(True)
        self.progress_label.setText(f"Running: 0/{total}")
        
        # Clear old cards
        for card in self._test_cards.values():
            card.deleteLater()
        self._test_cards.clear()
    
    def on_test_completed(self, test_name: str, **kwargs):
        """Handle individual test completion."""
        # Extract result (signature varies by test type)
        result = self._extract_result_from_kwargs(kwargs)
        
        # Create card if doesn't exist
        if test_name not in self._test_cards:
            card = self._create_test_card(test_name)
            self._test_cards[test_name] = card
            
            # Add to grid
            row = len(self._test_cards) // 3
            col = len(self._test_cards) % 3
            self.grid_layout.addWidget(card, row, col)
        
        # Update card
        card = self._test_cards[test_name]
        card.update_status(result.status)
        card.update_time(result.execution_time)
        
        # Update progress
        completed = len(self._test_cards)
        total = self._presenter.total_tests
        self.progress_label.setText(f"Running: {completed}/{total}")
    
    def on_all_tests_completed(self):
        """Handle all tests completed."""
        self.run_btn.setEnabled(True)
        self.stop_btn.setVisible(False)
        self.progress_label.setText("Completed")
    
    def on_worker_busy(self, worker_id: int):
        """Handle worker becoming busy."""
        self._presenter.on_worker_busy(worker_id)
        self._update_worker_count()
    
    def on_worker_idle(self, worker_id: int):
        """Handle worker becoming idle."""
        self._presenter.on_worker_idle(worker_id)
        self._update_worker_count()
    
    def _update_worker_count(self):
        """Update worker count display."""
        busy = self._presenter.busy_workers
        total = self._get_worker_count()
        self.worker_count_label.setText(f"Workers: {busy}/{total}")
    
    def save_to_database(self):
        """Save test results to database."""
        runner = self._get_runner_from_window()
        if runner:
            try:
                success = runner.save_test_results()
                if success:
                    # Notify parent window
                    if self.parent():
                        self.parent().enable_save_button()
            except Exception as e:
                from ...services.error_handler_service import ErrorHandlerService
                ErrorHandlerService.instance().handle_error(
                    e, "Failed to Save Results", parent=self
                )
    
    def _get_worker_count(self) -> int:
        """Get worker count from runner."""
        runner = self._get_runner_from_window()
        if runner:
            attr_name = self._config.runner_worker_attribute
            if hasattr(runner, attr_name):
                return len(getattr(runner, attr_name))
        return 0
    
    def _extract_result_from_kwargs(self, kwargs):
        """Extract result from kwargs (varies by test type)."""
        # Subclasses can override if needed
        return kwargs.get('result')
```

### Implementation Steps

1. **Create Configuration Model** (1 hour)
2. **Copy Presenter** (30 min)
3. **Extract Shared UI Setup** (3 hours)
4. **Extract Shared Event Handlers** (2 hours)
5. **Create Subclass Examples** (2 hours)
6. **Test Configuration-Driven Approach** (2 hours)

### Success Criteria

✅ 450 lines shared code extracted  
✅ Configuration-driven design works  
✅ All 3 status views can use base  
✅ Tests pass  
✅ Ready for migration

### Next Phase
After Phase 2B completes, proceed to **Phase 3A: Migrate BenchmarkerWindow**.

---

## Phase 3A: Migrate BenchmarkerWindow

**Status**: ⏳ Not Started  
**Estimated Time**: 6-8 hours  
**Risk Level**: 🔴 High (First migration)

### Objective
Migrate BenchmarkerWindow and BenchmarkerStatusView to use new base classes. This is the first real migration - validates the entire architecture.

### Files to Read

1. **`src/app/presentation/views/benchmarker/benchmarker_window.py`** (271 lines - FINAL READ)
2. **`src/app/presentation/views/benchmarker/benchmarker_status_view.py`** (220 lines - FINAL READ)

### Backup Strategy

```powershell
# Create backups
Copy-Item "src\app\presentation\views\benchmarker\benchmarker_window.py" `
          "src\app\presentation\views\benchmarker\benchmarker_window.py.backup"

Copy-Item "src\app\presentation\views\benchmarker\benchmarker_status_view.py" `
          "src\app\presentation\views\benchmarker\benchmarker_status_view.py.backup"

# Commit before changes
git add .
git commit -m "Backup before Phase 3A: Benchmarker migration"
```

### New BenchmarkerWindow (25 lines!)

**Replace entire file:**

```python
"""
Benchmarker window - migrated to TestWindowBase.

Reduced from 271 lines to 25 lines (91% reduction).
"""

from src.app.core.benchmarker import Benchmarker
from src.app.presentation.base.test_window_base import TestWindowBase
from .benchmarker_status_view import BenchmarkerStatusView
from ..widgets.testing_content_widget import TestingContentWidget


class BenchmarkerWindow(TestWindowBase):
    """Benchmarker window - now just configuration!"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._window_title = "Benchmarker"
        self._initialize_tool()
    
    def _create_runner(self):
        """Create Benchmarker instance."""
        return Benchmarker()
    
    def _create_status_view(self):
        """Create BenchmarkerStatusView."""
        return BenchmarkerStatusView(parent=self)
    
    def _get_testing_content_config(self):
        """Tab configuration."""
        return {
            "tabs": [
                {
                    "name": "Source Code",
                    "placeholder": "Write your code here..."
                },
                {
                    "name": "Test Cases",
                    "placeholder": "Write test cases here..."
                }
            ]
        }
    
    def _get_sidebar_config(self):
        """Sidebar configuration."""
        return {
            "title": "Benchmarker",
            "sections": [
                {
                    "name": "Actions",
                    "buttons": [
                        "Run Tests",
                        "Stop Tests",
                        "Clear Results"
                    ]
                },
                {
                    "name": "Export",
                    "buttons": [
                        "Export CSV",
                        "View Results"
                    ]
                }
            ]
        }
```

### New BenchmarkerStatusView (30 lines!)

**Replace entire file:**

```python
"""
Benchmarker status view - migrated to StatusViewBase.

Reduced from 220 lines to 30 lines (86% reduction).
"""

from src.app.presentation.components.status.status_view_base import StatusViewBase
from src.app.presentation.components.status.status_config import StatusViewConfig
from .benchmarker_test_card import BenchmarkerTestCard
from .benchmarker_detail_dialog import BenchmarkerDetailDialog


class BenchmarkerStatusView(StatusViewBase):
    """Benchmarker status view - now just configuration!"""
    
    def __init__(self, parent=None):
        # Create configuration
        config = StatusViewConfig(
            test_type="benchmark",
            card_class=BenchmarkerTestCard,
            dialog_class=BenchmarkerDetailDialog,
            runner_attribute="benchmarker",
            runner_worker_attribute="workers"
        )
        super().__init__(config, parent)
    
    def _create_test_card(self, test_name: str):
        """Create benchmarker test card."""
        return self._config.card_class(test_name)
    
    def _get_detail_dialog_class(self):
        """Get detail dialog class."""
        return self._config.dialog_class
    
    def _get_runner_from_window(self):
        """Get benchmarker from parent window."""
        if self.parent() and hasattr(self.parent(), 'benchmarker'):
            return self.parent().benchmarker
        return None
    
    def _extract_result_from_kwargs(self, kwargs):
        """Extract benchmark result."""
        return kwargs.get('result')
```

### Migration Steps

1. **Backup Files** (15 min)
   - Create .backup copies
   - Commit to git

2. **Replace BenchmarkerWindow** (1 hour)
   - Replace entire file with new 25-line version
   - Fix any import errors
   - Ensure compilation runs

3. **Replace BenchmarkerStatusView** (1 hour)
   - Replace with new 30-line version
   - Update attribute access (benchmarker vs _runner)
   - Test configuration works

4. **Update Imports** (30 min)
   ```python
   # Any files importing BenchmarkerWindow
   # Verify imports still work
   ```

5. **Integration Testing** (3-4 hours)
   ```powershell
   # Run application
   python main.py
   
   # Test benchmarker:
   # 1. Navigate to Benchmarker
   # 2. Enter source code
   # 3. Enter test cases  
   # 4. Click "Run Tests"
   # 5. Verify tests execute
   # 6. Verify status updates
   # 7. Click "Save Results"
   # 8. Verify save works
   # 9. Navigate to Results
   # 10. Verify results load
   ```

### Testing Checklist

**Functionality Tests**:
- [ ] Window opens successfully
- [ ] Sidebar renders correctly
- [ ] Source code tab works
- [ ] Test cases tab works
- [ ] "Run Tests" button works
- [ ] Tests execute and show progress
- [ ] Status cards appear
- [ ] Status cards update correctly
- [ ] "Stop Tests" button works
- [ ] Test completion triggers save button
- [ ] "Save Results" works
- [ ] Database save successful
- [ ] "View Results" navigates correctly
- [ ] "Back" button works
- [ ] AI panel integration works

**Error Scenarios**:
- [ ] Compilation errors show properly
- [ ] Test failures display correctly
- [ ] Worker crashes handled
- [ ] Save errors show dialog

### Success Criteria

✅ BenchmarkerWindow reduced from 271 to 25 lines (91%)  
✅ BenchmarkerStatusView reduced from 220 to 30 lines (86%)  
✅ All functionality works identically  
✅ No regressions  
✅ Tests pass  
✅ Ready to migrate Validator

### Rollback Procedure

If migration fails:
```powershell
# Restore backups
Copy-Item "src\app\presentation\views\benchmarker\benchmarker_window.py.backup" `
          "src\app\presentation\views\benchmarker\benchmarker_window.py" -Force

Copy-Item "src\app\presentation\views\benchmarker\benchmarker_status_view.py.backup" `
          "src\app\presentation\views\benchmarker\benchmarker_status_view.py" -Force

# Or git reset
git reset --hard HEAD~1
```

### Next Phase
After Phase 3A completes, proceed to **Phase 3B: Migrate ValidatorWindow**.

---

## Phase 3B: Migrate ValidatorWindow

**Status**: ⏳ Not Started  
**Estimated Time**: 4-5 hours  
**Risk Level**: 🟡 Medium (Pattern established)

### Objective
Migrate ValidatorWindow following the established pattern from Phase 3A. Should be faster since pattern is proven.

### Files to Migrate

1. **`src/app/presentation/views/validator/validator_window.py`** (271 lines)
2. **`src/app/presentation/views/validator/validator_status_view.py`** (215 lines)

### Backup

```powershell
Copy-Item "src\app\presentation\views\validator\*.py" `
          "src\app\presentation\views\validator\backup\" -Recurse

git commit -am "Backup before Phase 3B: Validator migration"
```

### New ValidatorWindow (25 lines)

```python
"""
Validator window - migrated to TestWindowBase.

Reduced from 271 lines to 25 lines (91% reduction).
"""

from src.app.core.validator import Validator
from src.app.presentation.base.test_window_base import TestWindowBase
from .validator_status_view import ValidatorStatusView


class ValidatorWindow(TestWindowBase):
    """Validator window - configuration only."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._window_title = "Validator"
        self._initialize_tool()
    
    def _create_runner(self):
        return Validator()
    
    def _create_status_view(self):
        return ValidatorStatusView(parent=self)
    
    def _get_testing_content_config(self):
        return {
            "tabs": [
                {"name": "Source Code", "placeholder": "Code to validate..."},
                {"name": "Test Cases", "placeholder": "Validation tests..."}
            ]
        }
    
    def _get_sidebar_config(self):
        return {
            "title": "Validator",
            "sections": [
                {"name": "Actions", "buttons": ["Run Tests", "Stop Tests", "Clear"]},
                {"name": "Export", "buttons": ["Export CSV", "View Results"]}
            ]
        }
```

### New ValidatorStatusView (30 lines)

**Note**: ValidatorRunner uses `validator_runner` attribute!

```python
"""
Validator status view - migrated to StatusViewBase.

Reduced from 215 lines to 30 lines (86% reduction).
"""

from src.app.presentation.components.status.status_view_base import StatusViewBase
from src.app.presentation.components.status.status_config import StatusViewConfig
from .validator_test_card import ValidatorTestCard
from .validator_detail_dialog import ValidatorDetailDialog


class ValidatorStatusView(StatusViewBase):
    """Validator status view - configuration only."""
    
    def __init__(self, parent=None):
        config = StatusViewConfig(
            test_type="validation",
            card_class=ValidatorTestCard,
            dialog_class=ValidatorDetailDialog,
            runner_attribute="validator_runner",  # NOTE: Different!
            runner_worker_attribute="validator_workers"  # NOTE: Different!
        )
        super().__init__(config, parent)
    
    def _create_test_card(self, test_name: str):
        return self._config.card_class(test_name)
    
    def _get_detail_dialog_class(self):
        return self._config.dialog_class
    
    def _get_runner_from_window(self):
        # NOTE: Uses validator_runner, not validator!
        if self.parent() and hasattr(self.parent(), 'validator_runner'):
            return self.parent().validator_runner
        return None
    
    def _extract_result_from_kwargs(self, kwargs):
        return kwargs.get('result')
```

### Key Differences from Benchmarker

1. **Runner Attribute**: `validator_runner` instead of `benchmarker`
2. **Worker Attribute**: `validator_workers` instead of `workers`
3. **Test Card**: `ValidatorTestCard` instead of `BenchmarkerTestCard`
4. **Dialog**: `ValidatorDetailDialog` instead of `BenchmarkerDetailDialog`

### Migration Steps

1. **Replace ValidatorWindow** (1 hour)
2. **Replace ValidatorStatusView** (1 hour)
3. **Test Thoroughly** (2-3 hours)
   - Validation-specific features
   - Error detection
   - Memory safety checks
   - Performance validation

### Success Criteria

✅ Validator reduced 271 → 25 lines  
✅ Status view reduced 215 → 30 lines  
✅ All validation features work  
✅ Error detection works  
✅ No regressions

### Next Phase
After Phase 3B completes, proceed to **Phase 3C: Migrate ComparatorWindow**.

---

## Phase 3C: Migrate ComparatorWindow

**Status**: ⏳ Not Started  
**Estimated Time**: 5-6 hours  
**Risk Level**: 🟡 Medium

### Objective
Complete the final test window migration. After this, all 3 test windows use base classes - achieving 1,400+ line reduction.

### Files to Migrate

1. **`src/app/presentation/views/comparator/comparator_window.py`** (271 lines)
2. **`src/app/presentation/views/comparator/comparator_status_view.py`** (215 lines)

### New ComparatorWindow (25 lines)

```python
"""
Comparator window - migrated to TestWindowBase.

Reduced from 271 lines to 25 lines (91% reduction).
"""

from src.app.core.comparator import Comparator
from src.app.presentation.base.test_window_base import TestWindowBase
from .comparator_status_view import ComparatorStatusView


class ComparatorWindow(TestWindowBase):
    """Comparator window - configuration only."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._window_title = "Comparator"
        self._initialize_tool()
    
    def _create_runner(self):
        return Comparator()
    
    def _create_status_view(self):
        return ComparatorStatusView(parent=self)
    
    def _get_testing_content_config(self):
        return {
            "tabs": [
                {"name": "Implementation A", "placeholder": "First implementation..."},
                {"name": "Implementation B", "placeholder": "Second implementation..."},
                {"name": "Test Cases", "placeholder": "Comparison tests..."}
            ]
        }
    
    def _get_sidebar_config(self):
        return {
            "title": "Comparator",
            "sections": [
                {"name": "Actions", "buttons": ["Run Comparison", "Stop", "Clear"]},
                {"name": "Export", "buttons": ["Export CSV", "View Results"]}
            ]
        }
```

### New ComparatorStatusView (30 lines)

**Note**: Comparator uses `comparator` attribute (same as benchmarker pattern)

```python
"""
Comparator status view - migrated to StatusViewBase.

Reduced from 215 lines to 30 lines (86% reduction).
"""

from src.app.presentation.components.status.status_view_base import StatusViewBase
from src.app.presentation.components.status.status_config import StatusViewConfig
from .comparator_test_card import ComparatorTestCard
from .comparator_detail_dialog import ComparatorDetailDialog


class ComparatorStatusView(StatusViewBase):
    """Comparator status view - configuration only."""
    
    def __init__(self, parent=None):
        config = StatusViewConfig(
            test_type="comparison",
            card_class=ComparatorTestCard,
            dialog_class=ComparatorDetailDialog,
            runner_attribute="comparator",
            runner_worker_attribute="workers"
        )
        super().__init__(config, parent)
    
    def _create_test_card(self, test_name: str):
        return self._config.card_class(test_name)
    
    def _get_detail_dialog_class(self):
        return self._config.dialog_class
    
    def _get_runner_from_window(self):
        if self.parent() and hasattr(self.parent(), 'comparator'):
            return self.parent().comparator
        return None
    
    def _extract_result_from_kwargs(self, kwargs):
        return kwargs.get('result')
```

### Migration Steps

1. **Replace ComparatorWindow** (1 hour)
2. **Replace ComparatorStatusView** (1 hour)
3. **Comprehensive Integration Testing** (3-4 hours)

### Comprehensive Integration Tests

Test all 3 windows together:

```powershell
# Run full application
python main.py
```

**Cross-Window Tests**:
1. **Navigation Flow**
   - Main → Benchmarker → Back → Validator → Back → Comparator
   - Verify each window initializes correctly
   - Verify Back button works

2. **Concurrent Test Runs**
   - Run benchmarker tests
   - While running, navigate away
   - Navigate back
   - Verify tests still running

3. **Configuration Persistence**
   - Set config in benchmarker
   - Navigate to validator
   - Return to benchmarker
   - Verify config persists

4. **Database Integration**
   - Run tests in all 3 windows
   - Save all results
   - Navigate to Results window
   - Verify all results loadable

5. **Error Handling**
   - Trigger compilation error in each window
   - Verify error handling consistent
   - Verify error dialogs appear

6. **Performance**
   - Run large test suites in each window
   - Monitor memory usage
   - Verify no memory leaks
   - Check UI responsiveness

### Final Metrics

**Before Refactoring**:
```
BenchmarkerWindow:       271 lines
ValidatorWindow:         271 lines  
ComparatorWindow:        271 lines
BenchmarkerStatusView:   220 lines
ValidatorStatusView:     215 lines
ComparatorStatusView:    215 lines
-----------------------------------
TOTAL:                 1,663 lines
```

**After Refactoring**:
```
TestWindowBase:          300 lines (shared)
StatusViewBase:          280 lines (shared)
BenchmarkerWindow:        25 lines
ValidatorWindow:          25 lines
ComparatorWindow:         25 lines  
BenchmarkerStatusView:    30 lines
ValidatorStatusView:      30 lines
ComparatorStatusView:     30 lines
-----------------------------------
TOTAL:                   745 lines

REDUCTION: 918 lines (55% reduction)
```

**Plus**: Eliminated 450 additional lines from status view duplication!

**Total Reduction**: ~1,368 lines (82% reduction in test window code)

### Success Criteria

✅ All 3 test windows migrated  
✅ Total 1,663 → 745 lines (55%)  
✅ All windows fully functional  
✅ No regressions  
✅ Integration tests pass  
✅ Performance maintained  
✅ Ready for service integration

### Celebration! 🎉

At this point, you've achieved:
- **82% code reduction** in test windows
- **Eliminated 1,368 lines** of duplicate code
- **Established clean architecture** with base classes
- **Proven template method pattern** works
- **Validated configuration-driven design**

This is the biggest win of the refactoring!

### Next Phase
After Phase 3C completes, proceed to **Phase 4A: Navigation Service Integration**.

---

## Phase 4A: Navigation Service Integration

**Status**: ⏳ Not Started  
**Estimated Time**: 4-5 hours  
**Risk Level**: 🟢 Low

### Objective
Replace all `self.parent.window_manager` coupling with NavigationService calls. Achieves Law of Demeter compliance.

### Files to Find & Modify

Search for coupling:
```powershell
# Find all parent.window_manager usage
Select-String -Path "src\app\presentation\**\*.py" -Pattern "parent.*window_manager"

# Expected files (~7 files, ~30 occurrences):
# - benchmarker_window.py (already done in Phase 3)
# - validator_window.py (already done in Phase 3)
# - comparator_window.py (already done in Phase 3)
# - code_editor_window.py
# - results_window.py
# - detailed_results_window.py
# - help_center_window.py
# - main_window_content.py
```

### Replacement Pattern

**Before**:
```python
if self.parent and hasattr(self.parent, "window_manager"):
    self.parent.window_manager.show_window("benchmarker")
```

**After**:
```python
from src.app.presentation.services.navigation_service import NavigationService

NavigationService.instance().navigate_to("benchmarker")
```

### Implementation

Update each file systematically:

**Example: `results_window.py`** (15+ occurrences!)
```python
# Old pattern (repeated 15 times)
if self.parent and hasattr(self.parent, "window_manager"):
    self.parent.window_manager.show_window("main")

# New pattern (single line)
NavigationService.instance().navigate_to("main")

# Old go_back pattern
if self.parent and hasattr(self.parent, "window_manager"):
    self.parent.window_manager.go_back()

# New go_back
NavigationService.instance().go_back()
```

### Testing

After each file update:
```powershell
# Test navigation
python main.py
# Click through all navigation paths
# Verify Back buttons work
# Verify window switching works
```

### Success Criteria

✅ No more `parent.window_manager` references  
✅ All navigation uses NavigationService  
✅ All windows navigate correctly  
✅ Back navigation works  
✅ Code is cleaner and testable

---

## Phase 4B: Error Handler Service Integration

**Status**: ⏳ Not Started  
**Estimated Time**: 3-4 hours  
**Risk Level**: 🟢 Low

### Objective
Replace scattered error handling with centralized ErrorHandlerService.

### Files to Find & Modify

```powershell
# Find print statements with errors
Select-String -Path "src\app\presentation\**\*.py" -Pattern "print.*[Ee]rror"

# Find QMessageBox usage
Select-String -Path "src\app\presentation\**\*.py" -Pattern "QMessageBox"

# Expected: 20+ occurrences across multiple files
```

### Replacement Pattern

**Before** (inconsistent):
```python
# Pattern 1: Print
print(f"Error: {e}")

# Pattern 2: QMessageBox
QMessageBox.critical(self, "Error", str(e))

# Pattern 3: Silent
except Exception as e:
    pass
```

**After** (consistent):
```python
from src.app.presentation.services.error_handler_service import (
    ErrorHandlerService, ErrorSeverity
)

try:
    operation()
except Exception as e:
    ErrorHandlerService.instance().handle_error(
        e,
        title="Operation Failed",
        severity=ErrorSeverity.ERROR,
        parent=self
    )
```

### Success Criteria

✅ No print statements for errors  
✅ Consistent QMessageBox usage via service  
✅ All errors logged  
✅ User sees appropriate dialogs  
✅ Severity levels used correctly

---

## Phase 4C: Window Registry Implementation

**Status**: ⏳ Not Started  
**Estimated Time**: 6-7 hours  
**Risk Level**: 🟡 Medium

### Objective
Implement WindowRegistry with WindowType enum for type-safe navigation.

### Implementation Steps

1. **Create WindowType Enum** (1 hour)
```python
# controllers/window_registry.py
from enum import Enum, auto

class WindowType(Enum):
    MAIN = auto()
    EDITOR = auto()
    BENCHMARKER = auto()
    VALIDATOR = auto()
    COMPARATOR = auto()
    RESULTS = auto()
    DETAILED_RESULTS = auto()
    HELP = auto()
```

2. **Implement WindowRegistry** (2 hours)
3. **Update WindowFactory** (2 hours)
4. **Update All navigate_to Calls** (2 hours)

### Success Criteria

✅ Type-safe navigation with enum  
✅ IDE autocomplete works  
✅ No string literals for windows  
✅ Window metadata available

---

## Phase 5A: Directory Restructuring

**Status**: ⏳ Not Started  
**Estimated Time**: 8-10 hours  
**Risk Level**: 🔴 High (Many files)

### Objective
Rename directories and move files to new structure.

### Major Moves

1. **Rename `widgets/` → `components/`**
   ```powershell
   git mv src\app\presentation\widgets src\app\presentation\components
   ```

2. **Rename `code_editor/` → `editor/`**
   ```powershell
   git mv src\app\presentation\views\code_editor src\app\presentation\views\editor
   ```

3. **Create `views/testing/`**
   ```powershell
   New-Item -ItemType Directory "src\app\presentation\views\testing"
   git mv src\app\presentation\views\benchmarker\*.py src\app\presentation\views\testing\
   git mv src\app\presentation\views\validator\*.py src\app\presentation\views\testing\
   git mv src\app\presentation\views\comparator\*.py src\app\presentation\views\testing\
   ```

4. **Update ALL Imports** (~100+ files)
   ```powershell
   # Search and replace across entire codebase
   # from ...widgets. → from ...components.
   # from ...code_editor. → from ...editor.
   ```

### Success Criteria

✅ New directory structure in place  
✅ All imports updated  
✅ All tests pass  
✅ Git history preserved  
✅ Application runs correctly

---

## Phase 5B: Cleanup Legacy Code

**Status**: ⏳ Not Started  
**Estimated Time**: 4-5 hours  
**Risk Level**: 🟢 Low

### Objective
Remove dead code and deprecated methods.

### Cleanup Tasks

1. **Remove from SidebarWindowBase**:
   - `_switch_to_test_mode()` (now in TestWindowBase)
   - `_switch_to_completed_mode()` (now in TestWindowBase)
   - `_restore_normal_mode()` (now in TestWindowBase)
   - `_integrate_status_view()` (now in TestWindowBase)
   - `refresh_ai_panels()` (now in TestWindowBase)

2. **Remove try/except signal disconnection** (Issue resolved in base)

3. **Remove defensive hasattr checks** (No longer needed)

4. **Remove commented-out code**

5. **Run dead code detection**:
   ```powershell
   pip install vulture
   vulture src\app\presentation\
   ```

### Success Criteria

✅ No dead code  
✅ Cleaner codebase  
✅ Reduced complexity  
✅ Better maintainability

---

## Phase 6A: Testing & Validation

**Status**: ⏳ Not Started  
**Estimated Time**: 12-16 hours  
**Risk Level**: 🟡 Medium

### Objective
Comprehensive testing of refactored code.

### Test Categories

**1. Unit Tests** (4 hours)
- Test all base classes
- Test all services
- Test protocols
- Target: 70%+ coverage

**2. Integration Tests** (4 hours)
- Window navigation flows
- Test execution end-to-end
- Database operations
- Error scenarios

**3. Performance Tests** (2 hours)
- Window load times
- Test execution speed
- Memory usage
- UI responsiveness

**4. Regression Tests** (2 hours)
- All existing functionality
- Edge cases
- Error conditions

**5. Manual Testing** (4 hours)
- User workflows
- Visual inspection
- Usability testing

### Success Criteria

✅ All tests pass  
✅ 70%+ coverage for new code  
✅ No regressions  
✅ Performance maintained  
✅ Memory leaks fixed  
✅ User acceptance

---

## Phase 6B: Documentation

**Status**: ⏳ Not Started  
**Estimated Time**: 8-10 hours  
**Risk Level**: 🟢 Low

### Objective
Document the new architecture completely.

### Documentation Tasks

1. **API Documentation** (4 hours)
   - All base classes
   - All services  
   - All protocols
   - Generate with Sphinx

2. **Architecture Diagrams** (2 hours)
   - Class hierarchy
   - Service dependencies
   - Window navigation flow
   - Use draw.io or mermaid

3. **Migration Guide** (2 hours)
   - How to add new test window
   - How to add new status view
   - Pattern examples

4. **Update README.md** (1 hour)
   - New architecture section
   - Quick start guide
   - Contribution guidelines

5. **Code Examples** (1 hour)
   - Template method usage
   - Service usage
   - Protocol implementation

### Success Criteria

✅ Comprehensive documentation  
✅ New developers can understand  
✅ Examples are clear  
✅ Architecture is visible  
✅ Contribution guide updated

---

## Phase 7: Final Review & Metrics

**Status**: ⏳ Not Started  
**Estimated Time**: 4-6 hours  
**Risk Level**: 🟢 Low

### Objective
Calculate final metrics and validate against goals.

### Metrics to Calculate

**1. Code Reduction**
```
Before: X lines
After: Y lines  
Reduction: Z lines (P%)
```

**2. Duplication Elimination**
```
Test Windows: 813 → 60 lines (93%)
Status Views: 450 → 90 lines (80%)
Total: 1,263 lines eliminated
```

**3. Test Coverage**
```
Before: X%
After: Y%
Improvement: +Z%
```

**4. Cyclomatic Complexity**
```
Before: Average X
After: Average Y
Improvement: -Z%
```

**5. Technical Debt**
```
Before: X issues
After: Y issues
Resolved: Z issues
```

### Validation Checklist

**Design Principles**:
- [ ] Single Responsibility Principle ✓
- [ ] Open/Closed Principle ✓
- [ ] Dependency Inversion ✓
- [ ] Don't Repeat Yourself ✓
- [ ] Law of Demeter ✓

**Critical Issues** (from analysis.md):
- [ ] 🔴 Test window duplication (813 lines) - RESOLVED
- [ ] 🔴 Status view duplication (450 lines) - RESOLVED
- [ ] 🔴 Tight coupling (parent.window_manager) - RESOLVED
- [ ] 🔴 Inconsistent error handling - RESOLVED
- [ ] 🔴 DisplayArea layout confusion - RESOLVED

### Executive Summary

Generate final report:

```markdown
# Refactoring Complete Summary

## Goals Achieved
- ✅ 73% code reduction in critical areas
- ✅ Eliminated 1,263+ lines of duplication
- ✅ Introduced clean architecture
- ✅ Improved testability
- ✅ Type-safe navigation

## Metrics
- Lines of Code: 8,500 → 5,500 (35% reduction)
- Duplication: 1,263 → 0 (100% elimination)
- Test Coverage: 15% → 72% (+57%)
- Cyclomatic Complexity: 18 → 8 (-56%)

## Business Value
- 40% faster bug fix time
- 60% faster feature addition
- 50% faster onboarding
- Better code quality
- Maintainable architecture

## Lessons Learned
[Document insights from refactoring]

## Recommendations
[Future improvement opportunities]
```

### Success Criteria

✅ 73% code reduction achieved  
✅ All critical issues resolved  
✅ Design principles validated  
✅ Metrics calculated  
✅ Executive summary created  
✅ Ready for production

---

## 🎉 REFACTORING COMPLETE! 🎉

Congratulations! You've successfully refactored the entire presentation layer:

- **1,263+ lines** of duplicate code eliminated
- **Clean architecture** with base classes and services  
- **Type-safe navigation** with protocols
- **Testable code** with dependency injection
- **73% reduction** in critical areas
- **Maintainable codebase** for future development

The presentation layer is now a model of clean architecture! 🏆

---

## Progress Tracker

| Phase | Status | Duration | Completed |
|-------|--------|----------|-----------|
| 0: Scaffolding | ⏳ Not Started | - | - |
| 1A: Protocols | ⏳ Not Started | - | - |
| 1B: Base Windows | ⏳ Not Started | - | - |
| 1C: Services | ⏳ Not Started | - | - |
| 2A: TestWindowBase | ⏳ Not Started | - | - |
| 2B: StatusViewBase | ⏳ Not Started | - | - |
| 3A: Benchmarker | ⏳ Not Started | - | - |
| 3B: Validator | ⏳ Not Started | - | - |
| 3C: Comparator | ⏳ Not Started | - | - |
| 4A: Navigation | ⏳ Not Started | - | - |
| 4B: Error Handler | ⏳ Not Started | - | - |
| 4C: Window Registry | ⏳ Not Started | - | - |
| 5A: Restructuring | ⏳ Not Started | - | - |
| 5B: Cleanup | ⏳ Not Started | - | - |
| 6A: Testing | ⏳ Not Started | - | - |
| 6B: Documentation | ⏳ Not Started | - | - |
| 7: Review | ⏳ Not Started | - | - |

---

## Rollback Procedures

If a phase fails or needs to be reverted:

```powershell
# Rollback to previous commit
git reset --hard HEAD~1

# Or rollback to specific tag
git reset --hard backup-before-refactor

# Or rollback specific phase
git revert <commit-hash-of-phase>
```

---

## Notes & Decisions

### Decision Log
- **2025-10-21**: Adopted template method pattern for TestWindowBase
- **2025-10-21**: Chose configuration-driven design for StatusViewBase
- **2025-10-21**: Selected singleton pattern for all services

### Issues Encountered
None yet

### Lessons Learned
None yet
