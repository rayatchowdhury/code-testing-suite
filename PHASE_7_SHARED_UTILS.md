# 🔧 PHASE 7: SHARED UTILITIES ORGANIZATION

**Duration**: 2-3 hours  
**Risk Level**: 🟢 Low  
**Prerequisites**: Phase 6 Complete  
**Goal**: Organize common utilities, constants, and helper functions into clean shared layer

---

## 📋 PHASE OVERVIEW

This phase creates a comprehensive shared utilities layer by intelligently analyzing and reorganizing common functionality across the application. We extract utilities, constants, and helpers while maintaining exact functionality and improving code reusability.

### Phase Objectives
1. **Utility Organization**: Group related utility functions into logical modules
2. **Constants Consolidation**: Centralize all application constants with clear categorization
3. **Helper Function Extraction**: Identify and extract reusable helper functions
4. **Exception Handling**: Create comprehensive exception hierarchy
5. **Resource Management**: Organize resource access and management utilities

### Refactoring Philosophy
- **DRY PRINCIPLE**: Eliminate all code duplication through smart extraction
- **LOGICAL GROUPING**: Group utilities by purpose, not by origin
- **DEPENDENCY CLARITY**: Clear utility dependencies with minimal coupling
- **BACKWARD COMPATIBILITY**: All existing functionality preserved exactly

---

## 🔍 STEP 7.1: UTILITY ANALYSIS

**Duration**: 45 minutes  
**Output**: Complete analysis of existing utilities with consolidation plan

### 7.1.1 Current Utility Landscape Analysis
```
CURRENT UTILITY DISTRIBUTION:

📁 src/app/utils/
├── api_validator.py          # 🔍 ANALYSIS: 95 lines, API key validation
├── file_operations.py        # 🔍 ANALYSIS: 180+ lines, file I/O operations  
├── logging_config.py         # 🔍 ANALYSIS: 120 lines, logging setup
├── window_factory.py         # 🔍 ANALYSIS: 85 lines, window creation
├── window_manager.py         # 🔍 ANALYSIS: 140 lines, window management

📁 src/app/constants/
├── paths.py                  # 🔍 ANALYSIS: 60 lines, file paths

📁 src/app/styles/constants/
├── colors.py                 # 🔍 ANALYSIS: 45 lines, color definitions
├── editor_colors.py          # 🔍 ANALYSIS: 35 lines, editor-specific colors
├── status_colors.py          # 🔍 ANALYSIS: 40 lines, status indicators

📁 SCATTERED UTILITIES (found in features):
├── config/config_manager.py     # Contains utility functions mixed with business logic
├── database/models.py           # Helper functions embedded in model classes
├── ai/validation/               # Validation utilities scattered
├── tools/                       # Tool-specific helpers
└── views/*/                     # UI helper functions in view classes

🎯 DUPLICATION ANALYSIS:
- File operations: Duplicated across editor, testing, config features
- Validation logic: Scattered in AI, config, database modules  
- Error handling: Inconsistent patterns across features
- Logging: Setup duplicated in multiple locations
- Path operations: Hardcoded paths in various modules
```

### 7.1.2 Smart Consolidation Strategy
```
🧠 INTELLIGENT GROUPING STRATEGY:

🔧 CORE UTILITIES (High-reuse, foundational):
- File operations → shared/utils/files.py
- Validation helpers → shared/utils/validation.py  
- String/data processing → shared/utils/data.py
- Async helpers → shared/utils/async_helpers.py

🛠️ INFRASTRUCTURE UTILITIES (System-level):
- Logging configuration → shared/utils/logging.py
- Environment setup → shared/utils/environment.py
- Resource management → shared/utils/resources.py
- System integration → shared/utils/system.py

🎯 DOMAIN UTILITIES (Business-specific):
- Code processing → shared/utils/code_analysis.py
- Test utilities → shared/utils/testing.py
- UI helpers → shared/utils/ui_helpers.py  
- Configuration helpers → shared/utils/config_helpers.py

📊 CONSTANTS ORGANIZATION (Logical grouping):
- Application constants → shared/constants/app.py
- Path constants → shared/constants/paths.py
- Style constants → shared/constants/styles.py  
- Configuration constants → shared/constants/config.py

⚠️ EXCEPTION HIERARCHY (Centralized error handling):
- Base exceptions → shared/exceptions/base.py
- Domain exceptions → shared/exceptions/domain.py
- Integration exceptions → shared/exceptions/integration.py
```

