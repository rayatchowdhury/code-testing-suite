"""
Help Center Content Data - Centralized storage for all help documentation
All help content defined here using HelpSectionData from qt_doc_engine
"""

from typing import List, Dict
from ..qt_doc_engine import HelpSectionData

# Alias for backwards compatibility and cleaner code
HelpSection = HelpSectionData


HELP_DOCUMENTS: Dict[str, Dict[str, any]] = {
    'Introduction': {
        'title': "Welcome to Code Testing Suite",
        'sections': [
            HelpSection(
                icon="👋",
                title="Introduction",
                content="Code Testing Suite is your comprehensive toolkit for competitive programming. Whether you're practicing for competitions or developing algorithmic solutions, our suite provides everything you need."
            ),
             
            HelpSection(
                icon="🚀",
                title="Main Features",
                items=[
                    "Advanced Code Editor with AI assistance",
                    "Comparison Testing for finding edge cases", 
                    "Benchmark Testing for performance optimization",
                    "Integrated compilation and execution"
                ]
            ),
            
            HelpSection(
                icon="📚",
                title="Using This Help",
                items=[
                    "Browse topics using the sidebar navigation",
                    "Each section provides detailed guidance",
                    "Check the FAQ for common questions", 
                    "Use Configuration for customization"
                ]
            )
        ]
    },
    
    'Getting Started': {
        'title': "Getting Started",
        'sections': [
            HelpSection(
                icon="👋",
                title="Welcome",
                content="Welcome to Code Testing Suite! This guide will help you get started with the essential features of the application."
            ),
             
            HelpSection(
                icon="🚀",
                title="Quick Start",
                items=[
                    "Launch the Code Editor from the main window",
                    "Create a new file or open an existing one",
                    "Write or paste your code",
                    "Use the integrated console for compilation and execution"
                ]
            ),
            
            HelpSection(
                icon="🎯",
                title="Key Features",
                items=[
                    "Advanced code editor with syntax highlighting",
                    "Integrated comparison testing capabilities",
                    "Time limit execution testing",
                    "AI-powered code assistance"
                ]
            )
        ]
    },
    
    'Code Editor Guide': {
        'title': "Code Editor Guide",
        'sections': [
            HelpSection(
                icon="📝",
                title="Basic Operations",
                items=[
                    "Create new files using the \"New File\" button",
                    "Open existing files with \"Open File\"",
                    "Save your work using Ctrl+S or the \"Save\" button",
                    "Multiple files can be managed using tabs"
                ]
            ),
             
            HelpSection(
                icon="🤖",
                title="AI Features",
                items=[
                    "Analysis: Get detailed explanation of selected code",
                    "Fix: Get suggestions for code improvements",
                    "Optimize: Receive optimization recommendations", 
                    "Document: Generate code documentation"
                ]
            ),
            
            HelpSection(
                icon="⚡",
                title="Shortcuts",
                items=[
                    "Ctrl+N: New File",
                    "Ctrl+O: Open File", 
                    "Ctrl+S: Save",
                    "Ctrl+F: Find",
                    "F5: Run Code"
                ]
            )
        ]
    },
    
    'Comparison Guide': {
        'title': "Comparison Testing Guide",
        'sections': [
            HelpSection(
                icon="🔍",
                title="What is Comparison Testing?",
                content="Comparison testing helps find edge cases by comparing your solution against a correct but slower solution using randomly generated test cases."
            ),
             
            HelpSection(
                icon="📝",
                title="Required Components",
                items=[
                    "Main Solution: Your optimized solution",
                    "Brute Force: A simple, correct solution",
                    "Test Generator: Creates random test cases"
                ]
            ),
            
            HelpSection(
                icon="🎯",
                title="How to Use",
                items=[
                    "Write your main and brute force solutions",
                    "Create a test case generator",
                    "Set number of test iterations",
                    "Run comparison test to find mismatches"
                ]
            )
        ]
    },
    
    'Benchmarking Guide': {
        'title': "Benchmark Testing Guide",
        'sections': [
            HelpSection(
                icon="⏱️",
                title="Performance Benchmarking",
                content="Benchmark Testing helps ensure your solution meets time constraints by simulating contest-like execution environments."
            ),
             
            HelpSection(
                icon="⚡",
                title="Features",
                items=[
                    "Set custom time limits",
                    "Monitor memory usage",
                    "Multiple test case execution",
                    "Performance metrics analysis"
                ]
            ),
            
            HelpSection(
                icon="📊",
                title="Performance Analysis",
                items=[
                    "Execution time breakdown",
                    "Memory usage patterns",
                    "Performance bottleneck detection",
                    "Optimization suggestions"
                ]
            )
        ]
    },
    
    'Validation Guide': {
        'title': "Code Validation Guide",
        'sections': [
            HelpSection(
                icon="📋",
                title="Overview",
                content="The Code Validator helps you maintain high-quality code by checking for syntax errors, style issues, code quality, security issues, and performance warnings."
            ),
             
            HelpSection(
                icon="🚀",
                title="Getting Started",
                items=[
                    "Open the Validator: Click the 'Validate' button in the main navigation",
                    "Load Your Code: Use file buttons to switch between main code, test cases, and style guides",
                    "Set Strictness Level: Use the validation strictness slider (1-Lenient to 5-Very Strict)",
                    "Run Validation: Click the validation button to analyze your code"
                ]
            ),
            
            HelpSection(
                icon="🔍",
                title="Validation Types",
                items=[
                    "Syntax Errors: Code that won't compile",
                    "Style Issues: Formatting and naming conventions", 
                    "Code Quality: Best practices and maintainability",
                    "Security Issues: Potential vulnerabilities",
                    "Performance Warnings: Optimization opportunities"
                ]
            ),
            
            HelpSection(
                icon="📊",
                title="Understanding Results",
                items=[
                    "Error Level: Critical issues that prevent compilation",
                    "Warning Level: Style and quality improvements",
                    "Info Level: General suggestions and tips",
                    "Color Coding: Red for errors, orange for warnings, blue for info"
                ]
            )
        ]
    },
    
    'Results Guide': {
        'title': "Results & Analytics Guide",
        'sections': [
            HelpSection(
                icon="📊",
                title="Overview",
                items=[
                    "View comprehensive test result history from comparison and benchmark tests",
                    "Analyze performance trends and success rates over time",
                    "Filter results by test type, date range, and project",
                    "Export results for external analysis"
                ]
            ),
             
            HelpSection(
                icon="📈",
                title="Statistics View",
                items=[
                    "Overall success rate tracking across all tests",
                    "Test type breakdown (Comparison vs Benchmark tests)",
                    "Average execution time analysis",
                    "Recent activity summary"
                ]
            ),
            
            HelpSection(
                icon="🔍",
                title="Detailed Analysis",
                items=[
                    "Click any test result to view detailed information",
                    "See input/output data for failed test cases",
                    "Review execution times and performance metrics",
                    "Track improvements in code efficiency"
                ]
            ),
            
            HelpSection(
                icon="💾",
                title="Data Management",
                items=[
                    "Export results to CSV format",
                    "Clear old test data to save space",
                    "Backup important test results",
                    "Share results with team members"
                ]
            )
        ]
    },
    
    'Configuration': {
        'title': "Configuration Guide",
        'sections': [
            HelpSection(
                icon="⚙️",
                title="C++ Settings",
                items=[
                    "C++ Version: Select your preferred C++ standard (11/14/17/20)",
                    "Compiler Flags: Set optimization levels and warning flags",
                    "Include Path: Configure additional include directories"
                ]
            ),
             
            HelpSection(
                icon="📁",
                title="Workspace Settings",
                items=[
                    "Workspace Path: Set your default code workspace location",
                    "Auto-save: Enable/disable automatic file saving",
                    "Auto-save Interval: Set time between auto-saves"
                ]
            ),
            
            HelpSection(
                icon="🎨",
                title="Editor Settings",
                items=[
                    "Font Size: Adjust text display size",
                    "Tab Width: Set number of spaces per tab",
                    "Bracket Matching: Enable/disable automatic bracket pairing"
                ]
            ),
            
            HelpSection(
                icon="🤖",
                title="AI Integration",
                items=[
                    "API Key: Set up your Gemini API key for AI features",
                    "Response Format: Configure AI response formatting",
                    "Context Length: Set maximum tokens for AI context"
                ]
            )
        ]
    },
    
    'About': {
        'title': "About Code Testing Suite",
        'sections': [
            HelpSection(
                icon="📌",
                title="Version",
                items=[
                    "Version 1.0.0",
                    "Built with Python and PySide6"
                ]
            ),
             
            HelpSection(
                icon="🎯",
                title="Purpose",
                content="Code Testing Suite is designed to help competitive programmers test and optimize their solutions efficiently. It combines code editing, comparison testing, and performance analysis in one integrated environment."
            ),
            
            HelpSection(
                icon="🔧",
                title="Technologies",
                items=[
                    "Python with PySide6 for the UI framework",
                    "Gemini AI API for intelligent code assistance",
                    "QScintilla for advanced code editing",
                    "Material Design inspired styling"
                ]
            ),
            
            HelpSection(
                icon="👨‍💻",
                title="Developer",
                items=[
                    "Developed by Rayat Chowdhury",
                    "Student, Department of CSE, MBSTU", 
                    "Contact: rayated.ray@gmail.com"
                ]
            ),
            
            HelpSection(
                icon="📞",
                title="Report Issues",
                content="Found a bug or have a suggestion? Feel free to contact the developer."
            )
        ]
    }
}


def get_document_data(topic: str) -> Dict[str, any]:
    """
    Get document data for a specific topic
    
    Args:
        topic: The help topic name
        
    Returns:
        Dictionary containing 'title' and 'sections' keys
        Returns a "not found" document if topic doesn't exist
    """
    if topic in HELP_DOCUMENTS:
        return HELP_DOCUMENTS[topic]
    
    # Return fallback for unknown topics
    return {
        'title': topic,
        'sections': [
            HelpSection(
                icon="⚠️",
                title="Content Not Found",
                content=f"The help section '{topic}' is currently under development."
            )
        ]
    }


def get_available_topics() -> List[str]:
    """Get list of all available help topics"""
    return list(HELP_DOCUMENTS.keys())
