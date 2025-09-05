# 🧠 PHASE 4: CORE LAYER REFACTORING

**Duration**: 3-4 hours  
**Risk Level**: 🟡 Medium  
**Prerequisites**: Phase 3 Complete  
**Goal**: Organize business logic into clean core architecture layers

---

## 📋 PHASE OVERVIEW

This phase transforms the flat src/app structure into a layered core architecture with proper separation of concerns. We create dedicated layers for AI services, testing logic, configuration management, and external tools while maintaining exact functionality.

### Phase Objectives
1. **Core Layer Creation**: Establish `src/app/core/` as business logic hub
2. **AI Services Organization**: Properly structure AI functionality with clean interfaces
3. **Testing Services Layer**: Consolidate stress testing and TLE testing logic
4. **Configuration Layer**: Clean configuration management with validation
5. **Tools Integration**: Organize external tool wrappers and utilities

### Refactoring Philosophy
- **ZERO FUNCTIONALITY LOSS**: Every feature works identically after refactoring
- **CLEAN INTERFACES**: Clear APIs between layers with proper abstraction
- **SMART REFACTORING**: Break down complex methods while preserving behavior
- **GRADUAL MIGRATION**: Move and refactor incrementally with validation

---

## 🏗️ STEP 4.1: CORE ARCHITECTURE SETUP

**Duration**: 45 minutes  
**Output**: Complete core layer structure with base abstractions

### 4.1.1 Create Core Directory Structure
```bash
echo "🏗️ Creating core architecture structure..."

# Create core layer directories
mkdir -p src/app/core/{
    ai/{services,models,validation,config},
    testing/{stress,tle,runners,validators},
    config/{management,persistence,validation},
    tools/{compilers,executors,wrappers}
}

# Create __init__.py files
find src/app/core/ -type d -exec touch {}/__init__.py \;

echo "✅ Core architecture structure created"
```

### 4.1.2 Create Base Service Abstractions
```python
# Create src/app/core/__init__.py
cat > src/app/core/__init__.py << 'EOF'
"""
Core Business Logic Layer

This layer contains the main business logic of the application organized into
clean, testable services with proper separation of concerns.

Architecture:
- ai/: AI services and integration
- testing/: Testing logic (stress, TLE)  
- config/: Configuration management
- tools/: External tool integration
"""

from .ai import AIService
from .testing import TestingService, StressTester, TLETester
from .config import ConfigService
from .tools import ToolsService

__version__ = "1.0.0"

# Lazy service initialization
_ai_service = None
_testing_service = None
_config_service = None
_tools_service = None

def get_ai_service():
    """Get singleton AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service

def get_testing_service():
    """Get singleton testing service instance"""
    global _testing_service
    if _testing_service is None:
        _testing_service = TestingService()
    return _testing_service

def get_config_service():
    """Get singleton config service instance"""
    global _config_service
    if _config_service is None:
        _config_service = ConfigService()
    return _config_service

def get_tools_service():
    """Get singleton tools service instance"""
    global _tools_service
    if _tools_service is None:
        _tools_service = ToolsService()
    return _tools_service

__all__ = [
    'AIService', 'TestingService', 'StressTester', 'TLETester',
    'ConfigService', 'ToolsService',
    'get_ai_service', 'get_testing_service', 
    'get_config_service', 'get_tools_service'
]
EOF
```

### 4.1.3 Create Service Base Classes
```python
# Create src/app/core/base.py
cat > src/app/core/base.py << 'EOF'
"""
Base classes for core services providing common functionality
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class BaseService(ABC):
    """Base class for all core services"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"core.{name}")
        self._initialized = False
        self._config = {}
    
    async def initialize(self) -> bool:
        """Initialize the service"""
        if self._initialized:
            return True
            
        try:
            await self._initialize_impl()
            self._initialized = True
            self.logger.info(f"{self.name} service initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.name}: {e}")
            return False
    
    @abstractmethod
    async def _initialize_impl(self):
        """Service-specific initialization logic"""
        pass
    
    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return self._initialized
    
    def get_config(self) -> Dict[str, Any]:
        """Get service configuration"""
        return self._config.copy()
    
    def update_config(self, config: Dict[str, Any]):
        """Update service configuration"""
        self._config.update(config)

class AsyncService(BaseService):
    """Base class for asynchronous services"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self._tasks = []
    
    async def start(self):
        """Start async service operations"""
        if not self._initialized:
            await self.initialize()
    
    async def stop(self):
        """Stop async service operations"""
        for task in self._tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete or timeout
        if self._tasks:
            await asyncio.wait(self._tasks, timeout=5.0)
        
        self._tasks.clear()
    
    def add_task(self, coro):
        """Add an async task to the service"""
        task = asyncio.create_task(coro)
        self._tasks.append(task)
        return task

class ServiceError(Exception):
    """Base exception for service errors"""
    
    def __init__(self, service_name: str, message: str, details: Optional[str] = None):
        self.service_name = service_name
        self.message = message
        self.details = details
        super().__init__(f"{service_name}: {message}")

__all__ = ['BaseService', 'AsyncService', 'ServiceError']
EOF
```

