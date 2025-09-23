"""
Simple Direct AI Client - No Dependencies

Just needs: API key, model name, and prompt.
Makes direct HTTP requests to AI service.
"""

import json
import logging
import os
import hashlib
import time
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from functools import lru_cache

# Suppress urllib3 noise directly
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)

class GeminiAI:
    """
    Simple direct AI client using HTTP requests.
    Just needs: API key, model name, and prompt.
    """
    
    def __init__(self, config_file: str = None):
        """Initialize simple AI client."""
        self._api_key = None
        self._model_name = None
        self._enabled = False
        self._response_cache = {}
        self._max_cache_size = 100
        self._base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
        # Load configuration
        if config_file:
            self.load_config(config_file)
        else:
            self._load_from_environment()

    def _load_from_environment(self):
        """Load configuration from environment variables."""
        self._api_key = os.getenv('GEMINI_API_KEY')
        self._model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        self._enabled = os.getenv('GEMINI_ENABLED', 'false').lower() == 'true'

    def load_config(self, config_file: str):
        """Load configuration from JSON file."""
        try:
            if not os.path.exists(config_file):
                logging.info("AI is disabled in config")
                return
                
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Handle both old and new config formats
            self._api_key = None
            self._model_name = None
            self._enabled = False
            
            # Try new format first (gemini section)
            gemini_config = config_data.get("gemini", {})
            if gemini_config:
                self._api_key = gemini_config.get("api_key")
                self._model_name = gemini_config.get("model")
                self._enabled = gemini_config.get("enabled", False)
            else:
                # Fall back to legacy format
                ai_settings = config_data.get('ai_settings', {})
                if ai_settings:
                    self._api_key = ai_settings.get('gemini_api_key')
                    self._model_name = ai_settings.get('preferred_model', 'gemini-2.5-flash')
                    self._enabled = ai_settings.get('enabled', False)
                
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            self._enabled = False

    def is_available(self) -> bool:
        """Check if the AI service is available."""
        return self._enabled and self._api_key is not None

    def is_ready(self) -> Tuple[bool, str]:
        """Check if the AI service is ready with detailed status."""
        if not self._enabled:
            return False, "AI service is disabled"
        if not self._api_key:
            return False, "API key is not configured"
        return True, "AI service is ready"

    @lru_cache(maxsize=128)
    def _get_cache_key(self, prompt: str, **kwargs) -> str:
        """Generate cache key for response caching."""
        content = f"{prompt}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()

    def _manage_cache(self):
        """Simple LRU cache management."""
        if len(self._response_cache) > self._max_cache_size:
            # Remove oldest 20% of entries
            to_remove = len(self._response_cache) // 5
            oldest_keys = list(self._response_cache.keys())[:to_remove]
            for key in oldest_keys:
                del self._response_cache[key]

    def _make_api_request(self, prompt: str) -> str:
        """Make direct HTTP request to AI API."""
        try:
            # Build request URL
            url = f"{self._base_url}/{self._model_name}:generateContent?key={self._api_key}"
            
            # Build request data
            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "topP": 0.8,
                    "topK": 40,
                    "maxOutputTokens": 16384,
                    "responseMimeType": "text/plain"
                },
                "safetySettings": [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
                ]
            }
            
            # Make request
            json_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(
                url,
                data=json_data,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'CodeTestingSuite/1.0'
                }
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                # Extract text from response
                if 'candidates' in result and result['candidates']:
                    candidate = result['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        parts = candidate['content']['parts']
                        if parts and 'text' in parts[0]:
                            return parts[0]['text'].strip()
                
                return "❌ Empty response from AI service."
                
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8') if e.fp else str(e)
            logging.error(f"HTTP error: {e.code} - {error_msg}")
            
            if e.code == 400:
                return "❌ Invalid request. Please check your input."
            elif e.code == 403:
                return "❌ Invalid API key or access denied."
            elif e.code == 429:
                return "❌ Too many requests. Please try again later."
            else:
                return f"❌ API error ({e.code}): Please try again."
                
        except urllib.error.URLError as e:
            logging.error(f"Connection error: {e}")
            return "❌ Connection error. Please check your internet connection."
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"API error: {error_msg}")
            return f"❌ Error: {error_msg}"

    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate AI response with caching."""
        if not self.is_available():
            return "❌ AI service is not available."
        
        # Check cache first
        cache_key = self._get_cache_key(prompt, **kwargs)
        if cache_key in self._response_cache:
            return self._response_cache[cache_key]
        
        start_time = time.time()
        result = self._make_api_request(prompt)
        
        # Cache the response if successful
        if not result.startswith("❌"):
            self._response_cache[cache_key] = result
            self._manage_cache()
            
            # Log performance
            duration = time.time() - start_time
            logging.info(f"AI response generated in {duration:.2f}s")
        
        return result

    def cleanup(self):
        """Cleanup resources."""
        try:
            if hasattr(self, '_response_cache'):
                self._response_cache.clear()
        except Exception as e:
            logging.error(f"Cleanup error: {e}")


# Global client management
_gemini_client = None

def get_gemini_client(config_file: str = None) -> GeminiAI:
    """Get or create global AI client instance."""
    global _gemini_client
    
    # If no config file provided, try to use the default one
    if config_file is None:
        try:
            from src.app.shared.constants import CONFIG_FILE
            config_file = CONFIG_FILE
        except ImportError:
            pass
    
    if _gemini_client is None:
        _gemini_client = GeminiAI(config_file)
    
    return _gemini_client

def initialize_gemini(config_file: str) -> bool:
    """Initialize global AI client from config file."""
    client = get_gemini_client(config_file)
    return client.is_available()

def is_gemini_available() -> bool:
    """Check if global AI client is available."""
    return _gemini_client is not None and _gemini_client.is_available()

def is_gemini_ready() -> Tuple[bool, str]:
    """Check if global AI client is ready."""
    if _gemini_client is None:
        return False, "AI client not initialized"
    return _gemini_client.is_ready()

def get_ai_key():
    """Get the API key if available."""
    client = get_gemini_client()
    return getattr(client, '_api_key', None)

def get_ai_key_info():
    """Get the API key if available."""
    client = get_gemini_client()
    return getattr(client, '_api_key', None)

def get_ai_model():
    """Get the selected model if available."""
    client = get_gemini_client()
    return getattr(client, '_model_name', None)

def should_show_ai_panel():
    """Check if AI panel should be shown."""
    client = get_gemini_client()
    return getattr(client, '_enabled', False)

def is_ai_ready():
    """Check if AI is ready for use."""
    ready, _ = is_gemini_ready()
    return ready

def generate_ai_response(prompt: str, **kwargs) -> str:
    """Generate AI response using global client."""
    client = get_gemini_client()
    return client.generate_response(prompt, **kwargs)
