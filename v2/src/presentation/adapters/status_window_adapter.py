# TODO: Create status window adapter implementing domain interfaces
"""
Status Window Adapter

Qt implementation of status view interfaces from domain layer.
Breaks the circular dependency from tools→views by implementing observer patterns.
"""
from typing import Optional, Protocol

try:
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
        QProgressBar, QTextEdit, QPushButton, QFrame
    )
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QFont
    HAS_QT = True
except ImportError:
    HAS_QT = False
    class QDialog: pass
    class QTimer: pass

from domain.services.status_view import CompilationStatusView, StressTestStatusView
from domain.models.compilation import CompilationStatus, TestCase
from infrastructure.theming.theme_service import ThemeService

class CompilationStatusWindowAdapter:
    """
    Qt adapter implementing CompilationStatusView interface.
    
    ASSUMPTION: Replaces v1/views/stress_tester/compilation_status_window.py
    but implements the domain interface to break circular dependencies.
    """
    
    def __init__(self, theme_service: ThemeService, parent=None):
        if not HAS_QT:
            raise RuntimeError("Qt is required for CompilationStatusWindowAdapter")
        
        self.theme_service = theme_service
        self.parent = parent
        self._dialog: Optional[QDialog] = None
        self._status_labels = {}
        self._progress_bar: Optional[QProgressBar] = None
        self._output_text: Optional[QTextEdit] = None
    
    def show(self) -> None:
        """Show the status window"""
        if self._dialog is None:
            self._create_dialog()
        self._dialog.show()
    
    def hide(self) -> None:
        """Hide the status window"""
        if self._dialog:
            self._dialog.hide()
    
    def close(self) -> None:
        """Close the status window"""
        if self._dialog:
            self._dialog.close()
            self._dialog = None
    
    def update_file_status(self, file_name: str, status: CompilationStatus) -> None:
        """Update status for a specific file"""
        if file_name not in self._status_labels:
            return
        
        label = self._status_labels[file_name]
        palette = self.theme_service.get_current_palette()
        
        if status == CompilationStatus.SUCCESS:
            label.setText(f"✅ {file_name}")
            label.setStyleSheet(f"color: {palette.primary};")
        elif status == CompilationStatus.FAILED:
            label.setText(f"❌ {file_name}")
            label.setStyleSheet(f"color: {palette.error};")
        elif status == CompilationStatus.IN_PROGRESS:
            label.setText(f"⚙️ {file_name}")
            label.setStyleSheet(f"color: {palette.secondary};")
        else:
            label.setText(f"⏳ {file_name}")
            label.setStyleSheet(f"color: {palette.text_secondary};")
    
    def show_compilation_output(self, file_name: str, output: str, is_error: bool = False) -> None:
        """Show compilation output for a file"""
        if self._output_text:
            palette = self.theme_service.get_current_palette()
            color = palette.error if is_error else palette.text_primary
            
            self._output_text.append(f"<div style='color: {color};'><b>{file_name}:</b></div>")
            self._output_text.append(f"<div style='color: {color};'>{output}</div>")
            self._output_text.append("<br>")
    
    def show_final_result(self, success: bool, message: str) -> None:
        """Show final compilation result"""
        if self._output_text:
            palette = self.theme_service.get_current_palette()
            color = palette.primary if success else palette.error
            icon = "🎉" if success else "💥"
            
            self._output_text.append(f"<div style='color: {color}; font-weight: bold;'>{icon} {message}</div>")
    
    def _create_dialog(self) -> None:
        """Create the status dialog"""
        self._dialog = QDialog(self.parent)
        self._dialog.setWindowTitle("Compilation Status")
        self._dialog.setFixedSize(500, 400)
        self._dialog.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        # Apply theme
        self._dialog.setStyleSheet(self.theme_service.get_dialog_style())
        
        layout = QVBoxLayout(self._dialog)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("Compilation Progress")
        title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {self.theme_service.get_color('primary')};
            margin-bottom: 8px;
        """)
        layout.addWidget(title)
        
        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {self.theme_service.get_color('outline')};
                border-radius: 4px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {self.theme_service.get_color('primary')};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self._progress_bar)
        
        # File status frame
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel)
        status_layout = QVBoxLayout(status_frame)
        
        # Add some example files (in real implementation, these would be dynamic)
        for file_name in ["generator.cpp", "solution.cpp"]:
            label = QLabel(f"⏳ {file_name}")
            label.setStyleSheet(f"color: {self.theme_service.get_color('text_secondary')};")
            self._status_labels[file_name] = label
            status_layout.addWidget(label)
        
        layout.addWidget(status_frame)
        
        # Output text
        self._output_text = QTextEdit()
        self._output_text.setReadOnly(True)
        self._output_text.setMaximumHeight(150)
        self._output_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.theme_service.get_color('surface_dim')};
                border: 1px solid {self.theme_service.get_color('outline')};
                border-radius: 4px;
                padding: 8px;
                font-family: 'Courier New', monospace;
            }}
        """)
        layout.addWidget(self._output_text)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(self.theme_service.get_button_style("secondary"))
        close_btn.clicked.connect(self.close)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

