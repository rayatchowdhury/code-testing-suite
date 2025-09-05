# 🧠 REFACTORING GUIDELINES - SMART CODE TRANSFORMATION

**Purpose**: Comprehensive guidelines for intelligently refactoring complex methods and reducing unnecessary complexity while preserving functionality and design language.

---

## 🎯 REFACTORING PHILOSOPHY

### Core Principles
1. **Preserve Functionality**: Every refactoring must maintain identical behavior
2. **Maintain Design Language**: UI/UX must remain pixel-perfect
3. **Reduce Complexity**: Break down large methods into focused, single-purpose functions
4. **Eliminate Waste**: Remove unnecessary imports, redundant code, over-engineering
5. **Improve Readability**: Code should tell a story, not require archeological skills

### Quality Metrics
- **Method Length**: Target max 20 lines (current: some >100 lines)
- **Cyclomatic Complexity**: Target <10 per method (current: some >20)
- **Import Count**: Target <10 imports per file (current: some >20)  
- **Test Coverage**: Maintain/improve coverage with each refactoring
- **Performance**: No degradation in startup time or memory usage

---

## 🔍 IDENTIFICATION PATTERNS

### Anti-Patterns to Refactor

#### 1. God Methods (>50 lines)
```python
# BEFORE: EditorDisplay._setup_ui() - 150 lines
def _setup_ui(self):
    # Layout setup (20 lines)
    main_layout = QVBoxLayout()
    self.setLayout(main_layout)
    # ... many layout operations
    
    # Control setup (30 lines)  
    self.control_panel = QWidget()
    # ... many control creations
    
    # Editor setup (40 lines)
    self.editor = CodeEditor()
    # ... many editor configurations
    
    # AI panel setup (30 lines)
    self.ai_panel = AIPanel()
    # ... many AI configurations
    
    # Signal connections (30 lines)
    self.editor.textChanged.connect(...)
    # ... many signal connections

# AFTER: Focused methods
def _setup_ui(self):
    """Setup the complete UI - orchestrates focused setup methods"""
    self._setup_layout()
    self._setup_controls()
    self._setup_editor()
    self._setup_ai_integration()
    self._connect_signals()

def _setup_layout(self):
    """Setup main layout structure"""
    main_layout = QVBoxLayout()
    self.setLayout(main_layout)
    # Only layout-related operations

def _setup_controls(self):
    """Setup control panel and buttons"""
    self.control_panel = QWidget()
    # Only control-related operations
```

#### 2. Import Bloat  
```python
# BEFORE: Unnecessary imports
import sys, os, json, time, datetime, pathlib, subprocess
from typing import Dict, List, Optional, Union, Any, Callable, Tuple
from PySide6.QtWidgets import *  # Import everything
from PySide6.QtCore import *     # Import everything
from PySide6.QtGui import *      # Import everything

# AFTER: Minimal imports
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Signal

# Heavy imports only when needed
def _initialize_ai(self):
    """Initialize AI services - import only when needed"""
    from google.generativeai import configure  # Lazy import
    configure(api_key=self.api_key)
```

#### 3. Complex Conditionals
```python  
# BEFORE: Complex nested conditionals
def handle_button_click(self, button_name):
    if button_name == "code_editor":
        if self.current_window != "code_editor":
            if self.has_unsaved_changes():
                if self.confirm_discard_changes():
                    self._switch_to_code_editor()
                else:
                    return
            else:
                self._switch_to_code_editor()
    elif button_name == "stress_tester":
        # Similar nested logic...
    # ... many more conditions

# AFTER: Strategy pattern with focused methods  
def handle_button_click(self, button_name):
    """Handle sidebar button clicks - delegates to specific handlers"""
    handler = self._get_button_handler(button_name)
    if handler:
        handler()

def _get_button_handler(self, button_name):
    """Get appropriate handler for button"""
    handlers = {
        "code_editor": self._handle_code_editor_click,
        "stress_tester": self._handle_stress_tester_click,
        "tle_tester": self._handle_tle_tester_click,
    }
    return handlers.get(button_name)

def _handle_code_editor_click(self):
    """Handle code editor button click"""
    if not self._can_switch_windows():
        return
    self._switch_to_code_editor()
```