---

## 🤖 STEP 4.2: AI SERVICES LAYER

**Duration**: 60 minutes  
**Output**: Properly organized AI services with clean interfaces

### 4.2.1 Create AI Service Architecture
```python
# Create src/app/core/ai/__init__.py
cat > src/app/core/ai/__init__.py << 'EOF'
"""
AI Services Layer

Provides clean interfaces for AI functionality including code analysis,
optimization, documentation, and debugging assistance.
"""

from .services import AIService
from .models import AIRequest, AIResponse, CodeAnalysis
from .config import AIConfig

__all__ = ['AIService', 'AIRequest', 'AIResponse', 'CodeAnalysis', 'AIConfig']
EOF
```

### 4.2.2 Migrate and Refactor AI Core
```python
# Create src/app/core/ai/services.py
cat > src/app/core/ai/services.py << 'EOF'
"""
Core AI Service providing code analysis, optimization, and assistance
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

from ..base import AsyncService, ServiceError
from .models import AIRequest, AIResponse, CodeAnalysis
from .config import AIConfig

logger = logging.getLogger(__name__)

class AIService(AsyncService):
    """Main AI service for code analysis and assistance"""
    
    def __init__(self):
        super().__init__("AI")
        self.config = AIConfig()
        self._api_client = None
        
    async def _initialize_impl(self):
        """Initialize AI service with API client"""
        try:
            # Import heavy AI modules only when needed
            from ...ai.core.editor_ai import EditorAI
            from ...ai.config.ai_config import AIConfigManager
            
            # Initialize configuration
            self.config_manager = AIConfigManager()
            await self.config_manager.load()
            
            # Initialize AI client
            self._api_client = EditorAI()
            await self._api_client.initialize()
            
            self.logger.info("AI service initialized successfully")
            
        except ImportError as e:
            raise ServiceError("AI", f"Failed to import AI modules: {e}")
        except Exception as e:
            raise ServiceError("AI", f"Failed to initialize AI client: {e}")
    
    async def analyze_code(self, code: str, language: str = "cpp") -> CodeAnalysis:
        """Analyze code for issues, complexity, and suggestions"""
        if not self._initialized:
            await self.initialize()
            
        try:
            request = AIRequest(
                action="analyze",
                code=code,
                language=language,
                context="Code analysis for optimization and debugging"
            )
            
            # Use existing AI implementation
            result = await self._api_client.analyze_code(code, language)
            
            return CodeAnalysis.from_ai_result(result)
            
        except Exception as e:
            self.logger.error(f"Code analysis failed: {e}")
            raise ServiceError("AI", f"Analysis failed: {e}")
    
    async def optimize_code(self, code: str, language: str = "cpp") -> AIResponse:
        """Generate optimized version of code"""
        if not self._initialized:
            await self.initialize()
            
        try:
            result = await self._api_client.optimize_code(code, language)
            return AIResponse(
                success=True,
                content=result.get("optimized_code", ""),
                suggestions=result.get("suggestions", []),
                metadata={"original_length": len(code)}
            )
        except Exception as e:
            self.logger.error(f"Code optimization failed: {e}")
            return AIResponse(
                success=False,
                error=str(e),
                content=""
            )
    
    async def fix_code(self, code: str, error_message: str = "", language: str = "cpp") -> AIResponse:
        """Fix code issues and compilation errors"""
        if not self._initialized:
            await self.initialize()
            
        try:
            result = await self._api_client.fix_code(code, error_message, language)
            return AIResponse(
                success=True,
                content=result.get("fixed_code", ""),
                suggestions=result.get("explanations", []),
                metadata={"error_message": error_message}
            )
        except Exception as e:
            self.logger.error(f"Code fixing failed: {e}")
            return AIResponse(
                success=False,
                error=str(e),
                content=code  # Return original on failure
            )
    
    async def document_code(self, code: str, language: str = "cpp") -> AIResponse:
        """Generate documentation for code"""
        if not self._initialized:
            await self.initialize()
            
        try:
            result = await self._api_client.document_code(code, language)
            return AIResponse(
                success=True,
                content=result.get("documented_code", ""),
                suggestions=result.get("documentation_notes", [])
            )
        except Exception as e:
            self.logger.error(f"Code documentation failed: {e}")
            return AIResponse(success=False, error=str(e), content="")
    
    async def get_custom_response(self, prompt: str, code: str = "", language: str = "cpp") -> AIResponse:
        """Get custom AI response for specific prompts"""
        if not self._initialized:
            await self.initialize()
            
        try:
            result = await self._api_client.get_custom_response(prompt, code, language)
            return AIResponse(
                success=True,
                content=result.get("response", ""),
                metadata={"prompt": prompt}
            )
        except Exception as e:
            self.logger.error(f"Custom AI request failed: {e}")
            return AIResponse(success=False, error=str(e), content="")
    
    def is_available(self) -> bool:
        """Check if AI service is available and configured"""
        return (
            self._initialized and 
            self._api_client is not None and
            self.config_manager.is_configured()
        )
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get AI usage statistics"""
        if not self._initialized:
            return {"error": "Service not initialized"}
            
        try:
            return await self._api_client.get_usage_stats()
        except Exception as e:
            return {"error": str(e)}

__all__ = ['AIService']
EOF
```

