import sqlite3
import json
import os
import difflib
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from ..constants import USER_DATA_DIR

@dataclass
class TestCaseResult:
    """Data class for individual test case results"""
    test_number: int
    passed: bool
    input_data: str
    expected_output: str
    actual_output: str
    execution_time: float
    memory_usage: int = 0
    error_message: str = ""
    timestamp: str = ""
    
@dataclass
class FilesSnapshot:
    """Data class for code files snapshot"""
    generator_code: str = ""
    correct_code: str = ""
    test_code: str = ""
    additional_files: Dict[str, str] = field(default_factory=dict)  # For any other files
    
@dataclass
class TestResult:
    """Data class for test results"""
    id: Optional[int] = None
    test_type: str = ""  # 'stress' or 'tle'
    file_path: str = ""
    test_count: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    total_time: float = 0.0
    timestamp: str = ""
    test_details: str = ""  # JSON string of detailed results
    project_name: str = ""
    files_snapshot: str = ""  # JSON string of all file contents
    mismatch_analysis: str = ""  # JSON string of detailed mismatch analysis

@dataclass
class Session:
    """Data class for editor sessions"""
    id: Optional[int] = None
    session_name: str = ""
    open_files: str = ""  # JSON string of file paths
    active_file: str = ""
    timestamp: str = ""
    project_name: str = ""

@dataclass
class ProjectData:
    """Data class for project information"""
    id: Optional[int] = None
    project_name: str = ""
    project_path: str = ""
    last_accessed: str = ""
    file_count: int = 0
    total_lines: int = 0
    languages: str = ""  # JSON string of languages used

