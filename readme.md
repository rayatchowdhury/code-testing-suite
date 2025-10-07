<div align="center">

# 🚀 Code Testing Suite

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![Qt](https://img.shields.io/badge/Qt-6.0+-green.svg)](https://www.qt.io)

<img src="resources/readme/header_image.png" alt="Code Testing Suite" width="300px">

<p align="center">
A powerful desktop application designed to streamline your coding workflow with advanced testing capabilities and AI assistance. 🎯
</p>

</div>

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🚀 Installation](#-installation)
- [📖 Usage](#-usage)
- [📸 Screenshots](#-screenshots)
- [⚙️ Configuration](#️-configuration)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## ✨ Features

<div align="center">
<table>
<tr>
<td width="50%" align="center">

### 📝 Code Editor

- Syntax highlighting
- Auto-completion
- Multiple file support
- AI-powered assistance

</td>
<td width="50%" align="center">

### 🔄 Comparator

- Custom test cases
- Automated testing
- Performance analysis
- Error detection

</td>
</tr>
<tr>
<td width="50%" align="center">

### ⏱️ Benchmarker

- Time limit testing
- Memory usage tracking
- Performance optimization
- Detailed reports

</td>
<td width="50%" align="center">

### 🤖 AI Assistant

- Code explanations
- Bug detection
- Optimization suggestions
- Smart documentation

</td>
</tr>
</table>
</div>

## 🏗️ Architecture

The Code Testing Suite features a clean, maintainable architecture built around the **BaseRunner Template Method Pattern**, achieved through a comprehensive migration that eliminated over 800 lines of duplicate code.

### 🎯 Core Architecture

<div align="center">

```
BaseRunner (Template Method Pattern)
├── ValidatorRunner    → Validation testing
├── TLERunner         → Time limit testing  
└── Comparator        → Comparison testing
```

</div>

### 🔧 Key Components

<div align="center">
<table>
<tr>
<td width="50%" align="center">

### 🏛️ Base Classes

- **BaseRunner**: Template method for test execution
- **BaseCompiler**: Unified compilation logic
- **BaseTestWorker**: Parallel test execution
- **ProcessExecutor**: System utilities

</td>
<td width="50%" align="center">

### ⚙️ Specialized Workers

- **ValidatorTestWorker**: 3-stage validation
- **TLETestWorker**: Performance monitoring  
- **ComparisonTestWorker**: Output comparison
- Optimized parallel execution per type

</td>
</tr>
</table>
</div>

### 🚀 Migration Benefits

- **✅ 70-80% code reduction** in core files
- **✅ Single source of truth** for all testing logic
- **✅ Template method pattern** for consistent behavior
- **✅ Easy extensibility** for new test types
- **✅ Improved maintainability** with centralized logic

### �️ Database Architecture

The application features a **modern, refactored database layer** with clean separation of concerns:

<div align="center">
<table>
<tr>
<td width="50%" align="center">

### 🏛️ Design Patterns

- **Repository Pattern**: Data access abstraction
- **Facade Pattern**: Simplified API interface
- **Singleton Pattern**: Connection management
- **Service Layer**: Business logic separation

</td>
<td width="50%" align="center">

### 📊 Key Benefits

- **✅ 12 focused modules** (vs 1 monolithic class)
- **✅ 151 targeted tests** (100% passing)
- **✅ Full type safety** with type hints
- **✅ Thread-safe operations** with proper locking

</td>
</tr>
</table>
</div>

**Quick Start:**
```python
from src.app.persistence.database import DatabaseManager, TestResult

db = DatabaseManager()

# Query test results
results = db.get_test_results(test_type='comparison', limit=100)

# Get statistics
stats = db.get_test_statistics()
print(f"Total tests: {stats['total_tests']}")
```

### 📖 For Developers

**Adding a new test type:**
```python
from src.app.core.tools.base.base_runner import BaseRunner

class MyCustomRunner(BaseRunner):
    def _create_worker(self):
        return MyCustomTestWorker()
    
    def _process_results(self, result):
        # Custom result processing
        pass
```

**Working with the database:**
```python
from src.app.persistence.database import DatabaseManager, TestResult

db = DatabaseManager()

# Create test result
result = TestResult(
    test_type='comparison',
    file_path='solution.cpp',
    test_count=10,
    passed_tests=10,
    failed_tests=0,
    total_time=0.5,
    timestamp=datetime.now().isoformat(),
    project_name='my_project',
    test_details='{}',
    files_snapshot='{}',
    mismatch_analysis=''
)
test_id = db.save_test_result(result)
```

<details>
<summary>📚 View Architecture Documentation</summary>

**Testing Architecture:**
- [Migration Plan](MIGRATION_PLAN_DETAILED.md) - Complete migration strategy
- [Architecture Patterns](ARCHITECTURE_PATTERNS.md) - Template method implementation  
- [Phase 5 Summary](PHASE_5_COMPLETION_SUMMARY.md) - Cleanup and optimization
- [Phase 6 Results](PHASE_6_VALIDATION_RESULTS.md) - Final validation

**Database Architecture:**
- [Database Architecture](DATABASE_ARCHITECTURE.md) - Comprehensive database documentation
- [Phase 8 Complete](PHASE8_COMPLETE.md) - Database refactoring summary
- [Migration Playbook](MIGRATION_PLAYBOOK.md) - Step-by-step migration guide

</details>

## 🚀 Installation

<details>
<summary>Click to expand installation steps</summary>

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/code-testing-suite.git
   cd code-testing-suite
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the application**:
   ```bash
   python main.py
   ```
</details>

## 📸 Screenshots

<div align="center">

<details>
<summary>Click to view screenshots</summary>

### 🖥️ Main Interface
<img src="resources/readme/main_window.png" alt="Main Window" width="800px">

### ✏️ Code Editor
<img src="resources/readme/editor_window.png" alt="Code Editor" width="800px">

### 🔄 Comparison Testing
<img src="resources/readme/stress_window.png" alt="Comparison Tester" width="800px">

### 📊 Results View
<img src="resources/readme/results.png" alt="Results" width="800px">

### ❓ Help Center
<img src="resources/readme/help_center.png" alt="Help Center" width="800px">

</details>

</div>

## ⚙️ Configuration

<div align="center">

| Setting | Description |
|---------|-------------|
| 📦 C++ Version | Select your preferred C++ standard |
| 📁 Workspace | Choose your project workspace folder |
| 🤖 API Key | Configure Gemini AI API access |
| ✏️ Editor | Customize editor appearance and behavior |

</div>

## 🤝 Contributing

We welcome contributions! Follow these steps:

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m 'Add AmazingFeature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

### Made with ❤️ for developers who love clean code and efficient testing

[⬆ Back to top](#-code-testing-suite)

</div>
