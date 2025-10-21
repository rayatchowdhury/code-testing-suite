# -*- coding: utf-8 -*-
"""
Comparator window - migrated to TestWindowBase.

Reduced from 271 lines to ~170 lines following Phase 3C migration pattern.
Inherits common test window behavior from TestWindowBase.

NOTE: Comparator uses 'comparator' attribute (same pattern as benchmarker)
"""

from PySide6.QtWidgets import QMessageBox

from src.app.core.tools.compiler_runner import CompilerRunner
from src.app.presentation.base.test_window_base import TestWindowBase
from src.app.presentation.widgets.display_area import DisplayArea
from src.app.presentation.widgets.testing_content_widget import TestingContentWidget
from src.app.presentation.widgets.sidebar import Sidebar
from src.app.presentation.widgets.sidebar_widgets import TestCountSlider

class ComparatorWindow(TestWindowBase):
    """Comparator window - migrated to TestWindowBase."""
    
    def __init__(self, parent=None):
        # Initialize base class first
        super().__init__(parent)

        self.sidebar = Sidebar("Comparator")

        # Replace options section with slider
        options_section = self.sidebar.add_section("Number of Tests")
        self.test_count_slider = TestCountSlider(mode="comparator")
        self.test_count_slider.valueChanged.connect(self.handle_test_count_changed)
        options_section.layout().addWidget(self.test_count_slider)

        # Add action buttons using base class helper
        self.action_section = self.sidebar.add_section("Actions")
        self._setup_standard_sidebar(self.action_section)

        # Create display area and testing content
        self.display_area = DisplayArea()
        
        # Create testing content with comparator configuration
        tab_config = {
            "Generator": {"cpp": "generator.cpp", "py": "generator.py", "java": "Generator.java"},
            "Correct Code": {"cpp": "correct.cpp", "py": "correct.py", "java": "CorrectCode.java"},
            "Test Code": {"cpp": "test.cpp", "py": "test.py", "java": "TestCode.java"},
        }
        self.testing_content = TestingContentWidget(
            parent=self,
            tab_config=tab_config,
            default_tab="Generator",
            test_type="comparator",
            compiler_runner_class=CompilerRunner,
            ai_panel_type="comparison",
        )
        self.display_area.set_content(self.testing_content)

        # Finalize window setup using base class helper
        self._finalize_window_setup()
    
    # ===== Template Methods (Required by TestWindowBase) =====
    
    def _create_runner(self):
        """Create Comparator with current configuration."""
        config = self._load_config()
        manifest = self.testing_content.test_tabs.get_compilation_manifest()
        files = manifest["files"]
        
        # Lazy import to avoid circular dependency
        from src.app.core.tools.comparator import Comparator
        
        return Comparator(
            workspace_dir=self.testing_content.workspace_dir,
            files=files,
            config=config
        )
    
    def _create_status_view(self):
        """Create ComparatorStatusView."""
        from src.app.presentation.views.comparator.comparator_status_view import ComparatorStatusView
        return ComparatorStatusView(parent=self)
    
    def _get_runner_attribute_name(self) -> str:
        """Return 'comparator' (same pattern as benchmarker)"""
        return "comparator"
    
    def _get_run_method_name(self) -> str:
        """Return the method name to call for running tests."""
        return "run_comparison_test"
    
    # ===== Comparator-Specific Methods =====
    
    def _initialize_tool(self):
        """Initialize or reinitialize the comparator tool with current file manifest."""
        # Disconnect old comparator's signals if it exists
        if hasattr(self, "comparator") and self.comparator:
            try:
                self.comparator.compilationOutput.disconnect()
                self.comparator.testingStarted.disconnect()
                self.comparator.testingCompleted.disconnect()
            except (RuntimeError, TypeError):
                # Signals may already be disconnected or object deleted
                pass

        # Create new runner
        self.comparator = self._create_runner()
        
        # Connect signals
        self.comparator.compilationOutput.connect(
            self.testing_content.console.displayOutput
        )
        self.comparator.testingStarted.connect(self._on_testing_started)
        self.comparator.testingCompleted.connect(self._on_testing_completed)

    def handle_action_button(self, button_text):
        """Handle action button clicks (Compile, Run, Stop, Results)."""
        if button_text == "Compile":
            # Clear console before compilation
            self.testing_content.console.clear()

            # Check for unsaved changes using base class helper
            if not self._check_unsaved_changes():
                return

            self.comparator.compile_all()
            
        elif button_text == "Run":
            # Run comparison tests
            test_count = self.test_count_slider.value()
            self.comparator.run_comparison_test(test_count)
            
        elif button_text == "Stop":
            # Stop running tests
            if hasattr(self.comparator, "stop"):
                self.comparator.stop()
                
        elif button_text == "Results":
            # Navigate to results window
            if self.can_close():
                if self.router:
                    self.router.navigate_to("results")
    
    def _on_run_requested(self):
        """Handle run request from status view - re-run comparison tests."""
        # Run comparison tests with same test count
        test_count = self.test_count_slider.value()
        self.comparator.run_comparison_test(test_count)
    
    def handle_test_count_changed(self, value):
        pass
    
    def handle_compare_options(self):
        """Add your compare options handling logic here."""
        pass