#### 4. Repeated Code Patterns
```python
# BEFORE: Repeated UI setup patterns
def _setup_stress_test_controls(self):
    # Button 1
    self.start_btn = QPushButton("Start Test")
    self.start_btn.setObjectName("start_button")
    self.start_btn.setStyleSheet(BUTTON_STYLE)
    self.start_btn.clicked.connect(self.start_test)
    layout.addWidget(self.start_btn)
    
    # Button 2  
    self.stop_btn = QPushButton("Stop Test")
    self.stop_btn.setObjectName("stop_button") 
    self.stop_btn.setStyleSheet(BUTTON_STYLE)
    self.stop_btn.clicked.connect(self.stop_test)
    layout.addWidget(self.stop_btn)
    
    # Button 3...

# AFTER: Factory method for common patterns
def _setup_stress_test_controls(self):
    """Setup stress testing control buttons"""
    buttons = [
        ("Start Test", "start_button", self.start_test),
        ("Stop Test", "stop_button", self.stop_test),
        ("Clear Results", "clear_button", self.clear_results),
    ]
    
    for text, name, handler in buttons:
        button = self._create_control_button(text, name, handler)
        self.control_layout.addWidget(button)

def _create_control_button(self, text, object_name, handler):
    """Create a standardized control button"""
    button = QPushButton(text)
    button.setObjectName(object_name)
    button.setStyleSheet(BUTTON_STYLE) 
    button.clicked.connect(handler)
    return button
```

---

## 🛠️ REFACTORING TECHNIQUES

### 1. Extract Method
**When**: Method >20 lines or does multiple things  
**How**: Identify logical chunks, extract to focused methods

```python
# Template for method extraction
def original_large_method(self):
    """Original method - too long and complex"""
    # Step 1: Setup (extract to _setup_initial_state)
    # Step 2: Processing (extract to _process_data)  
    # Step 3: Validation (extract to _validate_results)
    # Step 4: Cleanup (extract to _cleanup_resources)

def refactored_orchestrator_method(self):
    """Refactored orchestrator - tells the story"""
    self._setup_initial_state()
    data = self._process_data()
    if self._validate_results(data):
        self._apply_results(data)
    self._cleanup_resources()
```

### 2. Extract Class
**When**: Method has too many responsibilities or complex state  
**How**: Group related data and methods into focused classes

```python
# BEFORE: Monolithic class
class EditorDisplay(QWidget):
    def __init__(self):
        # Editor state
        self.editor = None
        self.syntax_highlighter = None
        
        # AI state  
        self.ai_panel = None
        self.ai_service = None
        
        # File state
        self.current_file = None
        self.file_watcher = None
        
    def _setup_editor(self):
        # 50 lines of editor setup
        
    def _setup_ai(self):
        # 40 lines of AI setup
        
    def _setup_file_management(self):
        # 30 lines of file setup

# AFTER: Focused classes with clear responsibilities  
class EditorDisplay(QWidget):
    """Main editor display - orchestrates components"""
    def __init__(self):
        self.editor_manager = EditorManager(self)
        self.ai_manager = AIManager(self)  
        self.file_manager = FileManager(self)
        
    def _setup_ui(self):
        self.editor_manager.setup_editor()
        self.ai_manager.setup_ai_panel()
        self.file_manager.setup_file_controls()

class EditorManager:
    """Manages code editor and syntax highlighting"""
    def setup_editor(self):
        # Focused on editor concerns only

class AIManager:
    """Manages AI integration and panel"""  
    def setup_ai_panel(self):
        # Focused on AI concerns only
```

### 3. Replace Conditionals with Polymorphism
**When**: Many if/elif chains based on type/mode  
**How**: Use strategy pattern or command pattern

