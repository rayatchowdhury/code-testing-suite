"""
Help Document Factory - Creates appropriate help documents based on topic
"""

from .introduction_doc import create_introduction_doc
from .getting_started_doc import create_getting_started_doc  
from .code_editor_guide_doc import create_code_editor_guide_doc
from .comparison_guide_doc import create_comparison_guide_doc
from .benchmarking_guide_doc import create_benchmarking_guide_doc
from .validation_guide_doc import create_validation_guide_doc
from .results_guide_doc import create_results_guide_doc
from .configuration_doc import create_configuration_doc
from .about_doc import create_about_doc


class HelpDocumentFactory:
    """Factory for creating help documents"""
    
    # Map topic names to document creators
    DOCUMENT_CREATORS = {
        'Introduction': create_introduction_doc,
        'Getting Started': create_getting_started_doc,
        'Code Editor Guide': create_code_editor_guide_doc,
        'Comparison Guide': create_comparison_guide_doc,
        'Benchmarking Guide': create_benchmarking_guide_doc,
        'Validation Guide': create_validation_guide_doc,
        'Results Guide': create_results_guide_doc,
        'Configuration': create_configuration_doc,
        'About': create_about_doc,
    }
    
    @classmethod
    def create_document(cls, topic: str):
        """Create a help document for the given topic"""
        creator = cls.DOCUMENT_CREATORS.get(topic)
        if creator:
            return creator()
        else:
            # Return a default "not found" document
            from .help_doc_engine import HelpDocument
            sections = [
                ("⚠️", "Content Not Found", 
                 f"The help section '{topic}' is currently under development.")
            ]
            return HelpDocument(topic, sections)
    
    @classmethod
    def get_available_topics(cls):
        """Get list of available help topics"""
        return list(cls.DOCUMENT_CREATORS.keys())


def create_help_document(topic: str):
    """Factory function for creating help documents"""
    return HelpDocumentFactory.create_document(topic)
