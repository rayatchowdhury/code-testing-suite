import google.generativeai as genai
import json
import os
import logging
from google.api_core import retry_async
from absl import logging as absl_logging
from typing import Optional, Tuple
from constants import USER_DATA_DIR

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
        absl_logging.use_absl_handler()
        absl_logging.set_verbosity(absl_logging.WARNING)
        self.model = None
        self.generator_docs = self._load_generator_description()
        self._setup_ai()

    def _setup_ai(self) -> None:
        """Configure the Gemini AI model."""
        try:
            api_key = self._load_api_key()
            if not api_key:
                return

            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name='gemini-2.0-flash',
                generation_config=self.MODEL_CONFIG,
                safety_settings=self.SAFETY_SETTINGS
            )
        except Exception as e:
            logging.error(f"AI setup error: {e}")
            self.model = None

    def _load_api_key(self) -> Optional[str]:
        """Load API key from config."""
        try:
            if not os.path.exists(USER_DATA_DIR):
                os.makedirs(USER_DATA_DIR, exist_ok=True)
                return None

            config_path = os.path.join(USER_DATA_DIR, 'config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config.get('gemini_api_key')
        except Exception as e:
            logging.error(f"API key load error: {e}")
            return None

    def _load_generator_description(self) -> str:
        """Load generator library docs."""
        try:
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              'tools', 'generator_description.txt')
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            logging.error(f"Generator docs load error: {e}")
            return ""

    @retry_async.AsyncRetry(predicate=retry_async.if_exception_type(Exception))
    async def _get_ai_response(self, prompt: str) -> Optional[str]:
        """Get AI response with retry."""
        if not self.model:
            return "AI service not available. Please check your API key configuration."
        try:
            response = await self.model.generate_content_async(prompt, stream=False)
            return response.text
        except Exception as e:
            logging.error(f"AI response error: {e}")
            raise

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
        """Configure the AI system."""
        self._setup_ai()
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            if not os.path.exists(USER_DATA_DIR):
                return {}
            
            config_path = os.path.join(USER_DATA_DIR, 'config.json')
            if not os.path.exists(config_path):
                return {}
                
            with open(config_path, 'r') as f:
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
