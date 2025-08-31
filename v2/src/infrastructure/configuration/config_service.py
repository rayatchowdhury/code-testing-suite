# TODO: Extract configuration logic from v1/views/config/ and v1/utils/ai_config.py
"""
Configuration Service - Centralized configuration management

This service consolidates configuration logic that was previously scattered across:
- v1/utils/ai_config.py
- v1/views/config/config_manager.py
- v1/views/config/config_view.py
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, NamedTuple
from dataclasses import dataclass

@dataclass
class AISettings:
    """AI configuration settings"""
    enabled: bool = False
    api_key: str = ""
    use_ai_panel: bool = False

@dataclass
class CompilerSettings:
    """Compiler configuration settings"""
    cpp_version: str = "c++17"
    optimization_level: str = "-O2"
    warnings_enabled: bool = True

@dataclass
class AppSettings:
    """Application configuration settings"""
    workspace_folder: str = ""
    theme: str = "dark"
    auto_save: bool = True

class ConfigResult(NamedTuple):
    """Result of configuration operation"""
    success: bool
    error_message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class ConfigService:
    """
    Configuration service providing centralized settings management.
    
    ASSUMPTION: Consolidates scattered configuration logic from v1 into a single service.
    """
    
    CONFIG_DIR = Path.home() / '.code_testing_suite'
    CONFIG_FILE = CONFIG_DIR / 'config.json'
    
    def __init__(self):
        self._config_cache: Optional[Dict[str, Any]] = None
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        self.CONFIG_DIR.mkdir(exist_ok=True)
    
    def get_ai_settings(self) -> AISettings:
        """Get AI configuration settings"""
        config = self._load_config()
        ai_config = config.get('ai_settings', {})
        
        return AISettings(
            enabled=ai_config.get('use_ai_panel', False),
            api_key=ai_config.get('gemini_api_key', ''),
            use_ai_panel=ai_config.get('use_ai_panel', False)
        )
    
    def get_compiler_settings(self) -> CompilerSettings:
        """Get compiler configuration settings"""
        config = self._load_config()
        
        return CompilerSettings(
            cpp_version=config.get('cpp_version', 'c++17'),
            optimization_level=config.get('optimization_level', '-O2'),
            warnings_enabled=config.get('warnings_enabled', True)
        )
    
    def get_app_settings(self) -> AppSettings:
        """Get application configuration settings"""
        config = self._load_config()
        
        return AppSettings(
            workspace_folder=config.get('workspace_folder', ''),
            theme=config.get('theme', 'dark'),
            auto_save=config.get('auto_save', True)
        )
    
    def get_workspace_path(self) -> Path:
        """Get configured workspace path"""
        app_settings = self.get_app_settings()
        if app_settings.workspace_folder:
            return Path(app_settings.workspace_folder)
        return Path.cwd()
    
    def is_ai_ready(self) -> tuple[bool, str]:
        """Check if AI is ready to use"""
        ai_settings = self.get_ai_settings()
        
        if not ai_settings.enabled:
            return False, "AI Panel is disabled in settings"
        
        if not ai_settings.api_key:
            return False, "No API key provided"
        
        if len(ai_settings.api_key) < 30:  # Basic validation
            return False, "API key appears to be invalid"
        
        return True, "AI is ready"
    
    def update_ai_settings(self, settings: AISettings) -> ConfigResult:
        """Update AI settings"""
        config = self._load_config()
        config['ai_settings'] = {
            'use_ai_panel': settings.enabled,
            'gemini_api_key': settings.api_key
        }
        return self._save_config(config)
    
    def update_compiler_settings(self, settings: CompilerSettings) -> ConfigResult:
        """Update compiler settings"""
        config = self._load_config()
        config.update({
            'cpp_version': settings.cpp_version,
            'optimization_level': settings.optimization_level,
            'warnings_enabled': settings.warnings_enabled
        })
        return self._save_config(config)
    
    def update_workspace_path(self, path: Path) -> ConfigResult:
        """Update workspace path"""
        config = self._load_config()
        config['workspace_folder'] = str(path)
        return self._save_config(config)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file with caching"""
        if self._config_cache is not None:
            return self._config_cache
        
        try:
            if not self.CONFIG_FILE.exists():
                self._config_cache = self._get_default_config()
                return self._config_cache
            
            with self.CONFIG_FILE.open('r', encoding='utf-8') as f:
                self._config_cache = json.load(f)
                return self._config_cache
                
        except (json.JSONDecodeError, OSError):
            # Return default config on error
            self._config_cache = self._get_default_config()
            return self._config_cache
    
    def _save_config(self, config: Dict[str, Any]) -> ConfigResult:
        """Save configuration to file"""
        try:
            # Create backup if file exists
            if self.CONFIG_FILE.exists():
                backup_path = self.CONFIG_FILE.with_suffix('.json.bak')
                backup_path.write_text(
                    self.CONFIG_FILE.read_text(encoding='utf-8'),
                    encoding='utf-8'
                )
            
            # Save new config
            with self.CONFIG_FILE.open('w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            # Update cache
            self._config_cache = config
            
            return ConfigResult(success=True, data=config)
            
        except Exception as e:
            return ConfigResult(success=False, error_message=str(e))
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'cpp_version': 'c++17',
            'workspace_folder': '',
            'optimization_level': '-O2',
            'warnings_enabled': True,
            'theme': 'dark',
            'auto_save': True,
            'ai_settings': {
                'use_ai_panel': False,
                'gemini_api_key': ''
            }
        }
    
    def invalidate_cache(self):
        """Invalidate configuration cache"""
        self._config_cache = None
