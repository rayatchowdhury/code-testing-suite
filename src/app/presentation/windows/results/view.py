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

from src.app.presentation.windows.results.widgets.results_widget import ResultsWidget
from src.app.presentation.shared.components.sidebar import Sidebar
from src.app.presentation.base.content_window_base import ContentWindowBase
from src.app.presentation.services import export_test_cases_to_zip, create_export_summary, ErrorHandlerService

class ResultsWindow(ContentWindowBase):
    """Window to display test results and analytics"""

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize detailed view tracking attributes
        self._original_sidebar = None
        self._original_display = None
        self.detailed_view_active = False
        self.detailed_view = None

        self.sidebar = Sidebar("Results & Analytics")

        # Actions section
        action_section = self.sidebar.add_section("Actions")

        for button_text in ["Refresh Data", "Export Results", "Clear Old Data"]:
            btn = self.sidebar.add_button(button_text, action_section)
            btn.clicked.connect(
                lambda _, text=button_text: self.handle_action_button(text)
            )

        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()

        # Footer buttons
        back_btn, options_btn = self.create_footer_buttons()
        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)

        self.display_area = ResultsWidget()

        self.setup_splitter(self.sidebar, self.display_area)

        self.display_area.results_window = self

        self.sidebar.button_clicked.connect(self.handle_button_click)

    def handle_action_button(self, button_text):
        if button_text == "Refresh Data":
            self.display_area._load_results()
        elif button_text == "Export Results":
            self.export_results()
        elif button_text == "Clear Old Data":
            self.clear_old_data()

    def export_results(self):
        """Export results to ZIP: code/, passed/, failed/, summary.txt"""
        error_service = ErrorHandlerService.instance()
        selected_rows = self.display_area.results_table.selectedItems()
        if not selected_rows:
            error_service.show_warning(
                "No Selection", "Please select a test result to export.", self
            )
            return

        row = selected_rows[0].row()
        result_id = self.display_area.results_table.item(row, 0).data(
            1
        )  # ID stored in UserRole

        results = self.display_area.db_manager.get_test_results(limit=1000)
        result = None
        for r in results:
            if r.id == result_id:
                result = r
                break

        if not result:
            error_service.show_warning(
                "Error", "Could not retrieve test result details.", self
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
                    from src.app.database import FilesSnapshot

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

                # 2. Extract and save test cases using export service
                export_test_cases_to_zip(zipf, result.test_details)

                # 3. Create summary file using export service
                summary = create_export_summary(result)
                zipf.writestr("summary.txt", summary.encode("utf-8"))

            error_service.show_success(
                "Export Successful",
                f"Test results exported successfully to:\n{file_path}",
                self
            )

        except (OSError, IOError, zipfile.BadZipFile) as e:
            error_service.show_error(
                "Export Failed", f"Failed to export results: {str(e)}", self
            )

    def clear_old_data(self):
        error_service = ErrorHandlerService.instance()
        reply = error_service.ask_question(
            "Clear Old Data",
            "This will delete test results older than 7 days. Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
            self
        )

        if reply == QMessageBox.Yes:
            self.display_area.db_manager.cleanup_old_data(7)
            self.display_area._load_results()
            error_service.show_success("Success", "Old data cleared successfully!", self)

    def show_detailed_view(self, test_result):
        """Show detailed view for test result (replaces sidebar and display area)."""
        from src.app.presentation.shared.dialogs.result_detail import DetailedResultDialog

        detailed_view = DetailedResultDialog(test_result, parent=self)

        detailed_view.backRequested.connect(self._on_detailed_back_requested)

        detailed_view.loadToTestRequested.connect(self._handle_load_to_test)

        self.detailed_view = detailed_view
        self.detailed_view_active = True

        if self._original_sidebar is None:
            self._original_sidebar = self.sidebar
            self._original_display = self.display_area

        while self.splitter.count() > 0:
            widget = self.splitter.widget(0)
            self.splitter.widget(0).setParent(None)

        self.splitter.addWidget(detailed_view.sidebar)
        self.splitter.addWidget(detailed_view.content_stack)

        # Update references
        self.sidebar = detailed_view.sidebar

        # Maintain splitter sizes
        self.update_splitter_sizes()

    def _on_detailed_back_requested(self):
        if self._original_sidebar is not None and self._original_display is not None:
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
        if button_text == "Back":
            # If detailed view is active, restore it instead of navigating away
            if self.detailed_view_active:
                self._on_detailed_back_requested()
                return

        if button_text == "Help Center":
            if self.can_close():
                if self.router:
                    self.router.navigate_to("help_center")
        else:
            super().handle_button_click(button_text)

    def refresh_ai_panels(self):
        pass

    def _handle_load_to_test(self, load_data: dict):
        error_service = ErrorHandlerService.instance()
        try:
            window_name = load_data["window_name"]
            language = load_data["language"]
            files = load_data["files"]

            
            show_result = self.router.navigate_to(window_name) if self.router else False

            if not show_result:
                error_service.show_error(
                    "Error", f"Failed to open {window_name.title()} window.", self
                )
                return

            # Check if parent has window_manager
            if self.parent is None or not hasattr(self.parent, "window_manager"):
                error_service.show_error("Error", "Cannot access window manager.", self)
                return

            window_manager = self.parent.window_manager
            target_window = window_manager.windows.get(window_name)

            if not target_window:
                error_service.show_error(
                    "Error", f"Failed to access {window_name.title()} window.", self
                )
                return

            self._load_code_into_window(target_window, load_data)

        except (AttributeError, ValueError, RuntimeError) as e:
            import traceback
            traceback.print_exc()
            error_service.show_error(
                "Load Error", f"Failed to load code files: {str(e)}", self
            )

    def _load_code_into_window(self, window, load_data: dict):
        try:
            language = load_data["language"]
            files = load_data["files"]
            test_type = load_data["test_type"]

            try:
                display_area = window.display_area
            except AttributeError:
                raise Exception("Window doesn't have a display_area")

            test_tabs = getattr(display_area, "test_tabs", None)

            file_key_mapping = self._get_file_key_mapping(test_type)

            for file_key, tab_name in file_key_mapping.items():
                if file_key in files:
                    code_content = files[file_key]

                    # Try to switch language if test_tabs supports it
                    if test_tabs is not None:
                        try:
                            if test_tabs.multi_language:
                                test_tabs.switch_language(tab_name, language)
                        except AttributeError:
                            pass  # test_tabs doesn't support multi_language

                    self._set_code_in_tab(display_area, tab_name, code_content)

            if not any(key in files for key in file_key_mapping.keys()):
                self._load_generic_files(display_area, files)

        except (AttributeError, ValueError, KeyError) as e:
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to load code: {str(e)}")

    def _get_file_key_mapping(self, test_type: str) -> dict:
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
        try:
            # Try to activate tab
            try:
                display_area.test_tabs.activate_tab(tab_name, skip_save_prompt=True)
            except AttributeError:
                pass  # display_area doesn't have test_tabs

            # Try to set code in editor
            try:
                editor = display_area.editor
                code_editor = getattr(editor, "codeEditor", None)

                # Try different methods to set text
                if code_editor is not None:
                    try:
                        code_editor.setPlainText(code_content)
                    except AttributeError:
                        pass
                else:
                    try:
                        editor.setPlainText(code_content)
                    except AttributeError:
                        try:
                            editor.setText(code_content)
                        except AttributeError:
                            pass

                # Mark tab as saved
                try:
                    display_area.test_tabs.mark_current_tab_saved()
                except AttributeError:
                    pass
            except AttributeError:
                pass  # display_area doesn't have editor

        except AttributeError as e:
            import traceback
            traceback.print_exc()

    def _load_generic_files(self, display_area, files: dict):
        for file_name, content in files.items():
            file_lower = file_name.lower()

            if "generator" in file_lower:
                self._set_code_in_tab(display_area, "Generator", content)
            elif "correct" in file_lower:
                self._set_code_in_tab(display_area, "Correct Code", content)
            elif "validator" in file_lower:
                self._set_code_in_tab(display_area, "Validator", content)
            elif "test" in file_lower:
                self._set_code_in_tab(display_area, "Test Code", content)