### 4.2.3 Create AI Data Models
```python
# Create src/app/core/ai/models.py
cat > src/app/core/ai/models.py << 'EOF'
"""
Data models for AI service requests and responses
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

class AIAction(Enum):
    """Available AI actions"""
    ANALYZE = "analyze"
    OPTIMIZE = "optimize"
    FIX = "fix"
    DOCUMENT = "document"
    CUSTOM = "custom"

@dataclass
class AIRequest:
    """Request model for AI operations"""
    action: str
    code: str
    language: str = "cpp"
    context: Optional[str] = None
    error_message: Optional[str] = None
    custom_prompt: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AIResponse:
    """Response model for AI operations"""
    success: bool
    content: str
    suggestions: List[str] = field(default_factory=list)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def has_content(self) -> bool:
        """Check if response has meaningful content"""
        return self.success and bool(self.content.strip())

@dataclass
class CodeAnalysis:
    """Detailed code analysis results"""
    complexity_score: int = 0
    issues: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    performance_notes: List[str] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)
    
    @classmethod
    def from_ai_result(cls, result: Dict[str, Any]) -> 'CodeAnalysis':
        """Create CodeAnalysis from AI service result"""
        return cls(
            complexity_score=result.get("complexity", 0),
            issues=result.get("issues", []),
            suggestions=result.get("suggestions", []),
            performance_notes=result.get("performance", []),
            best_practices=result.get("best_practices", [])
        )

__all__ = ['AIAction', 'AIRequest', 'AIResponse', 'CodeAnalysis']
EOF
```

---

## 🧪 STEP 4.3: TESTING SERVICES LAYER

**Duration**: 60 minutes  
**Output**: Unified testing service with stress and TLE testing capabilities

### 4.3.1 Create Testing Service Architecture
```python
# Create src/app/core/testing/__init__.py
cat > src/app/core/testing/__init__.py << 'EOF'
"""
Testing Services Layer

Unified interface for all testing functionality including stress testing,
time limit exceeded testing, and test case generation.
"""

from .services import TestingService
from .stress import StressTester
from .tle import TLETester
from .models import TestResult, TestCase, TestConfiguration

__all__ = [
    'TestingService', 'StressTester', 'TLETester',
    'TestResult', 'TestCase', 'TestConfiguration'
]
EOF
```

