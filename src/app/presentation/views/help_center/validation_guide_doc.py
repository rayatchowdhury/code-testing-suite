"""
Validation Guide Help Document - Code validation features and usage
"""

from .help_doc_engine import HelpDocument


class ValidationGuideDoc(HelpDocument):
    """Validation guide help document"""
    
    def __init__(self, parent=None):
        sections = [
            ("📋", "Overview", 
             "The Code Validator helps you maintain high-quality code by checking for syntax errors, style issues, code quality, security issues, and performance warnings."),
             
            ("🚀", "Getting Started", "", [
                "Open the Validator: Click the 'Validate' button in the main navigation",
                "Load Your Code: Use file buttons to switch between main code, test cases, and style guides",
                "Set Strictness Level: Use the validation strictness slider (1-Lenient to 5-Very Strict)",
                "Run Validation: Click the validation button to analyze your code"
            ]),
            
            ("🔍", "Validation Types", "", [
                "Syntax Errors: Code that won't compile",
                "Style Issues: Formatting and naming conventions", 
                "Code Quality: Best practices and maintainability",
                "Security Issues: Potential vulnerabilities",
                "Performance Warnings: Optimization opportunities"
            ]),
            
            ("📊", "Understanding Results", "", [
                "Error Level: Critical issues that prevent compilation",
                "Warning Level: Style and quality improvements",
                "Info Level: General suggestions and tips",
                "Color Coding: Red for errors, orange for warnings, blue for info"
            ])
        ]
        
        super().__init__("Code Validation Guide", sections, parent)


def create_validation_guide_doc():
    """Factory function for validation guide document"""
    return ValidationGuideDoc()
