# Multi-Language TestTabWidget Integration Guide

## How to Enable Multi-Language Support in Your Modules

### 1. Update Display Area Classes (Comparator, Validator, Benchmarker)

Replace the existing TestTabWidget initialization in your display area classes:

```python
# OLD: Single language mode
tab_config = {
    'Generator': 'generator.cpp',
    'Test Code': 'test.cpp'
}

self.test_tabs = TestTabWidget(
    parent=self,
    tab_config=tab_config,
    default_tab='Generator'
)

# NEW: Multi-language mode  
tab_config = {
    'Generator': {
        'cpp': 'generator.cpp',
        'py': 'generator.py', 
        'java': 'Generator.java'
    },
    'Test Code': {
        'cpp': 'test.cpp',
        'py': 'test.py',
        'java': 'TestCode.java'
    }
}

self.test_tabs = TestTabWidget(
    parent=self,
    tab_config=tab_config,
    default_tab='Generator',
    multi_language=True,  # Enable multi-language
    default_language='cpp'  # Default language
)
```

### 2. Update Signal Connections

Add the new language change signal:

```python
def _connect_signals(self):
    # Existing signals
    self.test_tabs.fileChanged.connect(self._handle_file_changed)
    self.test_tabs.tabClicked.connect(self._handle_tab_clicked)
    
    # NEW: Handle language changes
    self.test_tabs.languageChanged.connect(self._handle_language_changed)

def _handle_language_changed(self, tab_name, language):
    """Handle language switching."""
    print(f"Switched to {language.upper()} in {tab_name}")
    # You can add custom logic here, like updating syntax highlighting
```

### 3. Backward Compatibility

The widget maintains 100% backward compatibility:

- Old code without `multi_language=True` works exactly as before
- Existing display area classes don't need immediate changes
- Can migrate modules one by one

### 4. Configuration Examples

#### Comparator (3 tabs, 3 languages):
```python
tab_config = {
    'Generator': {
        'cpp': 'generator.cpp',
        'py': 'generator.py',
        'java': 'Generator.java'
    },
    'Correct Code': {
        'cpp': 'correct.cpp', 
        'py': 'correct.py',
        'java': 'CorrectCode.java'
    },
    'Test Code': {
        'cpp': 'test.cpp',
        'py': 'test.py', 
        'java': 'TestCode.java'
    }
}
```

#### Validator (3 tabs, 3 languages):
```python
tab_config = {
    'Generator': {
        'cpp': 'generator.cpp',
        'py': 'generator.py',
        'java': 'Generator.java'
    },
    'Test Code': {
        'cpp': 'test.cpp',
        'py': 'test.py',
        'java': 'TestCode.java'
    },
    'Validator Code': {
        'cpp': 'validator.cpp',
        'py': 'validator.py',
        'java': 'ValidatorCode.java'
    }
}
```

#### Benchmarker (2 tabs, 3 languages):
```python
tab_config = {
    'Generator': {
        'cpp': 'generator.cpp',
        'py': 'generator.py', 
        'java': 'Generator.java'
    },
    'Test Code': {
        'cpp': 'test.cpp',
        'py': 'test.py',
        'java': 'TestCode.java'
    }
}
```

### 5. New Methods Available

```python
# Get current language
current_lang = self.test_tabs.get_current_language()

# Switch language programmatically  
self.test_tabs.switch_language('Generator', 'py')

# Check if multi-language mode is enabled
if self.test_tabs.multi_language:
    print("Multi-language mode enabled")
```

### 6. File Structure

With multi-language support, your workspace will look like:

```
workspace/
├── generator.cpp
├── generator.py  
├── Generator.java
├── test.cpp
├── test.py
├── TestCode.java
├── validator.cpp
├── validator.py
└── ValidatorCode.java
```

### 7. Templates Included

The widget provides appropriate templates for:
- **C++**: STL containers, iostream, algorithms
- **Python**: Input handling, list comprehensions, pythonic code
- **Java**: Scanner, ArrayList, proper class structure

Each template is tailored for the specific tab type (Generator, Test Code, Validator Code).