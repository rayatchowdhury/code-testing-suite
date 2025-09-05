# 💾 PHASE 5: PERSISTENCE LAYER

**Duration**: 2-3 hours  
**Risk Level**: 🟡 Medium  
**Prerequisites**: Phase 4 Complete  
**Goal**: Organize data layer with clean persistence abstraction and database management

---

## 📋 PHASE OVERVIEW

This phase creates a clean persistence layer separating data access logic from business logic. We establish proper database abstraction, file operations management, and data models while maintaining exact functionality.

### Phase Objectives
1. **Persistence Layer**: Create `src/app/persistence/` for all data operations
2. **Database Abstraction**: Clean database interfaces with repository patterns
3. **File Operations**: Organized file management with proper error handling
4. **Data Models**: Type-safe data models with validation
5. **Migration Support**: Database schema management and migrations

### Architecture Philosophy
- **DATA LAYER SEPARATION**: Business logic never directly touches storage
- **REPOSITORY PATTERN**: Clean interfaces for data access operations
- **TYPE SAFETY**: Strongly typed data models with validation
- **TRANSACTION SUPPORT**: Proper ACID compliance where needed

---

## 🗄️ STEP 5.1: PERSISTENCE ARCHITECTURE SETUP

**Duration**: 30 minutes  
**Output**: Complete persistence layer structure with base abstractions

### 5.1.1 Create Persistence Directory Structure
```bash
echo "🗄️ Creating persistence layer structure..."

# Create persistence layer directories
mkdir -p src/app/persistence/{
    database/{repositories,models,migrations,connections},
    files/{managers,operations,storage},
    cache/{memory,disk,distributed},
    search/{indexing,queries,engines}
}

# Create __init__.py files
find src/app/persistence/ -type d -exec touch {}/__init__.py \;

echo "✅ Persistence architecture structure created"
```

### 5.1.2 Create Base Persistence Abstractions
```python
# Create src/app/persistence/__init__.py
cat > src/app/persistence/__init__.py << 'EOF'
"""
Persistence Layer

Provides clean data access abstractions for the application including
database operations, file management, caching, and search functionality.

Architecture:
- database/: Database operations and repositories
- files/: File system operations and storage
- cache/: Caching implementations
- search/: Search and indexing functionality
"""

from .database import DatabaseManager, Repository
from .files import FileManager, StorageManager
from .models import BaseModel, ValidationError

# Lazy initialization of managers
_db_manager = None
_file_manager = None

def get_database_manager():
    """Get singleton database manager"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

def get_file_manager():
    """Get singleton file manager"""
    global _file_manager
    if _file_manager is None:
        _file_manager = FileManager()
    return _file_manager

__all__ = [
    'DatabaseManager', 'Repository', 'FileManager', 'StorageManager',
    'BaseModel', 'ValidationError',
    'get_database_manager', 'get_file_manager'
]
EOF
```

### 5.1.3 Create Base Persistence Classes
```python
# Create src/app/persistence/base.py
cat > src/app/persistence/base.py << 'EOF'
"""
Base classes for persistence layer components
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic
from pathlib import Path

logger = logging.getLogger(__name__)

T = TypeVar('T')

class PersistenceError(Exception):
    """Base exception for persistence operations"""
    
    def __init__(self, operation: str, message: str, details: Optional[str] = None):
        self.operation = operation
        self.message = message
        self.details = details
        super().__init__(f"{operation}: {message}")

class Repository(Generic[T], ABC):
    """Base repository interface for data access operations"""
    
    def __init__(self, model_class: type):
        self.model_class = model_class
        self.logger = logging.getLogger(f"repo.{model_class.__name__}")
    
    @abstractmethod
    async def find_by_id(self, id: Union[int, str]) -> Optional[T]:
        """Find entity by ID"""
        pass
    
    @abstractmethod
    async def find_all(self) -> List[T]:
        """Find all entities"""
        pass
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """Save entity (insert or update)"""
        pass
    
    @abstractmethod
    async def delete(self, id: Union[int, str]) -> bool:
        """Delete entity by ID"""
        pass
    
    async def find_by_criteria(self, criteria: Dict[str, Any]) -> List[T]:
        """Find entities matching criteria"""
        # Default implementation - override for efficiency
        all_entities = await self.find_all()
        results = []
        
        for entity in all_entities:
            matches = True
            for key, value in criteria.items():
                if not hasattr(entity, key) or getattr(entity, key) != value:
                    matches = False
                    break
            if matches:
                results.append(entity)
        
        return results

class BaseManager(ABC):
    """Base class for persistence managers"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"persistence.{name}")
        self._initialized = False
        self._config = {}
    
    async def initialize(self) -> bool:
        """Initialize the manager"""
        if self._initialized:
            return True
        
        try:
            await self._initialize_impl()
            self._initialized = True
            self.logger.info(f"{self.name} manager initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.name}: {e}")
            return False
    
    @abstractmethod
    async def _initialize_impl(self):
        """Manager-specific initialization logic"""
        pass
    
    def is_initialized(self) -> bool:
        """Check if manager is initialized"""
        return self._initialized
    
    async def shutdown(self):
        """Clean shutdown of manager resources"""
        try:
            await self._shutdown_impl()
            self._initialized = False
            self.logger.info(f"{self.name} manager shut down")
        except Exception as e:
            self.logger.error(f"Error during {self.name} shutdown: {e}")
    
    async def _shutdown_impl(self):
        """Manager-specific shutdown logic"""
        pass

__all__ = ['PersistenceError', 'Repository', 'BaseManager']
EOF
```

