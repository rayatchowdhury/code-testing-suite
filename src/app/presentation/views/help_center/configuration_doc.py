"""
Configuration Guide Help Document - Application settings and configuration
"""

from .help_doc_engine import HelpDocument


class ConfigurationDoc(HelpDocument):
    """Configuration guide help document"""
    
    def __init__(self, parent=None):
        sections = [
            ("⚙️", "C++ Settings", "", [
                "C++ Version: Select your preferred C++ standard (11/14/17/20)",
                "Compiler Flags: Set optimization levels and warning flags",
                "Include Path: Configure additional include directories"
            ]),
             
            ("📁", "Workspace Settings", "", [
                "Workspace Path: Set your default code workspace location",
                "Auto-save: Enable/disable automatic file saving",
                "Auto-save Interval: Set time between auto-saves"
            ]),
            
            ("🎨", "Editor Settings", "", [
                "Font Size: Adjust text display size",
                "Tab Width: Set number of spaces per tab",
                "Bracket Matching: Enable/disable automatic bracket pairing"
            ]),
            
            ("🤖", "AI Integration", "", [
                "API Key: Set up your Gemini API key for AI features",
                "Response Format: Configure AI response formatting",
                "Context Length: Set maximum tokens for AI context"
            ])
        ]
        
        super().__init__("Configuration Guide", sections, parent)


def create_configuration_doc():
    """Factory function for configuration document"""
    return ConfigurationDoc()
