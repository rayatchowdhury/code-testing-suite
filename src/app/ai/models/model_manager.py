# -*- coding: utf-8 -*-
"""
Model Manager for Gemini AI integration.

Handles model discovery, caching, initialization, and configuration.
"""

import google.generativeai as genai
import logging
import threading
import time
import re
from typing import Optional, List
from utils.logging_config import LoggingConfig

# Ensure logging is configured
LoggingConfig.initialize()

class ModelManager:
    """Manages Gemini AI models with caching and dynamic discovery."""
    
    MODEL_CONFIG = {
        "temperature": 0.7,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 2048,
    }
    
    SAFETY_SETTINGS = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
    
    def __init__(self):
        self.model = None
        self._cached_models = None
        
    def get_available_models(self, force_refresh: bool = False) -> List[str]:
        """Get list of available Gemini models that support generateContent."""
        # Return cached models unless forced to refresh
        if self._cached_models and not force_refresh:
            return self._cached_models
            
        try:
            models = []
            model_discovery_complete = threading.Event()
            error_occurred = threading.Event()
            
            def discover_models():
                try:
                    for model in genai.list_models():
                        # Check if model supports generateContent and is a Gemini model
                        if ('generateContent' in model.supported_generation_methods and 
                            model.name.startswith('models/gemini')):
                            # Extract just the model name (remove 'models/' prefix)
                            model_name = model.name.replace('models/', '')
                            models.append(model_name)
                    model_discovery_complete.set()
                except Exception as e:
                    logging.error(f"Error in model discovery thread: {e}")
                    error_occurred.set()
            
            # Start discovery in separate thread
            discovery_thread = threading.Thread(target=discover_models, daemon=True)
            discovery_thread.start()
            
            # Wait up to 10 seconds for completion
            if model_discovery_complete.wait(timeout=10) and not error_occurred.is_set():
                # Sort models dynamically - no hardcoded version priorities
                def model_priority(model_name):
                    priority = 0
                    
                    # Extract version numbers dynamically
                    version_match = re.search(r'(\d+)\.(\d+)', model_name)
                    if version_match:
                        major, minor = map(int, version_match.groups())
                        priority += major * 100 + minor * 10  # Dynamic version priority
                    
                    # Prefer flash models for speed, then pro for quality
                    if 'flash' in model_name:
                        priority += 20
                    elif 'pro' in model_name:
                        priority += 15
                    elif 'vision' in model_name:
                        priority += 5  # Vision models lower priority for code tasks
                    
                    # Prefer newer variants (latest, experimental)
                    if 'latest' in model_name:
                        priority += 3
                    elif 'experimental' in model_name:
                        priority += 1
                    
                    return priority
                
                models.sort(key=model_priority, reverse=True)
                logging.info(f"Available Gemini models: {models}")
                # Cache the results
                self._cached_models = models
                return models
            else:
                raise TimeoutError("Model discovery timed out or failed")
                
        except Exception as e:
            logging.warning(f"Model discovery failed: {e}")
            # Return dynamic fallback models - no hardcoded versions
            fallback_models = [
                'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-1.5-flash-latest',
                'gemini-1.0-pro-latest', 'gemini-1.0-pro', 'gemini-pro'
            ]
            logging.info(f"Using fallback model list: {fallback_models}")
            # Cache the fallback models too
            self._cached_models = fallback_models
            return fallback_models
    
    def initialize_model(self, api_key: str, preferred_model: Optional[str] = None) -> bool:
        """Initialize the AI model with the given API key and optional preferred model."""
        try:
            # Test API key format
            if not api_key.startswith('AIza') or len(api_key) < 35:
                logging.error("API key format appears invalid")
                return False

            genai.configure(api_key=api_key)
            
            # Try user's preferred model first
            if preferred_model:
                if self._try_initialize_specific_model(preferred_model):
                    return True
                else:
                    logging.warning(f"Preferred model '{preferred_model}' failed, falling back to discovery")
            
            # Get available models and try them in order
            available_models = self.get_available_models()
            
            if not available_models:
                logging.error("No available Gemini models found")
                return False
            
            # Try models in order of preference
            for model_name in available_models:
                if self._try_initialize_specific_model(model_name):
                    return True
            
            logging.error("Failed to initialize any AI model")
            return False
            
        except Exception as e:
            logging.error(f"Model initialization error: {e}")
            return False
    
    def _try_initialize_specific_model(self, model_name: str) -> bool:
        """Try to initialize a specific model."""
        try:
            # Ensure model name has proper format
            if not model_name.startswith('models/'):
                full_model_name = model_name if model_name.startswith('gemini') else f'gemini-{model_name}'
            else:
                full_model_name = model_name.replace('models/', '')
            
            self.model = genai.GenerativeModel(
                model_name=full_model_name,
                generation_config=self.MODEL_CONFIG,
                safety_settings=self.SAFETY_SETTINGS
            )
            logging.info(f"AI model '{full_model_name}' initialized successfully")
            return True
        except Exception as model_error:
            logging.warning(f"Failed to initialize model '{model_name}': {model_error}")
            return False
    
    def refresh_model_cache(self) -> List[str]:
        """Force refresh the cached model list from Google's API."""
        return self.get_available_models(force_refresh=True)
    
    def get_current_model_name(self) -> Optional[str]:
        """Get the name of the currently active model."""
        if self.model and hasattr(self.model, 'model_name'):
            return self.model.model_name
        return None
    
    def is_initialized(self) -> bool:
        """Check if the model is initialized and ready."""
        return self.model is not None
    
    def cleanup(self):
        """Cleanup resources."""
        if self.model:
            try:
                # Clear model reference
                self.model = None
            except Exception:
                pass