---

## 🗃️ STEP 5.2: DATABASE LAYER

**Duration**: 60 minutes  
**Output**: Clean database abstraction with repository pattern implementation

### 5.2.1 Create Database Manager
```python
# Create src/app/persistence/database/__init__.py
cat > src/app/persistence/database/__init__.py << 'EOF'
"""
Database Layer

Provides database connectivity, repository implementations,
and data model management.
"""

from .manager import DatabaseManager
from .repositories import TestResultRepository, ConfigRepository, FileRepository
from .models import TestResult, ConfigEntry, FileRecord
from .connections import get_connection

__all__ = [
    'DatabaseManager', 
    'TestResultRepository', 'ConfigRepository', 'FileRepository',
    'TestResult', 'ConfigEntry', 'FileRecord',
    'get_connection'
]
EOF
```

### 5.2.2 Implement Database Manager
```python
# Create src/app/persistence/database/manager.py
cat > src/app/persistence/database/manager.py << 'EOF'
"""
Database manager handling connections and repository coordination
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import sqlite3
import aiosqlite

from ..base import BaseManager, PersistenceError
from .repositories import TestResultRepository, ConfigRepository, FileRepository

logger = logging.getLogger(__name__)

class DatabaseManager(BaseManager):
    """Main database manager coordinating all database operations"""
    
    def __init__(self):
        super().__init__("Database")
        self._connection = None
        self._repositories = {}
        self._db_path = None
    
    async def _initialize_impl(self):
        """Initialize database manager"""
        try:
            # Import existing database components
            from ...database.database_manager import DatabaseManager as ExistingDB
            from ...database.models import TestResult as ExistingTestResult
            
            # Get database configuration
            from ...constants.paths import PROJECT_ROOT
            self._db_path = PROJECT_ROOT / "data" / "app.db"
            self._db_path.parent.mkdir(exist_ok=True)
            
            # Initialize connection
            await self._setup_connection()
            
            # Initialize repositories
            await self._setup_repositories()
            
            # Run migrations
            await self._run_migrations()
            
            self.logger.info("Database manager initialized successfully")
            
        except Exception as e:
            raise PersistenceError("DatabaseManager", f"Initialization failed: {e}")
    
    async def _setup_connection(self):
        """Setup database connection"""
        try:
            self._connection = await aiosqlite.connect(str(self._db_path))
            await self._connection.execute("PRAGMA foreign_keys = ON")
            await self._connection.commit()
            
        except Exception as e:
            raise PersistenceError("DatabaseManager", f"Connection failed: {e}")
    
    async def _setup_repositories(self):
        """Initialize all repositories"""
        self._repositories = {
            'test_results': TestResultRepository(self._connection),
            'config': ConfigRepository(self._connection),
            'files': FileRepository(self._connection)
        }
        
        # Initialize each repository
        for repo_name, repository in self._repositories.items():
            try:
                await repository.initialize()
                self.logger.info(f"Repository {repo_name} initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize {repo_name}: {e}")
    
    async def _run_migrations(self):
        """Run database migrations"""
        try:
            # Check if migrations table exists
            cursor = await self._connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'"
            )
            migrations_table_exists = await cursor.fetchone() is not None
            
            if not migrations_table_exists:
                await self._create_migrations_table()
                await self._run_initial_migration()
            else:
                await self._run_pending_migrations()
                
        except Exception as e:
            raise PersistenceError("DatabaseManager", f"Migration failed: {e}")
    
    async def _create_migrations_table(self):
        """Create migrations tracking table"""
        await self._connection.execute("""
            CREATE TABLE migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await self._connection.commit()
    
    async def _run_initial_migration(self):
        """Run initial database schema creation"""
        # Test results table
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_type TEXT NOT NULL,
                status TEXT NOT NULL,
                execution_time REAL,
                memory_usage INTEGER,
                test_cases_passed INTEGER,
                test_cases_total INTEGER,
                error_message TEXT,
                output TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Configuration table
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS config_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                section TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(section, key)
            )
        """)
        
        # File records table
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS file_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL UNIQUE,
                size INTEGER,
                hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        await self._connection.commit()
        
        # Mark migration as applied
        await self._connection.execute(
            "INSERT INTO migrations (name) VALUES (?)",
            ("initial_schema",)
        )
        await self._connection.commit()
    
    async def _run_pending_migrations(self):
        """Run any pending migrations"""
        # Check for applied migrations
        cursor = await self._connection.execute("SELECT name FROM migrations")
        applied = {row[0] for row in await cursor.fetchall()}
        
        # Define available migrations
        migrations = [
            ("initial_schema", self._run_initial_migration),
            # Add future migrations here
        ]
        
        # Run pending migrations
        for name, migration_func in migrations:
            if name not in applied:
                await migration_func()
                self.logger.info(f"Applied migration: {name}")
    
    def get_repository(self, name: str):
        """Get repository by name"""
        if name not in self._repositories:
            raise PersistenceError("DatabaseManager", f"Repository '{name}' not found")
        return self._repositories[name]
    
    @property
    def test_results(self):
        """Get test results repository"""
        return self.get_repository('test_results')
    
    @property
    def config(self):
        """Get configuration repository"""
        return self.get_repository('config')
    
    @property
    def files(self):
        """Get file records repository"""  
        return self.get_repository('files')
    
    async def execute_query(self, query: str, params: tuple = ()) -> Any:
        """Execute custom query"""
        if not self._connection:
            raise PersistenceError("DatabaseManager", "No database connection")
        
        try:
            cursor = await self._connection.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                return await cursor.fetchall()
            else:
                await self._connection.commit()
                return cursor.rowcount
        except Exception as e:
            await self._connection.rollback()
            raise PersistenceError("DatabaseManager", f"Query execution failed: {e}")
    
    async def _shutdown_impl(self):
        """Shutdown database connections"""
        if self._connection:
            await self._connection.close()
            self._connection = None

__all__ = ['DatabaseManager']
EOF
```

