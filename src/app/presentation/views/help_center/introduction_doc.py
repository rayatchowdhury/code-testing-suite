"""
Introduction Help Document - Welcome and overview content
"""

from .help_doc_engine import HelpDocument


class IntroductionDoc(HelpDocument):
    """Introduction help document"""
    
    def __init__(self, parent=None):
        sections = [
            ("👋", "Introduction", 
             "Code Testing Suite is your comprehensive toolkit for competitive programming. Whether you're practicing for competitions or developing algorithmic solutions, our suite provides everything you need."),
             
            ("🚀", "Main Features", "", [
                "Advanced Code Editor with AI assistance",
                "Comparison Testing for finding edge cases", 
                "Benchmark Testing for performance optimization",
                "Integrated compilation and execution"
            ]),
            
            ("📚", "Using This Help", "", [
                "Browse topics using the sidebar navigation",
                "Each section provides detailed guidance",
                "Check the FAQ for common questions", 
                "Use Configuration for customization"
            ])
        ]
        
        super().__init__("Welcome to Code Testing Suite", sections, parent)


def create_introduction_doc():
    """Factory function for introduction document"""
    return IntroductionDoc()
