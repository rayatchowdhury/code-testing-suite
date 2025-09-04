"""
Logging configuration for the Code Testing Suite.

This module provides centralized logging configuration to suppress
unnecessary warnings from third-party libraries while maintaining
useful application logs. It also handles all cleanup to prevent
gRPC warnings on application exit.
"""

import os
import logging
import warnings
import sys
import atexit
from typing import Optional

# Configure environment variables VERY early to suppress gRPC verbosity
os.environ['GRPC_VERBOSITY'] = 'NONE'
os.environ['GRPC_TRACE'] = ''
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '3'

# Additional gRPC suppression environment variables
os.environ['GRPC_ENABLE_FORK_SUPPORT'] = '0'
os.environ['GRPC_POLL_STRATEGY'] = 'poll'

# Monkey patch stderr to filter gRPC messages
class FilteredStderr:
    def __init__(self, original_stderr):
        self.original_stderr = original_stderr
        
    def write(self, text):
        # Filter out specific gRPC messages
        if any(phrase in text for phrase in [
            'grpc_wait_for_shutdown_with_timeout',
            'All log messages before absl::InitializeLog',
            'grpc',
            'GRPC'
        ]):
            return  # Don't write gRPC messages
        self.original_stderr.write(text)
        
    def flush(self):
        self.original_stderr.flush()
        
    def __getattr__(self, name):
        return getattr(self.original_stderr, name)

# Apply stderr filter immediately
if not hasattr(sys.stderr, '_original_stderr'):
    sys.stderr._original_stderr = sys.stderr
    sys.stderr = FilteredStderr(sys.stderr)

def _cleanup_ai_resources():
    """Cleanup function to be called on exit."""
    try:
        import gc
        
        # Try to import and cleanup EditorAI instances
        try:
            from ai.core.editor_ai import EditorAI
            for obj in gc.get_objects():
                if isinstance(obj, EditorAI):
                    try:
                        obj.cleanup()
                    except Exception:
                        pass
        except ImportError:
            pass  # EditorAI might not be available
        
        # Force garbage collection
        gc.collect()
        
        # Give gRPC time to shutdown
        import time
        time.sleep(0.1)
        
    except Exception:
        pass  # Ignore all errors during exit cleanup

class LoggingConfig:
    """Centralized logging configuration."""
    
    _initialized = False
    
    @classmethod
    def initialize(cls, level: int = logging.WARNING):
        """Initialize logging configuration."""
        if cls._initialized:
            return
        
        # Register cleanup function
        atexit.register(_cleanup_ai_resources)
        
        # Suppress ALL warnings aggressively
        warnings.filterwarnings("ignore")
        
        # Configure absl logging (used by Google libraries)
        try:
            from absl import logging as absl_logging
            # Completely disable absl logging
            absl_logging.use_absl_handler()
            absl_logging.set_verbosity(absl_logging.FATAL)
            absl_logging.set_stderrthreshold(absl_logging.FATAL)
            
            # Patch absl to not initialize if not already done
            if hasattr(absl_logging, '_warn_preinit_stderr'):
                absl_logging._warn_preinit_stderr = False
                
        except ImportError:
            pass
        except Exception:
            pass  # Ignore if already configured
        
        # Configure standard logging
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Completely disable noisy loggers
        noisy_loggers = [
            'grpc',
            'grpc._channel',
            'grpc._common',
            'google.api_core.retry',
            'google.auth',
            'google.generativeai',
            'urllib3.connectionpool',
            'absl',
            'tensorflow'
        ]
        
        for logger_name in noisy_loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.CRITICAL + 1)  # Higher than CRITICAL
            logger.disabled = True
            logger.propagate = False
        
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
    def restore_stderr(cls):
        """Restore original stderr if needed."""
        if hasattr(sys.stderr, '_original_stderr'):
            sys.stderr = sys.stderr._original_stderr
    
    @classmethod
    def manual_cleanup(cls):
        """Manually trigger cleanup (useful for close events)."""
        _cleanup_ai_resources()
