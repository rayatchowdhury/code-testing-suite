# Phase 4 Refactoring Strategy

## High Priority Targets (>100 lines)

### 1. detailed_results_widget.py (_setup_ui methods)
**Current**: Multiple `_setup_ui()` methods ~100+ lines each, complex UI setup
**Strategy**: 
- Extract `_setup_layout()` - Container and tab setup
- Extract `_setup_tab_content()` - Individual tab creation  
- Extract `_setup_data_display()` - Data visualization
- Extract `_connect_signals()` - Signal connections
- Extract `_apply_styling()` - Style application

### 2. EditorWidget._setup_ui()
**Current**: ~120+ lines, handles editor + AI integration
**Strategy**:
- Extract `_setup_editor_core()` - Core editor setup
- Extract `_setup_ai_integration()` - AI panel integration
- Extract `_setup_syntax_highlighting()` - Syntax highlighting
- Extract `_connect_editor_signals()` - Editor signal connections

### 3. AIPanel._setup_ui()
**Current**: ~80 lines, handles multiple AI services  
**Strategy**:
- Extract `_setup_action_buttons()` - Analysis and action buttons
- Extract `_setup_custom_commands()` - Custom command interface
- Extract `_setup_button_layout()` - Button arrangement and spacing
- Extract `_connect_ai_signals()` - AI service signal connections

## Medium Priority Targets (50-100 lines)

### 4. Sidebar Widget Creation
**Current**: Multiple navigation setup methods ~70+ lines
**Strategy**:
- Extract `_setup_navigation_sections()` - Section creation
- Extract `_setup_footer_buttons()` - Footer with settings/exit
- Extract `_apply_sidebar_styling()` - Style and theming

### 5. Database Manager Methods
**Current**: Multiple database operations ~60+ lines each
**Strategy**:
- Extract `_setup_connection()` - Database connection setup
- Extract `_execute_migrations()` - Schema migration logic
- Extract `_handle_errors()` - Error handling and recovery

## Import Optimization Targets

### Circular Import Fixes
1. `views/main_window.py` → `widgets/sidebar.py` → `views/*` 
   **Fix**: Use dependency injection for window references
   
2. `styles/components/__init__.py` imports everything at module level
   **Fix**: Lazy imports, on-demand loading
   
3. `utils/window_factory.py` imports all view classes
   **Fix**: Registry pattern with lazy imports

### Heavy Import Reduction  
1. `ai/` modules import multiple heavy libraries
   **Fix**: Import only in functions that use them
   
2. `tools/` modules import subprocess/os at module level
   **Fix**: Import within execution functions
   
3. `styles/` components import entire style sheets
   **Fix**: Import specific styles only

## Performance Optimization Opportunities

### Startup Time Improvements
1. **Lazy Widget Loading**: Create widgets only when needed (especially in tabs)
2. **Lazy Style Loading**: Load styles on first use  
3. **Lazy AI Loading**: Initialize AI services on demand
4. **Lazy Database Loading**: Connect to database only when needed

### Memory Usage Optimization  
1. **Widget Cleanup**: Proper disposal of unused widgets (especially in results)
2. **Cache Management**: LRU cache for frequently used data
3. **Style Caching**: Cache computed styles for common components
4. **Database Connection Pooling**: Efficient database connection management

## Complexity Metrics (Current State)

**Identified Complex Files**:
- detailed_results_widget.py: ~600+ lines (3 classes with complex UI)
- database_manager.py: ~400+ lines (multiple responsibilities)
- editor.py (widget): ~350+ lines (editor + AI integration)
- results_widget.py: ~300+ lines (complex data display)
- config_styles.py: ~250+ lines (all styling mixed together)

**Method Complexity Targets**:
- Methods >50 lines: 23 identified
- Methods >100 lines: 8 identified  
- Classes >200 lines: 12 identified

**Target Metrics After Refactoring**:
- Max method length: 20 lines
- Max class complexity: Single responsibility
- Import count per file: <10 core imports
- Circular imports: 0
