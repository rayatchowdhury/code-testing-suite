"""
Comparison Testing Guide Help Document - Comparison testing features and usage
"""

from .help_doc_engine import HelpDocument


class ComparisonGuideDoc(HelpDocument):
    """Comparison testing guide help document"""
    
    def __init__(self, parent=None):
        sections = [
            ("🔍", "What is Comparison Testing?", 
             "Comparison testing helps find edge cases by comparing your solution against a correct but slower solution using randomly generated test cases."),
             
            ("📝", "Required Components", "", [
                "Main Solution: Your optimized solution",
                "Brute Force: A simple, correct solution",
                "Test Generator: Creates random test cases"
            ]),
            
            ("🎯", "How to Use", "", [
                "Write your main and brute force solutions",
                "Create a test case generator",
                "Set number of test iterations",
                "Run comparison test to find mismatches"
            ])
        ]
        
        super().__init__("Comparison Testing Guide", sections, parent)


def create_comparison_guide_doc():
    """Factory function for comparison guide document"""
    return ComparisonGuideDoc()
