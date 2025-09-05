"""
API Key Validation Utility

Provides actual API validation for Gemini API keys.
"""

import asyncio
import aiohttp
import json
from typing import Tuple, Optional
from PySide6.QtCore import QThread, Signal

class APIValidationThread(QThread):
    """Thread for validating API keys without blocking the UI"""
    
    validationComplete = Signal(bool, str)  # (is_valid, message)
    
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        
    def run(self):
        """Run the validation in a separate thread"""
        try:
            # Run the async validation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            is_valid, message = loop.run_until_complete(self._validate_api_key())
            loop.close()
            
            self.validationComplete.emit(is_valid, message)
        except Exception as e:
            self.validationComplete.emit(False, f"Validation error: {str(e)}")
    
    async def _validate_api_key(self) -> Tuple[bool, str]:
        """
        Validate Gemini API key by making a test request
        Returns: (is_valid, message)
        """
        if not self.api_key or len(self.api_key) < 10:
            return False, "API key is too short"
        
        # Test URL for Gemini API (list models endpoint - lightweight test)
        test_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"
        
        try:
            timeout = aiohttp.ClientTimeout(total=10)  # 10 second timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(test_url) as response:
                    if response.status == 200:
                        # Try to parse the response to ensure it's valid JSON
                        data = await response.json()
                        if 'models' in data:
                            return True, "API key is valid"
                        else:
                            return False, "Unexpected API response format"
                    elif response.status == 400:
                        error_text = await response.text()
                        if "API_KEY_INVALID" in error_text or "invalid" in error_text.lower():
                            return False, "Invalid API key"
                        else:
                            return False, f"API error: {error_text}"
                    elif response.status == 403:
                        return False, "API key lacks required permissions"
                    elif response.status == 429:
                        return False, "API quota exceeded - but key appears valid"
                    else:
                        return False, f"API request failed with status {response.status}"
                        
        except asyncio.TimeoutError:
            return False, "API validation timed out - check your internet connection"
        except aiohttp.ClientError as e:
            return False, f"Network error: {str(e)}"
        except json.JSONDecodeError:
            return False, "Invalid API response format"
        except Exception as e:
            return False, f"Validation failed: {str(e)}"

class APIValidator:
    """Utility class for API key validation"""
    
    @staticmethod
    def validate_key_async(api_key: str, callback):
        """
        Validate API key asynchronously
        callback should accept (is_valid: bool, message: str)
        """
        if not api_key or len(api_key) < 10:
            callback(False, "API key is too short")
            return None
            
        thread = APIValidationThread(api_key)
        thread.validationComplete.connect(callback)
        thread.start()
        return thread
    
    @staticmethod
    def quick_format_check(api_key: str) -> Tuple[bool, str]:
        """
        Quick format validation without API calls
        Returns: (passes_basic_check, message)
        """
        if not api_key:
            return False, "No API key provided"
        
        if len(api_key) < 20:
            return False, "API key is too short"
        
        if len(api_key) > 100:
            return False, "API key is too long"
            
        # Basic format check for Gemini API keys
        if not api_key.replace('_', '').replace('-', '').isalnum():
            return False, "API key contains invalid characters"
            
        return True, "Format looks valid"
