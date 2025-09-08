"""
Results Guide Help Document - Results and analytics features
"""

from .help_doc_engine import HelpDocument


class ResultsGuideDoc(HelpDocument):
    """Results guide help document"""
    
    def __init__(self, parent=None):
        sections = [
            ("📊", "Overview", "", [
                "View comprehensive test result history from comparison and benchmark tests",
                "Analyze performance trends and success rates over time",
                "Filter results by test type, date range, and project",
                "Export results for external analysis"
            ]),
             
            ("📈", "Statistics View", "", [
                "Overall success rate tracking across all tests",
                "Test type breakdown (Comparison vs Benchmark tests)",
                "Average execution time analysis",
                "Recent activity summary"
            ]),
            
            ("🔍", "Detailed Analysis", "", [
                "Click any test result to view detailed information",
                "See input/output data for failed test cases",
                "Review execution times and performance metrics",
                "Track improvements in code efficiency"
            ]),
            
            ("💾", "Data Management", "", [
                "Export results to CSV format",
                "Clear old test data to save space",
                "Backup important test results",
                "Share results with team members"
            ])
        ]
        
        super().__init__("Results & Analytics Guide", sections, parent)


def create_results_guide_doc():
    """Factory function for results guide document"""
    return ResultsGuideDoc()
