# -*- coding: utf-8 -*-
"""
Prompt Templates for AI interactions.

Contains all prompts and templates used for different AI operations.
"""

class PromptTemplates:
    """Collection of prompt templates for various AI operations."""
    
    # Base prompts
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

    # Explanation templates structure
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

    # Explanation templates for different types of analysis
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
            - Setup and configuration steps
            
            **2. Main Processing:**
            - Core algorithm implementation
            - Data transformation steps
            
            **3. Output Generation:**
            - Result formatting and delivery
            
            ## Edge Cases & Considerations ⚠️
            **Input Validation:**
            - Expected input ranges
            - Error handling approaches
            
            **Performance Notes:**
            - Time/space complexity
            - Optimization opportunities
            
            **Potential Issues:**
            - Common failure points
            - Debugging suggestions
            """
        },
        'issues': {
            'title': 'Potential Issues & Edge Cases',
            'content': """
            ## Critical Issues 🚨
            **Immediate Concerns:**
            
            ## Logic & Algorithm Issues 🔧
            **Potential Problems:**
            
            ## Input/Output Issues 📝
            **Data Handling:**
            
            ## Edge Cases 🎯
            **Boundary Conditions:**
            
            ## Performance Concerns ⚡
            **Efficiency Issues:**
            
            ## Best Practice Violations 📋
            **Code Quality:**
            
            ## Security Considerations 🔒
            **Vulnerability Assessment:**
            """
        },
        'tips': {
            'title': 'Improvement Tips & Suggestions',
            'content': """
            ## Quick Wins 🚀
            **Immediate Improvements:**
            
            ## Code Quality 📝
            **Structure & Style:**
            
            ## Performance Optimization ⚡
            **Speed & Efficiency:**
            
            ## Error Handling 🛡️
            **Robustness:**
            
            ## Best Practices 📋
            **Industry Standards:**
            
            ## Advanced Techniques 🎯
            **Next Level:**
            
            ## Testing & Debugging 🔍
            **Quality Assurance:**
            """
        }
    }

    # Code modification templates
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

    @classmethod
    def get_explanation_prompt(cls, template_type: str, code: str) -> str:
        """Get a formatted explanation prompt."""
        template = cls.EXPLANATION_TEMPLATES.get(template_type)
        if not template:
            raise ValueError(f"Unknown explanation template: {template_type}")
        
        return cls.EXPLANATION_BASE.format(
            title=template['title'],
            content=template['content'],
            code=code
        )

    @classmethod
    def get_code_prompt(cls, action: str, code: str, **kwargs) -> str:
        """Get a formatted code modification prompt."""
        if action == 'generate':
            file_type = kwargs.get('type', 'solution')
            if file_type.lower().endswith('generator.cpp'):
                template = cls.CODE_TEMPLATES['generator']
                docs = kwargs.get('docs', '')
                return cls.CODE_BASE.format(
                    instruction=template['instruction'],
                    guidelines=template['guidelines'].format(docs=docs),
                    code=code
                )
            else:
                return f"{cls.CODE_BASE_PROMPT}\nCreate a {file_type} solution.\n\nCODE:\n{code}"
        else:
            template = cls.CODE_TEMPLATES.get(action)
            if not template:
                raise ValueError(f"Unknown code action: {action}")
            
            return cls.CODE_BASE.format(
                instruction=template['instruction'].format(**kwargs),
                guidelines=template['guidelines'],
                code=code
            )

    @classmethod
    def get_custom_prompt(cls, command: str, code: str) -> str:
        """Get a prompt for custom commands."""
        return cls.get_code_prompt('custom', code, command=command)