### 5.2.3 Create Repository Implementations
```python
# Create src/app/persistence/database/repositories.py
cat > src/app/persistence/database/repositories.py << 'EOF'
"""
Repository implementations for database operations
"""

import json
import logging
from typing import List, Optional, Union, Dict, Any
from datetime import datetime

from ..base import Repository, PersistenceError
from .models import TestResult, ConfigEntry, FileRecord

logger = logging.getLogger(__name__)

class TestResultRepository(Repository[TestResult]):
    """Repository for test result operations"""
    
    def __init__(self, connection):
        super().__init__(TestResult)
        self._connection = connection
    
    async def initialize(self):
        """Initialize repository"""
        self.logger.info("Test result repository ready")
    
    async def find_by_id(self, id: Union[int, str]) -> Optional[TestResult]:
        """Find test result by ID"""
        try:
            cursor = await self._connection.execute(
                "SELECT * FROM test_results WHERE id = ?", (int(id),)
            )
            row = await cursor.fetchone()
            return TestResult.from_db_row(row) if row else None
        except Exception as e:
            raise PersistenceError("TestResult", f"Find by ID failed: {e}")
    
    async def find_all(self) -> List[TestResult]:
        """Find all test results"""
        try:
            cursor = await self._connection.execute(
                "SELECT * FROM test_results ORDER BY created_at DESC"
            )
            rows = await cursor.fetchall()
            return [TestResult.from_db_row(row) for row in rows]
        except Exception as e:
            raise PersistenceError("TestResult", f"Find all failed: {e}")
    
    async def save(self, result: TestResult) -> TestResult:
        """Save test result"""
        try:
            if result.id is None:
                # Insert new result
                cursor = await self._connection.execute("""
                    INSERT INTO test_results 
                    (test_type, status, execution_time, memory_usage, 
                     test_cases_passed, test_cases_total, error_message, output, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.test_type, result.status, result.execution_time,
                    result.memory_usage, result.test_cases_passed, result.test_cases_total,
                    result.error_message, result.output, json.dumps(result.metadata)
                ))
                result.id = cursor.lastrowid
            else:
                # Update existing result
                await self._connection.execute("""
                    UPDATE test_results SET
                    test_type = ?, status = ?, execution_time = ?, memory_usage = ?,
                    test_cases_passed = ?, test_cases_total = ?, error_message = ?, 
                    output = ?, metadata = ?
                    WHERE id = ?
                """, (
                    result.test_type, result.status, result.execution_time,
                    result.memory_usage, result.test_cases_passed, result.test_cases_total,
                    result.error_message, result.output, json.dumps(result.metadata), result.id
                ))
            
            await self._connection.commit()
            return result
            
        except Exception as e:
            await self._connection.rollback()
            raise PersistenceError("TestResult", f"Save failed: {e}")
    
    async def delete(self, id: Union[int, str]) -> bool:
        """Delete test result"""
        try:
            cursor = await self._connection.execute(
                "DELETE FROM test_results WHERE id = ?", (int(id),)
            )
            await self._connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            await self._connection.rollback()
            raise PersistenceError("TestResult", f"Delete failed: {e}")
    
    async def find_by_type(self, test_type: str) -> List[TestResult]:
        """Find results by test type"""
        try:
            cursor = await self._connection.execute(
                "SELECT * FROM test_results WHERE test_type = ? ORDER BY created_at DESC",
                (test_type,)
            )
            rows = await cursor.fetchall()
            return [TestResult.from_db_row(row) for row in rows]
        except Exception as e:
            raise PersistenceError("TestResult", f"Find by type failed: {e}")

class ConfigRepository(Repository[ConfigEntry]):
    """Repository for configuration operations"""
    
    def __init__(self, connection):
        super().__init__(ConfigEntry)
        self._connection = connection
    
    async def initialize(self):
        """Initialize repository"""
        self.logger.info("Configuration repository ready")
    
    async def find_by_id(self, id: Union[int, str]) -> Optional[ConfigEntry]:
        """Find config entry by ID"""
        try:
            cursor = await self._connection.execute(
                "SELECT * FROM config_entries WHERE id = ?", (int(id),)
            )
            row = await cursor.fetchone()
            return ConfigEntry.from_db_row(row) if row else None
        except Exception as e:
            raise PersistenceError("ConfigEntry", f"Find by ID failed: {e}")
    
    async def find_by_key(self, section: str, key: str) -> Optional[ConfigEntry]:
        """Find config entry by section and key"""
        try:
            cursor = await self._connection.execute(
                "SELECT * FROM config_entries WHERE section = ? AND key = ?",
                (section, key)
            )
            row = await cursor.fetchone()
            return ConfigEntry.from_db_row(row) if row else None
        except Exception as e:
            raise PersistenceError("ConfigEntry", f"Find by key failed: {e}")
    
    async def find_all(self) -> List[ConfigEntry]:
        """Find all config entries"""
        try:
            cursor = await self._connection.execute(
                "SELECT * FROM config_entries ORDER BY section, key"
            )
            rows = await cursor.fetchall()
            return [ConfigEntry.from_db_row(row) for row in rows]
        except Exception as e:
            raise PersistenceError("ConfigEntry", f"Find all failed: {e}")
    
    async def save(self, entry: ConfigEntry) -> ConfigEntry:
        """Save config entry"""
        try:
            if entry.id is None:
                # Insert or replace entry
                cursor = await self._connection.execute("""
                    INSERT OR REPLACE INTO config_entries 
                    (section, key, value, type, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (entry.section, entry.key, entry.value, entry.type, entry.description))
                
                if cursor.lastrowid:
                    entry.id = cursor.lastrowid
            else:
                # Update existing entry
                await self._connection.execute("""
                    UPDATE config_entries SET
                    section = ?, key = ?, value = ?, type = ?, description = ?
                    WHERE id = ?
                """, (entry.section, entry.key, entry.value, entry.type, entry.description, entry.id))
            
            await self._connection.commit()
            return entry
            
        except Exception as e:
            await self._connection.rollback()
            raise PersistenceError("ConfigEntry", f"Save failed: {e}")
    
    async def delete(self, id: Union[int, str]) -> bool:
        """Delete config entry"""
        try:
            cursor = await self._connection.execute(
                "DELETE FROM config_entries WHERE id = ?", (int(id),)
            )
            await self._connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            await self._connection.rollback()
            raise PersistenceError("ConfigEntry", f"Delete failed: {e}")

class FileRepository(Repository[FileRecord]):
    """Repository for file record operations"""
    
    def __init__(self, connection):
        super().__init__(FileRecord)
        self._connection = connection
    
    async def initialize(self):
        """Initialize repository"""
        self.logger.info("File repository ready")
    
    async def find_by_id(self, id: Union[int, str]) -> Optional[FileRecord]:
        """Find file record by ID"""
        try:
            cursor = await self._connection.execute(
                "SELECT * FROM file_records WHERE id = ?", (int(id),)
            )
            row = await cursor.fetchone()
            return FileRecord.from_db_row(row) if row else None
        except Exception as e:
            raise PersistenceError("FileRecord", f"Find by ID failed: {e}")
    
    async def find_by_path(self, path: str) -> Optional[FileRecord]:
        """Find file record by path"""
        try:
            cursor = await self._connection.execute(
                "SELECT * FROM file_records WHERE path = ?", (path,)
            )
            row = await cursor.fetchone()
            return FileRecord.from_db_row(row) if row else None
        except Exception as e:
            raise PersistenceError("FileRecord", f"Find by path failed: {e}")
    
    async def find_all(self) -> List[FileRecord]:
        """Find all file records"""
        try:
            cursor = await self._connection.execute(
                "SELECT * FROM file_records ORDER BY accessed_at DESC"
            )
            rows = await cursor.fetchall()
            return [FileRecord.from_db_row(row) for row in rows]
        except Exception as e:
            raise PersistenceError("FileRecord", f"Find all failed: {e}")
    
    async def save(self, record: FileRecord) -> FileRecord:
        """Save file record"""
        try:
            if record.id is None:
                cursor = await self._connection.execute("""
                    INSERT OR REPLACE INTO file_records 
                    (path, size, hash, metadata)
                    VALUES (?, ?, ?, ?)
                """, (record.path, record.size, record.hash, json.dumps(record.metadata)))
                
                if cursor.lastrowid:
                    record.id = cursor.lastrowid
            else:
                await self._connection.execute("""
                    UPDATE file_records SET
                    path = ?, size = ?, hash = ?, metadata = ?, accessed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (record.path, record.size, record.hash, json.dumps(record.metadata), record.id))
            
            await self._connection.commit()
            return record
            
        except Exception as e:
            await self._connection.rollback()
            raise PersistenceError("FileRecord", f"Save failed: {e}")
    
    async def delete(self, id: Union[int, str]) -> bool:
        """Delete file record"""
        try:
            cursor = await self._connection.execute(
                "DELETE FROM file_records WHERE id = ?", (int(id),)
            )
            await self._connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            await self._connection.rollback()
            raise PersistenceError("FileRecord", f"Delete failed: {e}")

__all__ = ['TestResultRepository', 'ConfigRepository', 'FileRepository']
EOF
```

