# TODO: Create main application class for v2 based on v1/main.py
"""
Application Bootstrap

Main application class that initializes the v2 architecture.
Based on v1/main.py but with clean dependency injection.
"""
import sys
import asyncio
from pathlib import Path
from typing import Optional

# Add Qt imports when ready for full migration
# from PySide6.QtWidgets import QApplication
# from PySide6.QtCore import Qt
# import qasync

from app.dependency_injection import get_container, register_services
from infrastructure.configuration.config_service import ConfigService
from infrastructure.file_system.file_service import FileService
from infrastructure.theming.theme_service import ThemeService

class Application:
    """
    Main application class for v2 architecture.
    
    ASSUMPTION: Initially console-based to test the architecture.
    GUI integration will be added in later weeks.
    """
    
    def __init__(self):
        self.container = get_container()
        self._config_service: Optional[ConfigService] = None
        self._file_service: Optional[FileService] = None
    
    def initialize(self) -> None:
        """Initialize the application"""
        print("🚀 Initializing Code Testing Suite v2...")
        
        # Register all services
        register_services()
        
        # Get core services
        self._config_service = self.container.get(ConfigService)
        self._file_service = self.container.get(FileService)
        
        print("✅ Application initialized")
    
    def run_console_mode(self) -> None:
        """Run application in console mode (for testing architecture)"""
        try:
            # Test configuration service
            ai_settings = self._config_service.get_ai_settings()
            compiler_settings = self._config_service.get_compiler_settings()
            workspace_path = self._config_service.get_workspace_path()
            
            print("\n📋 Configuration Status:")
            print(f"  AI Enabled: {ai_settings.enabled}")
            print(f"  C++ Version: {compiler_settings.cpp_version}")
            print(f"  Workspace: {workspace_path}")
            
            # Test file service
            print(f"\n📁 File Service Ready: {type(self._file_service).__name__}")
            
            # Test theme service
            theme_service = self.container.get(ThemeService)
            print(f"\n🎨 Theme Service Ready: {theme_service.get_theme_mode().value}")
            print(f"  Primary Color: {theme_service.get_color('primary')}")
            print(f"  Background: {theme_service.get_color('background')}")
            
            # Test AI readiness
            is_ready, message = self._config_service.is_ai_ready()
            print(f"\n🤖 AI Status: {message}")
            
            # Test configuration adapter (without Qt)
            print(f"\n⚙️ Configuration Adapter:")
            try:
                from presentation.adapters.config_view_adapter import ConfigurationViewAdapter
                adapter = ConfigurationViewAdapter(self._config_service, theme_service)
                print("  ✅ Adapter created successfully (without Qt)")
            except RuntimeError as e:
                print(f"  ⚠️ {e} (expected - demonstrates clean separation)")
            
            print("\n✨ v2 Architecture validation complete!")
            
        except Exception as e:
            print(f"❌ Error during validation: {e}")
            return False
        
        return True
    
    async def run_gui_mode(self) -> None:
        """Run application in GUI mode (TODO: implement in later weeks)"""
        print("🖥️  GUI mode not yet implemented")
        print("   This will be added in Week 3-4 when migrating presentation layer")
    
    def shutdown(self) -> None:
        """Shutdown the application"""
        print("🔄 Shutting down application...")
        self.container.clear()
        print("✅ Application shutdown complete")

def create_application() -> Application:
    """Create and initialize the application"""
    app = Application()
    app.initialize()
    return app
