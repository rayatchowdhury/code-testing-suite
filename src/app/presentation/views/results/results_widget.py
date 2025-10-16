import json
from datetime import datetime, timedelta

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTabBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.app.persistence.database import DatabaseManager, TestResult
from src.app.presentation.styles.components.code_editor_display_area import (
    OUTER_PANEL_STYLE,
    SPLITTER_STYLE,
)
from src.app.presentation.styles.components.results import (
    RESULTS_BUTTON_STYLE,
    RESULTS_CARD_STYLE,
    RESULTS_COMBO_STYLE,
    RESULTS_FILTERS_PANEL_STYLE,
    RESULTS_LABEL_DETAILS_STYLE,
    RESULTS_LABEL_FILTER_STYLE,
    RESULTS_LABEL_STAT_STYLE,
    RESULTS_LABEL_TITLE_STYLE,
    RESULTS_PROGRESS_BAR_STYLE,
    RESULTS_TAB_WIDGET_STYLE,
    RESULTS_TABLE_SMALL_STYLE,
    RESULTS_TABLE_STYLE,
    RESULTS_TEXT_EDIT_STYLE,
)
from src.app.presentation.styles.style import MATERIAL_COLORS


class TestResultsWidget(QWidget):
    """Widget to display test results from database"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self._setup_ui()
        self._load_results()

    def _setup_ui(self):
        # Main layout similar to CodeEditorDisplay
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet(SPLITTER_STYLE)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(0)

        # Create outer panel with gradient background
        outer_panel = QWidget()
        outer_panel.setMinimumWidth(400)
        outer_panel.setStyleSheet(OUTER_PANEL_STYLE)
        outer_layout = QVBoxLayout(outer_panel)
        outer_layout.setContentsMargins(3, 3, 3, 3)
        outer_layout.setSpacing(0)

        # Create inner panel with surface color
        main_panel = QWidget()
        main_panel.setStyleSheet(
            f"""
            background-color: {MATERIAL_COLORS['surface']};
        """
        )

        panel_layout = QVBoxLayout(main_panel)
        panel_layout.setContentsMargins(16, 16, 16, 16)
        panel_layout.setSpacing(16)

        # Filters section with Material Design styling
        filters_panel = QWidget()
        filters_panel.setStyleSheet(RESULTS_FILTERS_PANEL_STYLE)
        filters_main_layout = QVBoxLayout(filters_panel)
        filters_main_layout.setContentsMargins(16, 12, 16, 12)
        filters_main_layout.setSpacing(12)

        # First row: Type and Date filters
        filters_row1 = QHBoxLayout()
        filters_row1.setSpacing(16)

        # Test type filter
        type_label = QLabel("Test Type:")
        type_label.setStyleSheet(RESULTS_LABEL_FILTER_STYLE)
        self.test_type_combo = QComboBox()
        self.test_type_combo.addItems(
            ["All", "Comparison Tests", "Benchmark Tests", "Validator Tests"]
        )
        self.test_type_combo.currentTextChanged.connect(self._filter_results)
        self.test_type_combo.setStyleSheet(RESULTS_COMBO_STYLE)

        # Date range filter
        date_label = QLabel("Date Range:")
        date_label.setStyleSheet(RESULTS_LABEL_FILTER_STYLE)
        self.date_filter = QComboBox()
        self.date_filter.addItems(
            ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"]
        )
        self.date_filter.currentTextChanged.connect(self._filter_results)
        self.date_filter.setStyleSheet(RESULTS_COMBO_STYLE)

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(RESULTS_BUTTON_STYLE)
        refresh_btn.clicked.connect(self._load_results)

        filters_row1.addWidget(type_label)
        filters_row1.addWidget(self.test_type_combo)
        filters_row1.addWidget(date_label)
        filters_row1.addWidget(self.date_filter)
        filters_row1.addWidget(refresh_btn)
        filters_row1.addStretch()

        # Second row: Search filters (Phase 4 Issue #12)
        filters_row2 = QHBoxLayout()
        filters_row2.setSpacing(16)

        # Project name search
        project_label = QLabel("Project:")
        project_label.setStyleSheet(RESULTS_LABEL_FILTER_STYLE)
        self.project_search = QLineEdit()
        self.project_search.setPlaceholderText("Search by project name...")
        self.project_search.setStyleSheet(RESULTS_COMBO_STYLE)
        self.project_search.returnPressed.connect(self._perform_search)

        # File name search
        file_label = QLabel("File:")
        file_label.setStyleSheet(RESULTS_LABEL_FILTER_STYLE)
        self.file_search = QLineEdit()
        self.file_search.setPlaceholderText("Search by file name...")
        self.file_search.setStyleSheet(RESULTS_COMBO_STYLE)
        self.file_search.returnPressed.connect(self._perform_search)

        # Status filter
        status_label = QLabel("Status:")
        status_label.setStyleSheet(RESULTS_LABEL_FILTER_STYLE)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Passed Only", "Failed Only"])
        self.status_combo.currentTextChanged.connect(self._perform_search)
        self.status_combo.setStyleSheet(RESULTS_COMBO_STYLE)

        # Search button
        search_btn = QPushButton("Search")
        search_btn.setStyleSheet(RESULTS_BUTTON_STYLE)
        search_btn.clicked.connect(self._perform_search)

        # Clear search button
        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(RESULTS_BUTTON_STYLE)
        clear_btn.clicked.connect(self._clear_search)

        filters_row2.addWidget(project_label)
        filters_row2.addWidget(self.project_search)
        filters_row2.addWidget(file_label)
        filters_row2.addWidget(self.file_search)
        filters_row2.addWidget(status_label)
        filters_row2.addWidget(self.status_combo)
        filters_row2.addWidget(search_btn)
        filters_row2.addWidget(clear_btn)
        filters_row2.addStretch()

        filters_main_layout.addLayout(filters_row1)
        filters_main_layout.addLayout(filters_row2)

        panel_layout.addWidget(filters_panel)

        # Create tabs for different views
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(RESULTS_TAB_WIDGET_STYLE)

        # Results table tab
        self.results_tab = self._create_results_table()
        self.tab_widget.addTab(self.results_tab, "Test Results")

        # Statistics tab
        self.stats_tab = self._create_statistics_view()
        self.tab_widget.addTab(self.stats_tab, "Statistics")

        panel_layout.addWidget(self.tab_widget)

        # Add inner panel to outer panel
        outer_layout.addWidget(main_panel)

        # Add outer panel to splitter
        self.splitter.addWidget(outer_panel)

        # Add splitter to main layout
        main_layout.addWidget(self.splitter)

    def _create_results_table(self):
        """Create the results table widget"""
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {MATERIAL_COLORS['surface_variant']};")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(10)  # Phase 4: Added Delete column
        self.results_table.setHorizontalHeaderLabels(
            [
                "Date",
                "Type",
                "File",
                "Tests",
                "Passed",
                "Failed",
                "Time (s)",
                "Success Rate",
                "View Details",
                "Delete",
            ]
        )

        # Configure table
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.itemSelectionChanged.connect(self._on_result_selected)

        # Style the table
        self.results_table.setStyleSheet(RESULTS_TABLE_STYLE)

        layout.addWidget(self.results_table)

        # Details panel
        details_label = QLabel("Test Details:")
        details_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)

        self.details_panel = QTextEdit()
        self.details_panel.setMaximumHeight(150)
        self.details_panel.setPlaceholderText(
            "Select a test result to view detailed information"
        )
        self.details_panel.setStyleSheet(RESULTS_TEXT_EDIT_STYLE)

        layout.addWidget(details_label)
        layout.addWidget(self.details_panel)

        return widget

    def _create_statistics_view(self):
        """Create the statistics view widget"""
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {MATERIAL_COLORS['surface_variant']};")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Statistics panels
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)

        # Overall stats card
        overall_card = QWidget()
        overall_card.setStyleSheet(RESULTS_CARD_STYLE)
        overall_layout = QVBoxLayout(overall_card)
        overall_layout.setContentsMargins(16, 16, 16, 16)
        overall_layout.setSpacing(12)

        # Card title
        overall_title = QLabel("Overall Statistics")
        overall_title.setStyleSheet(RESULTS_LABEL_TITLE_STYLE)
        overall_layout.addWidget(overall_title)

        self.total_tests_label = QLabel("Total Tests: 0")
        self.success_rate_label = QLabel("Success Rate: 0%")
        self.avg_time_label = QLabel("Average Time: 0s")

        # Style stat labels
        for label in [
            self.total_tests_label,
            self.success_rate_label,
            self.avg_time_label,
        ]:
            label.setStyleSheet(RESULTS_LABEL_STAT_STYLE)
            overall_layout.addWidget(label)

        # Phase 3 (Issue #36): Removed success rate progress bar
        # The text label already shows success rate percentage

        stats_layout.addWidget(overall_card)

        # Test type breakdown card
        breakdown_card = QWidget()
        breakdown_card.setStyleSheet(RESULTS_CARD_STYLE)
        breakdown_layout = QVBoxLayout(breakdown_card)
        breakdown_layout.setContentsMargins(16, 16, 16, 16)
        breakdown_layout.setSpacing(12)

        # Card title
        breakdown_title = QLabel("Test Type Breakdown")
        breakdown_title.setStyleSheet(RESULTS_LABEL_TITLE_STYLE)
        breakdown_layout.addWidget(breakdown_title)

        self.compare_tests_label = QLabel("Comparison Tests: 0")
        self.benchmark_tests_label = QLabel("Benchmark Tests: 0")
        self.validator_tests_label = QLabel("Validator Tests: 0")

        # Style breakdown labels
        for label in [
            self.compare_tests_label,
            self.benchmark_tests_label,
            self.validator_tests_label,
        ]:
            label.setStyleSheet(RESULTS_LABEL_STAT_STYLE)
            breakdown_layout.addWidget(label)

        breakdown_layout.addStretch()
        stats_layout.addWidget(breakdown_card)

        layout.addLayout(stats_layout)

        # Phase 3 (Issue #35): Removed Recent Activity card
        # This was redundant with the main Results table tab

        return widget

    def _load_results(self):
        """Load test results from database

        Phase 4 (Issue #10): Optimized to use SQL-based date filtering
        instead of Python post-processing for better performance.
        """
        # Get filter values
        test_type = self._get_test_type_filter()
        days_filter = self._get_days_filter()

        # Load results with SQL-based filtering
        results = self.db_manager.get_test_results(
            test_type=test_type,
            days=days_filter,  # Phase 4: Pass days to SQL query
            limit=100,
        )

        self._populate_results_table(results)
        self._update_statistics(results)

    def _get_test_type_filter(self):
        """Get the test type filter value"""
        type_text = self.test_type_combo.currentText()
        if type_text == "Comparison Tests":
            return "comparison"  # Phase 1: Using new standardized naming
        if type_text == "Benchmark Tests":
            return "benchmark"  # Phase 1: Using new standardized naming
        if type_text == "Validator Tests":
            return "validator"  # Phase 3 (Issue #18): Added validator support
        return None

    def _get_days_filter(self):
        """Get the days filter value"""
        filter_text = self.date_filter.currentText()
        if filter_text == "Last 7 Days":
            return 7
        if filter_text == "Last 30 Days":
            return 30
        if filter_text == "Last 90 Days":
            return 90
        return None

    def _get_status_filter(self):
        """Get the status filter value

        Phase 4 (Issue #12): Added status filtering support
        Returns: 'passed', 'failed', or None for all results
        """
        status_text = self.status_combo.currentText()
        if status_text == "Passed Only":
            return "passed"
        if status_text == "Failed Only":
            return "failed"
        return None

    def _perform_search(self):
        """Perform comprehensive search with all filters

        Phase 4 (Issue #12): Comprehensive search functionality
        combining test type, date range, project name, file name, and status filters.
        """
        # Get all filter values
        test_type = self._get_test_type_filter()
        days_filter = self._get_days_filter()
        project_name = self.project_search.text().strip() or None
        file_name = self.file_search.text().strip() or None
        status = self._get_status_filter()

        # Load results with all filters
        results = self.db_manager.get_test_results(
            test_type=test_type,
            project_name=project_name,
            days=days_filter,
            file_name=file_name,
            status=status,
            limit=100,
        )

        self._populate_results_table(results)
        self._update_statistics(results)

    def _clear_search(self):
        """Clear all search filters and reload

        Phase 4 (Issue #12): Clear search functionality
        """
        self.project_search.clear()
        self.file_search.clear()
        self.status_combo.setCurrentIndex(0)  # Reset to "All"
        self._load_results()

    def _populate_results_table(self, results: list):
        """Populate the results table with data"""
        self.results_table.setRowCount(len(results))

        for row, result in enumerate(results):
            # Format date
            date_str = datetime.fromisoformat(result.timestamp).strftime(
                "%Y-%m-%d %H:%M"
            )
            date_item = QTableWidgetItem(date_str)
            date_item.setData(
                1, result.id
            )  # Phase 4: Store result ID for export/delete
            self.results_table.setItem(row, 0, date_item)

            # Test type
            type_display = (
                "Comparison Test"
                if result.test_type in ["stress", "comparison"]
                else (
                    "Benchmark Test"
                    if result.test_type in ["tle", "benchmark"]
                    else "Validator Test"
                )
            )
            self.results_table.setItem(row, 1, QTableWidgetItem(type_display))

            # File name (extract from path)
            file_name = (
                result.file_path.split("/")[-1] if result.file_path else "Unknown"
            )
            if "\\" in file_name:  # Handle Windows paths
                file_name = file_name.split("\\")[-1]
            self.results_table.setItem(row, 2, QTableWidgetItem(file_name))

            # Test counts
            self.results_table.setItem(row, 3, QTableWidgetItem(str(result.test_count)))
            self.results_table.setItem(
                row, 4, QTableWidgetItem(str(result.passed_tests))
            )
            self.results_table.setItem(
                row, 5, QTableWidgetItem(str(result.failed_tests))
            )

            # Time
            self.results_table.setItem(
                row, 6, QTableWidgetItem(f"{result.total_time:.2f}")
            )

            # Success rate
            if result.test_count > 0:
                success_rate = (result.passed_tests / result.test_count) * 100
                self.results_table.setItem(
                    row, 7, QTableWidgetItem(f"{success_rate:.1f}%")
                )
            else:
                self.results_table.setItem(row, 7, QTableWidgetItem("N/A"))

            # View Details button
            detail_btn = QPushButton("View Details")
            detail_btn.setStyleSheet(RESULTS_BUTTON_STYLE)
            detail_btn.clicked.connect(
                lambda checked, r=result: self._show_detailed_view(r)
            )
            self.results_table.setCellWidget(row, 8, detail_btn)

            # Delete button (Phase 4 Issue #14)
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet(RESULTS_BUTTON_STYLE)
            delete_btn.clicked.connect(
                lambda checked, r_id=result.id: self._delete_selected_result(r_id)
            )
            self.results_table.setCellWidget(row, 9, delete_btn)

        # Store results for detail view
        self.current_results = results

    def _show_detailed_view(self, test_result):
        """Show detailed view for a specific test result

        Phase 5 (Issue #34): Integrates into parent window's display area
        following the same pattern as status views in comparator/validator/benchmarker
        """
        try:
            # Get parent window using stored reference (not self.parent() which returns splitter)
            parent_window = getattr(self, "results_window", None)

            if parent_window is None:
                raise AttributeError(
                    "Results window reference not set - widget not properly initialized"
                )

            if not hasattr(parent_window, "show_detailed_view"):
                parent_type = type(parent_window).__name__
                raise AttributeError(
                    f"Parent window (type: {parent_type}) does not have show_detailed_view method"
                )

            parent_window.show_detailed_view(test_result)

        except Exception as e:
            # Show error dialog instead of crashing
            error_msg = QMessageBox(self)
            error_msg.setIcon(QMessageBox.Icon.Critical)
            error_msg.setWindowTitle("Error Loading Details")
            error_msg.setText("Failed to load detailed test results")
            error_msg.setDetailedText(
                f"Error: {str(e)}\n\nTest Result ID: {getattr(test_result, 'id', 'Unknown')}"
            )
            error_msg.exec()

    def _delete_selected_result(self, result_id: int):
        """Delete a selected test result with confirmation

        Phase 4 (Issue #14): Delete functionality for individual test results

        Args:
            result_id: The ID of the test result to delete
        """
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this test result?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,  # Default to No for safety
        )

        if reply == QMessageBox.Yes:
            try:
                # Attempt deletion
                success = self.db_manager.delete_test_result(result_id)

                if success:
                    # Refresh the results table
                    self._load_results()
                    QMessageBox.information(
                        self, "Success", "Test result deleted successfully."
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Not Found",
                        "Test result not found. It may have already been deleted.",
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to delete test result:\n{str(e)}"
                )

    def _update_statistics(self, results: list):
        """Update the statistics view"""
        if not results:
            self.total_tests_label.setText("Total Tests: 0")
            self.success_rate_label.setText("Success Rate: 0%")
            self.avg_time_label.setText("Average Time: 0s")
            # Phase 3 (Issue #36): Removed success_progress.setValue(0)
            self.compare_tests_label.setText("Comparison Tests: 0")
            self.benchmark_tests_label.setText("Benchmark Tests: 0")
            self.validator_tests_label.setText("Validator Tests: 0")
            return

        # Calculate statistics
        total_tests = len(results)
        total_passed = sum(r.passed_tests for r in results)
        total_attempted = sum(r.test_count for r in results)
        avg_time = sum(r.total_time for r in results) / len(results) if results else 0

        success_rate = (
            (total_passed / total_attempted * 100) if total_attempted > 0 else 0
        )

        comparison_count = sum(1 for r in results if r.test_type == "comparison")
        benchmark_count = sum(1 for r in results if r.test_type == "benchmark")
        validator_count = sum(1 for r in results if r.test_type == "validator")

        # Update labels
        self.total_tests_label.setText(f"Total Tests: {total_tests}")
        self.success_rate_label.setText(f"Success Rate: {success_rate:.1f}%")
        self.avg_time_label.setText(f"Average Time: {avg_time:.2f}s")
        # Phase 3 (Issue #36): Removed success_progress.setValue(int(success_rate))
        self.compare_tests_label.setText(f"Comparison Tests: {comparison_count}")
        self.benchmark_tests_label.setText(f"Benchmark Tests: {benchmark_count}")
        self.validator_tests_label.setText(f"Validator Tests: {validator_count}")

        # Phase 3 (Issue #35): Removed _update_recent_activity call
        # Recent Activity card was removed as redundant

    # Phase 3 (Issue #35): Removed _update_recent_activity() method
    # Recent Activity table was removed as redundant with main Results table

    def _filter_results(self):
        """Handle filter changes"""
        self._load_results()

    def _on_result_selected(self):
        """Handle result selection in table"""
        selected_rows = self.results_table.selectionModel().selectedRows()
        if not selected_rows or not hasattr(self, "current_results"):
            self.details_panel.clear()
            return

        row = selected_rows[0].row()
        if row < len(self.current_results):
            result = self.current_results[row]

            # Display detailed information
            details = f"""
Test Result Details:
-------------------
Test Type: {result.test_type.upper()}
File: {result.file_path}
Timestamp: {result.timestamp}
Project: {result.project_name or 'Unknown'}

Test Summary:
- Total Tests: {result.test_count}
- Passed: {result.passed_tests}
- Failed: {result.failed_tests}
- Total Time: {result.total_time:.2f} seconds
- Success Rate: {(result.passed_tests/result.test_count*100):.1f}% if result.test_count > 0 else 'N/A'

"""

            # Add detailed test data if available
            if result.test_details:
                try:
                    details_data = json.loads(result.test_details)
                    details += "Test Details:\n"
                    for i, test_detail in enumerate(
                        details_data[:5], 1
                    ):  # Show first 5
                        details += f"Test {i}: {'PASSED' if test_detail.get('passed', False) else 'FAILED'}\n"
                    if len(details_data) > 5:
                        details += f"... and {len(details_data) - 5} more tests\n"
                except Exception:
                    details += "Test details: Available but could not parse\n"

            self.details_panel.setText(details)
