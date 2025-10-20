# -*- coding: utf-8 -*-
"""
Benchmarker window - migrated to TestWindowBase.

Migrated from SidebarWindowBase (271 lines) to TestWindowBase.
Extracted shared test execution logic to base class while preserving
benchmarker-specific configuration (limits, compilation, etc.).

Reduced by extracting to TestWindowBase:
- _switch_to_test_mode()
- _switch_to_completed_mode()  
- _restore_normal_mode()
- _handle_rerun_tests()
- _on_testing_started() (partial)
- _on_testing_completed()
- showEvent()
- _load_config()
- _on_files_changed()
- enable_save_button()
- mark_results_saved()
- refresh_ai_panels()
- handle_button_click() (partial)
- _get_runner()
"""

from PySide6.QtWidgets import QMessageBox

from src.app.core.tools.benchmarker import BenchmarkCompilerRunner
from src.app.presentation.base.test_window_base import TestWindowBase
from src.app.presentation.widgets.display_area import DisplayArea
from src.app.presentation.widgets.testing_content_widget import TestingContentWidget
from src.app.presentation.widgets.sidebar import Sidebar
from src.app.presentation.widgets.sidebar_widgets import (
    LimitsInputWidget,
    TestCountSlider,
)


class BenchmarkerWindow(TestWindowBase):
    """
    Benchmarker window - uses TestWindowBase for shared test execution logic.
    
    TestWindowBase provides:
    - Test lifecycle management
    - UI mode switching
    - Tool initialization
    - Status view integration
    - Button/save handling
    
    Benchmarker-specific:
    - Time/memory limit widgets
    - Compile/Run actions with limits
    - Benchmarker runner creation
    """
    
    def __init__(self, parent=None):
        # Initialize base class
        super().__init__(parent)

        # Create sidebar
        self.sidebar = Sidebar("Benchmarker")

        # Add resource limits input section
        limits_section = self.sidebar.add_section("Resource Limits")
        self.limits_widget = LimitsInputWidget()
        self.limits_widget.timeLimitChanged.connect(self.handle_time_limit_changed)
        self.limits_widget.memoryLimitChanged.connect(self.handle_memory_limit_changed)
        limits_section.layout().addWidget(self.limits_widget)

        # Add test count slider
        test_count_section = self.sidebar.add_section("Number of Tests")
        self.test_count_slider = TestCountSlider(mode="benchmarker")
        self.test_count_slider.valueChanged.connect(self.handle_test_count_changed)
        test_count_section.layout().addWidget(self.test_count_slider)

        # Add action buttons
        self.action_section = self.sidebar.add_section("Actions")

        for button_text in ["Compile", "Run"]:
            btn = self.sidebar.add_button(button_text, self.action_section)
            btn.clicked.connect(
                lambda checked, text=button_text: self.handle_action_button(text)
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
        
        tab_config = {
            "Generator": {"cpp": "generator.cpp", "py": "generator.py", "java": "Generator.java"},
            "Test Code": {"cpp": "test.cpp", "py": "test.py", "java": "TestCode.java"},
        }
        self.testing_content = TestingContentWidget(
            parent=self,
            tab_config=tab_config,
            default_tab="Generator",
            test_type="benchmarker",
            compiler_runner_class=BenchmarkCompilerRunner,
            ai_panel_type="benchmark",
        )
        self.display_area.set_content(self.testing_content)

        # Setup splitter
        self.setup_splitter(self.sidebar, self.display_area)

        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)

        # Initialize tool (calls _create_runner)
        self._initialize_tool()

        # Connect file change signal
        self.testing_content.test_tabs.filesManifestChanged.connect(self._on_files_changed)

    # ===== TEMPLATE METHOD IMPLEMENTATIONS =====

    def _create_runner(self):
        """Create Benchmarker instance."""
        from src.app.core.tools.benchmarker import Benchmarker

        manifest = self.testing_content.test_tabs.get_compilation_manifest()
        config = self._load_config()

        return Benchmarker(
            workspace_dir=self.testing_content.workspace_dir,
            files=manifest["files"],
            config=config
        )

    def _create_status_view(self):
        """Create BenchmarkerStatusView with limits."""
        from src.app.presentation.views.benchmarker.benchmarker_status_view import (
            BenchmarkerStatusView,
        )

        return BenchmarkerStatusView(
            time_limit_ms=self.limits_widget.get_time_limit(),
            memory_limit_mb=self.limits_widget.get_memory_limit(),
            parent=self,
        )

    def _get_runner_attribute_name(self) -> str:
        """Return runner attribute name."""
        return "benchmarker"

    def _get_run_method_name(self) -> str:
        """Return run method name."""
        return "run_benchmark_test"

    # ===== BENCHMARKER-SPECIFIC METHODS =====

    def handle_action_button(self, button_text):
        """Handle Compile/Run/Stop/Results buttons."""
        if button_text == "Compile":
            # Clear console
            self.testing_content.console.clear()

            # Check for unsaved changes
            for btn_name, btn in self.testing_content.file_buttons.items():
                if btn.property("hasUnsavedChanges"):
                    reply = QMessageBox.question(
                        self,
                        "Unsaved Changes",
                        f"Do you want to save changes to {btn_name}?",
                        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                    )

                    if reply == QMessageBox.Save:
                        self.testing_content._handle_file_button(
                            btn_name, skip_save_prompt=True
                        )
                        if not self.testing_content.editor.saveFile():
                            return
                    elif reply == QMessageBox.Cancel:
                        return

            self.benchmarker.compile_all()
            
        elif button_text == "Run":
            time_limit = self.limits_widget.get_time_limit()
            memory_limit = self.limits_widget.get_memory_limit()
            test_count = self.test_count_slider.value()
            self.benchmarker.run_benchmark_test(test_count, time_limit, memory_limit)
            
        elif button_text == "Stop":
            if hasattr(self.benchmarker, "stop"):
                self.benchmarker.stop()
                
        elif button_text == "Results":
            if self.can_close():
                from src.app.presentation.services.navigation_service import NavigationService
                NavigationService.instance().navigate_to("results")

    def _on_run_requested(self):
        """Handle rerun from status view."""
        time_limit = self.limits_widget.get_time_limit()
        memory_limit = self.limits_widget.get_memory_limit()
        test_count = self.test_count_slider.value()
        self.benchmarker.run_benchmark_test(test_count, time_limit, memory_limit)

    def handle_time_limit_changed(self, value):
        print(f"Time limit changed to: {value} ms")

    def handle_memory_limit_changed(self, value):
        print(f"Memory limit changed to: {value} MB")

    def handle_test_count_changed(self, value):
        print(f"Test count changed to: {value} tests")