### 4.3.2 Create Unified Testing Service
```python
# Create src/app/core/testing/services.py
cat > src/app/core/testing/services.py << 'EOF'
"""
Unified testing service coordinating stress and TLE testing
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from ..base import AsyncService, ServiceError
from .stress import StressTester
from .tle import TLETester
from .models import TestResult, TestCase, TestConfiguration

logger = logging.getLogger(__name__)

class TestingService(AsyncService):
    """Main testing service coordinating all testing operations"""
    
    def __init__(self):
        super().__init__("Testing")
        self.stress_tester = StressTester(self)
        self.tle_tester = TLETester(self)
        self._active_tests = {}
    
    async def _initialize_impl(self):
        """Initialize testing service components"""
        try:
            await self.stress_tester.initialize()
            await self.tle_tester.initialize()
            self.logger.info("Testing service initialized")
        except Exception as e:
            raise ServiceError("Testing", f"Initialization failed: {e}")
    
    async def run_stress_test(self, 
                            code_path: Path, 
                            generator_path: Path,
                            config: TestConfiguration) -> str:
        """Run comprehensive stress testing"""
        if not self._initialized:
            await self.initialize()
        
        test_id = f"stress_{len(self._active_tests)}"
        self._active_tests[test_id] = {
            "type": "stress",
            "status": "running",
            "config": config
        }
        
        try:
            result = await self.stress_tester.run_test(code_path, generator_path, config)
            self._active_tests[test_id]["status"] = "completed"
            return test_id
        except Exception as e:
            self._active_tests[test_id]["status"] = "failed"
            self._active_tests[test_id]["error"] = str(e)
            raise ServiceError("Testing", f"Stress test failed: {e}")
    
    async def run_tle_test(self,
                          code_path: Path,
                          test_cases: List[TestCase],
                          time_limit: float) -> str:
        """Run time limit exceeded testing"""
        if not self._initialized:
            await self.initialize()
        
        test_id = f"tle_{len(self._active_tests)}"
        self._active_tests[test_id] = {
            "type": "tle",
            "status": "running",
            "time_limit": time_limit
        }
        
        try:
            result = await self.tle_tester.run_test(code_path, test_cases, time_limit)
            self._active_tests[test_id]["status"] = "completed"
            return test_id
        except Exception as e:
            self._active_tests[test_id]["status"] = "failed"
            self._active_tests[test_id]["error"] = str(e)
            raise ServiceError("Testing", f"TLE test failed: {e}")
    
    def get_test_status(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a test"""
        return self._active_tests.get(test_id)
    
    def get_active_tests(self) -> List[str]:
        """Get list of currently active test IDs"""
        return [tid for tid, info in self._active_tests.items() 
                if info["status"] == "running"]
    
    async def stop_test(self, test_id: str) -> bool:
        """Stop a running test"""
        if test_id not in self._active_tests:
            return False
        
        test_info = self._active_tests[test_id]
        if test_info["status"] != "running":
            return False
        
        try:
            if test_info["type"] == "stress":
                await self.stress_tester.stop_test()
            elif test_info["type"] == "tle":
                await self.tle_tester.stop_test()
            
            test_info["status"] = "stopped"
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop test {test_id}: {e}")
            return False
    
    def clear_completed_tests(self):
        """Clear completed test records"""
        self._active_tests = {
            tid: info for tid, info in self._active_tests.items()
            if info["status"] == "running"
        }

__all__ = ['TestingService']
EOF
```

### 4.3.3 Refactor Stress Tester
```python
# Create src/app/core/testing/stress.py
cat > src/app/core/testing/stress.py << 'EOF'
"""
Stress testing implementation with clean interface
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from ..base import BaseService, ServiceError
from .models import TestResult, TestCase, TestConfiguration

logger = logging.getLogger(__name__)

class StressTester(BaseService):
    """Handles stress testing operations"""
    
    def __init__(self, parent_service):
        super().__init__("StressTester")
        self.parent = parent_service
        self._current_test = None
        
    async def _initialize_impl(self):
        """Initialize stress tester"""
        try:
            # Import existing stress testing logic
            from ...tools.stress_tester import StressTesterLogic
            self._stress_logic = StressTesterLogic()
            await self._stress_logic.initialize()
        except ImportError as e:
            raise ServiceError("StressTester", f"Failed to import stress testing logic: {e}")
    
    async def run_test(self, 
                      code_path: Path, 
                      generator_path: Path, 
                      config: TestConfiguration) -> TestResult:
        """Run stress test with given configuration"""
        if not self._initialized:
            await self.initialize()
        
        self.logger.info(f"Starting stress test: {code_path} vs {generator_path}")
        
        try:
            # Delegate to existing implementation
            result = await self._stress_logic.run_stress_test(
                str(code_path),
                str(generator_path),
                config.to_dict()
            )
            
            return TestResult.from_stress_result(result)
            
        except Exception as e:
            self.logger.error(f"Stress test failed: {e}")
            raise ServiceError("StressTester", f"Test execution failed: {e}")
    
    async def stop_test(self):
        """Stop currently running stress test"""
        if self._current_test:
            try:
                await self._stress_logic.stop_test()
                self._current_test = None
            except Exception as e:
                self.logger.error(f"Failed to stop stress test: {e}")
    
    def get_progress(self) -> Optional[Dict[str, Any]]:
        """Get current test progress"""
        if self._stress_logic and hasattr(self._stress_logic, 'get_progress'):
            return self._stress_logic.get_progress()
        return None

__all__ = ['StressTester']
EOF
```

