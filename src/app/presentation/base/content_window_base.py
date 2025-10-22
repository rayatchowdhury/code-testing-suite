"""
Base class for windows with sidebar layout.

ContentWindowBase extends WindowBase to provide sidebar integration,
splitter management, and layout creation for content-focused windows.
"""

import logging

from PySide6.QtWidgets import QSplitter, QHBoxLayout, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from .window_base import WindowBase

logger = logging.getLogger(__name__)

class ContentWindowBase(WindowBase):
    """
    Base class for windows with sidebar + content layout.
    
    Responsibilities:
    - Sidebar widget integration
    - Splitter creation and management
    - Layout organization (sidebar | content)
    - Footer button creation
    
    Subclasses:
    - TestWindowBase: Test tool windows
    - EditorWindowBase: File editing windows
    - DocumentWindowBase: Static content windows
    - ResultsWindowBase: Results display windows
    
    Usage:
        class MyContentWindow(ContentWindowBase):
            def __init__(self, parent=None):
                super().__init__(parent)
                self._setup_sidebar()
                self._setup_content()
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sidebar = None
        self.display_area = None
        self.splitter = None
        self._config_notifier_connected = False  # Track if already connected
        
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        
        # Connect to global config change notifications (only once)
        if not self._config_notifier_connected:
            try:
                from src.app.presentation.navigation.window_manager import ConfigChangeNotifier
                notifier = ConfigChangeNotifier.instance()
                notifier.configChanged.connect(self._on_config_changed)
                self._config_notifier_connected = True
                logger.debug(f"{self.__class__.__name__} connected to ConfigChangeNotifier")
            except Exception as e:
                logger.warning(f"Could not connect to ConfigChangeNotifier: {e}")
    
    def _create_splitter(self) -> QSplitter:
        """Create horizontal splitter for sidebar and content."""
        splitter = QSplitter(Qt.Horizontal)
        
        try:
            from src.app.presentation.shared.design_system.styles.style import SPLITTER_STYLE
            splitter.setStyleSheet(SPLITTER_STYLE)
        except ImportError:
            pass  # Style not available, use default
        
        return splitter
    
    def setup_splitter(self, sidebar, content):
        """Set up window layout with sidebar and content area."""
        if not self.splitter:
            self.splitter = self._create_splitter()
            self.layout().addWidget(self.splitter)
        
        self.splitter.addWidget(sidebar)
        self.splitter.addWidget(content)
        
        sidebar.setMinimumWidth(250)
        content.setMinimumWidth(600)
        
        self.update_splitter_sizes()
    
    def update_splitter_sizes(self):
        """Maintain proper splitter proportions (250px sidebar, rest for content)."""
        total_width = self.width()
        if total_width > 0 and self.splitter:
            # 250px sidebar, rest for content
            self.splitter.setSizes([250, total_width - 250])
    
    def resizeEvent(self, event):
        """Maintain splitter proportions on resize."""
        super().resizeEvent(event)
        self.update_splitter_sizes()
    
    def create_footer_buttons(self):
        """Create standard footer buttons: (back_button, options_button)."""
        # Back button
        back_btn = QPushButton("Back")
        back_btn.setObjectName("back_button")
        back_btn.clicked.connect(lambda: self.handle_button_click("Back"))
        
        # Options button (gear emoji)
        options_btn = QPushButton("⚙️")
        options_btn.setObjectName("back_button")
        
        try:
            from src.app.presentation.shared.design_system.assets.fonts import set_emoji_font
            set_emoji_font(options_btn)
        except ImportError:
            pass  # Emoji font not available
        
        options_btn.setFont(QFont("Segoe UI", 14))
        options_btn.clicked.connect(lambda: self.handle_button_click("Options"))
        
        return back_btn, options_btn
    
    def handle_button_click(self, button_text: str):
        """Handle standard button clicks (override for additional buttons)."""
        if button_text == "Back":
            self._handle_back_click()
        elif button_text == "Options":
            self._handle_options_click()
    
    def _handle_back_click(self):
        """Handle Back button - checks can_close() before navigating."""
        # Check if tests are running
        if self._is_test_running():
            logger.debug("Back navigation blocked - tests running")
            from src.app.presentation.services import ErrorHandlerService
            error_service = ErrorHandlerService.instance()
            error_service.show_warning(
                "Tests Running",
                "Cannot navigate while tests are running.\n\nPlease stop the current test execution first.",
                self
            )
            return
        
        # Check if safe to close
        if self.can_close():
            if self.router and not self.router.go_back():
                if self.router:
                    self.router.navigate_to("main")
    
    def _handle_options_click(self):
        """Show configuration dialog - but not while tests are running."""
        # Check if tests are running
        if self._is_test_running():
            logger.debug("Config dialog blocked - tests running")
            from src.app.presentation.services import ErrorHandlerService
            error_service = ErrorHandlerService.instance()
            error_service.show_warning(
                "Tests Running",
                "Cannot open configuration while tests are running.\n\nPlease stop the current test execution first.",
                self
            )
            return
        try:
            # Lazy import to avoid slow startup
            from src.app.presentation.windows.config_options import ConfigView
            
            config_dialog = ConfigView(self)
            if hasattr(config_dialog, 'configSaved'):
                config_dialog.configSaved.connect(self._on_config_changed)
            config_dialog.exec()
        except ImportError:
            logger.warning("Config dialog not available")
    
    def _on_config_changed(self, config):
        """Handle config changes - reload AI config, refresh panels, reinitialize tools, reload compilers."""
        try:
            logger.info("Config changed - applying hot reload in ContentWindowBase")
            
            # Reload AI configuration
            try:
                from src.app.core.ai import reload_ai_config
                reload_ai_config()
            except ImportError:
                pass  # AI module not available
            
            # Apply editor settings if window has editors
            editor_settings = config.get("editor_settings", {})
            if editor_settings:
                # Apply to editor_widget if exists
                if hasattr(self, "editor_widget") and self.editor_widget:
                    if hasattr(self.editor_widget, "apply_settings"):
                        self.editor_widget.apply_settings(editor_settings)
                        logger.debug("Applied editor settings to editor_widget")
                
                # Apply to editor_display if exists (CodeEditorWindow)
                if hasattr(self, "editor_display") and self.editor_display:
                    if hasattr(self.editor_display, "tab_widget") and self.editor_display.tab_widget:
                        for i in range(self.editor_display.tab_widget.count()):
                            tab = self.editor_display.tab_widget.widget(i)
                            if tab and hasattr(tab, "editor"):
                                if hasattr(tab.editor, "apply_settings"):
                                    tab.editor.apply_settings(editor_settings)
                        logger.debug("Applied editor settings to all tabs in editor_display")
            
            # Reload CompilerRunner if exists (non-blocking)
            if hasattr(self, "editor_display") and self.editor_display:
                if hasattr(self.editor_display, "compiler_runner") and self.editor_display.compiler_runner:
                    if hasattr(self.editor_display.compiler_runner, "reload_config"):
                        self.editor_display.compiler_runner.reload_config()
                        logger.debug("Reloaded compiler_runner config")
            
            # Refresh AI panels if available
            if hasattr(self, "refresh_ai_panels"):
                self.refresh_ai_panels()
            
            # Reinitialize tools if available (for test windows)
            if hasattr(self, "_initialize_tool"):
                self._initialize_tool()
                
                # Show feedback if console available
                if hasattr(self, "display_area") and hasattr(self.display_area, "console"):
                    self.display_area.console.displayOutput(
                        "✓ Configuration updated - compilation settings reloaded", 
                        "success"
                    )
            
            logger.info("Config hot reload completed in ContentWindowBase")
            
        except Exception as e:
            logger.error(f"Error in _on_config_changed: {e}", exc_info=True)
