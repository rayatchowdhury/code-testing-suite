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

    CODE_BASE_PROMPT = (
        BASE_PROMPT
        + """
    - NO markdown code blocks (```cpp, etc.)
    - Return ONLY working code
    - Must compile and run as-is
    """
    )

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
        "analysis": {
            "title": "Code Analysis",
            "content": """
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
            """,
        },
        "issues": {
            "title": "Potential Issues & Edge Cases",
            "content": """
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
            """,
        },
        "tips": {
            "title": "Improvement Tips & Suggestions",
            "content": """
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
            """,
        },
    }

    # Code modification templates
    CODE_TEMPLATES = {
        "document": {
            "instruction": "Add comprehensive documentation to this code.",
            "guidelines": """
            1. File header with purpose and usage
            2. Function documentation (parameters, returns, edge cases)
            3. Important variable descriptions
            4. Complex logic explanations
            """,
        },
        "custom": {
            "instruction": "Modify this code according to: {command}",
            "guidelines": """
            1. Apply only requested changes
            2. Keep all working functionality
            3. Add comments for significant changes
            4. Preserve existing code structure
            """,
        },
        "generator": {
            "instruction": """
            Create a C++ test case generator based on the provided code/problem.
            
            TASK: Generate ONE random test case that matches the input pattern from the code.
            Analyze the code structure to understand input format, even if no explicit problem statement exists.
            
            CRITICAL: Return ONLY the generator.cpp code - NO solutions, NO explanations, NO markdown blocks.
            """,
            "guidelines": """
            GENERATOR REQUIREMENTS:
            1. #include "generator.h" at the top
            2. Write main() function that generates ONE test case to stdout
            3. Use generator.h functions for all randomization
            4. Add only minimal necessary comments
            5. Must compile and run as-is
            
            ANALYZE THE CODE FOR INPUT PATTERNS:
            - cin >> n, cin >> arr[i] → Array input
            - cin >> s → String input  
            - cin >> t followed by t test cases → Multiple test cases
            - cin >> n >> m → Grid/graph dimensions
            - Vector/array operations → Determine data types
            - Nested loops → Matrix or graph structures
            - String operations → Character constraints
            
            COMMON COMPETITIVE PROGRAMMING PATTERNS:
            - Single array: n, then n integers
            - Graph: n vertices, m edges, then m pairs
            - Matrix: n×m, then n rows of m elements
            - String problems: length n, then string of length n
            - Multiple queries: q, then q query lines
            - Tree: n nodes, then n-1 edges
            
            INFER FROM CODE STRUCTURE:
            - If you see vector<int> → use rvector<int>
            - If you see string → use rstring  
            - If you see graph/adjacency → use Graph or Tree
            - If you see coordinates → use points
            - If you see sorting/permutation → use permutation
            - If you see multiple test cases → generate T, then T cases
            
            GENERATOR.H QUICK REFERENCE:
            - random<int>(l, r) - random integer in [l,r]
            - rvector<int>(n, l, r) - vector of n random ints
            - rstring(len, charset) - random string
            - permutation(n) - random permutation of 1..n
            - Tree<int>(n) - random tree with n vertices
            - Graph<int>(n, m) - random graph n vertices, m edges
            - points(n, xl, xr, yl, yr) - n random 2D points
            - All have .print() method
            
            REALISTIC CONSTRAINTS:
            - Arrays: 1-100 or 1-1000 elements typically
            - Strings: 1-50 or 1-100 length typically  
            - Numbers: reasonable ranges like 1-10^6
            - Multiple test cases: 1-10 typically
            
            Library Documentation:
            {docs}
            """,
        },
        "validator": {
            "instruction": """
            Create a minimal C++ validator that checks if test output is valid for given input.
            
            TASK: Write clean validator.cpp that reads input.txt and output.txt, validates correctness silently.
            Analyze the code to understand what constitutes valid output.
            
            CRITICAL: Return ONLY clean validator.cpp code - NO explanations, NO debug prints, NO verbose comments.
            """,
            "guidelines": """
            VALIDATOR RULES:
            1. Use argc/argv for file paths: argv[1]=input.txt, argv[2]=output.txt
            2. Exit codes: 0=invalid, 1=valid, 2=error
            3. NO cout/cerr messages (silent validation)
            4. Minimal comments only
            5. Clean, concise code
            
            TEMPLATE STRUCTURE:
            #include <iostream>
            #include <fstream>
            using namespace std;
            
            bool isValid(/* input variables */, /* output variables */) {
                if (/* output according to input */)
                    return true;
                return false;
            }
            
            int main(int argc, char* argv[]) {
                if (argc < 3) return 2;
                ifstream in(argv[1]), out(argv[2]);
                if (!in || !out) return 2;
                
                // Read input variables
                // Read output variables  
                return isValid(/* pass variables */) ? 1 : 0;
            }
            
            VALIDATION APPROACH:
            - Create isValid() function with input and output parameters
            - Read input variables from argv[1]
            - Read output variables from argv[2] 
            - Call isValid() with the variables
            - Return 1 if valid, 0 if invalid, 2 if error
            
            STRUCTURE REQUIREMENTS:
            - Separate validation logic in isValid() function
            - Clean main() that handles I/O and calls isValid()
            - Pass specific variables, not file streams to isValid()
            
            COMMON PATTERNS:
            - Math: Check calculation correctness
            - Arrays: Verify sorting/permutation properties
            - Graphs: Validate paths/connectivity
            - Strings: Check transformations
            - Multiple solutions: Validate properties, not exact values
            
            KEEP IT SIMPLE:
            - No debug output
            - No verbose error messages
            - Focus on core validation logic
            - Minimal necessary code only
            """,
        },
    }

    @classmethod
    def get_explanation_prompt(cls, template_type: str, code: str) -> str:
        """Get a formatted explanation prompt."""
        template = cls.EXPLANATION_TEMPLATES.get(template_type)
        if not template:
            raise ValueError(f"Unknown explanation template: {template_type}")

        return cls.EXPLANATION_BASE.format(
            title=template["title"], content=template["content"], code=code
        )

    @classmethod
    def get_code_prompt(cls, action: str, code: str, **kwargs) -> str:
        """Get a formatted code modification prompt."""
        if action == "generate":
            file_type = kwargs.get("type", "solution")
            # Check if this is a generator file request
            if (
                file_type.lower().endswith("generator.cpp")
                or file_type.lower().endswith("generator")
                or "generator" in file_type.lower()
            ):
                template = cls.CODE_TEMPLATES["generator"]
                docs = kwargs.get("docs", "")
                return cls.CODE_BASE.format(
                    instruction=template["instruction"],
                    guidelines=template["guidelines"].format(docs=docs),
                    code=code,
                )

            return f"{cls.CODE_BASE_PROMPT}\nCreate a {file_type} solution.\n\nCODE:\n{code}"
        if action == "validator":
            # Handle validator template directly
            template = cls.CODE_TEMPLATES["validator"]
            return cls.CODE_BASE.format(
                instruction=template["instruction"],
                guidelines=template["guidelines"],
                code=code,
            )

        template = cls.CODE_TEMPLATES.get(action)
        if not template:
            raise ValueError(f"Unknown code action: {action}")

            return cls.CODE_BASE.format(
                instruction=template["instruction"].format(**kwargs),
                guidelines=template["guidelines"],
                code=code,
            )

    @classmethod
    def get_custom_prompt(cls, command: str, code: str) -> str:
        """Get a prompt for custom commands."""
        return cls.get_code_prompt("custom", code, command=command)
