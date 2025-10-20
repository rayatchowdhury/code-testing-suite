"""
Base class for windows with sidebar layout.

ContentWindowBase extends WindowBase to provide sidebar integration,
splitter management, and layout creation for content-focused windows.
"""

from PySide6.QtWidgets import QSplitter, QHBoxLayout, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from .window_base import WindowBase


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
        """
        Initialize ContentWindowBase.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.sidebar = None
        self.display_area = None
        self.splitter = None
        
        # Setup base layout
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
    
    def _create_splitter(self) -> QSplitter:
        """
        Create the horizontal splitter for sidebar and content.
        
        Returns:
            Configured QSplitter widget
        """
        splitter = QSplitter(Qt.Horizontal)
        
        # Apply styling
        try:
            from src.app.presentation.styles.style import SPLITTER_STYLE
            splitter.setStyleSheet(SPLITTER_STYLE)
        except ImportError:
            pass  # Style not available, use default
        
        return splitter
    
    def setup_splitter(self, sidebar, content):
        """
        Set up the window layout with sidebar and content area.
        
        Creates splitter, adds sidebar and display area, configures sizes.
        
        Args:
            sidebar: Sidebar widget to add to left
            content: Content widget to add to right
        """
        if not self.splitter:
            self.splitter = self._create_splitter()
            self.layout().addWidget(self.splitter)
        
        self.splitter.addWidget(sidebar)
        self.splitter.addWidget(content)
        
        # Set minimum widths
        sidebar.setMinimumWidth(250)
        content.setMinimumWidth(600)
        
        # Set initial proportions
        self.update_splitter_sizes()
    
    def update_splitter_sizes(self):
        """
        Update splitter sizes to maintain proper proportions.
        
        Called during resize events to keep sidebar at fixed width
        and content area responsive.
        """
        total_width = self.width()
        if total_width > 0 and self.splitter:
            # 250px sidebar, rest for content
            self.splitter.setSizes([250, total_width - 250])
    
    def resizeEvent(self, event):
        """
        Handle resize events to maintain splitter proportions.
        
        Args:
            event: QResizeEvent
        """
        super().resizeEvent(event)
        self.update_splitter_sizes()
    
    def create_footer_buttons(self):
        """
        Create standard footer buttons (Back, Options).
        
        Returns:
            Tuple of (back_button, options_button)
        """
        # Back button
        back_btn = QPushButton("Back")
        back_btn.setObjectName("back_button")
        back_btn.clicked.connect(lambda: self.handle_button_click("Back"))
        
        # Options button (gear emoji)
        options_btn = QPushButton("⚙️")
        options_btn.setObjectName("back_button")
        
        # Apply emoji font
        try:
            from src.app.presentation.styles.fonts.emoji import set_emoji_font
            set_emoji_font(options_btn)
        except ImportError:
            pass  # Emoji font not available
        
        options_btn.setFont(QFont("Segoe UI", 14))
        options_btn.clicked.connect(lambda: self.handle_button_click("Options"))
        
        return back_btn, options_btn
    
    def handle_button_click(self, button_text: str):
        """
        Handle standard button clicks (Back, Options).
        
        Args:
            button_text: Name of clicked button
            
        Override in subclasses to handle additional buttons.
        """
        if button_text == "Back":
            self._handle_back_click()
        elif button_text == "Options":
            self._handle_options_click()
    
    def _handle_back_click(self):
        """
        Handle Back button click.
        
        Checks can_close() before navigating back.
        Uses NavigationService for decoupled navigation.
        """
        if self.can_close():
            from src.app.presentation.services.navigation_service import NavigationService
            if not NavigationService.instance().go_back():
                NavigationService.instance().navigate_to("main")
    
    def _handle_options_click(self):
        """
        Handle Options button click.
        
        Shows configuration dialog.
        Will be updated in Phase 1C to use ConfigService.
        """
        try:
            # Lazy import to avoid slow startup
            from src.app.core.config import ConfigView
            
            config_dialog = ConfigView(self)
            if hasattr(config_dialog, 'configSaved'):
                config_dialog.configSaved.connect(self._on_config_changed)
            config_dialog.exec()
        except ImportError:
            print("Config dialog not available")
    
    def _on_config_changed(self, config):
        """
        Handle configuration changes.
        
        Reloads AI config, refreshes AI panels, and reinitializes tools.
        
        Args:
            config: The new configuration dictionary
        """
        # Reload AI configuration
        try:
            from src.app.core.ai import reload_ai_config
            reload_ai_config()
        except ImportError:
            pass  # AI module not available
        
        # Refresh AI panels if available
        if hasattr(self, "refresh_ai_panels"):
            self.refresh_ai_panels()
        
        # Reinitialize tools if available
        if hasattr(self, "_initialize_tool"):
            self._initialize_tool()
            
            # Show feedback if console available
            if hasattr(self, "display_area") and hasattr(self.display_area, "console"):
                self.display_area.console.displayOutput(
                    "✓ Configuration updated - compilation settings reloaded", 
                    "success"
                )