```python
# BEFORE: Complex conditionals
def handle_compile_request(self, language, code):
    if language == "cpp":
        compiler = "g++"
        flags = ["-std=c++17", "-O2"]
        extension = ".cpp"
    elif language == "python":
        compiler = "python"
        flags = []
        extension = ".py"
    elif language == "java":
        compiler = "javac" 
        flags = ["-cp", "."]
        extension = ".java"
    # ... complex compilation logic

# AFTER: Strategy pattern
class CompilationStrategy:
    """Base strategy for code compilation"""
    def get_compiler_config(self):
        raise NotImplementedError
        
class CppCompilationStrategy(CompilationStrategy):
    def get_compiler_config(self):
        return {
            "compiler": "g++",
            "flags": ["-std=c++17", "-O2"], 
            "extension": ".cpp"
        }

class PythonCompilationStrategy(CompilationStrategy):
    def get_compiler_config(self):
        return {
            "compiler": "python",
            "flags": [],
            "extension": ".py"
        }

def handle_compile_request(self, language, code):
    strategy = self._get_compilation_strategy(language)
    config = strategy.get_compiler_config()
    return self._execute_compilation(code, config)
```

### 4. Lazy Initialization
**When**: Heavy imports or expensive object creation  
**How**: Initialize only when first accessed

```python
# BEFORE: Heavy imports at module level
from google.generativeai import configure, GenerativeModel
from some_heavy_library import HeavyProcessor
import expensive_module

class AIService:
    def __init__(self):
        self.model = GenerativeModel("gemini-pro")  # Slow initialization
        self.processor = HeavyProcessor()           # Memory intensive

# AFTER: Lazy initialization
class AIService:
    def __init__(self):
        self._model = None
        self._processor = None
        
    @property
    def model(self):
        """Lazy-load AI model only when needed"""
        if self._model is None:
            from google.generativeai import GenerativeModel
            self._model = GenerativeModel("gemini-pro")
        return self._model
        
    @property  
    def processor(self):
        """Lazy-load processor only when needed"""
        if self._processor is None:
            from some_heavy_library import HeavyProcessor
            self._processor = HeavyProcessor()
        return self._processor
```

---

## 🎨 DESIGN LANGUAGE PRESERVATION

### UI/UX Preservation Checklist

#### Critical Elements (Cannot Change)
```python
# ✅ PRESERVE: Exact color values
SIDEBAR_COLORS = {
    'background': '#1b1b1e',      # Exact hex values
    'accent': '#007acc',          # Must not change
    'hover': '#2d2d30',          # Precise hover states
}

# ✅ PRESERVE: Layout dimensions  
SIDEBAR_WIDTH = 280              # Exact pixel values
SPLITTER_MIN_WIDTH = 150         # Minimum panel sizes
HEADER_HEIGHT = 40               # Exact heights

# ✅ PRESERVE: Component behavior
def _setup_hover_effects(self):
    """Maintain exact hover behavior"""
    # Original hover timing and effects must be identical
```

#### Safe Refactoring Areas
```python
# ✅ SAFE: Internal implementation details
def _calculate_layout_positions(self):
    """Internal calculation - can be optimized"""
    # Implementation can be improved as long as results are identical

# ✅ SAFE: Code organization  
def _setup_ui(self):
    """Can be broken into smaller methods"""
    self._setup_colors()        # Extract color setup
    self._setup_dimensions()    # Extract dimension setup  
    self._setup_interactions()  # Extract interaction setup

# ✅ SAFE: Performance optimizations
@lru_cache(maxsize=128)
def _get_computed_style(self, component_type):
    """Cache expensive style computations"""
    # Internal optimization - end result identical
```

### Testing Design Preservation
```python
def test_design_preservation():
    """Automated test for design language preservation"""
    
    # Test color values
    from app.styles.constants.colors import MATERIAL_COLORS
    assert MATERIAL_COLORS['primary'] == '#007acc'
    assert MATERIAL_COLORS['background'] == '#1b1b1e'
    
    # Test component dimensions
    sidebar = Sidebar("Test")
    assert sidebar.minimumWidth() == 280
    
    # Test style application
    button = QPushButton("Test")
    apply_button_style(button)
    assert "background-color: #007acc" in button.styleSheet()
```

---

## 🚦 REFACTORING WORKFLOW

### Phase-by-Phase Approach

#### Phase 4: Core Layer Refactoring
1. **AI Services** - Extract AI functionality into focused services
2. **Testing Services** - Extract testing logic from tools  
3. **Config Management** - Separate business logic from UI
4. **Tool Wrappers** - Organize external tool interfaces