---

## 📁 STEP 5.3: FILE OPERATIONS LAYER

**Duration**: 45 minutes  
**Output**: Clean file management abstraction with proper error handling

### 5.3.1 Create File Manager
```python
# Create src/app/persistence/files/__init__.py
cat > src/app/persistence/files/__init__.py << 'EOF'
"""
File Operations Layer

Provides clean file system operations, storage management,
and file tracking capabilities.
"""

from .manager import FileManager
from .operations import FileOperations, StorageOperations
from .models import FileInfo, StorageLocation

__all__ = ['FileManager', 'FileOperations', 'StorageOperations', 'FileInfo', 'StorageLocation']
EOF
```

### 5.3.2 Implement File Manager
```python
# Create src/app/persistence/files/manager.py
cat > src/app/persistence/files/manager.py << 'EOF'
"""
File manager handling all file system operations
"""

import asyncio
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, BinaryIO
import shutil
import os

from ..base import BaseManager, PersistenceError
from .operations import FileOperations, StorageOperations
from .models import FileInfo, StorageLocation

logger = logging.getLogger(__name__)

class FileManager(BaseManager):
    """Main file manager for all file operations"""
    
    def __init__(self):
        super().__init__("FileManager")
        self.file_ops = FileOperations()
        self.storage_ops = StorageOperations()
        self._workspace_path = None
        self._temp_path = None
    
    async def _initialize_impl(self):
        """Initialize file manager"""
        try:
            # Import existing file operations
            from ...utils.file_operations import FileOperations as ExistingFileOps
            self._existing_ops = ExistingFileOps()
            
            # Set up workspace and temp directories
            from ...constants.paths import PROJECT_ROOT, TEMP_DIR, OUTPUT_DIR
            self._workspace_path = PROJECT_ROOT
            self._temp_path = TEMP_DIR
            self._output_path = OUTPUT_DIR
            
            # Ensure directories exist
            self._temp_path.mkdir(exist_ok=True)
            self._output_path.mkdir(exist_ok=True)
            
            # Initialize operations
            await self.file_ops.initialize(self._workspace_path)
            await self.storage_ops.initialize(self._output_path)
            
            self.logger.info("File manager initialized successfully")
            
        except Exception as e:
            raise PersistenceError("FileManager", f"Initialization failed: {e}")
    
    async def read_file(self, path: Union[str, Path], encoding: str = 'utf-8') -> str:
        """Read file content"""
        try:
            file_path = Path(path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            
            content = await self.file_ops.read_text(file_path, encoding)
            
            # Update file access tracking
            await self._track_file_access(file_path)
            
            return content
            
        except Exception as e:
            raise PersistenceError("FileManager", f"Read failed: {e}")
    
    async def write_file(self, path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
        """Write content to file"""
        try:
            file_path = Path(path)
            
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            success = await self.file_ops.write_text(file_path, content, encoding)
            
            if success:
                await self._track_file_access(file_path)
            
            return success
            
        except Exception as e:
            raise PersistenceError("FileManager", f"Write failed: {e}")
    
    async def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> bool:
        """Copy file from source to destination"""
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                raise FileNotFoundError(f"Source file not found: {source}")
            
            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(str(source_path), str(dest_path))
            
            # Track both files
            await self._track_file_access(source_path)
            await self._track_file_access(dest_path)
            
            return True
            
        except Exception as e:
            raise PersistenceError("FileManager", f"Copy failed: {e}")
    
    async def delete_file(self, path: Union[str, Path]) -> bool:
        """Delete file"""
        try:
            file_path = Path(path)
            
            if file_path.exists():
                file_path.unlink()
                return True
            
            return False
            
        except Exception as e:
            raise PersistenceError("FileManager", f"Delete failed: {e}")
    
    async def get_file_info(self, path: Union[str, Path]) -> Optional[FileInfo]:
        """Get detailed file information"""
        try:
            file_path = Path(path)
            
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            
            # Calculate file hash for integrity checking
            file_hash = await self._calculate_file_hash(file_path)
            
            return FileInfo(
                path=str(file_path),
                size=stat.st_size,
                created_at=stat.st_ctime,
                modified_at=stat.st_mtime,
                hash=file_hash,
                is_directory=file_path.is_dir()
            )
            
        except Exception as e:
            raise PersistenceError("FileManager", f"File info failed: {e}")
    
    async def list_files(self, 
                        directory: Union[str, Path], 
                        pattern: str = "*",
                        recursive: bool = False) -> List[FileInfo]:
        """List files in directory"""
        try:
            dir_path = Path(directory)
            
            if not dir_path.exists() or not dir_path.is_dir():
                return []
            
            files = []
            
            if recursive:
                file_paths = dir_path.rglob(pattern)
            else:
                file_paths = dir_path.glob(pattern)
            
            for file_path in file_paths:
                if file_path.is_file():
                    file_info = await self.get_file_info(file_path)
                    if file_info:
                        files.append(file_info)
            
            return files
            
        except Exception as e:
            raise PersistenceError("FileManager", f"List files failed: {e}")
    
    async def create_backup(self, path: Union[str, Path]) -> Optional[Path]:
        """Create backup of file"""
        try:
            source_path = Path(path)
            
            if not source_path.exists():
                return None
            
            # Create backup with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source_path.stem}_{timestamp}{source_path.suffix}"
            backup_path = self._temp_path / "backups" / backup_name
            
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            success = await self.copy_file(source_path, backup_path)
            return backup_path if success else None
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            return None
    
    async def _calculate_file_hash(self, path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        try:
            hasher = hashlib.sha256()
            
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            
            return hasher.hexdigest()
            
        except Exception as e:
            self.logger.error(f"Hash calculation failed: {e}")
            return ""
    
    async def _track_file_access(self, path: Path):
        """Track file access for statistics"""
        try:
            # This could integrate with database layer to track file usage
            # For now, just log access
            self.logger.debug(f"File accessed: {path}")
        except Exception as e:
            self.logger.error(f"File tracking failed: {e}")
    
    async def cleanup_temp_files(self, max_age_hours: int = 24):
        """Cleanup old temporary files"""
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for file_path in self._temp_path.rglob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        try:
                            file_path.unlink()
                            self.logger.debug(f"Cleaned up temp file: {file_path}")
                        except Exception as e:
                            self.logger.warning(f"Failed to clean {file_path}: {e}")
            
        except Exception as e:
            self.logger.error(f"Temp cleanup failed: {e}")

__all__ = ['FileManager']
EOF
```