class DatabaseManager:
    """Manages SQLite database operations for the Code Testing Suite"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            os.makedirs(USER_DATA_DIR, exist_ok=True)
            db_path = os.path.join(USER_DATA_DIR, "code_testing_suite.db")
        
        self.db_path = db_path
        self.connection = None
        self._initialize_database()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            return self.connection
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def _initialize_database(self):
        """Create database tables if they don't exist"""
        connection = self.connect()
        if not connection:
            return
        
        try:
            cursor = connection.cursor()
            
            # Test Results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    test_count INTEGER NOT NULL,
                    passed_tests INTEGER NOT NULL,
                    failed_tests INTEGER NOT NULL,
                    total_time REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    test_details TEXT,
                    project_name TEXT,
                    files_snapshot TEXT,
                    mismatch_analysis TEXT
                )
            ''')
            
            # Migrate existing table to add new columns
            try:
                cursor.execute("ALTER TABLE test_results ADD COLUMN files_snapshot TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            try:
                cursor.execute("ALTER TABLE test_results ADD COLUMN mismatch_analysis TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            # Sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT NOT NULL,
                    open_files TEXT,
                    active_file TEXT,
                    timestamp TEXT NOT NULL,
                    project_name TEXT
                )
            ''')
            
            # Projects table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_name TEXT NOT NULL UNIQUE,
                    project_path TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    file_count INTEGER DEFAULT 0,
                    total_lines INTEGER DEFAULT 0,
                    languages TEXT
                )
            ''')
            
            # Configuration table for database-stored settings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            connection.commit()
            
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
        finally:
            self.close()
    
    def save_test_result(self, result: TestResult) -> int:
        """Save a test result to the database"""
        connection = self.connect()
        if not connection:
            return -1
        
        try:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO test_results 
                (test_type, file_path, test_count, passed_tests, failed_tests, 
                 total_time, timestamp, test_details, project_name, files_snapshot, mismatch_analysis)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.test_type, result.file_path, result.test_count,
                result.passed_tests, result.failed_tests, result.total_time,
                result.timestamp or datetime.now().isoformat(),
                result.test_details, result.project_name, 
                result.files_snapshot or "", result.mismatch_analysis or ""
            ))
            
            connection.commit()
            return cursor.lastrowid
            
        except sqlite3.Error as e:
            print(f"Error saving test result: {e}")
            return -1
        finally:
            self.close()
    
    def get_test_results(self, test_type: str = None, project_name: str = None, 
                        limit: int = 100) -> List[TestResult]:
        """Retrieve test results from the database"""
        connection = self.connect()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor()
            query = "SELECT * FROM test_results"
            params = []
            
            conditions = []
            if test_type:
                conditions.append("test_type = ?")
                params.append(test_type)
            if project_name:
                conditions.append("project_name = ?")
                params.append(project_name)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                result = TestResult(
                    id=row['id'],
                    test_type=row['test_type'],
                    file_path=row['file_path'],
                    test_count=row['test_count'],
                    passed_tests=row['passed_tests'],
                    failed_tests=row['failed_tests'],
                    total_time=row['total_time'],
                    timestamp=row['timestamp'],
                    test_details=row['test_details'],
                    project_name=row['project_name'],
                    files_snapshot=row['files_snapshot'] if 'files_snapshot' in row.keys() else '',
                    mismatch_analysis=row['mismatch_analysis'] if 'mismatch_analysis' in row.keys() else ''
                )
                results.append(result)
            
            return results
            
        except sqlite3.Error as e:
            print(f"Error retrieving test results: {e}")
            return []
        finally:
            self.close()
    
    def save_session(self, session: Session) -> int:
        """Save an editor session to the database"""
        connection = self.connect()
        if not connection:
            return -1
        
        try:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO sessions 
                (session_name, open_files, active_file, timestamp, project_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                session.session_name, session.open_files, session.active_file,
                session.timestamp or datetime.now().isoformat(), session.project_name
            ))
            
            connection.commit()
            return cursor.lastrowid
            
        except sqlite3.Error as e:
            print(f"Error saving session: {e}")
            return -1
        finally:
            self.close()
    
    def get_sessions(self, project_name: str = None, limit: int = 10) -> List[Session]:
        """Retrieve editor sessions from the database"""
        connection = self.connect()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor()
            if project_name:
                cursor.execute('''
                    SELECT * FROM sessions 
                    WHERE project_name = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (project_name, limit))
            else:
                cursor.execute('''
                    SELECT * FROM sessions 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            
            sessions = []
            for row in rows:
                session = Session(
                    id=row['id'],
                    session_name=row['session_name'],
                    open_files=row['open_files'],
                    active_file=row['active_file'],
                    timestamp=row['timestamp'],
                    project_name=row['project_name']
                )
                sessions.append(session)
            
            return sessions
            
        except sqlite3.Error as e:
            print(f"Error retrieving sessions: {e}")
            return []
        finally:
            self.close()
    
    def save_project_data(self, project: ProjectData) -> int:
        """Save or update project data"""
        connection = self.connect()
        if not connection:
            return -1
        
        try:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO projects 
                (project_name, project_path, last_accessed, file_count, total_lines, languages)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                project.project_name, project.project_path,
                project.last_accessed or datetime.now().isoformat(),
                project.file_count, project.total_lines, project.languages
            ))
            
            connection.commit()
            return cursor.lastrowid
            
        except sqlite3.Error as e:
            print(f"Error saving project data: {e}")
            return -1
        finally:
            self.close()
    
    def get_projects(self, limit: int = 50) -> List[ProjectData]:
        """Retrieve project data from the database"""
        connection = self.connect()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor()
            cursor.execute('''
                SELECT * FROM projects 
                ORDER BY last_accessed DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            
            projects = []
            for row in rows:
                project = ProjectData(
                    id=row['id'],
                    project_name=row['project_name'],
                    project_path=row['project_path'],
                    last_accessed=row['last_accessed'],
                    file_count=row['file_count'],
                    total_lines=row['total_lines'],
                    languages=row['languages']
                )
                projects.append(project)
            
            return projects
            
        except sqlite3.Error as e:
            print(f"Error retrieving projects: {e}")
            return []
        finally:
            self.close()
    
    def get_test_statistics(self, project_name: str = None) -> Dict:
        """Get test statistics and analytics"""
        connection = self.connect()
        if not connection:
            return {}
        
        try:
            cursor = connection.cursor()
            
            stats = {}
            
            # Basic counts
            base_query = "SELECT COUNT(*) as count FROM test_results"
            if project_name:
                base_query += " WHERE project_name = ?"
                params = (project_name,)
            else:
                params = ()
            
            cursor.execute(base_query, params)
            stats['total_tests'] = cursor.fetchone()['count']
            
            # Test type breakdown
            type_query = "SELECT test_type, COUNT(*) as count FROM test_results"
            if project_name:
                type_query += " WHERE project_name = ?"
            type_query += " GROUP BY test_type"
            
            cursor.execute(type_query, params)
            stats['by_type'] = {row['test_type']: row['count'] for row in cursor.fetchall()}
            
            # Success rate
            success_query = '''
                SELECT 
                    SUM(passed_tests) as total_passed,
                    SUM(test_count) as total_attempted
                FROM test_results
            '''
            if project_name:
                success_query += " WHERE project_name = ?"
            
            cursor.execute(success_query, params)
            result = cursor.fetchone()
            if result and result['total_attempted'] > 0:
                stats['success_rate'] = (result['total_passed'] / result['total_attempted']) * 100
            else:
                stats['success_rate'] = 0
            
            return stats
            
        except sqlite3.Error as e:
            print(f"Error getting test statistics: {e}")
            return {}
        finally:
            self.close()
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old data to maintain database size"""
        connection = self.connect()
        if not connection:
            return
        
        try:
            cursor = connection.cursor()
            # Use timedelta for proper date arithmetic
            from datetime import timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Clean old test results
            cursor.execute('''
                DELETE FROM test_results 
                WHERE timestamp < ?
            ''', (cutoff_date,))
            
            # Clean old sessions
            cursor.execute('''
                DELETE FROM sessions 
                WHERE timestamp < ?
            ''', (cutoff_date,))
            
            connection.commit()
            print(f"Cleaned up data older than {days} days")
            
        except sqlite3.Error as e:
            print(f"Error cleaning up old data: {e}")
        finally:
            self.close()
    
    def delete_all_data(self, confirm: bool = False):
        """Delete all data from the database
        
        Args:
            confirm: Must be True to actually delete data (safety check)
        """
        if not confirm:
            print("Warning: delete_all_data requires confirm=True parameter to execute")
            return False
        
        connection = self.connect()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            
            # Get count of records before deletion
            cursor.execute("SELECT COUNT(*) FROM test_results")
            test_results_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sessions")
            sessions_count = cursor.fetchone()[0]
            
            # Delete all test results
            cursor.execute("DELETE FROM test_results")
            
            # Delete all sessions
            cursor.execute("DELETE FROM sessions")
            
            # Reset auto-increment counters
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='test_results'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='sessions'")
            
            connection.commit()
            print(f"Successfully deleted all data:")
            print(f"  - {test_results_count} test results")
            print(f"  - {sessions_count} sessions")
            print(f"  - Reset ID counters")
            
            return True
            
        except sqlite3.Error as e:
            print(f"Error deleting all data: {e}")
            connection.rollback()
            return False
        finally:
            self.close()
    
    def get_database_stats(self):
        """Get statistics about the database contents"""
        connection = self.connect()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            
            # Count records in each table
            cursor.execute("SELECT COUNT(*) FROM test_results")
            test_results_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sessions")
            sessions_count = cursor.fetchone()[0]
            
            # Get date range of data
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM test_results")
            result = cursor.fetchone()
            oldest_test = result[0] if result[0] else "No data"
            newest_test = result[1] if result[1] else "No data"
            
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM sessions")
            result = cursor.fetchone()
            oldest_session = result[0] if result[0] else "No data"
            newest_session = result[1] if result[1] else "No data"
            
            # Get database file size
            import os
            db_size = 0
            if os.path.exists(self.db_path):
                db_size = os.path.getsize(self.db_path)
                db_size_mb = db_size / (1024 * 1024)  # Convert to MB
            
            stats = {
                'test_results_count': test_results_count,
                'sessions_count': sessions_count,
                'oldest_test': oldest_test,
                'newest_test': newest_test,
                'oldest_session': oldest_session,
                'newest_session': newest_session,
                'database_size_bytes': db_size,
                'database_size_mb': round(db_size_mb, 2) if db_size > 0 else 0
            }
            
            return stats
            
        except sqlite3.Error as e:
            print(f"Error getting database stats: {e}")
            return None
        finally:
            self.close()
    
    @staticmethod
    def analyze_output_mismatch(expected: str, actual: str) -> Dict:
        """Analyze differences between expected and actual output"""
        expected_lines = expected.strip().split('\n')
        actual_lines = actual.strip().split('\n')
        
        # Generate unified diff
        diff = list(difflib.unified_diff(
            expected_lines, actual_lines,
            fromfile='Expected Output',
            tofile='Actual Output',
            lineterm='',
            n=3
        ))
        
        # Character-by-character diff for precise analysis
        char_diff = []
        for i, (exp_char, act_char) in enumerate(zip(expected, actual)):
            if exp_char != act_char:
                char_diff.append({
                    'position': i,
                    'expected': exp_char,
                    'actual': act_char
                })
        
        # Line-by-line analysis
        line_analysis = []
        max_lines = max(len(expected_lines), len(actual_lines))
        
        for i in range(max_lines):
            exp_line = expected_lines[i] if i < len(expected_lines) else ""
            act_line = actual_lines[i] if i < len(actual_lines) else ""
            
            if exp_line != act_line:
                line_analysis.append({
                    'line_number': i + 1,
                    'expected': exp_line,
                    'actual': act_line,
                    'type': 'modified' if exp_line and act_line else ('missing' if exp_line else 'extra')
                })
        
        return {
            'unified_diff': diff,
            'character_differences': char_diff,
            'line_differences': line_analysis,
            'summary': {
                'total_char_differences': len(char_diff),
                'total_line_differences': len(line_analysis),
                'expected_length': len(expected),
                'actual_length': len(actual),
                'expected_lines': len(expected_lines),
                'actual_lines': len(actual_lines)
            }
        }
    
    @staticmethod
    def create_files_snapshot(workspace_dir: str) -> FilesSnapshot:
        """Create a snapshot of all relevant files in the workspace"""
        snapshot = FilesSnapshot()
        
        # Common file mappings
        file_mappings = {
            'generator.h': 'generator_code',
            'generator.cpp': 'generator_code', 
            'a.cpp': 'correct_code',
            'correct.cpp': 'correct_code',
            'b.cpp': 'test_code',
            'test.cpp': 'test_code',
            'tmp.cpp': 'test_code'
        }
        
        try:
            for filename in os.listdir(workspace_dir):
                filepath = os.path.join(workspace_dir, filename)
                if os.path.isfile(filepath) and filename.endswith(('.cpp', '.h', '.py', '.java')):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Map to known file types
                        if filename in file_mappings:
                            setattr(snapshot, file_mappings[filename], content)
                        else:
                            # Add to additional files
                            snapshot.additional_files[filename] = content
                    except Exception as e:
                        print(f"Error reading file {filename}: {e}")
        except Exception as e:
            print(f"Error creating files snapshot: {e}")
        
        return snapshot
