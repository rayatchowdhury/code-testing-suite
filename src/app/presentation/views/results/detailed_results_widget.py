from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                              QLabel, QScrollArea, QFrame, QTabWidget,
                              QTableWidget, QTableWidgetItem, QHeaderView,
                              QSplitter, QPushButton, QGroupBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor, QColor
import json
from datetime import datetime

from src.app.presentation.styles.components.results import (
    RESULTS_TEXT_EDIT_STYLE, RESULTS_CARD_STYLE, RESULTS_LABEL_TITLE_STYLE,
    RESULTS_LABEL_DETAILS_STYLE, RESULTS_TABLE_SMALL_STYLE, RESULTS_BUTTON_STYLE
)
from src.app.presentation.styles.style import MATERIAL_COLORS
from src.app.presentation.styles.helpers.inline_styles import (ERROR_LABEL_BOLD_STYLE, ERROR_TITLE_STYLE, 
                                           build_status_style, get_status_label_style)

class TestCaseDetailWidget(QWidget):
    """Widget to display detailed information about a single test case"""
    
    def __init__(self, test_case_data, parent=None):
        super().__init__(parent)
        self.test_case_data = test_case_data or {}
        try:
            self._setup_ui()
        except Exception as e:
            self._setup_error_ui(str(e))
    
    def _setup_error_ui(self, error_message):
        """Setup UI when there's an error in test case data"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        error_label = QLabel(f"Error loading test case data: {error_message}")
        error_label.setStyleSheet(ERROR_LABEL_BOLD_STYLE)
        layout.addWidget(error_label)
        
        if self.test_case_data:
            data_label = QLabel(f"Raw data: {str(self.test_case_data)[:200]}...")
            data_label.setWordWrap(True)
            layout.addWidget(data_label)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Test case header
        header = QLabel(f"Test Case #{self.test_case_data.get('test_number', 'Unknown')}")
        header.setStyleSheet(RESULTS_LABEL_TITLE_STYLE)
        layout.addWidget(header)
        
        # Status indicator
        status = "✅ PASSED" if self.test_case_data.get('passed', False) else "❌ FAILED"
        status_label = QLabel(status)
        status_color = MATERIAL_COLORS['primary'] if self.test_case_data.get('passed', False) else MATERIAL_COLORS['error']
        status_label.setStyleSheet(get_status_label_style(status_color, 'bold', '14px'))
        layout.addWidget(status_label)
        
        # Execution details
        if 'execution_time' in self.test_case_data:
            time_label = QLabel(f"Execution Time: {self.test_case_data['execution_time']:.4f}s")
            time_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
            layout.addWidget(time_label)
        
        # Create tabs for different views
        tab_widget = QTabWidget()
        
        # Input/Output tab
        io_tab = self._create_io_tab()
        tab_widget.addTab(io_tab, "Input/Output")
        
        # Mismatch Analysis tab (only for failed tests)
        if not self.test_case_data.get('passed', False) and 'mismatch_analysis' in self.test_case_data:
            mismatch_tab = self._create_mismatch_tab()
            tab_widget.addTab(mismatch_tab, "Mismatch Analysis")
        
        layout.addWidget(tab_widget)
    
    def _create_io_tab(self):
        """Create input/output comparison tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        try:
            # Input section
            if 'input' in self.test_case_data and self.test_case_data['input']:
                input_label = QLabel("Input:")
                input_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
                layout.addWidget(input_label)
                
                input_text = QTextEdit()
                input_text.setPlainText(str(self.test_case_data['input']))
                input_text.setMaximumHeight(150)
                input_text.setReadOnly(True)
                input_text.setStyleSheet(RESULTS_TEXT_EDIT_STYLE)
                layout.addWidget(input_text)
        except Exception as e:
            error_label = QLabel(f"Error loading input: {str(e)}")
            error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
            layout.addWidget(error_label)
        
        try:
            # Output comparison for failed tests
            if not self.test_case_data.get('passed', False):
                # Expected output
                if 'correct_output' in self.test_case_data and self.test_case_data['correct_output']:
                    expected_label = QLabel("Expected Output:")
                    expected_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
                    layout.addWidget(expected_label)
                    
                    expected_text = QTextEdit()
                    expected_text.setPlainText(str(self.test_case_data['correct_output']))
                    expected_text.setMaximumHeight(150)
                    expected_text.setReadOnly(True)
                    expected_text.setStyleSheet(RESULTS_TEXT_EDIT_STYLE)
                    layout.addWidget(expected_text)
                
                # Actual output
                if 'test_output' in self.test_case_data:
                    actual_label = QLabel("Actual Output:")
                    actual_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
                    layout.addWidget(actual_label)
                    
                    actual_text = QTextEdit()
                    actual_text.setPlainText(str(self.test_case_data.get('test_output', '')))
                    actual_text.setMaximumHeight(150)
                    actual_text.setReadOnly(True)
                    actual_text.setStyleSheet(RESULTS_TEXT_EDIT_STYLE)
                    layout.addWidget(actual_text)
            else:
                # For passed tests, just show output
                output_data = self.test_case_data.get('test_output') or self.test_case_data.get('output', '')
                if output_data:
                    output_label = QLabel("Output:")
                    output_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
                    layout.addWidget(output_label)
                    
                    output_text = QTextEdit()
                    output_text.setPlainText(str(output_data))
                    output_text.setMaximumHeight(150)
                    output_text.setReadOnly(True)
                    output_text.setStyleSheet(RESULTS_TEXT_EDIT_STYLE)
                    layout.addWidget(output_text)
        except Exception as e:
            error_label = QLabel(f"Error loading output: {str(e)}")
            error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
            layout.addWidget(error_label)
        
        if layout.count() == 0:
            no_data_label = QLabel("No input/output data available")
            no_data_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
            layout.addWidget(no_data_label)
        
        return widget
    
    def _create_mismatch_tab(self):
        """Create detailed mismatch analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        try:
            mismatch_data = self.test_case_data.get('mismatch_analysis', {})
            
            # Handle different data types for mismatch_analysis
            if isinstance(mismatch_data, str):
                try:
                    mismatch_data = json.loads(mismatch_data)
                except (json.JSONDecodeError, TypeError):
                    mismatch_data = {}
            elif isinstance(mismatch_data, dict):
                # Already a dictionary, use as-is
                pass
            else:
                # Unknown type, reset to empty dict
                mismatch_data = {}
            
            if not isinstance(mismatch_data, dict):
                mismatch_data = {}
            
            # Summary statistics
            if 'summary' in mismatch_data and isinstance(mismatch_data['summary'], dict):
                summary = mismatch_data['summary']
                stats_widget = QWidget()
                stats_widget.setStyleSheet(RESULTS_CARD_STYLE)
                stats_layout = QVBoxLayout(stats_widget)
                stats_layout.setContentsMargins(12, 12, 12, 12)
                
                stats_title = QLabel("Mismatch Summary")
                stats_title.setStyleSheet(RESULTS_LABEL_TITLE_STYLE)
                stats_layout.addWidget(stats_title)
                
                stats_info = []
                try:
                    stats_info.append(f"Character differences: {summary.get('total_char_differences', 0)}")
                    stats_info.append(f"Line differences: {summary.get('total_line_differences', 0)}")
                    stats_info.append(f"Expected length: {summary.get('expected_length', 0)} chars")
                    stats_info.append(f"Actual length: {summary.get('actual_length', 0)} chars")
                    
                    for info in stats_info:
                        info_label = QLabel(info)
                        info_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
                        stats_layout.addWidget(info_label)
                except Exception as e:
                    error_label = QLabel(f"Error displaying summary: {str(e)}")
                    error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
                    stats_layout.addWidget(error_label)
                
                layout.addWidget(stats_widget)
            
            # Line differences table
            if 'line_differences' in mismatch_data and isinstance(mismatch_data['line_differences'], list) and mismatch_data['line_differences']:
                try:
                    line_diff_label = QLabel("Line-by-Line Differences:")
                    line_diff_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
                    layout.addWidget(line_diff_label)
                    
                    diff_table = QTableWidget()
                    diff_table.setColumnCount(4)
                    diff_table.setHorizontalHeaderLabels(["Line", "Type", "Expected", "Actual"])
                    diff_table.setStyleSheet(RESULTS_TABLE_SMALL_STYLE)
                    
                    line_diffs = mismatch_data['line_differences'][:50]  # Limit to 50 differences
                    diff_table.setRowCount(len(line_diffs))
                    
                    for row, diff in enumerate(line_diffs):
                        if isinstance(diff, dict):
                            diff_table.setItem(row, 0, QTableWidgetItem(str(diff.get('line_number', ''))))
                            diff_table.setItem(row, 1, QTableWidgetItem(str(diff.get('type', ''))))
                            diff_table.setItem(row, 2, QTableWidgetItem(str(diff.get('expected', ''))))
                            diff_table.setItem(row, 3, QTableWidgetItem(str(diff.get('actual', ''))))
                        else:
                            diff_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                            diff_table.setItem(row, 1, QTableWidgetItem("Unknown"))
                            diff_table.setItem(row, 2, QTableWidgetItem(str(diff)))
                            diff_table.setItem(row, 3, QTableWidgetItem(""))
                    
                    diff_table.resizeColumnsToContents()
                    diff_table.setMaximumHeight(200)
                    layout.addWidget(diff_table)
                    
                    if len(mismatch_data['line_differences']) > 50:
                        note_label = QLabel(f"Showing first 50 of {len(mismatch_data['line_differences'])} differences")
                        note_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
                        layout.addWidget(note_label)
                        
                except Exception as e:
                    error_label = QLabel(f"Error displaying line differences: {str(e)}")
                    error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
                    layout.addWidget(error_label)
            
            # Unified diff view
            if 'unified_diff' in mismatch_data and mismatch_data['unified_diff']:
                try:
                    diff_label = QLabel("Unified Diff:")
                    diff_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
                    layout.addWidget(diff_label)
                    
                    diff_text = QTextEdit()
                    if isinstance(mismatch_data['unified_diff'], list):
                        diff_content = '\n'.join(str(line) for line in mismatch_data['unified_diff'])
                    else:
                        diff_content = str(mismatch_data['unified_diff'])
                    
                    diff_text.setPlainText(diff_content)
                    diff_text.setMaximumHeight(200)
                    diff_text.setReadOnly(True)
                    diff_text.setStyleSheet(RESULTS_TEXT_EDIT_STYLE)
                    layout.addWidget(diff_text)
                except Exception as e:
                    error_label = QLabel(f"Error displaying unified diff: {str(e)}")
                    error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
                    layout.addWidget(error_label)
            
            # If no mismatch data is available
            if layout.count() == 0:
                no_data_label = QLabel("No mismatch analysis data available")
                no_data_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
                layout.addWidget(no_data_label)
                
        except Exception as e:
            error_label = QLabel(f"Error creating mismatch analysis: {str(e)}")
            error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
            layout.addWidget(error_label)
        
        return widget


class FilesSnapshotWidget(QWidget):
    """Widget to display all files that were part of the test"""
    
    def __init__(self, files_data, parent=None):
        super().__init__(parent)
        self.files_data = files_data or {}
        try:
            self._setup_ui()
        except Exception as e:
            self._setup_error_ui(str(e))
    
    def _setup_error_ui(self, error_message):
        """Setup UI when there's an error in files data"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        error_label = QLabel(f"Error loading files data: {error_message}")
        error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']}; font-weight: bold;")
        layout.addWidget(error_label)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        try:
            # Title
            title = QLabel("Code Files Snapshot")
            title.setStyleSheet(RESULTS_LABEL_TITLE_STYLE)
            layout.addWidget(title)
            
            # Create tabs for different files
            tab_widget = QTabWidget()
            
            # Known file types
            file_mappings = {
                'generator_code': 'Generator',
                'correct_code': 'Correct Solution',
                'test_code': 'Test Solution'
            }
            
            tabs_added = 0
            
            for attr_name, display_name in file_mappings.items():
                try:
                    content = ''
                    if hasattr(self.files_data, attr_name):
                        content = getattr(self.files_data, attr_name, '')
                    elif isinstance(self.files_data, dict):
                        content = self.files_data.get(attr_name, '')
                    
                    if content:
                        tab = self._create_code_tab(content)
                        tab_widget.addTab(tab, display_name)
                        tabs_added += 1
                except Exception as e:
                    error_tab = QWidget()
                    error_layout = QVBoxLayout(error_tab)
                    error_label = QLabel(f"Error loading {display_name}: {str(e)}")
                    error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
                    error_layout.addWidget(error_label)
                    tab_widget.addTab(error_tab, f"{display_name} (Error)")
                    tabs_added += 1
            
            # Additional files
            try:
                additional_files = {}
                if hasattr(self.files_data, 'additional_files') and self.files_data.additional_files:
                    additional_files = self.files_data.additional_files
                elif isinstance(self.files_data, dict) and 'additional_files' in self.files_data:
                    additional_files = self.files_data['additional_files']
                
                if isinstance(additional_files, dict):
                    for filename, content in additional_files.items():
                        try:
                            tab = self._create_code_tab(content)
                            tab_widget.addTab(tab, str(filename))
                            tabs_added += 1
                        except Exception as e:
                            error_tab = QWidget()
                            error_layout = QVBoxLayout(error_tab)
                            error_label = QLabel(f"Error loading {filename}: {str(e)}")
                            error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
                            error_layout.addWidget(error_label)
                            tab_widget.addTab(error_tab, f"{filename} (Error)")
                            tabs_added += 1
            except Exception as e:
                error_tab = QWidget()
                error_layout = QVBoxLayout(error_tab)
                error_label = QLabel(f"Error loading additional files: {str(e)}")
                error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
                error_layout.addWidget(error_label)
                tab_widget.addTab(error_tab, "Additional Files (Error)")
                tabs_added += 1
            
            if tabs_added > 0:
                layout.addWidget(tab_widget)
            else:
                no_files_label = QLabel("No code files available in snapshot")
                no_files_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
                layout.addWidget(no_files_label)
                
        except Exception as e:
            error_label = QLabel(f"Error setting up files UI: {str(e)}")
            error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
            layout.addWidget(error_label)
    
    def _create_code_tab(self, code_content):
        """Create a tab with syntax-highlighted code"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        
        try:
            code_edit = QTextEdit()
            
            # Ensure code content is a string
            if code_content is None:
                code_content = "No content available"
            elif not isinstance(code_content, str):
                code_content = str(code_content)
            
            code_edit.setPlainText(code_content)
            code_edit.setReadOnly(True)
            code_edit.setStyleSheet(RESULTS_TEXT_EDIT_STYLE)
            
            # Set monospace font
            font = QFont("Consolas", 10)
            font.setStyleHint(QFont.Monospace)
            code_edit.setFont(font)
            
            layout.addWidget(code_edit)
        except Exception as e:
            error_label = QLabel(f"Error displaying code: {str(e)}")
            error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
            layout.addWidget(error_label)
        
        return widget


class DetailedResultsWidget(QWidget):
    """Comprehensive results viewer with all test details"""
    
    def __init__(self, test_result, parent=None):
        super().__init__(parent)
        self.test_result = test_result
        try:
            self._setup_ui()
            self._load_data()
        except Exception as e:
            self._setup_error_ui(str(e))
    
    def _setup_error_ui(self, error_message):
        """Setup UI when there's a critical error"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        error_title = QLabel("❌ Error Loading Detailed Results")
        error_title.setStyleSheet(ERROR_TITLE_STYLE)
        layout.addWidget(error_title)
        
        error_label = QLabel(f"Failed to load detailed test results: {error_message}")
        error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
        error_label.setWordWrap(True)
        layout.addWidget(error_label)
        
        if self.test_result:
            info_label = QLabel(f"Test Result ID: {getattr(self.test_result, 'id', 'Unknown')}\n"
                               f"Test Type: {getattr(self.test_result, 'test_type', 'Unknown')}")
            info_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
            layout.addWidget(info_label)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create main tabs
        self.main_tabs = QTabWidget()
        
        # Overview tab
        self.overview_tab = self._create_overview_tab()
        self.main_tabs.addTab(self.overview_tab, "Overview")
        
        # Test Cases tab
        self.test_cases_tab = self._create_test_cases_tab()
        self.main_tabs.addTab(self.test_cases_tab, "Test Cases")
        
        # Files tab
        self.files_tab = self._create_files_tab()
        self.main_tabs.addTab(self.files_tab, "Code Files")
        
        # Analysis tab
        self.analysis_tab = self._create_analysis_tab()
        self.main_tabs.addTab(self.analysis_tab, "Analysis")
        
        layout.addWidget(self.main_tabs)
    
    def _create_overview_tab(self):
        """Create overview tab with summary information"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Test summary card
        summary_card = QWidget()
        summary_card.setStyleSheet(RESULTS_CARD_STYLE)
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(16, 16, 16, 16)
        summary_layout.setSpacing(8)
        
        # Title
        title = QLabel(f"{self.test_result.test_type.upper()} Test Results")
        title.setStyleSheet(RESULTS_LABEL_TITLE_STYLE)
        summary_layout.addWidget(title)
        
        # Basic stats with error handling
        stats = []
        
        try:
            stats.append(f"Test Type: {self.test_result.test_type}")
            stats.append(f"Total Tests: {self.test_result.test_count}")
            stats.append(f"Passed: {self.test_result.passed_tests}")
            stats.append(f"Failed: {self.test_result.failed_tests}")
            
            # Safe division for success rate
            if self.test_result.test_count > 0:
                success_rate = (self.test_result.passed_tests / self.test_result.test_count) * 100
                stats.append(f"Success Rate: {success_rate:.1f}%")
            else:
                stats.append("Success Rate: N/A")
            
            stats.append(f"Total Time: {self.test_result.total_time:.2f}s")
            stats.append(f"Project: {self.test_result.project_name or 'Unknown'}")
            
            # Safe timestamp parsing
            try:
                if self.test_result.timestamp:
                    formatted_date = datetime.fromisoformat(self.test_result.timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    stats.append(f"Date: {formatted_date}")
                else:
                    stats.append("Date: Unknown")
            except (ValueError, AttributeError) as e:
                stats.append(f"Date: Invalid ({self.test_result.timestamp})")
                
        except Exception as e:
            stats = [f"Error loading test statistics: {str(e)}"]
        
        for stat in stats:
            stat_label = QLabel(stat)
            stat_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
            summary_layout.addWidget(stat_label)
        
        layout.addWidget(summary_card)
        layout.addStretch()
        
        return widget
    
    def _create_test_cases_tab(self):
        """Create tab with detailed test case information"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # This will be populated in _load_data
        self.test_cases_scroll = QScrollArea()
        self.test_cases_scroll.setWidgetResizable(True)
        self.test_cases_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        layout.addWidget(self.test_cases_scroll)
        return widget
    
    def _create_files_tab(self):
        """Create tab with code files snapshot"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # This will be populated in _load_data
        self.files_widget_container = widget
        self.files_widget_layout = layout  # Store reference to layout
        return widget
    
    def _create_analysis_tab(self):
        """Create tab with mismatch analysis and insights"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # This will be populated in _load_data
        self.analysis_container = layout
        return widget
    
    def _load_data(self):
        """Load and display the detailed test data"""
        try:
            # Parse test details
            test_details = []
            if self.test_result.test_details:
                try:
                    test_details = json.loads(self.test_result.test_details)
                    if not isinstance(test_details, list):
                        test_details = []
                except (json.JSONDecodeError, TypeError) as e:
                    error_label = QLabel(f"Error parsing test details: {str(e)}")
                    error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
                    self.analysis_container.addWidget(error_label)
                    test_details = []
            
            # Load test cases
            self._load_test_cases(test_details)
            
            # Load files snapshot
            if self.test_result.files_snapshot:
                try:
                    files_data = json.loads(self.test_result.files_snapshot)
                    files_widget = FilesSnapshotWidget(files_data)
                    self.files_widget_layout.addWidget(files_widget)
                except (json.JSONDecodeError, TypeError) as e:
                    error_label = QLabel(f"Error loading files snapshot: {str(e)}")
                    error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
                    self.files_widget_layout.addWidget(error_label)
                except Exception as e:
                    error_label = QLabel(f"Error creating files widget: {str(e)}")
                    error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
                    self.files_widget_layout.addWidget(error_label)
            
            # Load analysis
            if self.test_result.mismatch_analysis:
                try:
                    analysis_data = json.loads(self.test_result.mismatch_analysis)
                    self._load_analysis(analysis_data)
                except (json.JSONDecodeError, TypeError) as e:
                    error_label = QLabel(f"Error parsing mismatch analysis: {str(e)}")
                    error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
                    self.analysis_container.addWidget(error_label)
                except Exception as e:
                    error_label = QLabel(f"Error loading analysis: {str(e)}")
                    error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
                    self.analysis_container.addWidget(error_label)
                
        except Exception as e:
            error_label = QLabel(f"Critical error loading detailed data: {str(e)}")
            error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']}; font-weight: bold;")
            self.analysis_container.addWidget(error_label)
    
    def _load_test_cases(self, test_details):
        """Load individual test case widgets"""
        try:
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setSpacing(8)
            
            if not isinstance(test_details, list):
                test_details = []
            
            if not test_details:
                no_data_label = QLabel("No test case details available")
                no_data_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
                layout.addWidget(no_data_label)
            else:
                for i, test_case in enumerate(test_details):
                    try:
                        test_widget = TestCaseDetailWidget(test_case)
                        test_widget.setStyleSheet(RESULTS_CARD_STYLE)
                        layout.addWidget(test_widget)
                    except Exception as e:
                        error_widget = QWidget()
                        error_widget.setStyleSheet(RESULTS_CARD_STYLE)
                        error_layout = QVBoxLayout(error_widget)
                        error_layout.setContentsMargins(16, 16, 16, 16)
                        
                        error_header = QLabel(f"Test Case #{i+1} - Error")
                        error_header.setStyleSheet(RESULTS_LABEL_TITLE_STYLE)
                        error_layout.addWidget(error_header)
                        
                        error_label = QLabel(f"Error loading test case: {str(e)}")
                        error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
                        error_layout.addWidget(error_label)
                        
                        layout.addWidget(error_widget)
            
            layout.addStretch()
            self.test_cases_scroll.setWidget(container)
            
        except Exception as e:
            error_container = QWidget()
            error_layout = QVBoxLayout(error_container)
            error_label = QLabel(f"Error setting up test cases: {str(e)}")
            error_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")
            error_layout.addWidget(error_label)
            self.test_cases_scroll.setWidget(error_container)
    
    def _load_analysis(self, analysis_data):
        """Load analysis and insights"""
        if self.test_result.test_type == "stress":
            self._load_stress_analysis(analysis_data)
        elif self.test_result.test_type == "tle":
            self._load_tle_analysis(analysis_data)
    
    def _load_stress_analysis(self, analysis_data):
        """Load stress test specific analysis"""
        analysis_card = QWidget()
        analysis_card.setStyleSheet(RESULTS_CARD_STYLE)
        layout = QVBoxLayout(analysis_card)
        layout.setContentsMargins(16, 16, 16, 16)
        
        title = QLabel("Stress Test Analysis")
        title.setStyleSheet(RESULTS_LABEL_TITLE_STYLE)
        layout.addWidget(title)
        
        # Failed tests summary
        if 'failed_tests' in analysis_data:
            failed_count = len(analysis_data['failed_tests'])
            if failed_count > 0:
                summary_label = QLabel(f"Found {failed_count} failed test cases with detailed mismatch analysis")
                summary_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
                layout.addWidget(summary_label)
        
        self.analysis_container.addWidget(analysis_card)
    
    def _load_tle_analysis(self, analysis_data):
        """Load TLE test specific analysis"""
        analysis_card = QWidget()
        analysis_card.setStyleSheet(RESULTS_CARD_STYLE)
        layout = QVBoxLayout(analysis_card)
        layout.setContentsMargins(16, 16, 16, 16)
        
        title = QLabel("Performance Analysis")
        title.setStyleSheet(RESULTS_LABEL_TITLE_STYLE)
        layout.addWidget(title)
        
        # Performance summary
        if 'performance_summary' in analysis_data:
            perf = analysis_data['performance_summary']
            
            if perf.get('average_time'):
                avg_label = QLabel(f"Average Execution Time: {perf['average_time']:.4f}s")
                avg_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
                layout.addWidget(avg_label)
            
            if perf.get('fastest_test'):
                fast_label = QLabel(f"Fastest Test: {perf['fastest_test']:.4f}s")
                fast_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
                layout.addWidget(fast_label)
            
            if perf.get('slowest_test'):
                slow_label = QLabel(f"Slowest Test: {perf['slowest_test']:.4f}s")
                slow_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
                layout.addWidget(slow_label)
        
        # Time limit info
        if 'time_limit' in analysis_data:
            limit_label = QLabel(f"Time Limit: {analysis_data['time_limit']}s")
            limit_label.setStyleSheet(RESULTS_LABEL_DETAILS_STYLE)
            layout.addWidget(limit_label)
        
        self.analysis_container.addWidget(analysis_card)
