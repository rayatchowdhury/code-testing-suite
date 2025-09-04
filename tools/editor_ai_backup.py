import google.generativeai as genai
import json
import os
import logging
from google.api_core import retry_async
from typing import Optional, Tuple
from constants import USER_DATA_DIR
from utils.logging_config import LoggingConfig

# Ensure logging is configured before any gRPC operations
LoggingConfig.initialize()

# Additional gRPC suppression
try:
    # Monkey patch gRPC to suppress its internal logging
    import grpc._channel
    original_log = getattr(grpc._channel, '_log_operand_details', None)
    if original_log:
        setattr(grpc._channel, '_log_operand_details', lambda *args, **kwargs: None)
except ImportError:
    pass

class EditorAI:
    """AI-powered code editor assistant using Google's Gemini API."""
    
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

    BASE_PROMPT = """
    CRITICAL INSTRUCTION:
    - Return ONLY clean, properly formatted content
    - NO extra formatting or text markers
    - NO additional explanations or descriptions
    """

    CODE_BASE_PROMPT = BASE_PROMPT + """
    - NO markdown code blocks (```cpp, etc.)
    - Return ONLY working code
    - Must compile and run as-is
    """

    EXPLANATION_BASE = """
    # {title} 🔍

    {content}

    CODE TO ANALYZE:
    {code}
    """

    CODE_BASE = """
    {instruction}

    Guidelines:
    {guidelines}

    CODE:
    {code}

    strictly ensure the output is clean and properly formatted.
    """

    EXPLANATION_TEMPLATES = {
        'analysis': {
            'title': 'Code Analysis',
            'content': """
            ## Overview 🎯
            **Primary Purpose:** Main functionality and goals
            **Input/Output Flow:**
            - **Input:** Data types and formats
            - **Processing:** Key transformations
            - **Output:** Expected results
            **Language Elements:**
            - Core features used
            - Standard library usage
            - External dependencies
            
            ## Data & Logic Architecture 🏗️
            **Data Structures:**
            - **Structure:** Type - Purpose (Complexity)
            
            **Key Functions:**
            - **Function:** Parameters → Returns (Complexity) - Purpose
            
            **Variables & State:**
            - **Name (Scope):** Type - Role (Usage)
            
            ## Implementation Flow 🔄
            **1. Initialization Phase:**
            - Memory allocation
            - Variable setup
            - Initial validations
            
            **2. Core Processing:**
            ```text
            Step-by-step algorithm flow:
            1. Input processing
               └─ Validation & formatting
            2. Main logic execution
               ├─ Core operations
               ├─ Key decisions
               └─ Data transformations
            3. Result preparation
               ├─ Output formatting
               └─ Cleanup operations
            ```
            
            **3. Edge Cases & Error Handling:**
            - Boundary conditions
            - Input variations
            - Error scenarios
            
            ## Technical Details 🛠️
            **Complexity Analysis:**
            - **Time:** Overall O(x)
              - Best case: O(x)
              - Average case: O(x)
              - Worst case: O(x)
            - **Space:** O(x)
              - Stack: O(x)
              - Heap: O(x)
            
            **Dependencies:**
            - **Libraries:** Standard [list], External [list]
            - **System:** Memory [requirements], Resources [needs]
            
            **Optimization Potential:**
            - Current bottlenecks
            - Memory usage patterns
            - Performance critical paths
            """,
        },
        
        'issues': {
            'title': 'Code Issues Analysis',
            'content': """
            ## Critical Issues ❌
            **Logic & Correctness:**
            1. Algorithm implementation errors
            2. Invalid control flow
            3. Data handling mistakes
            
            **Resource Management:**
            1. Memory leaks and waste
            2. Resource cleanup issues
            3. Handle allocation problems

            ## Reliability Issues ⚠️
            **Edge Cases:**
            1. Boundary conditions
            2. Input validation gaps
            3. Error handling weaknesses
            
            **Performance Concerns:**
            1. Algorithm inefficiencies
            2. Resource misuse
            3. Optimization gaps

            ## Code Quality Issues ℹ️
            **Structure Problems:**
            1. Code organization
            2. Dependency issues
            3. Design pattern violations
            
            **Standard Violations:**
            1. Language conventions
            2. Library misuse
            3. Best practice deviations
            
            **Documentation Gaps:**
            1. Missing explanations
            2. Unclear comments
            3. Outdated documentation
            """,
        },
        
        'tips': {
            'title': 'Code Improvement Guide',
            'content': """
            ## Performance Optimizations 🚀
            **Algorithm Enhancements:**
            - **Current Implementation:**
              ```text
              [Show relevant code snippet]
              ```
            - **Suggested Changes:**
              ```text
              [Show relevant optimized code snippet]
              ```
            - **Expected Benefits:**
              - Time complexity: O(n) → O(log n)
              - Memory usage: Reduced by X%
              - Resource efficiency: [details]
            
            **Resource Usage:**
            - Memory Optimization
            - CPU Efficiency
            - I/O Improvements

            ## Code Quality Improvements 📖
            **Structure & Organization:**
            - **Current Structure:**
              ```text
              [Show current organization]
              ```
            - **Improved Structure:**
              ```text
              [Show better organization]
              ```
            
            **Readability:**
            - Naming Conventions
            - Code Formatting
            - Documentation

            ## Best Practices & Modern Features ⭐
            **Language Features:**
            - Modern Syntax
            - Built-in Functions
            - Standard Library Usage
            
            **Design Patterns:**
            - Applicable Patterns
            - Implementation Examples
            - Integration Steps
            """
        }
    }

    CODE_TEMPLATES = {
        'document': {
            'instruction': "Add comprehensive documentation to this code.",
            'guidelines': """
            1. File header with purpose and usage
            2. Function documentation (parameters, returns, edge cases)
            3. Important variable descriptions
            4. Complex logic explanations
            """
        },
        'custom': {
            'instruction': "Modify this code according to: {command}",
            'guidelines': """
            1. Apply only requested changes
            2. Keep all working functionality
            3. Add comments for significant changes
            4. Preserve existing code structure
            """
        },
        'generator': {
            'instruction': """
            Create a test case generator using generator.h
            Add clear parameter configuration guides.
            """,
            'guidelines': """
            1. Include "generator.h"
            2. Add configuration constants with:
               - Purpose and valid ranges
               - Effect on output
               - Special combinations
            3. Generate all data randomly
            4. No user input needed
            
            Library Documentation:
            {docs}
            """
        }
    }

    def __init__(self):
        """Initialize the EditorAI with model configuration."""
        # Logging is already configured by LoggingConfig
        self.model = None
        self._cached_models = None  # Cache for available models
        self.generator_docs = self._load_generator_description()
        self._setup_ai()

    def _get_available_models(self, force_refresh: bool = False) -> list:
        """Get list of available Gemini models that support generateContent."""
        # Return cached models unless forced to refresh
        if self._cached_models and not force_refresh:
            return self._cached_models
            
        try:
            import threading
            import time
            
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
                    import re
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

    def _setup_ai(self) -> None:
        """Configure the Gemini AI model."""
        try:
            api_key = self._load_api_key()
            if not api_key:
                logging.warning("No API key found - AI features will be disabled")
                return

            # Test API key format
            if not api_key.startswith('AIza') or len(api_key) < 35:
                logging.error("API key format appears invalid")
                return

            genai.configure(api_key=api_key)
            
            # Check for user-specified model first
            preferred_model = self._get_preferred_model()
            if preferred_model:
                if self._try_initialize_model(preferred_model):
                    return
                else:
                    logging.warning(f"User-specified model '{preferred_model}' failed, falling back to discovery")
            
            # Dynamically get available models
            available_models = self._get_available_models()
            
            if not available_models:
                logging.error("No available Gemini models found")
                return
            
            # Try models in order of preference
            for model_name in available_models:
                if self._try_initialize_model(model_name):
                    break
            
            if not self.model:
                logging.error("Failed to initialize any AI model")
                
        except Exception as e:
            logging.error(f"AI setup error: {e}")
            self.model = None
    
    def _get_preferred_model(self) -> Optional[str]:
        """Get user's preferred model from config."""
        try:
            config = self._load_config()
            ai_settings = config.get('ai_settings', {})
            return ai_settings.get('preferred_model')
        except Exception:
            return None
    
    def _try_initialize_model(self, model_name: str) -> bool:
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

    def _load_api_key(self) -> Optional[str]:
        """Load API key from config."""
        try:
            if not os.path.exists(USER_DATA_DIR):
                os.makedirs(USER_DATA_DIR, exist_ok=True)
                return None

            config_path = os.path.join(USER_DATA_DIR, 'config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Get API key from ai_settings section
            ai_settings = config.get('ai_settings', {})
            return ai_settings.get('gemini_api_key')
        except Exception as e:
            logging.error(f"API key load error: {e}")
            return None

    def _load_generator_description(self) -> str:
        """Load generator library docs."""
        try:
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              'tools', 'generator_description.txt')
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logging.error(f"Generator docs load error: {e}")
            return ""

    def refresh_model(self, force: bool = False) -> bool:
        """Refresh and reinitialize the AI model if needed."""
        if self.model and not force:
            return True  # Model is already working, no need to refresh
            
        logging.info("Attempting to refresh AI model...")
        self._setup_ai()
        return bool(self.model)

    def get_current_model_name(self) -> Optional[str]:
        """Get the name of the currently active model."""
        if self.model and hasattr(self.model, 'model_name'):
            return self.model.model_name
        return None
    
    def refresh_available_models(self) -> list:
        """Force refresh the cached model list from Google's API."""
        return self._get_available_models(force_refresh=True)

    @retry_async.AsyncRetry(predicate=retry_async.if_exception_type(Exception))
    async def _get_ai_response(self, prompt: str) -> Optional[str]:
        """Get AI response with retry and model refresh capability."""
        if not self.model:
            # Try to refresh model before failing
            if not self.refresh_model():
                api_key = self._load_api_key()
                if not api_key:
                    return "❌ AI service unavailable: No API key configured. Please check your settings."
                else:
                    return "❌ AI service unavailable: Model initialization failed. Please check your API key validity and network connection."
        
        try:
            current_model = self.get_current_model_name()
            logging.info(f"Sending request to AI model ({current_model})...")
            response = await self.model.generate_content_async(prompt, stream=False)
            if response and response.text:
                logging.info("AI response received successfully")
                return response.text
            else:
                logging.warning("AI response was empty")
                return "⚠️ AI returned an empty response. The request may have been blocked by safety filters. Please try rephrasing your code or question."
        except Exception as e:
            logging.error(f"AI response error: {e}")
            error_msg = str(e).lower()
            
            # If we get a model-related error, try refreshing the model
            if ("not found" in error_msg or "not supported" in error_msg or 
                "deprecated" in error_msg or "unavailable" in error_msg):
                logging.info("Model appears to be unavailable, attempting to refresh...")
                self.model = None  # Force refresh
                if self.refresh_model():
                    try:
                        response = await self.model.generate_content_async(prompt, stream=False)
                        if response and response.text:
                            logging.info("AI response successful after model refresh")
                            return response.text
                    except Exception as retry_error:
                        logging.error(f"Retry after model refresh failed: {retry_error}")
            
            # Return appropriate error message based on error type
            if 'quota' in error_msg or 'billing' in error_msg:
                return "❌ AI request failed: API quota exceeded or billing issue. Please check your Google Cloud Console."
            elif 'permission' in error_msg or 'unauthorized' in error_msg:
                return "❌ AI request failed: Invalid API key or insufficient permissions."
            elif 'network' in error_msg or 'connection' in error_msg:
                return "❌ AI request failed: Network connection error. Please check your internet connection."
            else:
                return f"❌ AI request failed: {str(e)}"

    def cleanup(self):
        """Clean up resources and connections."""
        try:
            if self.model:
                # Clear the model reference
                self.model = None
                
            # Clear any cached references
            if hasattr(self, 'generator_docs'):
                self.generator_docs = None
                
            # Force garbage collection to clean up any lingering gRPC connections
            import gc
            gc.collect()
            
            # Give gRPC connections time to close
            import time
            time.sleep(0.1)
            
        except Exception as e:
            # Use debug level to avoid noise during shutdown
            import logging
            logging.debug(f"Cleanup warning (can be ignored): {e}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except Exception:
            pass  # Ignore cleanup errors during destruction

    async def process_explanation(self, action: str, code: str) -> Optional[str]:
        """Handle explanation-type requests."""
        if action not in self.EXPLANATION_TEMPLATES:
            raise ValueError(f"Unknown explanation type: {action}")

        template = self.EXPLANATION_TEMPLATES[action]
        prompt = self.EXPLANATION_BASE.format(
            title=template['title'],
            content=template['content'],
            code=code
        )
        return await self._get_ai_response(prompt)

    async def process_code(self, action: str, code: str, **kwargs) -> Optional[str]:
        """Handle code-modification requests."""
        if action == 'generate':
            file_type = kwargs.get('type', 'solution')
            if file_type.lower().endswith('generator.cpp'):
                template = self.CODE_TEMPLATES['generator']
                prompt = self.CODE_BASE.format(
                    instruction=template['instruction'],
                    guidelines=template['guidelines'].format(docs=self.generator_docs),
                    code=code
                )
            else:
                prompt = f"{self.CODE_BASE_PROMPT}\nCreate a {file_type} solution.\n\nCODE:\n{code}"
        else:
            template = self.CODE_TEMPLATES.get(action)
            if not template:
                raise ValueError(f"Unknown code action: {action}")
                
            prompt = self.CODE_BASE.format(
                instruction=template['instruction'].format(**kwargs),
                guidelines=template['guidelines'],
                code=code
            )

        return await self._get_ai_response(self.CODE_BASE_PROMPT + "\n\n" + prompt)

    # Additional methods expected by tests
    def configure(self):
        """Configure the AI system - only if not already configured."""
        if not self.model:
            self._setup_ai()
    
    def _load_config(self):
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
    
    def _get_api_key(self):
        """Get API key from config."""
        return self._load_api_key()
    
    def is_ai_enabled(self):
        """Check if AI is enabled and configured."""
        return self.model is not None
    
    async def analyze_code(self, code):
        """Analyze code and provide insights."""
        if not self.is_ai_enabled():
            return {"error": "AI not configured", "content": ""}
        
        try:
            result = await self.process_explanation('analysis', code)
            return {"error": None, "content": result or ""}
        except Exception as e:
            return {"error": str(e), "content": ""}
    
    async def fix_issues(self, code):
        """Fix issues in the provided code."""
        if not self.is_ai_enabled():
            return {"error": "AI not configured", "content": ""}
        
        try:
            result = await self.process_code('fix', code)
            return {"error": None, "content": result or ""}
        except Exception as e:
            return {"error": str(e), "content": ""}
    
    async def optimize_code(self, code):
        """Optimize the provided code."""
        if not self.is_ai_enabled():
            return {"error": "AI not configured", "content": ""}
        
        try:
            result = await self.process_code('optimize', code)
            return {"error": None, "content": result or ""}
        except Exception as e:
            return {"error": str(e), "content": ""}
    
    async def document_code(self, code):
        """Add documentation to the provided code."""
        if not self.is_ai_enabled():
            return {"error": "AI not configured", "content": ""}
        
        try:
            result = await self.process_code('document', code)
            return {"error": None, "content": result or ""}
        except Exception as e:
            return {"error": str(e), "content": ""}