#### Phase 6: Presentation Layer Refactoring  
1. **Feature Grouping** - Organize by user features, not technical layers
2. **Widget Extraction** - Create reusable UI components
3. **Style Organization** - Organize styles by component hierarchy
4. **Interaction Patterns** - Standardize user interaction handling

### Step-by-Step Method Refactoring

#### For Each Complex Method:
```bash
# 1. Understand current behavior
python -c "
from app.views.main_window import MainWindow
import inspect
method = MainWindow._setup_ui  
print(f'Lines: {len(inspect.getsource(method).splitlines())}')
print('Current behavior documented')
"

# 2. Extract focused methods
# - Identify logical chunks (5-20 lines each)
# - Create descriptive method names
# - Maintain exact same end result

# 3. Test behavior preservation
pytest tests/test_method_refactoring.py::test_setup_ui_behavior

# 4. Optimize imports and performance
# - Remove unused imports
# - Add lazy loading where beneficial  
# - Cache expensive computations

# 5. Document the refactoring
# - Update docstrings
# - Add inline comments for complex logic
# - Update ADR if architectural changes
```

---

## 📊 QUALITY METRICS & VALIDATION

### Code Quality Targets
```python
# Complexity metrics (using radon)
def check_complexity():
    """Run after each refactoring to validate improvement"""
    import subprocess
    result = subprocess.run(['radon', 'cc', 'src/', '--min=B'], 
                          capture_output=True, text=True)
    
    # Target: No methods with complexity > B (11)
    if "C" in result.stdout or "D" in result.stdout:
        print("❌ High complexity methods still exist")
        return False
    
    print("✅ All methods within complexity targets") 
    return True

# Import analysis
def check_import_health():
    """Validate import optimization"""
    heavy_imports = []
    
    for file_path in Path("src").rglob("*.py"):
        with open(file_path) as f:
            lines = f.readlines()
            import_count = sum(1 for line in lines 
                             if line.strip().startswith(('import ', 'from ')))
            
            if import_count > 10:
                heavy_imports.append((file_path, import_count))
    
    if heavy_imports:
        print(f"⚠️  Files with many imports: {heavy_imports}")
    else:
        print("✅ Import counts within targets")

# Performance validation  
def validate_performance():
    """Ensure no performance regression"""
    import json
    
    # Load baseline
    with open('tests/performance_baseline.json') as f:
        baseline = json.load(f)
    
    # Measure current performance
    current = measure_current_performance()
    
    # Compare (allow 10% tolerance)
    for metric, baseline_value in baseline['imports'].items():
        current_value = current['imports'].get(metric, 0)
        if current_value > baseline_value * 1.1:
            print(f"❌ Performance regression in {metric}")
            return False
    
    print("✅ Performance maintained or improved")
    return True
```

### Automated Validation
```python
def run_refactoring_validation():
    """Complete validation after refactoring"""
    validations = [
        ("Complexity Check", check_complexity),
        ("Import Health", check_import_health), 
        ("Performance Validation", validate_performance),
        ("Design Preservation", test_design_preservation),
        ("Functional Tests", run_functional_tests)
    ]
    
    all_passed = True
    for name, validator in validations:
        print(f"\n🔍 Running {name}...")
        try:
            if not validator():
                all_passed = False
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            all_passed = False
    
    if all_passed:
        print("\n🎉 All validations passed! Refactoring successful.")
        return True
    else:
        print("\n💥 Some validations failed. Review and fix issues.")
        return False
```

---

## 🎯 SUCCESS DEFINITION

Refactoring is successful when:

1. **Functionality Preserved**: ✅
   - All features work identically
   - All tests pass
   - No behavioral changes

2. **Design Language Maintained**: ✅  
   - UI looks identical
   - Interactions work the same
   - Performance is maintained

3. **Code Quality Improved**: ✅
   - Methods under 20 lines
   - Complexity under 11
   - Imports optimized  
   - Clear separation of concerns

4. **Maintainability Enhanced**: ✅
   - Code tells a clear story
   - Easy to understand and modify
   - Good documentation
   - Proper error handling

---

**This document guides all refactoring decisions throughout the migration. Every code change should be validated against these guidelines to ensure we achieve our goals of improved maintainability while preserving the exact user experience.**