### 7.1.3 Extraction Boundaries Identification
```python
# SMART EXTRACTION EXAMPLES:

# 🎯 FILE OPERATIONS (Currently: utils/file_operations.py - 180+ lines)
class FileOperations:
    # EXTRACT TO: shared/utils/files.py
    
    # HIGH-REUSE METHODS (used by 4+ features):
    def read_file_safe() → shared/utils/files.py
    def write_file_safe() → shared/utils/files.py  
    def backup_file() → shared/utils/files.py
    def validate_file_path() → shared/utils/validation.py (better fit)
    
    # MEDIUM-REUSE METHODS (used by 2-3 features):
    def get_file_hash() → shared/utils/files.py
    def create_temp_file() → shared/utils/files.py
    
    # FEATURE-SPECIFIC METHODS:
    def compile_cpp_file() → features/code_editor/services/ (domain-specific)
    def execute_program() → core/tools/services.py (already moved in Phase 4)

# 🎯 VALIDATION SCATTERED FUNCTIONS:
# CURRENT LOCATIONS: ai/validation/, config/validation/, database/validation/

# CONSOLIDATE TO: shared/utils/validation.py
class ValidationHelpers:
    def validate_api_key() # From ai/validation/
    def validate_config_value() # From config/validation/
    def validate_file_path() # From file_operations.py
    def validate_email() # From config/validation/
    def validate_numeric_range() # From multiple locations
    
# RESULT: Single source of truth for all validation logic
```

---

## 🗂️ STEP 7.2: SHARED CONSTANTS ORGANIZATION

**Duration**: 30 minutes  
**Output**: Centralized constants with logical organization

### 7.2.1 Constants Consolidation Strategy
```
TARGET CONSTANTS STRUCTURE:

src/app/shared/constants/
├── __init__.py               # Central exports  
├── app.py                   # Application-level constants
├── paths.py                 # All path-related constants
├── styles.py                # UI/styling constants (reference only)
├── config.py                # Configuration defaults and limits
├── testing.py               # Testing-related constants
└── resources.py             # Resource identifiers and metadata
```

### 7.2.2 Smart Constants Organization
```python
# CURRENT: constants/paths.py (60 lines, mixed concerns)
# STRATEGY: Split by concern, improve organization

# shared/constants/paths.py (Enhanced)
"""Centralized path constants with smart organization"""

class ApplicationPaths:
    """Application directory structure"""
    # EXTRACT FROM: constants/paths.py + hardcoded paths across features
    
    # Root paths (from existing constants/paths.py)
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent.parent
    SRC_ROOT: Path = PROJECT_ROOT / "src"
    
    # Resource paths (from existing + scattered hardcoded paths)  
    RESOURCES_DIR: Path = SRC_ROOT / "resources"
    ICONS_DIR: Path = RESOURCES_DIR / "icons"
    TEMPLATES_DIR: Path = RESOURCES_DIR / "templates"
    
    # Working directories (from existing + new organization)
    WORKSPACE_DIR: Path = PROJECT_ROOT / "workspace"  
    TEMP_DIR: Path = PROJECT_ROOT / "temp"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    BACKUPS_DIR: Path = PROJECT_ROOT / "backups"
    
    # Database paths (from persistence layer)
    DATA_DIR: Path = PROJECT_ROOT / "data"
    DB_PATH: Path = DATA_DIR / "app.db"

class ResourcePaths:
    """Resource file constants"""
    # EXTRACT FROM: hardcoded resource paths in features
    
    # Icon files (currently hardcoded in multiple places)
    APP_ICON: str = str(ApplicationPaths.ICONS_DIR / "app_icon.png")
    SETTINGS_ICON: str = str(ApplicationPaths.ICONS_DIR / "settings.png")  
    CHECK_ICON: str = str(ApplicationPaths.ICONS_DIR / "check.png")
    
    # Template files (from editor feature)
    CPP_TEMPLATE: str = str(ApplicationPaths.TEMPLATES_DIR / "template.cpp")
    PYTHON_TEMPLATE: str = str(ApplicationPaths.TEMPLATES_DIR / "template.py")

# shared/constants/app.py (New consolidation)
"""Application-level constants"""

class ApplicationInfo:
    """Application metadata"""
    NAME: str = "Code Testing Suite"
    VERSION: str = "1.0.0"
    AUTHOR: str = "Code Testing Suite Team"
    DESCRIPTION: str = "PySide6 Desktop Application for Code Testing"

class ApplicationLimits:
    """Application limits and constraints"""  
    # EXTRACT FROM: scattered hardcoded limits
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB (from editor)
    MAX_TEST_CASES: int = 1000  # from testing features
    MAX_RECENT_FILES: int = 10  # from editor
    TIMEOUT_SECONDS: int = 30   # from testing features
    
class FeatureFlags:
    """Feature enablement flags"""
    # NEW: Centralized feature control
    AI_FEATURES_ENABLED: bool = True
    STRESS_TESTING_ENABLED: bool = True
    TLE_TESTING_ENABLED: bool = True
    ADVANCED_EDITOR_ENABLED: bool = True

# shared/constants/config.py (Consolidation from config/)
"""Configuration constants and defaults"""

class ConfigDefaults:
    """Default configuration values"""
    # EXTRACT FROM: config/config_manager.py defaults
    
    EDITOR_FONT_SIZE: int = 12
    EDITOR_TAB_WIDTH: int = 4
    AUTO_SAVE_INTERVAL: int = 300  # 5 minutes
    
    CPP_VERSION: str = "17"
    COMPILER_FLAGS: List[str] = ["-std=c++17", "-O2", "-Wall"]
    
    AI_MAX_TOKENS: int = 4000
    AI_TEMPERATURE: float = 0.7

class ConfigValidation:
    """Configuration validation constants"""
    # EXTRACT FROM: config validation scattered across modules
    
    FONT_SIZE_RANGE: Tuple[int, int] = (8, 48)
    TAB_WIDTH_RANGE: Tuple[int, int] = (1, 16)
    AUTO_SAVE_RANGE: Tuple[int, int] = (60, 3600)  # 1 min to 1 hour
```

