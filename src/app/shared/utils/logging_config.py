"""
Simplified logging configuration for Code Testing Suite.

Lightweight solution to suppress noisy third-party library logs
while maintaining clean application logging.
"""

import os
import logging
import warnings
import atexit

# Suppress noisy environment early
os.environ.update({
    'GRPC_VERBOSITY': 'NONE',
    'GRPC_TRACE': '',
    'TF_CPP_MIN_LOG_LEVEL': '3'
})

class LoggingConfig:
    """Simplified logging configuration."""
    
    _initialized = False
    
    @classmethod
    def initialize(cls, level: int = logging.WARNING):
        """Setup clean logging configuration."""
        if cls._initialized:
            return
            
        # Basic logging setup
        logging.basicConfig(
            level=level,
            format='%(name)s - %(levelname)s - %(message)s'
        )
        
        # Suppress noisy third-party loggers
        noisy_loggers = [
            'google.generativeai',
            'google.auth', 
            'google.api_core.retry',
            'urllib3.connectionpool',
            'grpc',
            'grpc._channel',
            'grpc._common'
        ]
        
        for logger_name in noisy_loggers:
            logging.getLogger(logger_name).setLevel(logging.ERROR)
        
        # Suppress warnings
        warnings.filterwarnings("ignore", category=UserWarning)
        
        # Register cleanup
        atexit.register(cls._cleanup)
        cls._initialized = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get a logger with the application's configuration."""
        cls.initialize()
        return logging.getLogger(name)
    
    @classmethod
    def suppress_warnings(cls):
        """Suppress common third-party warnings."""
        cls.initialize()
    
    @classmethod
    def manual_cleanup(cls):
        """Manually trigger cleanup (useful for close events)."""
        cls._cleanup()
    
    @classmethod 
    def _cleanup(cls):
        """Simple cleanup on exit."""
        try:
            import gc
            # Try to cleanup EditorAI instances
            try:
                from src.app.core.ai.core.editor_ai import EditorAI
                for obj in gc.get_objects():
                    if isinstance(obj, EditorAI):
                        try:
                            obj.cleanup()
                        except Exception:
                            pass
            except ImportError:
                pass
            gc.collect()
        except Exception:
            pass
