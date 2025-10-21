"""
DetailedResultDialog

Phase 4: Results Detail Consolidation
Unified QDialog for displaying detailed test results with sidebar navigation.
Consolidates functionality from detailed_results_widget.py and detailed_results_window.py
"""

import json
import os
import zipfile
from typing import Dict

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.app.persistence.database import TestResult
from src.app.presentation.dialogs.result_detail.viewmodel import DetailedResultViewModel
from src.app.presentation.styles.components.results import (
    RESULTS_BUTTON_STYLE,
    RESULTS_CARD_STYLE,
    RESULTS_LABEL_DETAILS_STYLE,
    RESULTS_LABEL_TITLE_STYLE,
    RESULTS_SCROLL_STYLE,
    RESULTS_SEPARATOR_STYLE,
    RESULTS_TEXT_EDIT_STYLE,
)
from src.app.presentation.styles.fonts.emoji import set_emoji_font
from src.app.presentation.styles.helpers.common_styles import bold_label
from src.app.presentation.styles.style import MATERIAL_COLORS
from src.app.presentation.services import (
    export_test_cases_to_zip,
    create_export_summary,
)
from src.app.presentation.widgets.sidebar import Sidebar


class DetailedResultDialog(QDialog):
    """Unified detailed results dialog with sidebar navigation.
    
    Phase 4: Consolidates duplicate implementations from:
    - views/results/detailed_results_widget.py
    - views/results/detailed_results_window.py
    
    Features:
    - Sidebar navigation with 4 content pages
    - Summary statistics with formatted data
    - Code files viewer with tabs
    - Separate views for passed/failed tests
    - Export to ZIP functionality
    - Load to test functionality
    """

    # Signals
    loadToTestRequested = Signal(dict)  # Emits test_result data for loading
    backRequested = Signal()  # Emitted when user wants to go back

    def __init__(self, test_result: TestResult, parent=None):
        super().__init__(parent)
        self.test_result = test_result
        self.viewmodel = DetailedResultViewModel(test_result)
        self.current_page = 0

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Create main widget layout with sidebar and content area."""
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create sidebar
        self.sidebar = Sidebar(f"Test Details")

        # Add "Details" section
        details_section = self.sidebar.add_section("Details")

        # Navigation buttons
        detail_sections = [
            ("📊 Summary", 0),
            ("💻 Code Files", 1),
            ("✅ Passed Tests", 2),
            ("❌ Failed Tests", 3),
        ]

        self.nav_buttons = []
        for text, idx in detail_sections:
            btn = self.sidebar.add_button(text, details_section)
            btn.clicked.connect(lambda _, i=idx: self._show_page(i))
            self.nav_buttons.append(btn)

        # Add "Options" section
        options_section = self.sidebar.add_section("Options")

        # Export button
        export_btn = self.sidebar.add_button("📤 Export as ZIP", options_section)
        export_btn.clicked.connect(self._export_results)

        # Load to Test button
        load_btn = self.sidebar.add_button("🔄 Load to Test", options_section)
        load_btn.clicked.connect(self._load_to_test)
        load_btn.setToolTip("Load code files into the appropriate test window")

        # Add footer
        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()

        # Back button (for embedded widget mode)
        back_btn = QPushButton("Back")
        back_btn.setObjectName("back_button")
        back_btn.clicked.connect(self.backRequested.emit)

        # Options button (placeholder for visual consistency)
        options_btn = QPushButton("⚙️")
        options_btn.setObjectName("back_button")
        options_btn.setFont(QFont("Segoe UI", 14))

        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)

        # Create content area with stacked widget
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(
            f"background-color: {MATERIAL_COLORS['surface']};"
        )
        self._create_content_pages()

        # Add to layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_stack, 1)

        # Show summary by default
        self._show_page(0)

    def _connect_signals(self):
        """Connect internal signals."""
        pass  # Signals connected in _setup_ui

    def _show_page(self, page_index: int):
        """Switch to specified content page."""
        self.current_page = page_index
        self.content_stack.setCurrentIndex(page_index)

    def _create_content_pages(self):
        """Create 4 content pages: summary, code files, passed tests, failed tests."""
        self.content_stack.addWidget(self._create_summary_page())
        self.content_stack.addWidget(self._create_code_files_page())
        self.content_stack.addWidget(self._create_passed_tests_page())
        self.content_stack.addWidget(self._create_failed_tests_page())

    # Page Creation Methods

    def _create_summary_page(self):
        """Create summary statistics page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Title
        title = QLabel("📊 Test Results Summary")
        set_emoji_font(title)
        title.setStyleSheet(
            f"""
            {bold_label(24, MATERIAL_COLORS['on_surface'])}
            padding-bottom: 16px;
        """
        )
        layout.addWidget(title)

        # Get summary data from viewmodel
        summary = self.viewmodel.get_summary_data()

        # Statistics card
        stats_card = QFrame()
        stats_card.setStyleSheet(RESULTS_CARD_STYLE)
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setSpacing(12)

        # Project info
        stats_layout.addWidget(
            self._create_info_label("Project:", summary["project_name"])
        )
        stats_layout.addWidget(
            self._create_info_label("Test Type:", summary["test_type"])
        )
        stats_layout.addWidget(
            self._create_info_label("File:", os.path.basename(summary["file_path"]))
        )
        stats_layout.addWidget(
            self._create_info_label("Timestamp:", summary["timestamp"])
        )

        stats_layout.addWidget(self._create_divider())

        # Test statistics
        stats_layout.addWidget(
            self._create_info_label("Total Tests:", str(summary["total_tests"]))
        )
        stats_layout.addWidget(
            self._create_info_label(
                "✅ Passed:",
                str(summary["passed_tests"]),
                MATERIAL_COLORS["primary"],
            )
        )
        stats_layout.addWidget(
            self._create_info_label(
                "❌ Failed:", str(summary["failed_tests"]), MATERIAL_COLORS["error"]
            )
        )
        stats_layout.addWidget(
            self._create_info_label("Success Rate:", summary["success_rate"])
        )
        stats_layout.addWidget(
            self._create_info_label("Total Time:", summary["total_time"])
        )

        layout.addWidget(stats_card)

        # Mismatch analysis (if exists)
        analysis = self.viewmodel.get_mismatch_analysis()
        if analysis:
            layout.addWidget(self._create_section_label("Mismatch Analysis:"))
            analysis_text = QTextEdit()
            analysis_text.setPlainText(json.dumps(analysis, indent=2))
            analysis_text.setReadOnly(True)
            analysis_text.setMaximumHeight(200)
            analysis_text.setStyleSheet(RESULTS_TEXT_EDIT_STYLE)
            layout.addWidget(analysis_text)

        layout.addStretch()
        return page

    def _create_code_files_page(self):
        """Create code files viewer page with tabs."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Title
        title = QLabel("💻 Source Code Files")
        set_emoji_font(title)
        title.setStyleSheet(
            f"""
            {bold_label(24, MATERIAL_COLORS['on_surface'])}
        """
        )
        layout.addWidget(title)

        # Get code file tabs from viewmodel
        code_tabs_data = self.viewmodel.get_code_file_tabs()

        if not code_tabs_data:
            no_files_label = QLabel("No source code files available")
            no_files_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
            layout.addWidget(no_files_label)
            layout.addStretch()
            return page

        # Create tab widget
        code_tabs = QTabWidget()
        code_tabs.setStyleSheet(
            f"""
            QTabWidget::pane {{
                border: 1px solid {MATERIAL_COLORS['outline']};
                background: {MATERIAL_COLORS['surface']};
            }}
            QTabBar::tab {{
                background: {MATERIAL_COLORS['surface_variant']};
                color: {MATERIAL_COLORS['on_surface']};
                padding: 10px 20px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {MATERIAL_COLORS['primary']};
                color: {MATERIAL_COLORS['on_primary']};
                font-weight: bold;
            }}
        """
        )

        # Add tabs from viewmodel data
        for label, content in code_tabs_data:
            viewer = self._create_code_viewer(content)
            code_tabs.addTab(viewer, label)

        layout.addWidget(code_tabs)
        return page

    def _create_passed_tests_page(self):
        """Create page showing passed tests."""
        return self._create_test_list_page(passed_only=True)

    def _create_failed_tests_page(self):
        """Create page showing failed tests with error details."""
        return self._create_test_list_page(passed_only=False)

    def _create_test_list_page(self, passed_only: bool):
        """Create page with list of test cases filtered by status."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Title
        icon = "✅" if passed_only else "❌"
        status_text = "Passed" if passed_only else "Failed"
        title = QLabel(f"{icon} {status_text} Tests")
        title.setStyleSheet(
            f"""
            {bold_label(24, MATERIAL_COLORS['on_surface'])}
        """
        )
        layout.addWidget(title)

        # Get filtered tests from viewmodel
        filtered_tests = (
            self.viewmodel.get_passed_tests()
            if passed_only
            else self.viewmodel.get_failed_tests()
        )

        # Count label
        count_label = QLabel(f"Total: {len(filtered_tests)} tests")
        count_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
        layout.addWidget(count_label)

        if not filtered_tests:
            no_tests_label = QLabel(f"No {status_text.lower()} tests")
            no_tests_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
            layout.addWidget(no_tests_label)
            layout.addStretch()
            return page

        # Scroll area for test cases
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(RESULTS_SCROLL_STYLE)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(12)

        # Add test case widgets
        for test in filtered_tests:
            test_widget = self._create_test_case_widget(test, show_errors=not passed_only)
            scroll_layout.addWidget(test_widget)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        return page

    # Widget Creation Helper Methods

    def _create_code_viewer(self, code: str):
        """Create read-only code viewer with monospace font."""
        viewer = QTextEdit()
        viewer.setPlainText(str(code))
        viewer.setReadOnly(True)
        viewer.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {MATERIAL_COLORS['surface_variant']};
                color: {MATERIAL_COLORS['on_surface']};
                border: 1px solid {MATERIAL_COLORS['outline']};
                border-radius: 4px;
                padding: 12px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.5;
            }}
        """
        )

        # Set monospace font
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        viewer.setFont(font)

        return viewer

    def _create_test_case_widget(self, test: Dict, show_errors: bool = False):
        """Create widget displaying a single test case."""
        widget = QFrame()
        widget.setStyleSheet(RESULTS_CARD_STYLE)
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        # Get formatted test data from viewmodel
        test_data = self.viewmodel.get_test_case_display_data(test)

        # Test number and status
        status_icon = "✅" if test_data["passed"] else "❌"
        header = QLabel(f"{status_icon} Test #{test_data['test_number']}")
        header.setStyleSheet(
            f"""
            {bold_label(16, MATERIAL_COLORS['on_surface'])}
        """
        )
        layout.addWidget(header)

        # Execution time
        if test_data["execution_time"]:
            time_label = QLabel(f"⏱️ Execution Time: {test_data['execution_time']:.4f}s")
            set_emoji_font(time_label)
            time_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
            layout.addWidget(time_label)

        # Input
        if test_data["input"]:
            layout.addWidget(self._create_section_label("Input:"))
            input_text = QTextEdit()
            input_text.setPlainText(str(test_data["input"])[:500])  # Limit to 500 chars
            input_text.setReadOnly(True)
            input_text.setMaximumHeight(100)
            input_text.setStyleSheet(RESULTS_TEXT_EDIT_STYLE)
            layout.addWidget(input_text)

        # Output comparison (for failed tests)
        if show_errors and not test_data["passed"]:
            if test_data["expected_output"]:
                layout.addWidget(self._create_section_label("Expected Output:"))
                expected_text = QTextEdit()
                expected_text.setPlainText(str(test_data["expected_output"])[:500])
                expected_text.setReadOnly(True)
                expected_text.setMaximumHeight(80)
                expected_text.setStyleSheet(RESULTS_TEXT_EDIT_STYLE)
                layout.addWidget(expected_text)

            if test_data["actual_output"]:
                layout.addWidget(self._create_section_label("Actual Output:"))
                actual_text = QTextEdit()
                actual_text.setPlainText(str(test_data["actual_output"])[:500])
                actual_text.setReadOnly(True)
                actual_text.setMaximumHeight(80)
                actual_text.setStyleSheet(RESULTS_TEXT_EDIT_STYLE)
                layout.addWidget(actual_text)

            # Error details
            if test_data["error"]:
                layout.addWidget(
                    self._create_section_label("Error:", MATERIAL_COLORS["error"])
                )
                error_label = QLabel(str(test_data["error"]))
                error_label.setWordWrap(True)
                error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
                layout.addWidget(error_label)

        return widget

    def _create_info_label(self, label: str, value: str, color: str = None):
        """Create horizontal info label with label and value."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        label_widget = QLabel(label)
        label_widget.setStyleSheet(
            f"""
            font-weight: bold;
            color: {MATERIAL_COLORS['on_surface_variant']};
            min-width: 120px;
        """
        )
        layout.addWidget(label_widget)

        value_widget = QLabel(value)
        value_color = color if color else MATERIAL_COLORS["on_surface"]
        value_widget.setStyleSheet(bold_label(color=value_color))
        layout.addWidget(value_widget)

        layout.addStretch()
        return widget

    def _create_section_label(self, text: str, color: str = None):
        """Create section header label."""
        label = QLabel(text)
        label_color = color if color else MATERIAL_COLORS["on_surface"]
        label.setStyleSheet(
            f"""
            {bold_label(14, label_color)}
            padding-top: 8px;
        """
        )
        return label

    def _create_divider(self):
        """Create horizontal divider line."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(RESULTS_SEPARATOR_STYLE)
        line.setMaximumHeight(1)
        return line

    # Action Methods

    def _export_results(self):
        """Export test results to ZIP file."""
        try:
            # Get default filename from viewmodel
            default_name = self.viewmodel.get_export_file_name()

            # Ask user for save location
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Test Results", default_name, "ZIP Files (*.zip)"
            )

            if not file_path:
                return  # User cancelled

            with zipfile.ZipFile(file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                # 1. Export source code files
                files = self.viewmodel.get_files_snapshot()
                if files:
                    for file_name, content in files.items():
                        clean_name = os.path.basename(file_name) if isinstance(file_name, str) else str(file_name)
                        content_str = str(content) if content else ""
                        zipf.writestr(f"code/{clean_name}", content_str.encode("utf-8"))

                # 2. Export test cases using service
                export_test_cases_to_zip(zipf, self.test_result.test_details)

                # 3. Create summary file using service
                summary = create_export_summary(self.test_result)
                zipf.writestr("summary.txt", summary.encode("utf-8"))

            QMessageBox.information(
                self,
                "Export Successful",
                f"Test results exported successfully to:\n{file_path}",
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Export Failed", f"Failed to export results: {str(e)}"
            )

    def _load_to_test(self):
        """Load code files to workspace for testing."""
        try:
            from src.app.persistence.database import FilesSnapshot
            from src.app.shared.constants import WORKSPACE_DIR

            # Check if files exist
            if not self.viewmodel.has_code_files():
                QMessageBox.warning(
                    self,
                    "No Code Files",
                    "This test result doesn't contain any code files to load.",
                )
                return

            # Parse files snapshot
            snapshot = FilesSnapshot.from_json(self.test_result.files_snapshot)

            if not snapshot.files:
                QMessageBox.warning(
                    self,
                    "No Code Files",
                    "This test result doesn't contain any code files to load.",
                )
                return

            # Map test types to directories
            test_type_map = {
                "comparison": "comparator",
                "validation": "validator",
                "benchmark": "benchmarker",
            }

            test_subdir = test_type_map.get(snapshot.test_type)

            if not test_subdir:
                QMessageBox.warning(
                    self,
                    "Unsupported Test Type",
                    f"Cannot load files for test type: {snapshot.test_type}",
                )
                return

            # Confirm with user
            file_list = "\n".join(f"  • {filename}" for filename in snapshot.files.keys())
            reply = QMessageBox.question(
                self,
                "Load to Test",
                f"Load code files to workspace?\n\n"
                f"Project: {self.test_result.project_name}\n"
                f"Test Type: {test_subdir.title()}\n"
                f"Language: {snapshot.primary_language.upper()}\n"
                f"Files ({len(snapshot.files)}):\n{file_list}\n\n"
                f"This will overwrite any existing files in:\n"
                f"{WORKSPACE_DIR}\\{test_subdir}\\\n\n"
                f"Continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply != QMessageBox.Yes:
                return

            # Write files to workspace
            target_dir = os.path.join(WORKSPACE_DIR, test_subdir)
            os.makedirs(target_dir, exist_ok=True)

            written_files = []
            for filename, file_data in snapshot.files.items():
                file_path = os.path.join(target_dir, filename)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(file_data["content"])
                written_files.append(filename)

            # Show success message
            QMessageBox.information(
                self,
                "Files Loaded Successfully",
                f"Successfully wrote {len(written_files)} files to workspace.\n\n"
                f"Navigate to the {test_subdir.title()} window to view and test them.",
            )

            # Emit signal for parent to handle navigation
            self.loadToTestRequested.emit({"test_type": test_subdir})

        except json.JSONDecodeError as e:
            QMessageBox.critical(
                self, "Error", f"Failed to parse code files from test result:\n{str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load files: {str(e)}\n\n"
                f"Ensure the workspace directory exists and is writable.",
            )
