import json
import os
import zipfile
from datetime import datetime

from PySide6.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.app.presentation.views.results.results_widget import TestResultsWidget
from src.app.presentation.widgets.sidebar import Sidebar
from src.app.presentation.window_controller.base_window import SidebarWindowBase


class ResultsWindow(SidebarWindowBase):
    """Window to display test results and analytics"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.sidebar = Sidebar("Results & Analytics")

        # Actions section
        action_section = self.sidebar.add_section("Actions")

        # Add action buttons
        for button_text in ["Refresh Data", "Export Results", "Clear Old Data"]:
            btn = self.sidebar.add_button(button_text, action_section)
            btn.clicked.connect(
                lambda checked, text=button_text: self.handle_action_button(text)
            )

        # Phase 3 (Issue #17): Removed redundant "View Options" section
        # Filters are already available in the main results widget

        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()

        # Footer buttons
        back_btn, options_btn = self.create_footer_buttons()
        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)

        # Create display area with results widget
        self.display_area = TestResultsWidget()

        # Setup splitter (this will reparent display_area to splitter)
        self.setup_splitter(self.sidebar, self.display_area)

        # Store reference to parent window in display_area for Phase 5 integration
        # (needed because splitter reparents the widget)
        self.display_area.results_window = self

        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)

    def handle_action_button(self, button_text):
        """Handle action button clicks"""
        if button_text == "Refresh Data":
            self.display_area._load_results()
        elif button_text == "Export Results":
            self.export_results()
        elif button_text == "Clear Old Data":
            self.clear_old_data()

    # Phase 3 (Issue #17): Removed handle_view_button() method
    # View options section was redundant with main widget filters

    def export_results(self):
        """Export results to ZIP file with code, test cases, and summary

        Phase 4 (Issues #11, #33): Comprehensive ZIP export functionality
        Creates a ZIP file containing:
        - code/ folder: Source code files from files_snapshot
        - passed/ folder: Passed test cases
        - failed/ folder: Failed test cases
        - summary.txt: Test statistics and metadata
        """
        # Get currently selected result
        selected_rows = self.display_area.results_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(
                self, "No Selection", "Please select a test result to export."
            )
            return

        # Get result ID from first column of selected row
        row = selected_rows[0].row()
        result_id = self.display_area.results_table.item(row, 0).data(
            1
        )  # ID stored in UserRole

        # Get full result from database
        results = self.display_area.db_manager.get_test_results(limit=1000)
        result = None
        for r in results:
            if r.id == result_id:
                result = r
                break

        if not result:
            QMessageBox.warning(
                self, "Error", "Could not retrieve test result details."
            )
            return

        # Ask user for save location
        default_name = f"test_export_{result.project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Test Results", default_name, "ZIP Files (*.zip)"
        )

        if not file_path:
            return  # User cancelled

        try:
            with zipfile.ZipFile(file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                # 1. Extract and save source code files
                if result.files_snapshot:
                    from src.app.persistence.database import FilesSnapshot

                    # Parse snapshot (handles both old and new formats)
                    snapshot = FilesSnapshot.from_json(result.files_snapshot)

                    # Export files with proper filenames and extensions
                    for filename, file_data in snapshot.files.items():
                        content = file_data.get("content", "")
                        language = file_data.get("language", "txt")
                        role = file_data.get("role", "unknown")

                        # Create subfolder based on role for organization
                        subfolder = f"code/{role}" if role != "unknown" else "code"
                        zipf.writestr(
                            f"{subfolder}/{filename}", content.encode("utf-8")
                        )

                    # Also create a metadata file with language info
                    metadata = "Files Snapshot Metadata\n"
                    metadata += f"{'='*60}\n\n"
                    metadata += f"Test Type: {snapshot.test_type}\n"
                    metadata += f"Primary Language: {snapshot.primary_language}\n"
                    metadata += f"Total Files: {len(snapshot.files)}\n\n"
                    metadata += "Files:\n"
                    for filename, file_data in snapshot.files.items():
                        metadata += f"  - {filename} ({file_data.get('language', 'unknown')}) [{file_data.get('role', 'unknown')}]\n"

                    zipf.writestr("code/FILES_INFO.txt", metadata.encode("utf-8"))

                # 2. Extract and save test cases
                if result.test_details:
                    test_data = json.loads(result.test_details)

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
                summary = "Test Results Export\n"
                summary += f"{'='*60}\n\n"
                summary += f"Project: {result.project_name}\n"
                summary += f"Test Type: {result.test_type}\n"
                summary += f"File: {os.path.basename(result.file_path)}\n"
                summary += f"Timestamp: {result.timestamp}\n\n"
                summary += "Test Statistics:\n"
                summary += f"  Total Tests: {result.test_count}\n"
                summary += f"  Passed: {result.passed_tests}\n"
                summary += f"  Failed: {result.failed_tests}\n"
                summary += f"  Success Rate: {(result.passed_tests/result.test_count*100) if result.test_count > 0 else 0:.1f}%\n"
                summary += f"  Total Time: {result.total_time:.3f} seconds\n\n"

                if result.mismatch_analysis:
                    summary += "\nMismatch Analysis:\n"
                    summary += f"{result.mismatch_analysis}\n"

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

    def clear_old_data(self):
        """Clear old data from database"""
        reply = QMessageBox.question(
            self,
            "Clear Old Data",
            "This will delete test results older than 7 days. Continue?",  # Phase 3 (Issue #32): Changed from 30 to 7 days
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.display_area.db_manager.cleanup_old_data(
                7
            )  # Phase 3 (Issue #32): Changed from 30 to 7 days
            self.display_area._load_results()
            QMessageBox.information(self, "Success", "Old data cleared successfully!")

    def show_detailed_view(self, test_result):
        """
        Show detailed view for a specific test result.
        Replaces BOTH sidebar and display area with detailed view (Phase 5: Issue #34).

        Args:
            test_result: TestResult object to display details for
        """
        from src.app.presentation.views.results.detailed_results_window import (
            DetailedResultsWidget,
        )

        # Create detailed view widget
        detailed_view = DetailedResultsWidget(test_result, parent=self)

        # Connect back signal to restore display area
        detailed_view.backRequested.connect(self._on_detailed_back_requested)

        # Connect load to test signal
        detailed_view.loadToTestRequested.connect(self._handle_load_to_test)

        # Store references
        self.detailed_view = detailed_view
        self.detailed_view_active = True

        # Store original sidebar and display area for restoration
        if not hasattr(self, "_original_sidebar"):
            self._original_sidebar = self.sidebar
            self._original_display = self.display_area

        # Remove current widgets from splitter
        while self.splitter.count() > 0:
            widget = self.splitter.widget(0)
            self.splitter.widget(0).setParent(None)

        # Add detailed view's sidebar and content to splitter
        self.splitter.addWidget(detailed_view.sidebar)
        self.splitter.addWidget(detailed_view.content_stack)

        # Update references
        self.sidebar = detailed_view.sidebar

        # Maintain splitter sizes
        self.update_splitter_sizes()

    def _on_detailed_back_requested(self):
        """Handle back request from detailed view - restore original sidebar and display area"""
        if hasattr(self, "_original_sidebar") and hasattr(self, "_original_display"):
            # Remove detailed view widgets from splitter
            while self.splitter.count() > 0:
                widget = self.splitter.widget(0)
                widget.setParent(None)

            # Restore original widgets
            self.splitter.addWidget(self._original_sidebar)
            self.splitter.addWidget(self._original_display)

            # Restore references
            self.sidebar = self._original_sidebar
            self.display_area = self._original_display

            # Maintain splitter sizes
            self.update_splitter_sizes()

        self.detailed_view_active = False
        self.detailed_view = None

    def handle_button_click(self, button_text):
        """Handle sidebar button clicks"""
        if button_text == "Back":
            # If detailed view is active, restore it instead of navigating away
            if hasattr(self, "detailed_view_active") and self.detailed_view_active:
                self._on_detailed_back_requested()
                return

        if button_text == "Help Center":
            if self.can_close():
                from src.app.presentation.services.navigation_service import NavigationService
                NavigationService.instance().navigate_to("help_center")
        else:
            super().handle_button_click(button_text)

    def refresh_ai_panels(self):
        """Refresh AI panel visibility (not applicable for results window)"""

    def _handle_load_to_test(self, load_data: dict):
        """Handle loading code files into test window

        Args:
            load_data: Dictionary containing test_type, window_name, language, files, project_name
        """
        try:
            print("\n" + "=" * 60)
            print("DEBUG: Load to Test - Signal Received")
            print("=" * 60)
            print(
                f"Load data contents: {json.dumps({k: (v if k != 'files' else f'{len(v)} files') for k, v in load_data.items()}, indent=2)}"
            )

            window_name = load_data["window_name"]
            language = load_data["language"]
            files = load_data["files"]

            print(f"\nDEBUG: Target window: {window_name}")
            print(f"DEBUG: Language: {language}")
            print(f"DEBUG: Files to load: {list(files.keys())}")

            # Use NavigationService for navigation (Phase 4A)
            from src.app.presentation.services.navigation_service import NavigationService
            
            # Show the target window (creates it if doesn't exist)
            print(f"\nDEBUG: Calling navigate_to('{window_name}')...")
            show_result = NavigationService.instance().navigate_to(window_name)
            print(f"DEBUG: navigate_to result: {show_result}")

            if not show_result:
                print(f"DEBUG: ERROR - Failed to show window '{window_name}'")
                QMessageBox.critical(
                    self, "Error", f"Failed to open {window_name.title()} window."
                )
                return

            # Get the window instance from parent's window_manager for accessing windows dict
            # TODO: Phase 4C - Consider adding get_window method to NavigationService
            if not hasattr(self, "parent") or not hasattr(
                self.parent, "window_manager"
            ):
                print("DEBUG: ERROR - Cannot access window manager for window lookup!")
                QMessageBox.critical(self, "Error", "Cannot access window manager.")
                return

            window_manager = self.parent.window_manager
            
            # Get the window instance
            print("\nDEBUG: Retrieving window instance from windows dict...")
            print(f"DEBUG: Available windows: {list(window_manager.windows.keys())}")
            target_window = window_manager.windows.get(window_name)
            print(
                f"DEBUG: Target window obtained: {type(target_window).__name__ if target_window else 'None'}"
            )

            if not target_window:
                print(f"DEBUG: ERROR - Window instance not found for '{window_name}'")
                QMessageBox.critical(
                    self, "Error", f"Failed to access {window_name.title()} window."
                )
                return

            # Load code into the window based on test type
            print("\nDEBUG: Calling _load_code_into_window...")
            self._load_code_into_window(target_window, load_data)
            print("DEBUG: Load to Test - Complete")
            print("=" * 60 + "\n")

        except Exception as e:
            print(f"\nDEBUG: EXCEPTION in _handle_load_to_test: {str(e)}")
            import traceback

            traceback.print_exc()
            QMessageBox.critical(
                self, "Load Error", f"Failed to load code files: {str(e)}"
            )

    def _load_code_into_window(self, window, load_data: dict):
        """Load code files into a specific test window

        Args:
            window: The target window (ComparatorWindow, ValidatorWindow, or BenchmarkerWindow)
            load_data: Dictionary with language, files, etc.
        """
        try:
            print("\nDEBUG: _load_code_into_window - Starting")
            language = load_data["language"]
            files = load_data["files"]
            test_type = load_data["test_type"]

            print(f"DEBUG: Test type: {test_type}")
            print(f"DEBUG: Language to set: {language}")
            print(f"DEBUG: Files available: {list(files.keys())}")

            # Access the display area
            print("\nDEBUG: Checking for display_area...")
            print(f"  - Has display_area: {hasattr(window, 'display_area')}")

            if not hasattr(window, "display_area"):
                print("DEBUG: ERROR - Window doesn't have display_area!")
                raise Exception("Window doesn't have a display_area")

            display_area = window.display_area
            print(f"DEBUG: display_area obtained: {type(display_area).__name__}")
            print(f"  - Has test_tabs: {hasattr(display_area, 'test_tabs')}")

            # Get test_tabs reference for language switching
            test_tabs = None
            if hasattr(display_area, "test_tabs"):
                test_tabs = display_area.test_tabs
                print(f"DEBUG: test_tabs obtained: {type(test_tabs).__name__}")
                print(
                    f"  - Has switch_language: {hasattr(test_tabs, 'switch_language')}"
                )
                print(
                    f"  - Has multi_language attr: {hasattr(test_tabs, 'multi_language')}"
                )
                if hasattr(test_tabs, "multi_language"):
                    print(f"  - multi_language value: {test_tabs.multi_language}")
            else:
                print("DEBUG: WARNING - No test_tabs found")

            # Map file keys to tab names based on test type
            print(f"\nDEBUG: Getting file key mapping for test_type='{test_type}'...")
            file_key_mapping = self._get_file_key_mapping(test_type)
            print(f"DEBUG: File key mapping: {file_key_mapping}")

            # Load each code file (and switch language per tab)
            print("\nDEBUG: Loading code files...")
            files_loaded = 0
            for file_key, tab_name in file_key_mapping.items():
                print(f"\nDEBUG: Checking file_key='{file_key}' -> tab='{tab_name}'")
                if file_key in files:
                    code_content = files[file_key]
                    print(
                        f"  - Found file_key '{file_key}', content length: {len(code_content)}"
                    )

                    # Switch language for this tab if multi-language supported
                    if (
                        test_tabs
                        and hasattr(test_tabs, "switch_language")
                        and hasattr(test_tabs, "multi_language")
                        and test_tabs.multi_language
                    ):
                        print(
                            f"  - Switching tab '{tab_name}' to language '{language}'..."
                        )
                        test_tabs.switch_language(tab_name, language)
                        print("  - Language switched successfully")

                    print(f"  - Attempting to load code into tab '{tab_name}'...")
                    self._set_code_in_tab(display_area, tab_name, code_content)
                    files_loaded += 1
                    print(f"  - Successfully loaded into '{tab_name}'")
                else:
                    print(f"  - File key '{file_key}' not found in files")

            print(
                f"\nDEBUG: Files loaded via mapping: {files_loaded}/{len(file_key_mapping)}"
            )

            # If no specific keys found, try generic loading
            if not any(key in files for key in file_key_mapping.keys()):
                print("\nDEBUG: No mapped keys found, attempting generic loading...")
                self._load_generic_files(display_area, files)
            else:
                print("DEBUG: Mapped keys found, skipping generic loading")

            print("DEBUG: _load_code_into_window - Complete\n")

        except Exception as e:
            print(f"\nDEBUG: EXCEPTION in _load_code_into_window: {str(e)}")
            import traceback

            traceback.print_exc()
            raise Exception(f"Failed to load code: {str(e)}")

    def _get_file_key_mapping(self, test_type: str) -> dict:
        """Get mapping of file keys to tab names for each test type"""
        if test_type == "comparison":
            return {
                "generator_code": "Generator",
                "correct_code": "Correct Code",
                "test_code": "Test Code",
            }
        if test_type == "validation":
            return {
                "generator_code": "Generator",
                "validator_code": "Validator",
                "test_code": "Test Code",
            }
        if test_type == "benchmark":
            return {"test_code": "Test Code"}
        return {}

    def _set_code_in_tab(self, display_area, tab_name: str, code_content: str):
        """Set code content in a specific tab

        Args:
            display_area: The display area containing test_tabs and editor
            tab_name: Name of the tab to activate
            code_content: Code content to set
        """
        try:
            print(f"  DEBUG: _set_code_in_tab - tab_name='{tab_name}'")

            # Activate the tab
            if hasattr(display_area, "test_tabs"):
                print(f"    - Has test_tabs, calling activate_tab('{tab_name}')...")
                display_area.test_tabs.activate_tab(tab_name, skip_save_prompt=True)
                print("    - Tab activated successfully")
            else:
                print("    - WARNING: No test_tabs to activate")

            # Set the code in editor
            if hasattr(display_area, "editor"):
                editor = display_area.editor
                print(f"    - Editor obtained: {type(editor).__name__}")
                print(f"      - Has setPlainText: {hasattr(editor, 'setPlainText')}")
                print(f"      - Has setText: {hasattr(editor, 'setText')}")
                print(f"      - Has codeEditor: {hasattr(editor, 'codeEditor')}")

                # EditorWidget has a codeEditor property (QPlainTextEdit)
                code_editor = None
                if hasattr(editor, "codeEditor"):
                    code_editor = editor.codeEditor
                    print(f"      - codeEditor type: {type(code_editor).__name__}")
                    print(
                        f"      - codeEditor has setPlainText: {hasattr(code_editor, 'setPlainText')}"
                    )

                # Try to set code content
                if code_editor and hasattr(code_editor, "setPlainText"):
                    print(
                        f"    - Setting code via codeEditor.setPlainText() ({len(code_content)} chars)"
                    )
                    code_editor.setPlainText(code_content)
                    print("    - Code set successfully via codeEditor")
                elif hasattr(editor, "setPlainText"):
                    print(
                        f"    - Setting code with editor.setPlainText() ({len(code_content)} chars)"
                    )
                    editor.setPlainText(code_content)
                    print("    - Code set successfully")
                elif hasattr(editor, "setText"):
                    print(
                        f"    - Setting code with editor.setText() ({len(code_content)} chars)"
                    )
                    editor.setText(code_content)
                    print("    - Code set successfully")
                else:
                    print("    - ERROR: No method found to set editor content!")

                # Mark as saved (no unsaved changes)
                if hasattr(display_area, "test_tabs"):
                    print("    - Marking tab as saved...")
                    display_area.test_tabs.mark_current_tab_saved()
                    print("    - Tab marked as saved")
            else:
                print("    - WARNING: No editor found!")

        except Exception as e:
            print(f"  DEBUG: EXCEPTION in _set_code_in_tab for '{tab_name}': {str(e)}")
            import traceback

            traceback.print_exc()
            print(f"Warning: Failed to set code in tab {tab_name}: {e}")

    def _load_generic_files(self, display_area, files: dict):
        """Load files generically by file name patterns"""
        print("DEBUG: _load_generic_files - Starting generic pattern matching")
        print(f"DEBUG: Files to match: {list(files.keys())}")

        matched_files = 0
        for file_name, content in files.items():
            file_lower = file_name.lower()
            print(f"\nDEBUG: Checking file '{file_name}'...")

            # Try to match by file name patterns
            if "generator" in file_lower:
                print("  - Matched 'generator' pattern -> loading to Generator tab")
                self._set_code_in_tab(display_area, "Generator", content)
                matched_files += 1
            elif "correct" in file_lower:
                print("  - Matched 'correct' pattern -> loading to Correct Code tab")
                self._set_code_in_tab(display_area, "Correct Code", content)
                matched_files += 1
            elif "validator" in file_lower:
                print("  - Matched 'validator' pattern -> loading to Validator tab")
                self._set_code_in_tab(display_area, "Validator", content)
                matched_files += 1
            elif "test" in file_lower:
                print("  - Matched 'test' pattern -> loading to Test Code tab")
                self._set_code_in_tab(display_area, "Test Code", content)
                matched_files += 1
            else:
                print(f"  - No pattern match for '{file_name}'")

        print(
            f"\nDEBUG: Generic loading complete: {matched_files}/{len(files)} files matched"
        )
