import json
import os
import os.path
from .config_exceptions import *
from constants import USER_DATA_DIR, CONFIG_FILE

class ConfigManager:
    CONFIG_DIR = USER_DATA_DIR
    
    def __init__(self, config_file='config.json'):
        self.config_file = os.path.join(self.CONFIG_DIR, config_file)

    def load_config(self):
        try:
            if not os.path.exists(self.config_file):
                return self.get_default_config()

            if not os.access(self.config_file, os.R_OK):
                raise ConfigPermissionError("reading", self.config_file)

            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            except json.JSONDecodeError as e:
                raise ConfigFormatError(e.msg, e.lineno)
            
            validation_errors = self._validate_config_structure(config)
            if validation_errors:
                raise ConfigValidationError("configuration structure",
                    "Invalid configuration format",
                    "\n".join(validation_errors))
            
            return config

        except ConfigError:
            raise
        except Exception as e:
            raise ConfigLoadError(str(e))

    def save_config(self, config):
        try:
            # Ensure config directory exists
            os.makedirs(self.CONFIG_DIR, exist_ok=True)

            # Backup existing config
            if os.path.exists(self.config_file):
                backup_file = f"{self.config_file}.bak"
                try:
                    os.replace(self.config_file, backup_file)
                except Exception:
                    pass  # Ignore backup failures

            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)

        except Exception as e:
            raise ConfigSaveError(f"Failed to save config: {str(e)}")

    def _validate_config_structure(self, config):
        errors = []
        required_keys = {
            'cpp_version': str,
            'workspace_folder': str,
            'ai_settings': dict,  # Changed from gemini_api_key
            'editor_settings': dict
        }
        
        for key, expected_type in required_keys.items():
            if key not in config:
                errors.append(f"Missing required key: {key}")
            elif not isinstance(config[key], expected_type):
                errors.append(f"Invalid type for {key}: expected {expected_type.__name__}")
        
        if 'ai_settings' in config:
            ai_settings = config['ai_settings']
            required_ai_settings = {
                'use_ai_panel': bool,
                'gemini_api_key': str
            }
            
            for key, expected_type in required_ai_settings.items():
                if key not in ai_settings:
                    errors.append(f"Missing AI setting: {key}")
                elif not isinstance(ai_settings[key], expected_type):
                    errors.append(f"Invalid type for AI setting {key}")
            
            # Note: We don't require a valid API key, just the correct structure
        
        if 'editor_settings' in config:
            editor_settings = config['editor_settings']
            required_settings = {
                'autosave': bool,
                'autosave_interval': int,
                'tab_width': int,
                'font_size': int,
                'bracket_matching': bool
            }
            
            for key, expected_type in required_settings.items():
                if key not in editor_settings:
                    errors.append(f"Missing editor setting: {key}")
                elif not isinstance(editor_settings[key], expected_type):
                    errors.append(f"Invalid type for editor setting {key}")
        
        if missing_keys := [k for k in required_keys if k not in config]:
            raise ConfigMissingError(f"Required keys: {', '.join(missing_keys)}")
        
        return errors

    def get_default_config(self):
        return {
            'cpp_version': 'c++17',
            'workspace_folder': '',
            'ai_settings': {  # Changed from gemini_api_key
                'use_ai_panel': False,
                'gemini_api_key': ''
            },
            'editor_settings': {
                'autosave': True,
                'autosave_interval': 5,
                'tab_width': 4,
                'font_size': 12,
                'font_family': 'Consolas',
                'bracket_matching': True  # Add this line
            }
        }