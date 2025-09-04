# -*- coding: utf-8 -*-
"""
Core EditorAI class - Streamlined and modular.

Main interface for AI-powered code assistance.
"""

import os
import json
import logging
from typing import Optional
from google.api_core import retry_async

from constants import USER_DATA_DIR
from utils.logging_config import LoggingConfig
from ..models.model_manager import ModelManager
from ..templates.prompt_templates import PromptTemplates

# Ensure logging is configured
LoggingConfig.initialize()

# Additional gRPC suppression
try:
    import grpc._channel
    original_log = getattr(grpc._channel, '_log_operand_details', None)
    if original_log:
        setattr(grpc._channel, '_log_operand_details', lambda *args, **kwargs: None)
except ImportError:
    pass


class EditorAI:
    """AI-powered code editor assistant using Google's Gemini API."""
    
    def __init__(self):
        """Initialize the EditorAI with model configuration."""
        self.model_manager = ModelManager()
        self.prompt_templates = PromptTemplates()
        self.generator_docs = self._load_generator_description()
        self._initialize_ai()

    def _initialize_ai(self) -> None:
        """Initialize the AI system with user configuration."""
        try:
            api_key = self._load_api_key()
            if not api_key:
                logging.warning("No API key found - AI features will be disabled")
                return

            preferred_model = self._get_preferred_model()
            success = self.model_manager.initialize_model(api_key, preferred_model)
            
            if not success:
                logging.error("Failed to initialize AI model")
                
        except Exception as e:
            logging.error(f"AI initialization error: {e}")

    def _load_api_key(self) -> Optional[str]:
        """Load API key from config."""
        try:
            if not os.path.exists(USER_DATA_DIR):
                os.makedirs(USER_DATA_DIR, exist_ok=True)
                return None

            config_path = os.path.join(USER_DATA_DIR, 'config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            ai_settings = config.get('ai_settings', {})
            return ai_settings.get('gemini_api_key')
        except Exception as e:
            logging.error(f"API key load error: {e}")
            return None

    def _get_preferred_model(self) -> Optional[str]:
        """Get user's preferred model from config."""
        try:
            config = self._load_config()
            ai_settings = config.get('ai_settings', {})
            return ai_settings.get('preferred_model')
        except Exception:
            return None

    def _load_config(self) -> dict:
        """Load configuration from file."""
        try:
            if not os.path.exists(USER_DATA_DIR):
                return {}
            
            config_path = os.path.join(USER_DATA_DIR, 'config.json')
            if not os.path.exists(config_path):
                return {}
                
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Config load error: {e}")
            return {}

    def _load_generator_description(self) -> str:
        """Load generator library docs."""
        try:
            path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                              'tools', 'generator_description.txt')
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logging.error(f"Generator docs load error: {e}")
            return ""

    @retry_async.AsyncRetry(predicate=retry_async.if_exception_type(Exception))
    async def _get_ai_response(self, prompt: str) -> Optional[str]:
        """Get AI response with retry and model refresh capability."""
        if not self.model_manager.is_initialized():
            # Try to refresh model before failing
            if not self.refresh_model():
                api_key = self._load_api_key()
                if not api_key:
                    return "❌ AI service unavailable: No API key configured. Please check your settings."
                else:
                    return "❌ AI service unavailable: Failed to initialize model. Please check your API key and internet connection."

        try:
            response = await self.model_manager.model.generate_content_async(prompt, stream=False)
            
            if response and hasattr(response, 'text'):
                result = response.text.strip()
                if result:
                    return result
                else:
                    return "❌ AI returned an empty response. The request may have been blocked by safety filters."
            else:
                return "❌ AI response was empty or invalid."
                
        except Exception as e:
            logging.warning(f"AI response error: {e}")
            # Try refreshing model once
            try:
                if self.refresh_model():
                    try:
                        response = await self.model_manager.model.generate_content_async(prompt, stream=False)
                        if response and hasattr(response, 'text'):
                            result = response.text.strip()
                            return result if result else "❌ AI returned an empty response after retry."
                    except Exception as retry_e:
                        logging.error(f"AI retry failed: {retry_e}")
                return f"❌ AI request failed: {str(e)}"
            except Exception as refresh_e:
                logging.error(f"Model refresh failed: {refresh_e}")
                return f"❌ AI service error: {str(e)}"

    # Public API methods
    def refresh_model(self, force: bool = False) -> bool:
        """Refresh and reinitialize the AI model if needed."""
        if self.model_manager.is_initialized() and not force:
            return True

        logging.info("Attempting to refresh AI model...")
        self._initialize_ai()
        return self.model_manager.is_initialized()

    def get_current_model_name(self) -> Optional[str]:
        """Get the name of the currently active model."""
        return self.model_manager.get_current_model_name()

    def refresh_available_models(self) -> list:
        """Force refresh the cached model list from Google's API."""
        return self.model_manager.refresh_model_cache()

    def is_ai_enabled(self) -> bool:
        """Check if AI is enabled and configured."""
        return self.model_manager.is_initialized()

    # AI processing methods
    async def process_explanation(self, explanation_type: str, code: str) -> Optional[str]:
        """Process explanation requests (analysis, issues, tips)."""
        if not self.is_ai_enabled():
            return "❌ AI not configured"

        try:
            prompt = self.prompt_templates.get_explanation_prompt(explanation_type, code)
            return await self._get_ai_response(prompt)
        except ValueError as e:
            return f"❌ {str(e)}"
        except Exception as e:
            return f"❌ Processing error: {str(e)}"

    async def process_code(self, action: str, code: str, **kwargs) -> Optional[str]:
        """Handle code-modification requests."""
        if not self.is_ai_enabled():
            return "❌ AI not configured"

        try:
            # Add generator docs for generator templates
            if action == 'generate' and kwargs.get('type', '').lower().endswith('generator.cpp'):
                kwargs['docs'] = self.generator_docs
            
            prompt_with_base = (self.prompt_templates.CODE_BASE_PROMPT + "\n\n" + 
                              self.prompt_templates.get_code_prompt(action, code, **kwargs))
            
            return await self._get_ai_response(prompt_with_base)
        except ValueError as e:
            return f"❌ {str(e)}"
        except Exception as e:
            return f"❌ Processing error: {str(e)}"

    async def process_custom_command(self, command: str, code: str) -> Optional[str]:
        """Handle custom command requests."""
        if not self.is_ai_enabled():
            return "❌ AI not configured"

        try:
            prompt_with_base = (self.prompt_templates.CODE_BASE_PROMPT + "\n\n" + 
                              self.prompt_templates.get_custom_prompt(command, code))
            
            return await self._get_ai_response(prompt_with_base)
        except Exception as e:
            return f"❌ Processing error: {str(e)}"

    # Legacy compatibility methods
    def configure(self):
        """Configure the AI system - only if not already configured."""
        if not self.model_manager.is_initialized():
            self._initialize_ai()

    def _get_api_key(self):
        """Get API key from config."""
        return self._load_api_key()

    async def analyze_code(self, code):
        """Analyze code and provide insights."""
        if not self.is_ai_enabled():
            return {"error": "AI not configured", "content": ""}

        try:
            result = await self.process_explanation('analysis', code)
            return {"error": None, "content": result or ""}
        except Exception as e:
            return {"error": str(e), "content": ""}

    def cleanup(self):
        """Cleanup AI resources."""
        try:
            if hasattr(self, 'model_manager'):
                self.model_manager.cleanup()
            if hasattr(self, 'generator_docs'):
                self.generator_docs = None
        except Exception:
            pass