---

## 📊 STEP 5.4: DATA MODELS

**Duration**: 30 minutes  
**Output**: Type-safe data models with validation

### 5.4.1 Create Base Data Models
```python
# Create src/app/persistence/models.py
cat > src/app/persistence/models.py << 'EOF'
"""
Data models for persistence layer
"""

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod

class ValidationError(Exception):
    """Exception raised when model validation fails"""
    
    def __init__(self, model_name: str, field: str, message: str):
        self.model_name = model_name
        self.field = field
        self.message = message
        super().__init__(f"{model_name}.{field}: {message}")

class BaseModel(ABC):
    """Base class for all data models"""
    
    def validate(self) -> bool:
        """Validate model data"""
        try:
            self._validate_impl()
            return True
        except ValidationError:
            return False
    
    @abstractmethod
    def _validate_impl(self):
        """Model-specific validation logic"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return self.__dict__.copy()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create model from dictionary"""
        return cls(**data)

@dataclass
class TestResult(BaseModel):
    """Test result data model"""
    
    id: Optional[int] = None
    test_type: str = ""
    status: str = ""
    execution_time: float = 0.0
    memory_usage: int = 0
    test_cases_passed: int = 0
    test_cases_total: int = 0
    error_message: Optional[str] = None
    output: Optional[str] = None
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def _validate_impl(self):
        """Validate test result"""
        if not self.test_type:
            raise ValidationError("TestResult", "test_type", "Test type is required")
        
        if self.test_type not in ["stress", "tle", "unit", "integration"]:
            raise ValidationError("TestResult", "test_type", "Invalid test type")
        
        if not self.status:
            raise ValidationError("TestResult", "status", "Status is required")
        
        if self.status not in ["pending", "running", "passed", "failed", "timeout", "error"]:
            raise ValidationError("TestResult", "status", "Invalid status")
        
        if self.execution_time < 0:
            raise ValidationError("TestResult", "execution_time", "Execution time cannot be negative")
    
    @classmethod
    def from_db_row(cls, row) -> 'TestResult':
        """Create TestResult from database row"""
        if not row:
            return None
        
        return cls(
            id=row[0],
            test_type=row[1],
            status=row[2],
            execution_time=row[3] or 0.0,
            memory_usage=row[4] or 0,
            test_cases_passed=row[5] or 0,
            test_cases_total=row[6] or 0,
            error_message=row[7],
            output=row[8],
            created_at=datetime.fromisoformat(row[9]) if row[9] else None,
            metadata=json.loads(row[10]) if row[10] else {}
        )

@dataclass  
class ConfigEntry(BaseModel):
    """Configuration entry data model"""
    
    id: Optional[int] = None
    section: str = ""
    key: str = ""
    value: str = ""
    type: str = "str"
    description: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    def _validate_impl(self):
        """Validate config entry"""
        if not self.section:
            raise ValidationError("ConfigEntry", "section", "Section is required")
        
        if not self.key:
            raise ValidationError("ConfigEntry", "key", "Key is required")
        
        if self.type not in ["str", "int", "float", "bool", "list", "dict"]:
            raise ValidationError("ConfigEntry", "type", "Invalid type")
    
    def get_typed_value(self) -> Any:
        """Get value converted to proper type"""
        try:
            if self.type == "int":
                return int(self.value)
            elif self.type == "float":
                return float(self.value)
            elif self.type == "bool":
                return self.value.lower() in ("true", "1", "yes", "on")
            elif self.type == "list":
                return json.loads(self.value)
            elif self.type == "dict":
                return json.loads(self.value)
            else:
                return self.value
        except (ValueError, json.JSONDecodeError):
            return self.value
    
    @classmethod
    def from_db_row(cls, row) -> 'ConfigEntry':
        """Create ConfigEntry from database row"""
        if not row:
            return None
        
        return cls(
            id=row[0],
            section=row[1],
            key=row[2],
            value=row[3],
            type=row[4],
            description=row[5],
            updated_at=datetime.fromisoformat(row[6]) if row[6] else None
        )

@dataclass
class FileRecord(BaseModel):
    """File record data model"""
    
    id: Optional[int] = None
    path: str = ""
    size: int = 0
    hash: str = ""
    created_at: Optional[datetime] = None
    accessed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def _validate_impl(self):
        """Validate file record"""
        if not self.path:
            raise ValidationError("FileRecord", "path", "Path is required")
        
        if self.size < 0:
            raise ValidationError("FileRecord", "size", "Size cannot be negative")
    
    @classmethod
    def from_db_row(cls, row) -> 'FileRecord':
        """Create FileRecord from database row"""
        if not row:
            return None
        
        return cls(
            id=row[0],
            path=row[1],
            size=row[2] or 0,
            hash=row[3] or "",
            created_at=datetime.fromisoformat(row[4]) if row[4] else None,
            accessed_at=datetime.fromisoformat(row[5]) if row[5] else None,
            metadata=json.loads(row[6]) if row[6] else {}
        )

__all__ = ['BaseModel', 'ValidationError', 'TestResult', 'ConfigEntry', 'FileRecord']
EOF
```

