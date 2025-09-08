"""
Benchmarking Guide Help Document - Performance benchmarking features and usage
"""

from .help_doc_engine import HelpDocument


class BenchmarkingGuideDoc(HelpDocument):
    """Benchmarking guide help document"""
    
    def __init__(self, parent=None):
        sections = [
            ("⏱️", "Performance Benchmarking", 
             "Benchmark Testing helps ensure your solution meets time constraints by simulating contest-like execution environments."),
             
            ("⚡", "Features", "", [
                "Set custom time limits",
                "Monitor memory usage",
                "Multiple test case execution",
                "Performance metrics analysis"
            ]),
            
            ("📊", "Performance Analysis", "", [
                "Execution time breakdown",
                "Memory usage patterns",
                "Performance bottleneck detection",
                "Optimization suggestions"
            ])
        ]
        
        super().__init__("Benchmark Testing Guide", sections, parent)


def create_benchmarking_guide_doc():
    """Factory function for benchmarking guide document"""
    return BenchmarkingGuideDoc()