### 7.2.3 Style Constants Integration
```python
# STRATEGY: Reference existing styles, don't duplicate
# shared/constants/styles.py (Reference layer only)

"""Style constants integration layer"""

# Import existing style constants (maintain exact same styling)
from ...styles.constants.colors import COLORS, MATERIAL_COLORS
from ...styles.constants.editor_colors import EDITOR_COLORS  
from ...styles.constants.status_colors import STATUS_COLORS

# Re-export for convenience (optional)
__all__ = ['COLORS', 'MATERIAL_COLORS', 'EDITOR_COLORS', 'STATUS_COLORS']

# BENEFIT: Central import point without duplicating style definitions
# RISK: Zero - exact same styling system maintained
```

---

## 🛠️ STEP 7.3: UTILITY FUNCTIONS ORGANIZATION

**Duration**: 60 minutes  
**Output**: Clean utility modules with smart function grouping

### 7.3.1 Core Utilities Extraction
```python
# shared/utils/files.py (Consolidation from multiple sources)
"""File operation utilities with enhanced error handling"""

import asyncio
import hashlib
import shutil
from pathlib import Path
from typing import Optional, List, Union, Dict, Any

from ..exceptions.base import FileOperationError
from ..constants.paths import ApplicationPaths

class FileUtils:
    """Smart file operations with consistent error handling"""
    
    # EXTRACT FROM: utils/file_operations.py (high-reuse methods)
    @staticmethod
    async def read_file_safe(path: Union[str, Path], 
                           encoding: str = 'utf-8') -> Optional[str]:
        """Safe file reading with comprehensive error handling"""
        # IMPROVED VERSION of existing read_file methods
        # CONSOLIDATES: Similar methods from editor, config, testing features
        # ADDS: Better error handling, async support, encoding detection
    
    @staticmethod  
    async def write_file_safe(path: Union[str, Path], 
                            content: str,
                            encoding: str = 'utf-8',
                            create_backup: bool = False) -> bool:
        """Safe file writing with backup option"""
        # IMPROVED VERSION of existing write methods
        # ADDS: Automatic backup, atomic writes, directory creation
    
    @staticmethod
    async def copy_file_safe(source: Union[str, Path], 
                           dest: Union[str, Path]) -> bool:
        """Safe file copying with validation"""
        # CONSOLIDATES: Copy operations from multiple features
        # ADDS: Integrity checking, progress reporting for large files
    
    @staticmethod
    def calculate_file_hash(path: Union[str, Path], 
                          algorithm: str = 'sha256') -> str:
        """Calculate file hash for integrity verification"""
        # EXTRACT FROM: file_operations.py
        # ENHANCE: Support multiple hash algorithms
    
    @staticmethod
    def get_file_info(path: Union[str, Path]) -> Dict[str, Any]:
        """Get comprehensive file information"""
        # CONSOLIDATES: File stat operations from multiple features
        # RETURNS: Size, dates, permissions, hash in consistent format

# shared/utils/validation.py (Consolidation from scattered validation)
"""Validation utilities for all application data"""

import re
from typing import Any, Optional, Union, List
from pathlib import Path

from ..exceptions.base import ValidationError

class ValidationUtils:
    """Centralized validation logic"""
    
    # EXTRACT FROM: ai/validation/api_validator.py  
    @staticmethod
    def validate_api_key(key: str) -> bool:
        """Validate API key format"""
        # MOVE FROM: utils/api_validator.py
        # ENHANCE: Support multiple API key formats
    
    # EXTRACT FROM: config validation scattered across modules
    @staticmethod
    def validate_config_value(value: Any, 
                            value_type: str,
                            constraints: Optional[Dict] = None) -> bool:
        """Generic configuration value validation"""
        # CONSOLIDATES: All config validation logic
        # SUPPORTS: Range checking, format validation, type coercion
    
    # EXTRACT FROM: file_operations.py and various features
    @staticmethod
    def validate_file_path(path: Union[str, Path], 
                         must_exist: bool = False,
                         allowed_extensions: Optional[List[str]] = None) -> bool:
        """Comprehensive file path validation"""
        # CONSOLIDATES: Path validation from editor, testing, config
        # ADDS: Extension checking, security validation
    
    @staticmethod
    def validate_numeric_range(value: Union[int, float],
                             min_val: Union[int, float], 
                             max_val: Union[int, float]) -> bool:
        """Numeric range validation"""
        # EXTRACT FROM: Multiple config validation locations
        # STANDARDIZES: Range checking across application

# shared/utils/async_helpers.py (New utility for async operations)
"""Async operation utilities"""

import asyncio
from typing import Awaitable, Optional, Any, Callable
from functools import wraps

class AsyncUtils:
    """Async operation helpers"""
    
    @staticmethod
    async def run_with_timeout(coro: Awaitable[Any], 
                             timeout_seconds: float) -> Optional[Any]:
        """Run coroutine with timeout"""
        # CONSOLIDATES: Timeout patterns from testing, AI features
        # STANDARDIZES: Timeout handling across application
    
    @staticmethod
    def async_retry(max_attempts: int = 3, 
                   delay: float = 1.0,
                   backoff: float = 2.0):
        """Decorator for async retry logic"""
        # NEW UTILITY: For AI service calls, file operations
        # PATTERN: Common retry logic extracted
        
    @staticmethod
    async def gather_with_limit(coroutines: List[Awaitable[Any]], 
                              limit: int = 10) -> List[Any]:
        """Run multiple coroutines with concurrency limit"""
        # NEW UTILITY: For batch operations in testing, file processing
```

