"""
About Help Document - Application information and credits
"""

from .help_doc_engine import HelpDocument


class AboutDoc(HelpDocument):
    """About help document"""
    
    def __init__(self, parent=None):
        sections = [
            ("📌", "Version", "", [
                "Version 1.0.0",
                "Built with Python and PySide6"
            ]),
             
            ("🎯", "Purpose", 
             "Code Testing Suite is designed to help competitive programmers test and optimize their solutions efficiently. It combines code editing, comparison testing, and performance analysis in one integrated environment."),
            
            ("🔧", "Technologies", "", [
                "Python with PySide6 for the UI framework",
                "Gemini AI API for intelligent code assistance",
                "QScintilla for advanced code editing",
                "Material Design inspired styling"
            ]),
            
            ("👨‍💻", "Developer", "", [
                "Developed by Rayat Chowdhury",
                "Student, Department of CSE, MBSTU", 
                "Contact: rayated.ray@gmail.com"
            ]),
            
            ("📞", "Report Issues", 
             "Found a bug or have a suggestion? Feel free to contact the developer.")
        ]
        
        super().__init__("About Code Testing Suite", sections, parent)


def create_about_doc():
    """Factory function for about document"""
    return AboutDoc()
