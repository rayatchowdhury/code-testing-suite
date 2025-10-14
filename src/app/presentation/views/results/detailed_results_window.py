"""
Detailed Results Window with Sidebar Navigation

Phase 5 (Issue #34): Redesigned detailed view using sidebar and display area
Follows the same architecture pattern as other windows in the system.
"""

import json
import os
import zipfile
from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
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
from src.app.presentation.styles.components.results import (
    RESULTS_BUTTON_STYLE,
    RESULTS_CARD_STYLE,
    RESULTS_LABEL_DETAILS_STYLE,
    RESULTS_LABEL_TITLE_STYLE,
    RESULTS_TABLE_SMALL_STYLE,
    RESULTS_TEXT_EDIT_STYLE,
)
from src.app.presentation.styles.style import MATERIAL_COLORS
from src.app.presentation.widgets.sidebar import Sidebar


class DetailedResultsWidget(QWidget):
    """Detailed view widget using sidebar and display area (like status views)

    Phase 5 (Issue #34): Complete redesign of detailed results view.
    Features:
    - Widget-based (not window) following status_view pattern
    - Sidebar navigation with 5 sections
    - Stacked widget for content pages in display area
    - Separate views for passed/failed tests
    - Code file viewer with tabs
    - Integrates into parent window's display area
    """

    # Signals
    backRequested = Signal()
    loadToTestRequested = Signal(dict)  # Emits test_result data for loading

    def __init__(self, test_result: TestResult, parent=None):
        super().__init__(parent)
        self.test_result = test_result
        self.current_page = 0

        # Create main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create sidebar
        self.sidebar = Sidebar(f"Test Details - {test_result.test_type.upper()}")

        # Add "Details" section
        details_section = self.sidebar.add_section("Details")

        # Details navigation buttons
        detail_sections = [
            "📊 Summary",
            "💻 Code Files",
            "✅ Passed Tests",
            "❌ Failed Tests",
        ]

        self.nav_buttons = []
        for i, text in enumerate(detail_sections):
            btn = self.sidebar.add_button(text, details_section)
            btn.clicked.connect(lambda checked, idx=i: self._show_page(idx))
            self.nav_buttons.append(btn)

        # Add "Options" section
        options_section = self.sidebar.add_section("Options")

        # Export button
        export_btn = self.sidebar.add_button("📤 Export as ZIP", options_section)
        export_btn.clicked.connect(self._show_export_message)

        # Load to Test button
        load_btn = self.sidebar.add_button("🔄 Load to Test", options_section)
        load_btn.clicked.connect(self._load_to_test)
        load_btn.setToolTip("Load code files into the appropriate test window")

        # Add footer - exactly matching ResultsWindow design
        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()

        # Create Back and Options buttons using exact same pattern as base_window
        back_btn = QPushButton("Back")
        back_btn.setObjectName("back_button")
        back_btn.clicked.connect(self.backRequested.emit)

        options_btn = QPushButton("⚙️")
        options_btn.setObjectName("back_button")
        options_btn.setFont(QFont("Segoe UI", 14))
        # Options button doesn't do anything in detailed view, just for visual consistency

        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)

        # Create display area with stacked widget
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(
            f"background-color: {MATERIAL_COLORS['surface']};"
        )
        self._create_content_pages()

        # Add widgets to layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_stack, 1)  # Content stretches

        # Show summary by default
        self._show_page(0)

    def _show_page(self, page_index: int):
        """Show specific page in content stack"""
        self.current_page = page_index
        self.content_stack.setCurrentIndex(page_index)

    def _create_content_pages(self):
        """Create stacked pages for sidebar navigation

        Updated: 4 content pages (removed export page, now a button)
        """
        self.content_stack.addWidget(self._create_summary_page())
        self.content_stack.addWidget(self._create_code_page())
        self.content_stack.addWidget(self._create_passed_tests_page())
        self.content_stack.addWidget(self._create_failed_tests_page())

    def _create_summary_page(self):
        """Create summary statistics page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Title
        title = QLabel("📊 Test Results Summary")
        title.setStyleSheet(
            f"""
            font-size: 24px;
            font-weight: bold;
            color: {MATERIAL_COLORS['on_surface']};
            padding-bottom: 16px;
        """
        )
        layout.addWidget(title)

        # Statistics card
        stats_card = QFrame()
        stats_card.setStyleSheet(RESULTS_CARD_STYLE)
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setSpacing(12)

        # Project info
        stats_layout.addWidget(
            self._create_info_label("Project:", self.test_result.project_name)
        )
        stats_layout.addWidget(
            self._create_info_label("Test Type:", self.test_result.test_type.upper())
        )
        stats_layout.addWidget(
            self._create_info_label(
                "File:", os.path.basename(self.test_result.file_path)
            )
        )
        stats_layout.addWidget(
            self._create_info_label("Timestamp:", self.test_result.timestamp)
        )

        stats_layout.addWidget(self._create_divider())

        # Test statistics
        success_rate = (
            (self.test_result.passed_tests / self.test_result.test_count * 100)
            if self.test_result.test_count > 0
            else 0
        )
        stats_layout.addWidget(
            self._create_info_label("Total Tests:", str(self.test_result.test_count))
        )
        stats_layout.addWidget(
            self._create_info_label(
                "✅ Passed:",
                str(self.test_result.passed_tests),
                MATERIAL_COLORS["primary"],
            )
        )
        stats_layout.addWidget(
            self._create_info_label(
                "❌ Failed:",
                str(self.test_result.failed_tests),
                MATERIAL_COLORS["error"],
            )
        )
        stats_layout.addWidget(
            self._create_info_label("Success Rate:", f"{success_rate:.1f}%")
        )
        stats_layout.addWidget(
            self._create_info_label(
                "Total Time:", f"{self.test_result.total_time:.3f}s"
            )
        )

        layout.addWidget(stats_card)

        # Mismatch analysis (if exists)
        if self.test_result.mismatch_analysis:
            layout.addWidget(self._create_section_label("Mismatch Analysis:"))
            analysis_text = QTextEdit()
            analysis_text.setPlainText(self.test_result.mismatch_analysis)
            analysis_text.setReadOnly(True)
            analysis_text.setMaximumHeight(200)
            analysis_text.setStyleSheet(RESULTS_TEXT_EDIT_STYLE)
            layout.addWidget(analysis_text)

        layout.addStretch()
        return page

    def _create_code_page(self):
        """Code files page with tabs for each file

        Phase 5 (Task 4): Separate tabs for generator, test, correct, validator code
        """
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Title
        title = QLabel("💻 Source Code Files")
        title.setStyleSheet(
            f"""
            font-size: 24px;
            font-weight: bold;
            color: {MATERIAL_COLORS['on_surface']};
        """
        )
        layout.addWidget(title)

        # Parse files_snapshot
        try:
            files_snapshot = (
                json.loads(self.test_result.files_snapshot)
                if self.test_result.files_snapshot
                else {}
            )
        except json.JSONDecodeError:
            files_snapshot = {}

        if not files_snapshot:
            no_files_label = QLabel("No source code files available")
            no_files_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
            layout.addWidget(no_files_label)
            layout.addStretch()
            return page

        # Tabs for each code file
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

        # Add tabs for each file type
        file_types = [
            ("generator_code", "🔢 Generator"),
            ("test_code", "🧪 Test"),
            ("correct_code", "✅ Correct"),
            ("validator_code", "✔️ Validator"),
        ]

        for key, label in file_types:
            if key in files_snapshot and files_snapshot[key]:
                viewer = self._create_code_viewer(files_snapshot[key])
                code_tabs.addTab(viewer, label)

        # If no known keys, show all files
        if code_tabs.count() == 0:
            for file_name, content in files_snapshot.items():
                viewer = self._create_code_viewer(content)
                code_tabs.addTab(viewer, os.path.basename(file_name))

        layout.addWidget(code_tabs)
        return page

    def _create_code_viewer(self, code: str):
        """Create code viewer widget"""
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

        # Set font
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        viewer.setFont(font)

        return viewer

    def _create_passed_tests_page(self):
        """Page showing only passed tests

        Phase 5 (Task 5): Filtered view of passed tests only
        """
        return self._create_test_list_page(passed_only=True)

    def _create_failed_tests_page(self):
        """Page showing only failed tests

        Phase 5 (Task 5): Filtered view of failed tests with error details
        """
        return self._create_test_list_page(passed_only=False)

    def _create_test_list_page(self, passed_only: bool):
        """Create page with filtered test list"""
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
            font-size: 24px;
            font-weight: bold;
            color: {MATERIAL_COLORS['on_surface']};
        """
        )
        layout.addWidget(title)

        # Parse test details
        try:
            test_details = (
                json.loads(self.test_result.test_details)
                if self.test_result.test_details
                else []
            )
        except json.JSONDecodeError:
            test_details = []

        # Filter by status
        filtered_tests = [
            t for t in test_details if self._test_passed(t) == passed_only
        ]

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
        scroll.setStyleSheet(f"background-color: {MATERIAL_COLORS['surface']};")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(12)

        # Add test case widgets
        for test in filtered_tests:
            test_widget = self._create_test_case_widget(
                test, show_errors=not passed_only
            )
            scroll_layout.addWidget(test_widget)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        return page

    def _test_passed(self, test: dict) -> bool:
        """Check if test passed"""
        return test.get("passed", test.get("status", "").lower() == "pass")

    def _create_test_case_widget(self, test: dict, show_errors: bool = False):
        """Create widget for single test case"""
        widget = QFrame()
        widget.setStyleSheet(RESULTS_CARD_STYLE)
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        # Test number and status
        test_num = test.get("test", test.get("test_number", "?"))
        passed = self._test_passed(test)
        status_icon = "✅" if passed else "❌"

        header = QLabel(f"{status_icon} Test #{test_num}")
        header.setStyleSheet(
            f"""
            font-size: 16px;
            font-weight: bold;
            color: {MATERIAL_COLORS['on_surface']};
        """
        )
        layout.addWidget(header)

        # Execution time
        exec_time = test.get("execution_time", test.get("total_time"))
        if exec_time:
            time_label = QLabel(f"⏱️ Execution Time: {exec_time:.4f}s")
            time_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
            layout.addWidget(time_label)

        # Input
        if "input" in test and test["input"]:
            layout.addWidget(self._create_section_label("Input:"))
            input_text = QTextEdit()
            input_text.setPlainText(str(test["input"])[:500])  # Limit to 500 chars
            input_text.setReadOnly(True)
            input_text.setMaximumHeight(100)
            input_text.setStyleSheet(RESULTS_TEXT_EDIT_STYLE)
            layout.addWidget(input_text)

        # Output comparison (for failed tests)
        if show_errors and not passed:
            expected = test.get(
                "output", test.get("expected_output", test.get("correct_output", ""))
            )
            actual = test.get("actual_output", test.get("test_output", ""))

            if expected:
                layout.addWidget(self._create_section_label("Expected Output:"))
                expected_text = QTextEdit()
                expected_text.setPlainText(str(expected)[:500])
                expected_text.setReadOnly(True)
                expected_text.setMaximumHeight(80)
                expected_text.setStyleSheet(RESULTS_TEXT_EDIT_STYLE)
                layout.addWidget(expected_text)

            if actual:
                layout.addWidget(self._create_section_label("Actual Output:"))
                actual_text = QTextEdit()
                actual_text.setPlainText(str(actual)[:500])
                actual_text.setReadOnly(True)
                actual_text.setMaximumHeight(80)
                actual_text.setStyleSheet(RESULTS_TEXT_EDIT_STYLE)
                layout.addWidget(actual_text)

            # Error details
            error = test.get("error", test.get("error_details", ""))
            if error:
                layout.addWidget(
                    self._create_section_label("Error:", MATERIAL_COLORS["error"])
                )
                error_label = QLabel(str(error))
                error_label.setWordWrap(True)
                error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
                layout.addWidget(error_label)

        return widget

    def _show_export_message(self):
        """Export current test result as ZIP"""
        try:
            # Ask user for save location
            import zipfile

            from PySide6.QtWidgets import QFileDialog

            default_name = f"test_export_{self.test_result.project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Test Results", default_name, "ZIP Files (*.zip)"
            )

            if not file_path:
                return  # User cancelled

            with zipfile.ZipFile(file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                # 1. Extract and save source code files
                if self.test_result.files_snapshot:
                    files_data = json.loads(self.test_result.files_snapshot)
                    for file_name, content in files_data.items():
                        # Clean file path for ZIP
                        clean_name = os.path.basename(file_name)
                        # Ensure content is string and encode to bytes
                        content_str = str(content) if content else ""
                        zipf.writestr(f"code/{clean_name}", content_str.encode("utf-8"))

                # 2. Extract and save test cases
                if self.test_result.test_details:
                    test_data = json.loads(self.test_result.test_details)

                    # Separate passed and failed tests
                    for i, test_case in enumerate(test_data, 1):
                        test_num = test_case.get("test", i)
                        status = test_case.get("status", "unknown")

                        # Create test case file content
                        test_content = f"Test #{test_num}\n"
                        test_content += f"Status: {status}\n"
                        test_content += f"{'='*50}\n\n"

                        if "input" in test_case:
                            test_content += f"INPUT:\n{test_case['input']}\n\n"

                        if "output" in test_case:
                            test_content += (
                                f"EXPECTED OUTPUT:\n{test_case['output']}\n\n"
                            )

                        if "actual_output" in test_case:
                            test_content += (
                                f"ACTUAL OUTPUT:\n{test_case['actual_output']}\n\n"
                            )

                        if "error" in test_case:
                            test_content += f"ERROR:\n{test_case['error']}\n\n"

                        if "execution_time" in test_case:
                            test_content += f"Execution Time: {test_case['execution_time']} seconds\n"

                        # Save to appropriate folder
                        folder = "passed" if status.lower() == "pass" else "failed"
                        zipf.writestr(
                            f"{folder}/test_{test_num}.txt",
                            test_content.encode("utf-8"),
                        )

                # 3. Create summary file
                summary = f"Test Results Export\n"
                summary += f"{'='*60}\n\n"
                summary += f"Project: {self.test_result.project_name}\n"
                summary += f"Test Type: {self.test_result.test_type}\n"
                summary += f"File: {os.path.basename(self.test_result.file_path)}\n"
                summary += f"Timestamp: {self.test_result.timestamp}\n\n"
                summary += f"Test Statistics:\n"
                summary += f"  Total Tests: {self.test_result.test_count}\n"
                summary += f"  Passed: {self.test_result.passed_tests}\n"
                summary += f"  Failed: {self.test_result.failed_tests}\n"
                summary += f"  Success Rate: {(self.test_result.passed_tests/self.test_result.test_count*100) if self.test_result.test_count > 0 else 0:.1f}%\n"
                summary += (
                    f"  Total Time: {self.test_result.total_time:.3f} seconds\n\n"
                )

                if self.test_result.mismatch_analysis:
                    summary += f"\nMismatch Analysis:\n"
                    summary += f"{self.test_result.mismatch_analysis}\n"

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
        """Load code files into the appropriate test window.

        NEW APPROACH: Simply writes files to workspace and lets the window read them.
        No complex widget navigation needed - windows automatically load from workspace.
        """
        try:
            from src.app.persistence.database import FilesSnapshot
            from src.app.shared.constants import WORKSPACE_DIR

            # Parse files_snapshot using new FilesSnapshot class (handles old format automatically)
            if not self.test_result.files_snapshot:
                QMessageBox.warning(
                    self,
                    "No Code Files",
                    "This test result doesn't contain any code files to load.",
                )
                return

            snapshot = FilesSnapshot.from_json(self.test_result.files_snapshot)

            if not snapshot.files:
                QMessageBox.warning(
                    self,
                    "No Code Files",
                    "This test result doesn't contain any code files to load.",
                )
                return

            # Map test types to window names and subdirectories
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

            # Confirm with user before overwriting
            file_list = "\n".join(
                f"  • {filename}" for filename in snapshot.files.keys()
            )
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

            # Write files to workspace/{test_subdir}/
            target_dir = os.path.join(WORKSPACE_DIR, test_subdir)
            os.makedirs(target_dir, exist_ok=True)

            written_files = []
            for filename, file_data in snapshot.files.items():
                file_path = os.path.join(target_dir, filename)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(file_data["content"])
                written_files.append(filename)

            # Show success message and open window
            QMessageBox.information(
                self,
                "Files Loaded Successfully",
                f"Successfully wrote {len(written_files)} files to workspace.\n\n"
                f"Navigate to the {test_subdir.title()} window to view and test them.",
            )

            # Optionally open the target window
            if hasattr(self.parent, "window_manager"):
                self.parent.window_manager.show_window(test_subdir)

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

    def _detect_language(self, files_snapshot: dict) -> str:
        """Detect programming language from file extensions or keys"""
        # Check for language-specific keys
        for key in files_snapshot.keys():
            if key.endswith(".py") or "py" in key.lower():
                return "py"
            elif key.endswith(".cpp") or "cpp" in key.lower():
                return "cpp"
            elif key.endswith(".java") or "java" in key.lower():
                return "java"

        # Check known key patterns
        if "generator_code" in files_snapshot or "test_code" in files_snapshot:
            # Try to detect from content (look for typical patterns)
            content = list(files_snapshot.values())[0] if files_snapshot else ""
            if "import " in content or "def " in content:
                return "py"
            elif "#include" in content or "int main" in content:
                return "cpp"
            elif "public class" in content or "import java" in content:
                return "java"

        # Default to cpp
        return "cpp"

    # Helper methods for UI elements

    def _create_info_label(self, label: str, value: str, color: str = None):
        """Create info label with label and value"""
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
        value_widget.setStyleSheet(f"color: {value_color}; font-weight: bold;")
        layout.addWidget(value_widget)

        layout.addStretch()
        return widget

    def _create_section_label(self, text: str, color: str = None):
        """Create section label"""
        label = QLabel(text)
        label_color = color if color else MATERIAL_COLORS["on_surface"]
        label.setStyleSheet(
            f"""
            font-size: 14px;
            font-weight: bold;
            color: {label_color};
            padding-top: 8px;
        """
        )
        return label

    def _create_divider(self):
        """Create horizontal divider"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {MATERIAL_COLORS['outline']};")
        line.setMaximumHeight(1)
        return line
