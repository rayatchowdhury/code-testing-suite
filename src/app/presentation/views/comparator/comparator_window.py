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

        # Split actions into two sections
        self.action_section = self.sidebar.add_section("Actions")
        self.compile_btn = None
        self.run_btn = None
        self.stop_btn = None
        self.status_view_active = False  # Track if status view is active

        for button_text in ["Compile", "Run"]:
            btn = self.sidebar.add_button(button_text, self.action_section)
            btn.clicked.connect(
                lambda _, text=button_text: self.handle_action_button(text)
            )
            if button_text == "Compile":
                self.compile_btn = btn
            elif button_text == "Run":
                self.run_btn = btn

        self.sidebar.add_results_button()
        self.sidebar.add_footer_button_divider()
        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()

        back_btn, options_btn = self.create_footer_buttons()
        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)

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

        # Setup splitter with sidebar and display area
        self.setup_splitter(self.sidebar, self.display_area)

        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)

        # Initialize tool with multi-language support
        self._initialize_tool()

        # Connect filesManifestChanged signal to reinitialize tool
        self.testing_content.test_tabs.filesManifestChanged.connect(self._on_files_changed)
    
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

            # Check all files for unsaved changes
            for btn_name, btn in self.testing_content.file_buttons.items():
                if btn.property("hasUnsavedChanges"):
                    reply = QMessageBox.question(
                        self,
                        "Unsaved Changes",
                        f"Do you want to save changes to {btn_name}?",
                        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                    )

                    if reply == QMessageBox.Save:
                        # Switch to this file (skip save prompt since we already handled it)
                        self.testing_content._handle_file_button(
                            btn_name, skip_save_prompt=True
                        )
                        if not self.testing_content.editor.saveFile():
                            return
                    elif reply == QMessageBox.Cancel:
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
                from src.app.presentation.services.navigation_service import NavigationService
                NavigationService.instance().navigate_to("results")
    
    def _on_run_requested(self):
        """Handle run request from status view - re-run comparison tests."""
        # Run comparison tests with same test count
        test_count = self.test_count_slider.value()
        self.comparator.run_comparison_test(test_count)
    
    def handle_test_count_changed(self, value):
        """Handle the slider value change."""
        print(f"Test count changed to: {value}")
        # You can store this value or use it in your comparison testing logic
    
    def handle_compare_options(self):
        """Add your compare options handling logic here."""
        pass