---

## ⚙️ STEP 4.4: CONFIGURATION LAYER

**Duration**: 45 minutes  
**Output**: Clean configuration management with validation and persistence

### 4.4.1 Create Configuration Service
```python
# Create src/app/core/config/__init__.py
cat > src/app/core/config/__init__.py << 'EOF'
"""
Configuration Management Layer

Handles all application configuration with validation, persistence,
and hot-reloading capabilities.
"""

from .services import ConfigService
from .models import ConfigSection, ConfigValue, ValidationError

__all__ = ['ConfigService', 'ConfigSection', 'ConfigValue', 'ValidationError']
EOF
```

### 4.4.2 Implement Configuration Service
```python
# Create src/app/core/config/services.py
cat > src/app/core/config/services.py << 'EOF'
"""
Core configuration service with validation and persistence
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path

from ..base import BaseService, ServiceError
from .models import ConfigSection, ConfigValue, ValidationError

logger = logging.getLogger(__name__)

class ConfigService(BaseService):
    """Main configuration service"""
    
    def __init__(self):
        super().__init__("Config")
        self._sections = {}
        self._validators = {}
        self._change_callbacks = []
        self._file_path = None
        
    async def _initialize_impl(self):
        """Initialize configuration service"""
        try:
            # Import existing config management
            from ...config.config_manager import ConfigManager
            from ...config.config_persistence import ConfigPersistence
            
            self._manager = ConfigManager()
            self._persistence = ConfigPersistence()
            
            # Load existing configuration
            await self._load_configuration()
            
            self.logger.info("Configuration service initialized")
            
        except ImportError as e:
            raise ServiceError("Config", f"Failed to import config modules: {e}")
    
    async def _load_configuration(self):
        """Load configuration from persistence layer"""
        try:
            config_data = await self._persistence.load()
            
            # Convert to internal format
            for section_name, section_data in config_data.items():
                section = ConfigSection(section_name)
                
                for key, value in section_data.items():
                    config_value = ConfigValue(key, value)
                    section.add_value(config_value)
                
                self._sections[section_name] = section
                
        except Exception as e:
            self.logger.warning(f"Failed to load config: {e}")
            # Initialize with defaults
            await self._create_default_config()
    
    async def _create_default_config(self):
        """Create default configuration"""
        # AI Configuration
        ai_section = ConfigSection("ai")
        ai_section.add_value(ConfigValue("api_key", "", str, "Gemini API Key"))
        ai_section.add_value(ConfigValue("model", "gemini-pro", str, "AI Model"))
        ai_section.add_value(ConfigValue("max_tokens", 4000, int, "Maximum tokens"))
        self._sections["ai"] = ai_section
        
        # Editor Configuration  
        editor_section = ConfigSection("editor")
        editor_section.add_value(ConfigValue("font_size", 12, int, "Editor font size"))
        editor_section.add_value(ConfigValue("tab_width", 4, int, "Tab width"))
        editor_section.add_value(ConfigValue("auto_save", True, bool, "Auto-save enabled"))
        self._sections["editor"] = editor_section
        
        # Workspace Configuration
        workspace_section = ConfigSection("workspace")  
        workspace_section.add_value(ConfigValue("default_path", str(Path.home()), str, "Default workspace path"))
        workspace_section.add_value(ConfigValue("cpp_version", "17", str, "C++ standard version"))
        self._sections["workspace"] = workspace_section
    
    def get_value(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        if section not in self._sections:
            return default
            
        section_obj = self._sections[section]
        return section_obj.get_value(key, default)
    
    async def set_value(self, section: str, key: str, value: Any) -> bool:
        """Set configuration value with validation"""
        try:
            # Validate value if validator exists
            validator_key = f"{section}.{key}"
            if validator_key in self._validators:
                validator = self._validators[validator_key]
                if not validator(value):
                    raise ValidationError(f"Invalid value for {validator_key}: {value}")
            
            # Ensure section exists
            if section not in self._sections:
                self._sections[section] = ConfigSection(section)
            
            # Set value
            old_value = self.get_value(section, key)
            self._sections[section].set_value(key, value)
            
            # Persist changes
            await self._save_configuration()
            
            # Notify callbacks
            await self._notify_change(section, key, old_value, value)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set {section}.{key}: {e}")
            return False
    
    def register_validator(self, section: str, key: str, validator: Callable[[Any], bool]):
        """Register value validator"""
        self._validators[f"{section}.{key}"] = validator
    
    def add_change_callback(self, callback: Callable[[str, str, Any, Any], None]):
        """Add callback for configuration changes"""
        self._change_callbacks.append(callback)
    
    async def _notify_change(self, section: str, key: str, old_value: Any, new_value: Any):
        """Notify all callbacks of configuration change"""
        for callback in self._change_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(section, key, old_value, new_value)
                else:
                    callback(section, key, old_value, new_value)
            except Exception as e:
                self.logger.error(f"Config callback failed: {e}")
    
    async def _save_configuration(self):
        """Save current configuration to persistence"""
        try:
            config_data = {}
            for section_name, section in self._sections.items():
                config_data[section_name] = section.to_dict()
            
            await self._persistence.save(config_data)
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def get_section_keys(self, section: str) -> List[str]:
        """Get all keys in a section"""
        if section not in self._sections:
            return []
        return self._sections[section].get_keys()
    
    def get_all_sections(self) -> List[str]:
        """Get all section names"""
        return list(self._sections.keys())

__all__ = ['ConfigService']
EOF
```

