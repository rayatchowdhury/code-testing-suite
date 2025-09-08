"""
Code Editor Guide Help Document - Code editor features and usage
"""

from .help_doc_engine import HelpDocument


class CodeEditorGuideDoc(HelpDocument):
    """Code editor guide help document"""
    
    def __init__(self, parent=None):
        sections = [
            ("📝", "Basic Operations", "", [
                "Create new files using the \"New File\" button",
                "Open existing files with \"Open File\"",
                "Save your work using Ctrl+S or the \"Save\" button",
                "Multiple files can be managed using tabs"
            ]),
             
            ("🤖", "AI Features", "", [
                "Analysis: Get detailed explanation of selected code",
                "Fix: Get suggestions for code improvements",
                "Optimize: Receive optimization recommendations", 
                "Document: Generate code documentation"
            ]),
            
            ("⚡", "Shortcuts", "", [
                "Ctrl+N: New File",
                "Ctrl+O: Open File", 
                "Ctrl+S: Save",
                "Ctrl+F: Find",
                "F5: Run Code"
            ])
        ]
        
        super().__init__("Code Editor Guide", sections, parent)


def create_code_editor_guide_doc():
    """Factory function for code editor guide document"""
    return CodeEditorGuideDoc()
