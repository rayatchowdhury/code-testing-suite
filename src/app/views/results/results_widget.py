from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                              QTableWidgetItem, QHeaderView, QPushButton, QLabel,
                              QComboBox, QDateEdit, QSpinBox, QTextEdit, QSplitter,
                              QTabWidget, QGroupBox, QProgressBar, QTabBar)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont
import json
from datetime import datetime, timedelta

from src.app.database import DatabaseManager, TestResult
from src.app.styles.style import MATERIAL_COLORS
from src.app.styles.components.code_editor_display_area import SPLITTER_STYLE, OUTER_PANEL_STYLE
from src.app.styles.components.results import (
    RESULTS_COMBO_STYLE, RESULTS_BUTTON_STYLE, RESULTS_TAB_WIDGET_STYLE,
    RESULTS_TABLE_STYLE, RESULTS_TABLE_SMALL_STYLE, RESULTS_TEXT_EDIT_STYLE,
    RESULTS_PROGRESS_BAR_STYLE, RESULTS_FILTERS_PANEL_STYLE, RESULTS_CARD_STYLE,
    RESULTS_LABEL_TITLE_STYLE, RESULTS_LABEL_FILTER_STYLE, RESULTS_LABEL_STAT_STYLE,
    RESULTS_LABEL_DETAILS_STYLE
)
from src.app.views.results.detailed_results_widget import DetailedResultsWidget

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
        main_panel.setStyleSheet(f"""
            background-color: {MATERIAL_COLORS['surface']};
        """)
        
        panel_layout = QVBoxLayout(main_panel)
        panel_layout.setContentsMargins(16, 16, 16, 16)
        panel_layout.setSpacing(16)

        # Filters section with Material Design styling
        filters_panel = QWidget()
        filters_panel.setStyleSheet(RESULTS_FILTERS_PANEL_STYLE)
        filters_layout = QHBoxLayout(filters_panel)
        filters_layout.setContentsMargins(16, 12, 16, 12)
        filters_layout.setSpacing(16)

        # Test type filter
        type_label = QLabel("Test Type:")
        type_label.setStyleSheet(RESULTS_LABEL_FILTER_STYLE)
        self.test_type_combo = QComboBox()
        self.test_type_combo.addItems(["All", "Stress Tests", "TLE Tests"])
        self.test_type_combo.currentTextChanged.connect(self._filter_results)
        self.test_type_combo.setStyleSheet(RESULTS_COMBO_STYLE)

        # Date range filter
        date_label = QLabel("Date Range:")
        date_label.setStyleSheet(RESULTS_LABEL_FILTER_STYLE)
        self.date_filter = QComboBox()
        self.date_filter.addItems(["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"])
        self.date_filter.currentTextChanged.connect(self._filter_results)
        self.date_filter.setStyleSheet(RESULTS_COMBO_STYLE)

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(RESULTS_BUTTON_STYLE)
        refresh_btn.clicked.connect(self._load_results)

        filters_layout.addWidget(type_label)
        filters_layout.addWidget(self.test_type_combo)
        filters_layout.addWidget(date_label)
        filters_layout.addWidget(self.date_filter)
        filters_layout.addWidget(refresh_btn)
        filters_layout.addStretch()

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
        self.results_table.setColumnCount(9)
        self.results_table.setHorizontalHeaderLabels([
            "Date", "Type", "File", "Tests", "Passed", "Failed", "Time (s)", "Success Rate", "View Details"
        ])
        
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
        self.details_panel.setPlaceholderText("Select a test result to view detailed information")
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
        for label in [self.total_tests_label, self.success_rate_label, self.avg_time_label]:
            label.setStyleSheet(RESULTS_LABEL_STAT_STYLE)
            overall_layout.addWidget(label)
        
        # Success rate progress bar
        progress_label = QLabel("Success Rate:")
        progress_label.setStyleSheet(f"color: {MATERIAL_COLORS['on_surface']}; font-weight: 500; margin-top: 8px;")
        overall_layout.addWidget(progress_label)
        
        self.success_progress = QProgressBar()
        self.success_progress.setRange(0, 100)
        self.success_progress.setStyleSheet(RESULTS_PROGRESS_BAR_STYLE)
        overall_layout.addWidget(self.success_progress)
        
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
        
        self.compare_tests_label = QLabel("Compare Tests: 0")
        self.benchmark_tests_label = QLabel("Benchmark Tests: 0")
        
        # Style breakdown labels
        for label in [self.compare_tests_label, self.benchmark_tests_label]:
            label.setStyleSheet(RESULTS_LABEL_STAT_STYLE)
            breakdown_layout.addWidget(label)
        
        breakdown_layout.addStretch()
        stats_layout.addWidget(breakdown_card)
        
        layout.addLayout(stats_layout)
        
        # Recent activity card
        recent_card = QWidget()
        recent_card.setStyleSheet(RESULTS_CARD_STYLE)
        recent_layout = QVBoxLayout(recent_card)
        recent_layout.setContentsMargins(16, 16, 16, 16)
        recent_layout.setSpacing(12)
        
        # Card title
        recent_title = QLabel("Recent Activity")
        recent_title.setStyleSheet(RESULTS_LABEL_TITLE_STYLE)
        recent_layout.addWidget(recent_title)
        
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(4)
        self.recent_table.setHorizontalHeaderLabels(["Date", "Type", "File", "Result"])
        self.recent_table.setMaximumHeight(200)
        self.recent_table.setStyleSheet(RESULTS_TABLE_SMALL_STYLE)
        
        recent_layout.addWidget(self.recent_table)
        layout.addWidget(recent_card)
        
        return widget
    
    def _load_results(self):
        """Load test results from database"""
        # Get filter values
        test_type = self._get_test_type_filter()
        days_filter = self._get_days_filter()
        
        # Load results
        results = self.db_manager.get_test_results(test_type=test_type, limit=100)
        
        # Apply date filter
        if days_filter:
            cutoff_date = datetime.now() - timedelta(days=days_filter)
            results = [r for r in results if datetime.fromisoformat(r.timestamp) >= cutoff_date]
        
        self._populate_results_table(results)
        self._update_statistics(results)
    
    def _get_test_type_filter(self):
        """Get the test type filter value"""
        type_text = self.test_type_combo.currentText()
        if type_text == "Stress Tests":
            return "stress"
        elif type_text == "TLE Tests":
            return "tle"
        return None
    
    def _get_days_filter(self):
        """Get the days filter value"""
        filter_text = self.date_filter.currentText()
        if filter_text == "Last 7 Days":
            return 7
        elif filter_text == "Last 30 Days":
            return 30
        elif filter_text == "Last 90 Days":
            return 90
        return None
    
    def _populate_results_table(self, results: list):
        """Populate the results table with data"""
        self.results_table.setRowCount(len(results))
        
        for row, result in enumerate(results):
            # Format date
            date_str = datetime.fromisoformat(result.timestamp).strftime("%Y-%m-%d %H:%M")
            self.results_table.setItem(row, 0, QTableWidgetItem(date_str))
            
            # Test type
            type_display = "Stress Test" if result.test_type == "stress" else "TLE Test"
            self.results_table.setItem(row, 1, QTableWidgetItem(type_display))
            
            # File name (extract from path)
            file_name = result.file_path.split('/')[-1] if result.file_path else "Unknown"
            if '\\' in file_name:  # Handle Windows paths
                file_name = file_name.split('\\')[-1]
            self.results_table.setItem(row, 2, QTableWidgetItem(file_name))
            
            # Test counts
            self.results_table.setItem(row, 3, QTableWidgetItem(str(result.test_count)))
            self.results_table.setItem(row, 4, QTableWidgetItem(str(result.passed_tests)))
            self.results_table.setItem(row, 5, QTableWidgetItem(str(result.failed_tests)))
            
            # Time
            self.results_table.setItem(row, 6, QTableWidgetItem(f"{result.total_time:.2f}"))
            
            # Success rate
            if result.test_count > 0:
                success_rate = (result.passed_tests / result.test_count) * 100
                self.results_table.setItem(row, 7, QTableWidgetItem(f"{success_rate:.1f}%"))
            else:
                self.results_table.setItem(row, 7, QTableWidgetItem("N/A"))
            
            # View Details button
            detail_btn = QPushButton("View Details")
            detail_btn.setStyleSheet(RESULTS_BUTTON_STYLE)
            detail_btn.clicked.connect(lambda checked, r=result: self._show_detailed_view(r))
            self.results_table.setCellWidget(row, 8, detail_btn)
        
        # Store results for detail view
        self.current_results = results
    
    def _show_detailed_view(self, test_result):
        """Show detailed view for a specific test result"""
        try:
            # Create the detailed view widget
            self.detailed_widget = DetailedResultsWidget(test_result)
            
            # Create a new tab for the detailed view
            detail_tab_index = self.tab_widget.addTab(self.detailed_widget, f"Details - {test_result.test_type.upper()}")
            self.tab_widget.setCurrentIndex(detail_tab_index)
            
            # Add a close button to the tab
            close_btn = QPushButton("×")
            close_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    font-size: 16px;
                    font-weight: bold;
                    color: #999;
                    padding: 2px 6px;
                    margin: 0px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                    border-radius: 3px;
                }
            """)
            close_btn.clicked.connect(lambda: self._close_detailed_view(detail_tab_index))
            
            # Add close button to tab bar
            self.tab_widget.tabBar().setTabButton(detail_tab_index, QTabBar.ButtonPosition.RightSide, close_btn)
            
        except Exception as e:
            # Show error dialog instead of crashing
            from PySide6.QtWidgets import QMessageBox
            error_msg = QMessageBox(self)
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.setWindowTitle("Error Loading Details")
            error_msg.setText("Failed to load detailed test results")
            error_msg.setDetailedText(f"Error: {str(e)}\n\nTest Result ID: {getattr(test_result, 'id', 'Unknown')}")
            error_msg.exec()
    
    def _close_detailed_view(self, tab_index):
        """Close the detailed view tab"""
        self.tab_widget.removeTab(tab_index)
    
    def _update_statistics(self, results: list):
        """Update the statistics view"""
        if not results:
            self.total_tests_label.setText("Total Tests: 0")
            self.success_rate_label.setText("Success Rate: 0%")
            self.avg_time_label.setText("Average Time: 0s")
            self.success_progress.setValue(0)
            self.compare_tests_label.setText("Compare Tests: 0")
            self.benchmark_tests_label.setText("Benchmark Tests: 0")
            return
        
        # Calculate statistics
        total_tests = len(results)
        total_passed = sum(r.passed_tests for r in results)
        total_attempted = sum(r.test_count for r in results)
        avg_time = sum(r.total_time for r in results) / len(results) if results else 0
        
        success_rate = (total_passed / total_attempted * 100) if total_attempted > 0 else 0
        
        compare_count = sum(1 for r in results if r.test_type == "compare")
        benchmark_count = sum(1 for r in results if r.test_type == "benchmark")
        
        # Update labels
        self.total_tests_label.setText(f"Total Tests: {total_tests}")
        self.success_rate_label.setText(f"Success Rate: {success_rate:.1f}%")
        self.avg_time_label.setText(f"Average Time: {avg_time:.2f}s")
        self.success_progress.setValue(int(success_rate))
        self.compare_tests_label.setText(f"Compare Tests: {compare_count}")
        self.benchmark_tests_label.setText(f"Benchmark Tests: {benchmark_count}")
        
        # Update recent activity table
        self._update_recent_activity(results[:10])  # Show last 10
    
    def _update_recent_activity(self, recent_results: list):
        """Update the recent activity table"""
        self.recent_table.setRowCount(len(recent_results))
        
        for row, result in enumerate(recent_results):
            date_str = datetime.fromisoformat(result.timestamp).strftime("%m-%d %H:%M")
            self.recent_table.setItem(row, 0, QTableWidgetItem(date_str))
            
            type_display = "Stress" if result.test_type == "stress" else "TLE"
            self.recent_table.setItem(row, 1, QTableWidgetItem(type_display))
            
            file_name = result.file_path.split('/')[-1] if result.file_path else "Unknown"
            self.recent_table.setItem(row, 2, QTableWidgetItem(file_name))
            
            if result.test_count > 0:
                success_rate = (result.passed_tests / result.test_count) * 100
                result_text = f"{result.passed_tests}/{result.test_count} ({success_rate:.0f}%)"
            else:
                result_text = "No tests"
            self.recent_table.setItem(row, 3, QTableWidgetItem(result_text))
    
    def _filter_results(self):
        """Handle filter changes"""
        self._load_results()
    
    def _on_result_selected(self):
        """Handle result selection in table"""
        selected_rows = self.results_table.selectionModel().selectedRows()
        if not selected_rows or not hasattr(self, 'current_results'):
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
                    for i, test_detail in enumerate(details_data[:5], 1):  # Show first 5
                        details += f"Test {i}: {'PASSED' if test_detail.get('passed', False) else 'FAILED'}\n"
                    if len(details_data) > 5:
                        details += f"... and {len(details_data) - 5} more tests\n"
                except:
                    details += "Test details: Available but could not parse\n"
            
            self.details_panel.setText(details)