### 7.3.2 Domain-Specific Utilities
```python
# shared/utils/code_analysis.py (Domain utility)
"""Code analysis utilities for editor and AI features"""

import ast
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class CodeAnalysisUtils:
    """Utilities for code analysis and processing"""
    
    # EXTRACT FROM: ai/core/editor_ai.py (code analysis helpers)
    @staticmethod
    def detect_language(file_path: Union[str, Path]) -> str:
        """Detect programming language from file"""
        # CONSOLIDATES: Language detection from editor, AI features
        # SUPPORTS: C++, Python, Java, JavaScript
    
    @staticmethod
    def extract_functions(code: str, language: str) -> List[Dict]:
        """Extract function definitions from code"""
        # EXTRACT FROM: AI analysis features
        # SUPPORTS: Multiple programming languages
    
    @staticmethod
    def count_complexity(code: str, language: str) -> int:
        """Calculate code complexity score"""
        # EXTRACT FROM: AI analysis features
        # IMPLEMENTS: Cyclomatic complexity calculation
    
    @staticmethod
    def extract_imports(code: str, language: str) -> List[str]:
        """Extract import/include statements"""
        # NEW UTILITY: For dependency analysis

# shared/utils/testing.py (Testing utilities)
"""Testing-related utility functions"""

import time
import statistics
from typing import List, Dict, Any, Optional

class TestingUtils:
    """Utilities for test execution and analysis"""
    
    # EXTRACT FROM: stress_tester, tle_tester features
    @staticmethod
    def calculate_statistics(execution_times: List[float]) -> Dict[str, float]:
        """Calculate execution time statistics"""
        # CONSOLIDATES: Statistics calculation from testing features
        # RETURNS: min, max, mean, median, std_dev
    
    @staticmethod
    def format_time_duration(seconds: float) -> str:
        """Format time duration for display"""
        # EXTRACT FROM: Multiple testing UI components
        # STANDARDIZES: Time formatting across application
    
    @staticmethod
    def generate_test_report(results: List[Dict]) -> str:
        """Generate formatted test report"""
        # CONSOLIDATES: Report generation from testing features
        # SUPPORTS: Multiple output formats (text, HTML, JSON)

# shared/utils/ui_helpers.py (UI utility functions)
"""UI helper functions for consistent behavior"""

from PySide6.QtWidgets import QWidget, QLayout
from typing import Optional, List

class UIUtils:
    """UI operation helpers"""
    
    # EXTRACT FROM: Multiple view classes with setup_ui methods
    @staticmethod
    def clear_layout(layout: QLayout):
        """Safely clear all widgets from layout"""
        # CONSOLIDATES: Layout clearing from multiple UI components
        # ADDS: Proper widget deletion and memory management
    
    @staticmethod
    def set_widget_loading_state(widget: QWidget, loading: bool):
        """Set widget to loading state"""
        # NEW UTILITY: Consistent loading states across features
        # STANDARDIZES: Loading indicators and disabled states
    
    @staticmethod
    def auto_resize_columns(table_widget):
        """Auto-resize table columns to content"""
        # EXTRACT FROM: Results table, config tables
        # STANDARDIZES: Table column sizing
```