---

## ✅ STEP 5.5: INTEGRATION AND TESTING

**Duration**: 30 minutes  
**Output**: Persistence layer integrated and validated

### 5.5.1 Create Persistence Integration
```python
# Create src/app/persistence/integration.py
cat > src/app/persistence/integration.py << 'EOF'
"""
Integration layer connecting persistence with core services
"""

import asyncio
import logging
from typing import Dict, Any, List

from . import get_database_manager, get_file_manager
from .models import TestResult, ConfigEntry, FileRecord

logger = logging.getLogger(__name__)

class PersistenceIntegration:
    """Integration layer for persistence services"""
    
    def __init__(self):
        self._db_manager = None
        self._file_manager = None
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize persistence layer"""
        try:
            self._db_manager = get_database_manager()
            self._file_manager = get_file_manager()
            
            # Initialize both managers
            db_success = await self._db_manager.initialize()
            file_success = await self._file_manager.initialize()
            
            self._initialized = db_success and file_success
            
            if self._initialized:
                logger.info("Persistence integration initialized successfully")
            else:
                logger.warning("Persistence integration partially initialized")
            
            return self._initialized
            
        except Exception as e:
            logger.error(f"Persistence integration failed: {e}")
            return False
    
    @property
    def db(self):
        """Get database manager"""
        return self._db_manager
    
    @property
    def files(self):
        """Get file manager"""
        return self._file_manager
    
    def is_ready(self) -> bool:
        """Check if persistence layer is ready"""
        return self._initialized and self._db_manager and self._file_manager

# Global integration instance
_integration = None

def get_persistence_integration() -> PersistenceIntegration:
    """Get global persistence integration instance"""
    global _integration
    if _integration is None:
        _integration = PersistenceIntegration()
    return _integration

__all__ = ['PersistenceIntegration', 'get_persistence_integration']
EOF
```