class StressTestStatusWindowAdapter:
    """
    Qt adapter implementing StressTestStatusView interface.
    
    ASSUMPTION: Replaces v1/views/stress_tester/stress_test_status_window.py
    """
    
    def __init__(self, theme_service: ThemeService, parent=None):
        if not HAS_QT:
            raise RuntimeError("Qt is required for StressTestStatusWindowAdapter")
        
        self.theme_service = theme_service
        self.parent = parent
        self._dialog: Optional[QDialog] = None
        self._current_test_label: Optional[QLabel] = None
        self._progress_bar: Optional[QProgressBar] = None
        self._results_text: Optional[QTextEdit] = None
        self._passed_count = 0
        self._total_count = 0
    
    def show(self) -> None:
        """Show the status window"""
        if self._dialog is None:
            self._create_dialog()
        self._dialog.show()
    
    def hide(self) -> None:
        """Hide the status window"""
        if self._dialog:
            self._dialog.hide()
    
    def close(self) -> None:
        """Close the status window"""
        if self._dialog:
            self._dialog.close()
            self._dialog = None
    
    def show_test_running(self, test_number: int, total_tests: int) -> None:
        """Show that a test is currently running"""
        self._total_count = total_tests
        
        if self._current_test_label:
            self._current_test_label.setText(f"Running test {test_number} of {total_tests}...")
        
        if self._progress_bar:
            self._progress_bar.setMaximum(total_tests)
            self._progress_bar.setValue(test_number - 1)
    
    def show_test_complete(self, test_case: TestCase) -> None:
        """Show completion of a single test"""
        if test_case.result.value == "passed":
            self._passed_count += 1
        
        if self._results_text:
            palette = self.theme_service.get_current_palette()
            
            if test_case.result.value == "passed":
                color = palette.primary
                icon = "✅"
            else:
                color = palette.error
                icon = "❌"
            
            self._results_text.append(
                f"<div style='color: {color};'>{icon} Test {test_case.test_number}: "
                f"{test_case.result.value.upper()} ({test_case.execution_time:.3f}s)</div>"
            )
        
        # Update progress
        if self._progress_bar:
            self._progress_bar.setValue(test_case.test_number)
    
    def show_all_passed(self, all_passed: bool) -> None:
        """Show final result of all tests"""
        if self._current_test_label:
            if all_passed:
                self._current_test_label.setText("🎉 All tests passed!")
                self._current_test_label.setStyleSheet(f"color: {self.theme_service.get_color('primary')};")
            else:
                self._current_test_label.setText(f"💥 {self._passed_count}/{self._total_count} tests passed")
                self._current_test_label.setStyleSheet(f"color: {self.theme_service.get_color('error')};")
    
    def update_progress(self, completed: int, total: int) -> None:
        """Update overall progress"""
        if self._progress_bar:
            self._progress_bar.setMaximum(total)
            self._progress_bar.setValue(completed)
    
    def _create_dialog(self) -> None:
        """Create the stress test status dialog"""
        self._dialog = QDialog(self.parent)
        self._dialog.setWindowTitle("Stress Test Status")
        self._dialog.setFixedSize(600, 450)
        self._dialog.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        # Apply theme
        self._dialog.setStyleSheet(self.theme_service.get_dialog_style())
        
        layout = QVBoxLayout(self._dialog)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("Stress Testing Progress")
        title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {self.theme_service.get_color('primary')};
            margin-bottom: 8px;
        """)
        layout.addWidget(title)
        
        # Current test label
        self._current_test_label = QLabel("Preparing tests...")
        self._current_test_label.setStyleSheet(f"color: {self.theme_service.get_color('text_secondary')};")
        layout.addWidget(self._current_test_label)
        
        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {self.theme_service.get_color('outline')};
                border-radius: 4px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {self.theme_service.get_color('primary')};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self._progress_bar)
        
        # Results text
        self._results_text = QTextEdit()
        self._results_text.setReadOnly(True)
        self._results_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.theme_service.get_color('surface_dim')};
                border: 1px solid {self.theme_service.get_color('outline')};
                border-radius: 4px;
                padding: 8px;
                font-family: 'Courier New', monospace;
            }}
        """)
        layout.addWidget(self._results_text)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(self.theme_service.get_button_style("secondary"))
        close_btn.clicked.connect(self.close)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