---

## ⚠️ STEP 7.4: EXCEPTION HIERARCHY ORGANIZATION

**Duration**: 30 minutes  
**Output**: Comprehensive exception handling system

### 7.4.1 Exception Hierarchy Design
```python
# shared/exceptions/__init__.py
"""Centralized exception handling for the application"""

from .base import (
    ApplicationError, ConfigurationError, ValidationError,
    FileOperationError, NetworkError
)
from .domain import (
    EditorError, TestingError, AIServiceError, 
    CompilationError, ExecutionError
)
from .integration import (
    DatabaseError, ExternalToolError, ResourceError
)

__all__ = [
    'ApplicationError', 'ConfigurationError', 'ValidationError',
    'FileOperationError', 'NetworkError', 'EditorError', 
    'TestingError', 'AIServiceError', 'CompilationError',
    'ExecutionError', 'DatabaseError', 'ExternalToolError',
    'ResourceError'
]

# shared/exceptions/base.py
"""Base exception classes"""

class ApplicationError(Exception):
    """Base exception for all application errors"""
    
    def __init__(self, message: str, details: Optional[str] = None, 
                 error_code: Optional[str] = None):
        self.message = message
        self.details = details  
        self.error_code = error_code
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/reporting"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'details': self.details,
            'error_code': self.error_code
        }

class ValidationError(ApplicationError):
    """Validation-related errors"""
    
    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.value = value
        super().__init__(f"{field}: {message}")

class FileOperationError(ApplicationError):
    """File operation errors"""
    
    def __init__(self, operation: str, path: str, message: str):
        self.operation = operation
        self.path = path
        super().__init__(f"{operation} failed for {path}: {message}")

# shared/exceptions/domain.py  
"""Domain-specific exceptions"""

class EditorError(ApplicationError):
    """Editor-related errors"""
    pass

class AIServiceError(ApplicationError):
    """AI service errors"""
    
    def __init__(self, service: str, message: str, api_error: Optional[str] = None):
        self.service = service
        self.api_error = api_error
        super().__init__(f"AI service {service}: {message}")

class TestingError(ApplicationError):
    """Testing-related errors"""
    
    def __init__(self, test_type: str, message: str, test_data: Optional[Dict] = None):
        self.test_type = test_type
        self.test_data = test_data or {}
        super().__init__(f"{test_type} test error: {message}")
```