---

## 🔧 STEP 4.5: TOOLS INTEGRATION LAYER

**Duration**: 30 minutes  
**Output**: Organized external tool integration with proper abstraction

### 4.5.1 Create Tools Service
```python
# Create src/app/core/tools/__init__.py
cat > src/app/core/tools/__init__.py << 'EOF'
"""
Tools Integration Layer

Manages external tools like compilers, executors, and other utilities
with proper abstraction and error handling.
"""

from .services import ToolsService
from .models import ToolResult, CompilerResult, ExecutionResult

__all__ = ['ToolsService', 'ToolResult', 'CompilerResult', 'ExecutionResult']
EOF
```

### 4.5.2 Implement Tools Service
```python
# Create src/app/core/tools/services.py
cat > src/app/core/tools/services.py << 'EOF'
"""
External tools integration service
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..base import BaseService, ServiceError
from .models import ToolResult, CompilerResult, ExecutionResult

logger = logging.getLogger(__name__)

class ToolsService(BaseService):
    """Service for managing external tools and utilities"""
    
    def __init__(self):
        super().__init__("Tools")
        self._tools = {}
        
    async def _initialize_impl(self):
        """Initialize tools service"""
        try:
            # Import existing tool implementations
            from ...tools.compiler import CompilerTool
            from ...tools.executor import ExecutorTool
            from ...tools.file_manager import FileManagerTool
            
            # Register tools
            self._tools['compiler'] = CompilerTool()
            self._tools['executor'] = ExecutorTool()
            self._tools['file_manager'] = FileManagerTool()
            
            # Initialize all tools
            for tool_name, tool in self._tools.items():
                await tool.initialize()
                
            self.logger.info("Tools service initialized")
            
        except ImportError as e:
            # Continue with limited functionality if tools not available
            self.logger.warning(f"Some tools unavailable: {e}")
    
    async def compile_code(self, 
                          source_path: Path, 
                          output_path: Optional[Path] = None,
                          language: str = "cpp",
                          flags: List[str] = None) -> CompilerResult:
        """Compile source code"""
        if 'compiler' not in self._tools:
            return CompilerResult(
                success=False,
                error="Compiler tool not available"
            )
        
        try:
            compiler = self._tools['compiler']
            result = await compiler.compile(source_path, output_path, language, flags or [])
            
            return CompilerResult(
                success=result.get('success', False),
                output_path=result.get('output_path'),
                error=result.get('error'),
                warnings=result.get('warnings', []),
                compile_time=result.get('compile_time', 0.0)
            )
            
        except Exception as e:
            self.logger.error(f"Compilation failed: {e}")
            return CompilerResult(success=False, error=str(e))
    
    async def execute_program(self,
                            executable_path: Path,
                            input_data: str = "",
                            timeout: float = 5.0) -> ExecutionResult:
        """Execute compiled program"""
        if 'executor' not in self._tools:
            return ExecutionResult(
                success=False,
                error="Executor tool not available"
            )
        
        try:
            executor = self._tools['executor']
            result = await executor.execute(executable_path, input_data, timeout)
            
            return ExecutionResult(
                success=result.get('success', False),
                output=result.get('output', ''),
                error=result.get('error', ''),
                return_code=result.get('return_code', -1),
                execution_time=result.get('execution_time', 0.0),
                memory_usage=result.get('memory_usage', 0)
            )
            
        except Exception as e:
            self.logger.error(f"Execution failed: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def is_tool_available(self, tool_name: str) -> bool:
        """Check if a specific tool is available"""
        return tool_name in self._tools
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return list(self._tools.keys())

__all__ = ['ToolsService']
EOF
```