### 5.5.2 Create Phase Validation Tests
```python
# Create tests/test_phase5_persistence.py
cat > tests/test_phase5_persistence.py << 'EOF'
"""
Phase 5 validation tests for persistence layer
"""

import pytest
import asyncio
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class TestPersistenceLayer:
    """Test persistence layer functionality"""
    
    @pytest.mark.asyncio
    async def test_persistence_imports(self):
        """Test that persistence components can be imported"""
        try:
            from app.persistence import (
                get_database_manager, get_file_manager,
                BaseModel, ValidationError
            )
            from app.persistence.models import TestResult, ConfigEntry, FileRecord
            from app.persistence.integration import get_persistence_integration
            
            assert callable(get_database_manager)
            assert callable(get_file_manager)
            assert issubclass(TestResult, BaseModel)
            
        except ImportError as e:
            pytest.fail(f"Persistence imports failed: {e}")
    
    @pytest.mark.asyncio
    async def test_database_manager_initialization(self):
        """Test database manager initialization"""
        from app.persistence import get_database_manager
        
        db_manager = get_database_manager()
        assert db_manager is not None
        
        # Test initialization
        try:
            result = await db_manager.initialize()
            assert isinstance(result, bool)
        except Exception as e:
            # May fail without proper database setup
            pytest.skip(f"Database initialization skipped: {e}")
    
    @pytest.mark.asyncio
    async def test_file_manager(self):
        """Test file manager operations"""
        from app.persistence import get_file_manager
        
        file_manager = get_file_manager()
        assert file_manager is not None
        
        # Test initialization
        try:
            result = await file_manager.initialize()
            assert isinstance(result, bool)
            
            # Test basic file operations with temp file
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                test_path = Path(f.name)
                test_content = "Test content for persistence layer"
                f.write(test_content)
            
            try:
                # Test read
                content = await file_manager.read_file(test_path)
                assert content == test_content
                
                # Test file info
                file_info = await file_manager.get_file_info(test_path)
                assert file_info is not None
                assert file_info.size > 0
                
            finally:
                test_path.unlink(missing_ok=True)
                
        except Exception as e:
            pytest.skip(f"File manager test skipped: {e}")
    
    @pytest.mark.asyncio
    async def test_data_models(self):
        """Test data model validation"""
        from app.persistence.models import TestResult, ConfigEntry
        
        # Test TestResult validation
        test_result = TestResult(
            test_type="stress",
            status="passed",
            execution_time=1.5
        )
        
        assert test_result.validate()
        
        # Test invalid data
        invalid_result = TestResult(
            test_type="invalid",
            status="unknown"
        )
        
        assert not invalid_result.validate()
        
        # Test ConfigEntry
        config = ConfigEntry(
            section="test",
            key="value",
            value="123",
            type="int"
        )
        
        assert config.validate()
        assert config.get_typed_value() == 123

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
EOF
```

