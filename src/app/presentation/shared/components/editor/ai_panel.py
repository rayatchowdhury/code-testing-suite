import asyncio
import os
import threading

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# Import styles directly from individual module (not via __init__.py)
from src.app.presentation.shared.design_system.styles.components.ai_panel import (
    AI_PANEL_STYLE,
    CUSTOM_COMMAND_STYLE,
)

class AIActionButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("ai_button")
        self.setFixedHeight(24)  # Reduced height
        self.setCursor(Qt.PointingHandCursor)

class AICustomCommandInput(QFrame):
    commandSubmitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("custom_command_frame")
        self.setStyleSheet(CUSTOM_COMMAND_STYLE)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(8)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Type custom command here.")
        self.input.setObjectName("custom_command_input")
        self.input.returnPressed.connect(self._handle_submit)

        layout.addWidget(self.input)

    def _handle_submit(self):
        command = self.input.text().strip()
        if command:
            self.commandSubmitted.emit(command)
            self.input.clear()

class AIPanel(QWidget):
    # Define signals for each action
    analysisRequested = Signal(str)
    issuesRequested = Signal(str)  # Changed from fixRequested
    tipsRequested = Signal(str)  # Changed from optimizeRequested
    documentRequested = Signal(str)
    generateRequested = Signal(str)
    customCommandRequested = Signal(str, str)

    def __init__(self, parent=None, panel_type="editor"):
        super().__init__(parent)
        self.panel_type = panel_type
        self.setObjectName("ai_panel")
        self.setStyleSheet(AI_PANEL_STYLE)

        # Check if AI panel should be shown
        self.refresh_visibility()

        # Remove background AI initialization to avoid threading issues
        # AI will be initialized on first use instead

    def _initialize_ai_background(self):
        """Initialize AI model - simplified without threading."""
        # Removed background threading to fix AI threading issues
        # AI is now initialized lazily on first use

    def refresh_visibility(self):
        """Refresh panel visibility based on current AI configuration"""
        if self._should_show_ai_panel():
            if self.layout() is None:
                self._setup_ui()
            self.show()
            # Removed background AI initialization to avoid threading issues
        else:
            self.hide()

    def set_panel_type(self, panel_type):
        """Update panel type and recreate buttons"""
        if self.panel_type != panel_type:
            self.panel_type = panel_type
            self._setup_ui()  # Recreate UI with new panel type

    def _setup_ui(self):
        if self.layout():
            QWidget().setLayout(self.layout())

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 6, 8, 6)  # Reduced margins
        main_layout.setSpacing(8)  # Reduced spacing

        # All button sections container
        button_sections = QWidget()
        button_sections.setObjectName("ai_button_sections")
        button_sections.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        button_layout = QHBoxLayout(button_sections)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(6)

        # Add all buttons in one go
        self.action_buttons = {}

        # Define button configurations
        self.button_configs = {
            "explanation_buttons": [
                ("Analysis", "Get complete analysis of your code"),
                ("Issues", "List potential issues and edge cases"),
                ("Tips", "Get improvement suggestions"),
            ],
            "code_buttons": {
                "editor": (
                    "Document",
                    "Add comprehensive documentation (applies to code)",
                ),
                "other": ("Generate", "Generate new code from requirements"),
            },
        }

        # Create explanation buttons
        for text, tooltip in self.button_configs["explanation_buttons"]:
            btn = self._create_action_button(text, tooltip)
            button_layout.addWidget(btn)

        # Add separator
        button_layout.addWidget(self._create_separator())

        # Add context-specific button
        specific = self.button_configs["code_buttons"][
            "editor" if self.panel_type == "editor" else "other"
        ]
        btn = self._create_action_button(*specific)
        button_layout.addWidget(btn)

        # Add final separator and custom command
        button_layout.addWidget(self._create_separator())
        self.custom_command = AICustomCommandInput()

        # Add sections to main layout with proper sizing
        main_layout.addWidget(button_sections)
        main_layout.addWidget(self.custom_command, 1)

        self._connect_signals()

    def _create_action_button(self, text: str, tooltip: str) -> AIActionButton:
        """Create a standardized action button."""
        btn = AIActionButton(text)
        btn.setToolTip(tooltip)
        self.action_buttons[text.lower()] = btn
        return btn

    def _create_separator(self) -> QFrame:
        """Create a standardized separator."""
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setObjectName("ai_separator")
        return sep

    def _connect_signals(self):
        """Connect button signals with proper code context"""
        # Connect button signals
        signal_map = {
            "analysis": self.analysisRequested,
            "issues": self.issuesRequested,  # Changed from fix
            "tips": self.tipsRequested,  # Changed from optimize
            "document": self.documentRequested,
            "generate": self.generateRequested,
        }

        # Connect all buttons including generate
        for action, btn in self.action_buttons.items():
            if action in signal_map:
                btn.clicked.connect(
                    lambda _, s=signal_map[action]: self._emit_with_current_code(
                        s
                    )
                )

        # Connect custom command signal
        self.custom_command.commandSubmitted.connect(
            lambda cmd: self._emit_custom_command_with_current_code(cmd)
        )

    def _emit_with_current_code(self, signal):
        """Emit a signal with the current code from parent"""
        current_code = ""
        if self.parent():
            try:
                current_code = self.parent().getCode()
            except AttributeError:
                pass  # Parent doesn't have getCode method
        signal.emit(current_code)

    def _emit_custom_command_with_current_code(self, command):
        """Emit custom command signal with current code"""
        current_code = ""
        if self.parent():
            try:
                current_code = self.parent().getCode()
            except AttributeError:
                pass  # Parent doesn't have getCode method
        self.customCommandRequested.emit(command, current_code)

    def set_enabled(self, enabled):
        """Enable or disable all AI actions"""
        for btn in self.action_buttons.values():
            btn.setEnabled(enabled)
        self.custom_command.input.setEnabled(enabled)

    def update_code_context(self, code):
        """Update code context for all buttons"""
        for action, btn in self.action_buttons.items():
            try:
                btn.clicked.disconnect()
            except TypeError:
                pass  # In case not connected

            signal = None
            if action == "generate":
                signal = self.generateRequested
            else:
                signal = getattr(self, f"{action}Requested", None)

            if signal:
                btn.clicked.connect(lambda _, s=signal, c=code: s.emit(c))

    def refresh_from_config(self):
        """Refresh AI panel visibility based on current configuration"""
        should_show = self._should_show_ai_panel()

        if should_show and self.isHidden():
            # Show panel and setup UI if needed
            if self.layout() is None:
                self._setup_ui()
            self.show()
        elif not should_show and self.isVisible():
            # Hide panel
            self.hide()

        # Update status if visible
        if self.isVisible():
            self._update_ai_status()

    def _update_ai_status(self):
        """Update AI status display"""
        is_ready, message = self._is_ai_ready()

        # You could add a status indicator here if needed
        # For now, just update tooltips
        try:
            for btn in self.action_buttons.values():
                if is_ready:
                    btn.setEnabled(True)
                    btn.setToolTip(
                        btn.toolTip().split("\n")[0]
                    )  # Keep original tooltip
                else:
                    btn.setEnabled(False)
                    original_tooltip = btn.toolTip().split("\n")[0]
                    btn.setToolTip(f"{original_tooltip}\n⚠️ {message}")
        except AttributeError:
            pass  # action_buttons not initialized yet

    def _should_show_ai_panel(self):
        """Lazy import gemini client to check if AI panel should be shown"""
        try:
            from src.app.core.ai.gemini_client import should_show_ai_panel

            return should_show_ai_panel()
        except (ImportError, AttributeError):
            return False

    def _is_ai_ready(self):
        """Lazy import gemini client to check if AI is ready"""
        try:
            from src.app.core.ai.gemini_client import is_ai_ready

            return is_ai_ready()
        except (ImportError, AttributeError):
            return False, "AI configuration not available"
