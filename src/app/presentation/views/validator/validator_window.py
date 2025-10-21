# -*- coding: utf-8 -*-
"""
Validator window - migrated to TestWindowBase.

Reduced from 271 lines to ~170 lines following Phase 3B migration pattern.
Inherits common test window behavior from TestWindowBase.

NOTE: ValidatorRunner uses 'validator_runner' attribute (not 'validator')
"""

from PySide6.QtWidgets import QMessageBox

from src.app.core.tools.compiler_runner import CompilerRunner
from src.app.presentation.base.test_window_base import TestWindowBase
from src.app.presentation.widgets.display_area import DisplayArea
from src.app.presentation.widgets.testing_content_widget import TestingContentWidget
from src.app.presentation.widgets.sidebar import Sidebar
from src.app.presentation.widgets.sidebar_widgets import TestCountSlider

class ValidatorWindow(TestWindowBase):
    """Validator window - migrated to TestWindowBase."""
    
    def __init__(self, parent=None):
        # Initialize base class first
        super().__init__(parent)

        self.sidebar = Sidebar("Validator")

        # Replace options section with slider (exactly like comparator)
        options_section = self.sidebar.add_section("Number of Tests")
        self.test_count_slider = TestCountSlider(mode="validator")
        self.test_count_slider.valueChanged.connect(self.handle_test_count_changed)
        options_section.layout().addWidget(self.test_count_slider)

        # Add action buttons using base class helper
        self.action_section = self.sidebar.add_section("Actions")
        self._setup_standard_sidebar(self.action_section)

        # Create display area and testing content
        self.display_area = DisplayArea()
        
        # Create testing content with validator configuration
        tab_config = {
            "Generator": {"cpp": "generator.cpp", "py": "generator.py", "java": "Generator.java"},
            "Test Code": {"cpp": "test.cpp", "py": "test.py", "java": "TestCode.java"},
            "Validator Code": {"cpp": "validator.cpp", "py": "validator.py", "java": "ValidatorCode.java"},
        }
        self.testing_content = TestingContentWidget(
            parent=self,
            tab_config=tab_config,
            default_tab="Generator",
            test_type="validator",
            compiler_runner_class=CompilerRunner,
            ai_panel_type="validator",
        )
        self.display_area.set_content(self.testing_content)

        # Finalize window setup using base class helper
        self._finalize_window_setup()
    
    # ===== Template Methods (Required by TestWindowBase) =====
    
    def _create_runner(self):
        """Create ValidatorRunner with current configuration."""
        config = self._load_config()
        manifest = self.testing_content.test_tabs.get_compilation_manifest()
        files = manifest["files"]
        
        # Lazy import to avoid circular dependency
        from src.app.core.tools.validator import ValidatorRunner
        
        return ValidatorRunner(
            workspace_dir=self.testing_content.workspace_dir,
            files=files,
            config=config
        )
    
    def _create_status_view(self):
        """Create ValidatorStatusView."""
        from src.app.presentation.views.validator.validator_status_view import ValidatorStatusView
        return ValidatorStatusView(parent=self)
    
    def _get_runner_attribute_name(self) -> str:
        """Return 'validator_runner' (NOTE: different from benchmarker!)"""
        return "validator_runner"
    
    def _get_run_method_name(self) -> str:
        """Return the method name to call for running tests."""
        return "run_validation_test"
    
    # ===== Validator-Specific Methods =====
    
    def _initialize_tool(self):
        """Initialize or reinitialize the validator tool with current file manifest."""
        # Disconnect old runner's signals if it exists
        if hasattr(self, "validator_runner") and self.validator_runner:
            try:
                self.validator_runner.compilationOutput.disconnect()
                self.validator_runner.testingStarted.disconnect()
                self.validator_runner.testingCompleted.disconnect()
            except (RuntimeError, TypeError):
                # Signals already disconnected or runner deleted
                pass

        # Create new runner
        self.validator_runner = self._create_runner()
        
        # Connect signals
        self.validator_runner.compilationOutput.connect(
            self.testing_content.console.displayOutput
        )
        self.validator_runner.testingStarted.connect(self._on_testing_started)
        self.validator_runner.testingCompleted.connect(self._on_testing_completed)

    def handle_action_button(self, button_text):
        """Handle action button clicks (Compile, Run, Stop, Results)."""
        if button_text == "Compile":
            # Clear console before compilation
            self.testing_content.console.clear()

            # Check for unsaved changes using base class helper
            if not self._check_unsaved_changes():
                return

            self.validator_runner.compile_all()
            
        elif button_text == "Run":
            test_count = self.test_count_slider.value()
            self.validator_runner.run_validation_test(test_count)
            
        elif button_text == "Stop":
            # Stop running tests
            if hasattr(self.validator_runner, "stop"):
                self.validator_runner.stop()
                
        elif button_text == "Results":
            # Navigate to results window
            if self.can_close():
                from src.app.presentation.services.navigation_service import NavigationService
                NavigationService.instance().navigate_to("results")
    
    def _on_run_requested(self):
        """Handle run request from status view - re-run validation tests."""
        # Run validation tests with same test count
        test_count = self.test_count_slider.value()
        self.validator_runner.run_validation_test(test_count)
    
    def handle_test_count_changed(self, value):
        pass
    
    def handle_validate_options(self):
        """Add your validate options handling logic here."""
        pass