---

## ✅ STEP 4.6: INTEGRATION AND VALIDATION

**Duration**: 45 minutes  
**Output**: Core layer integrated with existing UI and tested

### 4.6.1 Create Integration Bridge
```python
# Create src/app/core/bridge.py
cat > src/app/core/bridge.py << 'EOF'
"""
Integration bridge between core services and UI layer

This module provides compatibility shims and adapters to gradually
migrate the UI to use the new core services.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

from . import get_ai_service, get_testing_service, get_config_service, get_tools_service

logger = logging.getLogger(__name__)

class CoreBridge:
    """Bridge for gradual migration to core services"""
    
    def __init__(self):
        self._ai_service = None
        self._testing_service = None
        self._config_service = None
        self._tools_service = None
    
    @property
    def ai(self):
        """Lazy-loaded AI service"""
        if self._ai_service is None:
            self._ai_service = get_ai_service()
        return self._ai_service
    
    @property  
    def testing(self):
        """Lazy-loaded testing service"""
        if self._testing_service is None:
            self._testing_service = get_testing_service()
        return self._testing_service
    
    @property
    def config(self):
        """Lazy-loaded config service"""
        if self._config_service is None:
            self._config_service = get_config_service()
        return self._config_service
    
    @property
    def tools(self):
        """Lazy-loaded tools service"""
        if self._tools_service is None:
            self._tools_service = get_tools_service()
        return self._tools_service
    
    async def initialize_all(self):
        """Initialize all core services"""
        services = [self.ai, self.testing, self.config, self.tools]
        
        results = []
        for service in services:
            try:
                success = await service.initialize()
                results.append((service.name, success))
            except Exception as e:
                logger.error(f"Failed to initialize {service.name}: {e}")
                results.append((service.name, False))
        
        return results

# Global bridge instance
_bridge = None

def get_core_bridge() -> CoreBridge:
    """Get global core bridge instance"""
    global _bridge
    if _bridge is None:
        _bridge = CoreBridge()
    return _bridge

__all__ = ['CoreBridge', 'get_core_bridge']
EOF
```

### 4.6.2 Update Main Application Entry Point
```python
# Update src/app/__main__.py to use core services
cat >> src/app/__main__.py << 'EOF'

# Add core services initialization
async def initialize_core_services():
    """Initialize core services on startup"""
    try:
        from .core.bridge import get_core_bridge
        bridge = get_core_bridge()
        results = await bridge.initialize_all()
        
        print("🧠 Core Services Status:")
        for service_name, success in results:
            status = "✅" if success else "❌"
            print(f"  {status} {service_name}")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Core services initialization failed: {e}")
        return False

# Update main() function to initialize services
def main():
    """Main application entry point with core services"""
    try:
        # ... existing setup code ...
        
        # Initialize core services  
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        # Initialize services before creating window
        with loop:
            services_ready = loop.run_until_complete(initialize_core_services())
            
            # Create window
            window = create_main_window()
            window.show()
            
            if services_ready:
                print("🎉 Application started with core services")
            else:
                print("⚠️ Application started with limited functionality")
            
            # Run event loop
            loop.run_forever()
            
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        sys.exit(1)
EOF
```

