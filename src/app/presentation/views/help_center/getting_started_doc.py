"""
Getting Started Help Document - Quick start guide
"""

from .help_doc_engine import HelpDocument


class GettingStartedDoc(HelpDocument):
    """Getting started help document"""
    
    def __init__(self, parent=None):
        sections = [
            ("👋", "Welcome", 
             "Welcome to Code Testing Suite! This guide will help you get started with the essential features of the application."),
             
            ("🚀", "Quick Start", "", [
                "Launch the Code Editor from the main window",
                "Create a new file or open an existing one",
                "Write or paste your code",
                "Use the integrated console for compilation and execution"
            ]),
            
            ("🎯", "Key Features", "", [
                "Advanced code editor with syntax highlighting",
                "Integrated comparison testing capabilities",
                "Time limit execution testing",
                "AI-powered code assistance"
            ])
        ]
        
        super().__init__("Getting Started", sections, parent)


def create_getting_started_doc():
    """Factory function for getting started document"""
    return GettingStartedDoc()