### 7.4.2 Error Handling Patterns
```python
# shared/utils/error_handling.py
"""Standardized error handling patterns"""

import logging
from typing import Optional, Callable, Any, Union
from functools import wraps

from ..exceptions.base import ApplicationError

class ErrorHandler:
    """Centralized error handling utilities"""
    
    @staticmethod
    def handle_gracefully(operation_name: str, 
                         fallback_value: Any = None,
                         log_level: str = "error"):
        """Decorator for graceful error handling"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger = logging.getLogger(func.__module__)
                    getattr(logger, log_level)(
                        f"{operation_name} failed: {e}"
                    )
                    return fallback_value
            return wrapper
        return decorator
    
    @staticmethod
    async def handle_async_gracefully(operation_name: str,
                                    fallback_value: Any = None):
        """Async version of graceful error handling"""
        # Similar pattern for async operations
        
    @staticmethod
    def convert_exception(from_exception: type, 
                        to_exception: type,
                        message_transform: Optional[Callable] = None):
        """Convert one exception type to another"""
        # For converting external library exceptions to application exceptions
```

---

## 🔗 STEP 7.5: RESOURCE MANAGEMENT

**Duration**: 30 minutes  
**Output**: Centralized resource management system

### 7.5.1 Resource Management Utilities
```python
# shared/utils/resources.py
"""Resource management and access utilities"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, Union
from functools import lru_cache

from ..constants.paths import ApplicationPaths, ResourcePaths
from ..exceptions.base import ResourceError

class ResourceManager:
    """Centralized resource access and management"""
    
    def __init__(self):
        self._cache = {}
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        # CONSOLIDATES: Directory creation from multiple locations
        required_dirs = [
            ApplicationPaths.TEMP_DIR,
            ApplicationPaths.LOGS_DIR, 
            ApplicationPaths.BACKUPS_DIR,
            ApplicationPaths.DATA_DIR
        ]
        
        for directory in required_dirs:
            directory.mkdir(parents=True, exist_ok=True)
    
    @lru_cache(maxsize=128)
    def get_icon_path(self, icon_name: str) -> Optional[str]:
        """Get icon file path with caching"""
        # CONSOLIDATES: Icon path resolution from multiple features
        icon_path = ApplicationPaths.ICONS_DIR / f"{icon_name}.png"
        return str(icon_path) if icon_path.exists() else None
    
    @lru_cache(maxsize=32)
    def get_template(self, template_name: str) -> Optional[str]:
        """Get code template content"""
        # EXTRACT FROM: Editor feature template loading
        template_path = ApplicationPaths.TEMPLATES_DIR / f"{template_name}.template"
        
        if template_path.exists():
            try:
                return template_path.read_text(encoding='utf-8')
            except Exception as e:
                raise ResourceError(f"Failed to load template {template_name}: {e}")
        return None
    
    def get_help_content(self, topic: str) -> Optional[str]:
        """Get help content for topic"""
        # CONSOLIDATES: Help content loading from help_center feature
        help_path = ApplicationPaths.RESOURCES_DIR / "help" / f"{topic}.html"
        
        if help_path.exists():
            return help_path.read_text(encoding='utf-8')
        return None
    
    def create_backup_path(self, original_path: Union[str, Path]) -> Path:
        """Create backup file path"""
        # STANDARDIZES: Backup path generation across features
        from datetime import datetime
        
        original = Path(original_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{original.stem}_{timestamp}{original.suffix}"
        
        return ApplicationPaths.BACKUPS_DIR / backup_name

# Global resource manager instance
_resource_manager = None

def get_resource_manager() -> ResourceManager:
    """Get global resource manager instance"""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager
```

### 7.5.2 Environment Configuration
```python
# shared/utils/environment.py
"""Environment setup and configuration utilities"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from ..constants.app import ApplicationInfo
from ..constants.paths import ApplicationPaths

class EnvironmentManager:
    """Environment configuration and setup"""
    
    @staticmethod
    def setup_application_environment():
        """Setup application environment variables and paths"""
        # CONSOLIDATES: Environment setup from __main__.py and other modules
        
        # Set Qt API before any Qt imports
        os.environ['QT_API'] = 'pyside6'
        
        # Set application paths
        os.environ['APP_ROOT'] = str(ApplicationPaths.PROJECT_ROOT)
        os.environ['APP_NAME'] = ApplicationInfo.NAME
        os.environ['APP_VERSION'] = ApplicationInfo.VERSION
        
        # Add src to Python path if needed
        src_path = str(ApplicationPaths.SRC_ROOT)
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get system information for debugging/logging"""
        # NEW UTILITY: System information collection
        import platform
        
        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'architecture': platform.architecture()[0],
            'app_version': ApplicationInfo.VERSION,
            'working_directory': str(Path.cwd())
        }
    
    @staticmethod
    def validate_environment() -> Dict[str, bool]:
        """Validate application environment requirements"""
        # NEW UTILITY: Environment validation
        validations = {}
        
        # Check required directories
        required_dirs = [
            ApplicationPaths.RESOURCES_DIR,
            ApplicationPaths.ICONS_DIR,
            ApplicationPaths.TEMP_DIR
        ]
        
        for directory in required_dirs:
            validations[f"dir_{directory.name}"] = directory.exists()
        
        # Check Python version
        validations['python_version'] = sys.version_info >= (3, 8)
        
        # Check required packages (basic check)
        try:
            import PySide6
            validations['pyside6'] = True
        except ImportError:
            validations['pyside6'] = False
        
        return validations
```

