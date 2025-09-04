# Database Integration Migration Guide

## Overview

This document outlines the database integration added to the Code Testing Suite. The application now uses SQLite for persistent data storage, replacing text files for test results and session management.

## What's New

### 🗄️ Database Storage
- **SQLite Database**: Local database file stored in user data directory
- **Automatic Initialization**: Database tables created automatically on first run
- **No External Dependencies**: SQLite is included with Python

### 📊 Test Results Storage
- **Persistent History**: All stress test and TLE test results are automatically saved
- **Detailed Tracking**: Input/output data, execution times, and success rates stored
- **Analytics Ready**: Data structured for statistical analysis and trending

### 🖥️ Results Window
- **New Results Window**: Comprehensive view of all test history
- **Filter Options**: Filter by test type, date range, and project
- **Statistics View**: Success rates, performance trends, and analytics
- **Detailed Analysis**: Click any result to see full test details

### 💾 Enhanced Session Management
- **Database Sessions**: Editor sessions saved to database alongside JSON files
- **Better Tracking**: Track project usage and file access patterns
- **Recovery Options**: More robust session restoration capabilities

## Database Schema

### Test Results Table
```sql
CREATE TABLE test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_type TEXT NOT NULL,           -- 'stress' or 'tle'
    file_path TEXT NOT NULL,
    test_count INTEGER NOT NULL,
    passed_tests INTEGER NOT NULL,
    failed_tests INTEGER NOT NULL,
    total_time REAL NOT NULL,
    timestamp TEXT NOT NULL,
    test_details TEXT,                 -- JSON with detailed results
    project_name TEXT
);
```

### Sessions Table
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_name TEXT NOT NULL,
    open_files TEXT,                   -- JSON array of file paths
    active_file TEXT,
    timestamp TEXT NOT NULL,
    project_name TEXT
);
```

### Projects Table
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL UNIQUE,
    project_path TEXT NOT NULL,
    last_accessed TEXT NOT NULL,
    file_count INTEGER DEFAULT 0,
    total_lines INTEGER DEFAULT 0,
    languages TEXT                     -- JSON array of languages
);
```

## File Structure Changes

### New Files Added
```
database/
├── __init__.py              # Database package initialization
├── database_manager.py      # Main database management class
└── models.py               # Data models (TestResult, Session, ProjectData)

views/results/
├── __init__.py              # Results package initialization
├── results_window.py        # Results window with sidebar
└── results_widget.py       # Main results display widget

views/help_center/content/
└── results_guide.html       # Help documentation for results feature

test_database.py             # Database integration test script
```

### Modified Files
```
tools/stresser.py            # Added database saving for stress test results
tools/tle_runner.py          # Added database saving for TLE test results
views/main_window.py         # Added Results button to navigation
views/main_window.html       # Added Results feature description
views/stress_tester/stress_tester_window.py  # Added Results button
views/tle_tester/tle_tester_window.py        # Added Results button
views/code_editor/code_editor_window.py      # Enhanced session management
utils/window_factory.py     # Added results window registration
requirements.txt            # Updated with database notes
```

## Migration Process

### For Existing Users
1. **Automatic Database Creation**: Database is created automatically on first run
2. **Backwards Compatibility**: Existing JSON session files continue to work
3. **Gradual Migration**: Old data remains accessible while new data uses database
4. **No Action Required**: Users don't need to do anything for migration

### For Developers
1. **Import Database Package**: `from database import DatabaseManager, TestResult`
2. **Initialize Manager**: `db_manager = DatabaseManager()`
3. **Save Results**: Use provided data classes to save test results
4. **Query Data**: Use built-in methods for retrieving and filtering data

## Usage Examples

### Saving Test Results
```python
from database import DatabaseManager, TestResult
from datetime import datetime
import json

db = DatabaseManager()

# Save stress test result
result = TestResult(
    test_type="stress",
    file_path="/path/to/test.cpp",
    test_count=10,
    passed_tests=8,
    failed_tests=2,
    total_time=45.5,
    timestamp=datetime.now().isoformat(),
    test_details=json.dumps(detailed_results),
    project_name="My Project"
)

result_id = db.save_test_result(result)
```

### Querying Results
```python
# Get all results
all_results = db.get_test_results(limit=100)

# Get stress tests only
stress_results = db.get_test_results(test_type="stress", limit=50)

# Get project statistics
stats = db.get_test_statistics(project_name="My Project")
print(f"Success rate: {stats['success_rate']:.1f}%")
```

## Benefits

### For Users
- **Complete Test History**: Never lose test results again
- **Performance Tracking**: See how your code improves over time
- **Better Analytics**: Understand your testing patterns and success rates
- **Faster Access**: Quick filtering and searching of test results

### For Developers
- **Structured Data**: Well-defined schema for test results and sessions
- **Extensible**: Easy to add new data types and analytics
- **Reliable Storage**: SQLite provides ACID compliance and data integrity
- **No Dependencies**: No external database server required

## Future Enhancements

### Planned Features
- **Export Functionality**: Export results to CSV, JSON, or PDF
- **Advanced Analytics**: Performance trends, comparison charts
- **Project Management**: Better project organization and tracking
- **Backup/Restore**: Easy backup and restore of all data

### Possible Extensions
- **Cloud Sync**: Optional cloud synchronization of results
- **Team Features**: Share results and analytics with team members
- **Custom Reports**: Generate custom reports and summaries
- **API Integration**: Connect with external testing platforms

## Troubleshooting

### Common Issues
1. **Database Locked**: Close other instances of the application
2. **Permission Errors**: Ensure write access to user data directory
3. **Corruption**: Database includes automatic recovery mechanisms

### Reset Database
If needed, delete the database file to start fresh:
```bash
# Windows
del "%APPDATA%\Code Testing Suite\code_testing_suite.db"

# Linux/Mac
rm ~/.local/share/Code Testing Suite/code_testing_suite.db
```

## Testing

Run the database test script to verify integration:
```bash
python test_database.py
```

This will test all database operations and confirm the integration is working correctly.

---

**Note**: The database integration is designed to be transparent to users. All existing functionality continues to work exactly as before, with the added benefit of persistent result storage and analytics.