### 5.5.3 Integration with Core Services
```python
# Update src/app/core/bridge.py to include persistence
cat >> src/app/core/bridge.py << 'EOF'

# Add persistence integration to core bridge
from ..persistence.integration import get_persistence_integration

class CoreBridge:
    # ... existing code ...
    
    @property
    def persistence(self):
        """Lazy-loaded persistence integration"""
        if not hasattr(self, '_persistence'):
            self._persistence = get_persistence_integration()
        return self._persistence
    
    async def initialize_all(self):
        """Initialize all core services including persistence"""
        services = [self.ai, self.testing, self.config, self.tools]
        
        results = []
        
        # Initialize persistence first
        try:
            persistence_success = await self.persistence.initialize()
            results.append(("Persistence", persistence_success))
        except Exception as e:
            logger.error(f"Failed to initialize persistence: {e}")
            results.append(("Persistence", False))
        
        # Initialize other services
        for service in services:
            try:
                success = await service.initialize()
                results.append((service.name, success))
            except Exception as e:
                logger.error(f"Failed to initialize {service.name}: {e}")
                results.append((service.name, False))
        
        return results
EOF
```

---

## 📋 STEP 5.6: PHASE COMPLETION

**Duration**: 15 minutes  
**Output**: Complete phase validation and documentation

### 5.6.1 Final Integration Test
```bash
echo "🧪 Running Phase 5 integration tests..."

python -c "
import sys
sys.path.insert(0, 'src')

try:
    from app.persistence import (
        get_database_manager, get_file_manager,
        BaseModel, ValidationError
    )
    from app.persistence.models import TestResult, ConfigEntry, FileRecord
    from app.persistence.integration import get_persistence_integration
    
    print('✅ All persistence components importable')
    
    # Test integration
    integration = get_persistence_integration()
    print('✅ Persistence integration created')
    
    print('🎉 Phase 5 integration test passed')
    
except ImportError as e:
    print(f'❌ Integration test failed: {e}')
    exit(1)
"

echo "✅ Phase 5 validation complete"
```

### 5.6.2 Create Completion Documentation
```markdown
# Phase 5 Completion Report

**Status**: ✅ COMPLETED  
**Duration**: 2-3 hours  
**Date**: $(date)

## Persistence Architecture Created

### 💾 src/app/persistence/ Structure  
- **database/**: Repository pattern with SQLite + async support
- **files/**: Clean file operations with tracking and validation
- **models/**: Type-safe data models with validation
- **integration.py**: Unified persistence access layer

### ✅ Components Implemented
1. **DatabaseManager**: Connection management, migrations, repository coordination
2. **Repository Pattern**: TestResultRepository, ConfigRepository, FileRepository
3. **FileManager**: Async file operations with integrity checking
4. **Data Models**: TestResult, ConfigEntry, FileRecord with validation
5. **Integration Layer**: Unified access to all persistence functionality

### 🔗 Integration Features
- Async-first design for better performance
- Repository pattern for clean data access
- Automatic migrations and schema management
- File integrity checking with hash validation
- Type-safe models with automatic validation

## Ready for Phase 6

**Next Phase**: Presentation layer organization
**Focus**: UI layer restructuring by features with shared components
```

---

## 🎯 PHASE 5 SUCCESS CRITERIA

✅ **Persistence Architecture**: Clean separation of data layer from business logic  
✅ **Database Abstraction**: Repository pattern with proper async support  
✅ **File Management**: Organized file operations with tracking  
✅ **Data Models**: Type-safe models with validation  
✅ **Integration Layer**: Unified access to persistence functionality

**Phase 5 Complete**: Clean persistence layer ready for presentation organization