---

## 🔧 STEP 7.6: INTEGRATION AND CLEANUP

**Duration**: 45 minutes  
**Output**: Integrated shared utilities with updated imports across application

### 7.6.1 Import Path Updates Strategy
```python
# SMART IMPORT UPDATE STRATEGY:

# Before: Multiple scattered imports
from utils.file_operations import FileOperations
from constants.paths import APP_ICON  
from styles.constants.colors import MATERIAL_COLORS
from config.config_manager import validate_config_value

# After: Clean centralized imports  
from shared.utils.files import FileUtils
from shared.constants.paths import ResourcePaths
from shared.constants.styles import MATERIAL_COLORS
from shared.utils.validation import ValidationUtils

# MIGRATION PATTERN for each feature:

# features/code_editor/services/editor_manager.py
# OLD IMPORTS:
# from utils.file_operations import FileOperations
# from constants.paths import TEMP_DIR

# NEW IMPORTS:
from ....shared.utils.files import FileUtils
from ....shared.constants.paths import ApplicationPaths
from ....shared.exceptions.domain import EditorError

class EditorManager:
    async def save_file(self, path, content):
        # OLD: FileOperations.write_file(path, content)  
        # NEW: FileUtils.write_file_safe(path, content, create_backup=True)
        
        try:
            success = await FileUtils.write_file_safe(path, content, create_backup=True)
            if not success:
                raise EditorError("File save failed", details=f"Could not write to {path}")
        except Exception as e:
            raise EditorError("File save error", details=str(e))
```

### 7.6.2 Backward Compatibility Strategy
```python
# TEMPORARY COMPATIBILITY SHIMS (Remove after migration):

# utils/__init__.py (Compatibility layer)
"""
DEPRECATED: This module has moved to shared.utils
Please update your imports.
"""
import warnings

# Provide temporary backward compatibility
from ..shared.utils.files import FileUtils as FileOperations
from ..shared.utils.validation import ValidationUtils

def __getattr__(name):
    warnings.warn(
        f"Importing {name} from utils is deprecated. "
        f"Use 'from shared.utils.{module} import {name}' instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Return appropriate utility
    mapping = {
        'FileOperations': FileOperations,
        'ValidationUtils': ValidationUtils
    }
    
    if name in mapping:
        return mapping[name]
    
    raise AttributeError(f"module 'utils' has no attribute '{name}'")
```

