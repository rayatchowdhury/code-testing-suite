"""
Main Window Content Data - Pure content without UI dependencies
Feature data and configuration for the main welcome screen
"""

from typing import List, Tuple


# Application feature data: (title, accent_color, features)
FEATURE_DATA: List[Tuple[str, str, List[str]]] = [
    (
        "Code Editor",
        "#0096C7",
        [
            "Advanced multi-tab code editing environment",
            "AI-powered code assistance (Analysis, Fix, Optimize, Document)",
            "Integrated compiler and execution console",
            "Auto-save and session restoration",
        ],
    ),
    (
        "Compare",
        "#F72585",
        [
            "Separate code generators, correct solutions, and test solutions",
            "Customizable comparison testing options",
            "Real-time comparison of outputs",
            "Detailed test results analysis",
        ],
    ),
    (
        "Benchmark",
        "#ffb600",
        [
            "Time limit execution testing",
            "Memory usage monitoring",
            "Multiple test case execution",
            "Performance optimization insights",
        ],
    ),
    (
        "Validate",
        "#4CAF50",
        [
            "Automated code validation and testing",
            "Custom validation rules and constraints",
            "Input/output format verification",
            "Edge case detection and testing",
        ],
    ),
    (
        "Results & Analytics",
        "#00D9FF",
        [
            "Comprehensive test result history",
            "Performance analytics and trends",
            "Success rate tracking",
            "Detailed test execution reports",
        ],
    ),
    (
        "Configuration",
        "#B565D8",
        [
            "Customizable C++ version settings",
            "Workspace folder management",
            "Editor preferences configuration",
            "AI integration settings",
        ],
    ),
]


# Main window welcome text
WELCOME_TITLE = "CODE TESTING SUITE"
WELCOME_SUBTITLE = ">> SYSTEM READY"
CTA_TITLE = ">> SELECT FEATURE TO BEGIN"
CTA_SUBTITLE = "Choose any tool from the sidebar to start"