### 4.6.3 Create Phase Validation Tests
```python
# Create tests/test_phase4_core_layer.py
cat > tests/test_phase4_core_layer.py << 'EOF'
"""
Phase 4 validation tests for core layer architecture
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class TestCoreServices:
    """Test core service layer functionality"""
    
    @pytest.mark.asyncio
    async def test_core_services_import(self):
        """Test that all core services can be imported"""
        try:
            from app.core import (
                get_ai_service, get_testing_service,
                get_config_service, get_tools_service
            )
            assert callable(get_ai_service)
            assert callable(get_testing_service)
            assert callable(get_config_service)
            assert callable(get_tools_service)
        except ImportError as e:
            pytest.fail(f"Core services import failed: {e}")
    
    @pytest.mark.asyncio
    async def test_ai_service_initialization(self):
        """Test AI service can be initialized"""
        from app.core import get_ai_service
        
        ai_service = get_ai_service()
        assert ai_service is not None
        assert ai_service.name == "AI"
        
        # Test initialization (may fail without API key, that's expected)
        try:
            result = await ai_service.initialize()
            # Either succeeds or fails gracefully
            assert isinstance(result, bool)
        except Exception:
            # Expected if API not configured
            pass
    
    @pytest.mark.asyncio  
    async def test_config_service(self):
        """Test configuration service"""
        from app.core import get_config_service
        
        config_service = get_config_service()
        assert config_service is not None
        
        # Initialize
        await config_service.initialize()
        assert config_service.is_initialized()
        
        # Test basic operations
        await config_service.set_value("test", "key", "value")
        result = config_service.get_value("test", "key")
        assert result == "value"
    
    @pytest.mark.asyncio
    async def test_bridge_integration(self):
        """Test core bridge integration"""
        from app.core.bridge import get_core_bridge
        
        bridge = get_core_bridge()
        assert bridge is not None
        
        # Test lazy loading
        assert bridge.ai is not None
        assert bridge.config is not None
        assert bridge.testing is not None
        assert bridge.tools is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
EOF
```

---

## 📋 STEP 4.7: PHASE COMPLETION AND VALIDATION

**Duration**: 15 minutes  
**Output**: Complete phase validation and documentation

### 4.7.1 Final Integration Test
```bash
echo "🧪 Running Phase 4 integration tests..."

# Test core services can be imported
python -c "
import sys
sys.path.insert(0, 'src')

try:
    from app.core import get_ai_service, get_config_service, get_testing_service, get_tools_service
    from app.core.bridge import get_core_bridge
    
    print('✅ All core services importable')
    
    # Test bridge
    bridge = get_core_bridge()
    print('✅ Core bridge created successfully')
    
    print('🎉 Phase 4 integration test passed')
    
except ImportError as e:
    print(f'❌ Integration test failed: {e}')
    exit(1)
"

echo "✅ Phase 4 validation complete"
```

### 4.7.2 Create Completion Documentation
```markdown
# Phase 4 Completion Report

**Status**: ✅ COMPLETED  
**Duration**: 3-4 hours  
**Date**: $(date)

## Core Architecture Created

### 🧠 src/app/core/ Structure
- **ai/**: Clean AI service interfaces with async support
- **testing/**: Unified testing services (stress + TLE)  
- **config/**: Configuration management with validation
- **tools/**: External tool integration layer
- **bridge.py**: Compatibility bridge for gradual migration

### ✅ Services Implemented
1. **AIService**: Code analysis, optimization, fixing, documentation
2. **TestingService**: Unified stress and TLE testing coordination  
3. **ConfigService**: Configuration with validation and persistence
4. **ToolsService**: Compiler, executor, and tool management
5. **CoreBridge**: Integration layer for UI compatibility

### 🔗 Integration Points
- Services use existing implementations under the hood
- Bridge pattern enables gradual migration
- Async-first design for better responsiveness
- Clean interfaces with proper error handling

## Ready for Phase 5

**Next Phase**: [PHASE_5_PERSISTENCE.md](PHASE_5_PERSISTENCE.md)
**Focus**: Data layer organization and persistence abstraction
```

---

## 🎯 PHASE 4 SUCCESS CRITERIA

✅ **Core Architecture**: Clean 4-layer structure (ai, testing, config, tools)  
✅ **Service Interfaces**: Async services with proper error handling  
✅ **Backward Compatibility**: Existing functionality preserved via bridge  
✅ **Clean Abstractions**: Services hide implementation complexity  
✅ **Integration Ready**: Core services ready for UI layer consumption

**Phase 4 Complete**: Ready for persistence layer organization in Phase 5