### 7.6.3 Testing and Validation
```python
# tests/test_phase7_shared_utils.py
"""Phase 7 validation tests for shared utilities"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class TestSharedUtils:
    """Test shared utilities functionality"""
    
    def test_utility_imports(self):
        """Test that all utilities can be imported"""
        from app.shared.utils import (
            FileUtils, ValidationUtils, AsyncUtils,
            CodeAnalysisUtils, TestingUtils, UIUtils
        )
        
        # Verify classes exist and are callable
        assert callable(FileUtils.read_file_safe)
        assert callable(ValidationUtils.validate_api_key)
        assert callable(AsyncUtils.run_with_timeout)
    
    def test_constants_consolidation(self):
        """Test consolidated constants"""
        from app.shared.constants import (
            ApplicationPaths, ResourcePaths, ApplicationInfo,
            ConfigDefaults
        )
        
        # Verify paths exist and are Path objects
        assert isinstance(ApplicationPaths.PROJECT_ROOT, Path)
        assert isinstance(ApplicationPaths.RESOURCES_DIR, Path)
        
        # Verify application info
        assert ApplicationInfo.NAME == "Code Testing Suite"
        assert ApplicationInfo.VERSION
    
    def test_exception_hierarchy(self):
        """Test exception handling system"""
        from app.shared.exceptions import (
            ApplicationError, ValidationError, EditorError,
            TestingError, AIServiceError
        )
        
        # Test exception inheritance
        assert issubclass(ValidationError, ApplicationError)
        assert issubclass(EditorError, ApplicationError)
        
        # Test exception creation
        error = ValidationError("test_field", "test message", "test_value")
        assert error.field == "test_field"
        assert "test_field" in str(error)
    
    def test_resource_management(self):
        """Test resource manager"""
        from app.shared.utils.resources import get_resource_manager
        
        manager = get_resource_manager()
        assert manager is not None
        
        # Test resource access (may not exist in test environment)
        icon_path = manager.get_icon_path("app_icon")
        # Either returns valid path or None - both are acceptable
        assert icon_path is None or isinstance(icon_path, str)

class TestUtilityFunctionality:
    """Test actual utility functionality"""
    
    @pytest.mark.asyncio
    async def test_file_utils(self):
        """Test file utilities with temporary file"""
        from app.shared.utils.files import FileUtils
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            test_path = Path(f.name)
            test_content = "Test content for shared utilities"
            f.write(test_content)
        
        try:
            # Test read
            content = await FileUtils.read_file_safe(test_path)
            assert content == test_content
            
            # Test file info
            info = FileUtils.get_file_info(test_path)
            assert info['size'] > 0
            assert 'modified_at' in info
            
        finally:
            test_path.unlink(missing_ok=True)
    
    def test_validation_utils(self):
        """Test validation utilities"""
        from app.shared.utils.validation import ValidationUtils
        
        # Test numeric range validation
        assert ValidationUtils.validate_numeric_range(5, 1, 10) == True
        assert ValidationUtils.validate_numeric_range(15, 1, 10) == False
        
        # Test file path validation
        assert ValidationUtils.validate_file_path("/valid/path/file.txt") == True
        assert ValidationUtils.validate_file_path("invalid<>path") == False
```

---

## 📋 STEP 7.7: PHASE COMPLETION CHECKLIST

### ✅ Utility Organization Completed
- [ ] **File Utilities**: Consolidated file operations with enhanced error handling
- [ ] **Validation**: Centralized all validation logic into shared utilities
- [ ] **Async Helpers**: Created async operation utilities with timeout/retry patterns
- [ ] **Code Analysis**: Extracted code processing utilities for editor/AI features
- [ ] **Testing Utils**: Consolidated testing-related helper functions
- [ ] **UI Helpers**: Extracted common UI operation patterns

### ✅ Constants Consolidation
- [ ] **Path Constants**: Centralized all file path definitions with logical grouping
- [ ] **App Constants**: Application metadata, limits, and feature flags consolidated
- [ ] **Config Constants**: Default values and validation constraints organized
- [ ] **Style Constants**: Reference layer for existing style system created

### ✅ Exception System  
- [ ] **Exception Hierarchy**: Comprehensive exception classes with proper inheritance
- [ ] **Error Handling**: Standardized error handling patterns and decorators
- [ ] **Domain Exceptions**: Feature-specific exception types for clear error reporting

### ✅ Resource Management
- [ ] **Resource Manager**: Centralized resource access with caching and validation
- [ ] **Environment Setup**: Application environment configuration utilities
- [ ] **Directory Management**: Automatic creation and management of required directories

### ✅ Integration and Quality
- [ ] **Import Updates**: All features updated to use shared utilities
- [ ] **Backward Compatibility**: Temporary compatibility shims for gradual migration  
- [ ] **Testing**: Comprehensive tests for all shared utilities and constants
- [ ] **Documentation**: Clear documentation for all utility functions and patterns

---

## 🎯 PHASE 7 SUCCESS CRITERIA

✅ **Utility Consolidation**: All common functionality extracted to shared layer  
✅ **Code Deduplication**: Eliminated duplicate utility functions across features  
✅ **Consistent Patterns**: Standardized error handling and operation patterns  
✅ **Resource Management**: Centralized resource access and environment setup  
✅ **Import Optimization**: Clean dependency structure with shared utilities

**Phase 7 Complete**: Comprehensive shared utilities layer ready for final integration

**Next Phase**: [PHASE_8_FINALIZATION.md](PHASE_8_FINALIZATION.md)  
**Focus**: Final integration, testing, documentation, and deployment preparation
