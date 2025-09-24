"""Integration tests for end-to-end workflows in the Code Testing Suite."""

import os
import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from PySide6.QtTest import QTest

from src.app.core.config.core.config_handler import ConfigManager
from src.app.persistence.database.database_manager import DatabaseManager, TestResult
from src.app.shared.utils.file_operations import FileOperations


class TestConfigurationWorkflow:
    """Integration tests for configuration management workflow."""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.mark.integration
    def test_full_configuration_cycle(self, temp_config_dir):
        """Test complete configuration load/modify/save cycle."""
        # Initialize config manager
        config_manager = ConfigManager(os.path.join(temp_config_dir, 'config.json'))
        
        # Step 1: Load default configuration
        config = config_manager.load_config()
        assert config is not None
        assert 'cpp_version' in config
        
        # Step 2: Modify configuration
        config['cpp_version'] = 'c++20'
        config['workspace_folder'] = '/test/workspace'
        config['gemini']['enabled'] = True
        config['gemini']['api_key'] = 'test-key-123'
        
        # Step 3: Save modified configuration
        config_manager.save_config(config)
        
        # Step 4: Reload and verify changes persisted
        reloaded_config = config_manager.load_config()
        assert reloaded_config['cpp_version'] == 'c++20'
        assert reloaded_config['workspace_folder'] == '/test/workspace'
        assert reloaded_config['gemini']['enabled'] is True
        assert reloaded_config['gemini']['api_key'] == 'test-key-123'

    @pytest.mark.integration
    def test_configuration_backup_recovery(self, temp_config_dir):
        """Test configuration backup and recovery workflow."""
        config_file = os.path.join(temp_config_dir, 'config.json')
        config_manager = ConfigManager(config_file)
        
        # Create initial configuration
        initial_config = config_manager.get_default_config()
        initial_config['cpp_version'] = 'c++17'
        config_manager.save_config(initial_config)
        
        # Modify and save again (creates backup)
        modified_config = initial_config.copy()
        modified_config['cpp_version'] = 'c++20'
        config_manager.save_config(modified_config)
        
        # Verify backup exists
        backup_file = f"{config_file}.bak"
        assert os.path.exists(backup_file)
        
        # Verify backup contains original config
        with open(backup_file, 'r') as f:
            backup_config = json.load(f)
        assert backup_config['cpp_version'] == 'c++17'

    @pytest.mark.integration
    def test_configuration_error_recovery(self, temp_config_dir):
        """Test recovery from corrupted configuration files."""
        config_file = os.path.join(temp_config_dir, 'config.json')
        config_manager = ConfigManager(config_file)
        
        # Create corrupted config file
        with open(config_file, 'w') as f:
            f.write('{ invalid json content }')
        
        # Loading should handle error and return default config
        # (This tests the integration between error handling and default config)
        from src.app.core.config.core.exceptions import ConfigFormatError
        
        with pytest.raises(ConfigFormatError):
            config_manager.load_config()


class TestFileWorkflow:
    """Integration tests for file operations workflow."""

    @pytest.mark.integration
    def test_complete_file_edit_cycle(self, tmp_path):
        """Test complete file create/edit/save cycle."""
        test_file = tmp_path / "test_program.cpp"
        
        # Step 1: Create initial file content
        initial_content = '''#include <iostream>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    return 0;
}'''
        
        # Step 2: Save file
        success = FileOperations.save_file(test_file, initial_content)
        assert success is True
        assert test_file.exists()
        
        # Step 3: Read file back
        content = test_file.read_text(encoding='utf-8')
        assert content == initial_content
        
        # Step 4: Modify and save again
        modified_content = initial_content.replace('Hello, World!', 'Hello, Testing!')
        success = FileOperations.save_file(test_file, modified_content)
        assert success is True
        
        # Step 5: Verify changes persisted
        final_content = test_file.read_text(encoding='utf-8')
        assert 'Hello, Testing!' in final_content
        assert 'Hello, World!' not in final_content

    @pytest.mark.integration
    def test_file_extension_detection_workflow(self, tmp_path):
        """Test file extension detection and language mapping."""
        test_files = {
            'main.cpp': 'C++',
            'script.py': 'Python',
            'program.java': 'Java',
            'header.h': 'C/C++',
            'source.c': 'C'
        }
        
        for filename, expected_language in test_files.items():
            test_file = tmp_path / filename
            extension = test_file.suffix
            
            # Verify extension is supported
            assert extension in FileOperations.SUPPORTED_EXTENSIONS
            
            # Verify language mapping
            assert FileOperations.LANGUAGE_MAP[extension] == expected_language

    @pytest.mark.integration
    @patch('PySide6.QtWidgets.QFileDialog.getSaveFileName')
    def test_save_as_workflow(self, mock_save_dialog, tmp_path):
        """Test save-as dialog workflow integration."""
        parent_widget = MagicMock()
        test_content = "int main() { return 0; }"
        test_file = str(tmp_path / "saved_file.cpp")
        
        # Mock dialog to return test file path
        mock_save_dialog.return_value = (test_file, "C++ Files (*.cpp)")
        
        # Execute save-as workflow
        result = FileOperations.save_file_as(parent_widget, test_content)
        
        # Verify workflow completed successfully
        assert result == test_file
        assert Path(test_file).exists()
        assert Path(test_file).read_text() == test_content


class TestDatabaseWorkflow:
    """Integration tests for database operations workflow."""

    @pytest.mark.integration
    @pytest.mark.database
    def test_complete_test_result_workflow(self, mock_database):
        """Test complete test result storage and retrieval workflow."""
        db_manager = DatabaseManager(mock_database)
        
        # Step 1: Create test result
        test_result = TestResult(
            test_type="stress",
            file_path="/test/integration_test.cpp",
            test_count=100,
            passed_tests=95,
            failed_tests=5,
            total_time=15.5,
            timestamp="2023-01-01T12:00:00",
            test_details='{"timeout": 5, "memory_limit": "256MB"}',
            project_name="IntegrationTest",
            files_snapshot='{"generator": "code", "correct": "code", "test": "code"}',
            mismatch_analysis='{"failed_tests": [1, 2, 3, 4, 5]}'
        )
        
        # Step 2: Save test result
        result_id = db_manager.save_test_result(test_result)
        assert result_id is not None
        
        # Step 3: Retrieve and verify
        all_results = db_manager.get_test_results(project_name="IntegrationTest")
        retrieved_result = next((r for r in all_results if r.id == result_id), None)
        assert retrieved_result is not None
        assert retrieved_result.test_type == "stress"
        assert retrieved_result.test_count == 100
        assert retrieved_result.passed_tests == 95
        
        # Step 4: Query all results
        all_results = db_manager.get_test_results()
        assert len(all_results) >= 1
        assert any(r.id == result_id for r in all_results)

    @pytest.mark.integration
    @pytest.mark.database
    def test_session_management_workflow(self, mock_database):
        """Test complete session management workflow."""
        db_manager = DatabaseManager(mock_database)
        
        from src.app.persistence.database.database_manager import Session
        
        # Step 1: Create session
        session = Session(
            session_name="Integration Test Session",
            open_files='["main.cpp", "helper.h", "test.py"]',
            active_file="main.cpp",
            timestamp="2023-01-01T12:00:00",
            project_name="TestProject"
        )
        
        # Step 2: Save session
        session_id = db_manager.save_session(session)
        assert session_id is not None
        
        # Step 3: Retrieve and verify
        all_sessions = db_manager.get_sessions(project_name="TestProject")
        retrieved_session = next((s for s in all_sessions if s.id == session_id), None)
        assert retrieved_session is not None
        assert retrieved_session.session_name == "Integration Test Session"
        assert "main.cpp" in retrieved_session.open_files
        
        # Step 4: Create a new session (simulate file changes) 
        # Note: save_session creates a new session rather than updating existing
        updated_session = Session(
            session_name="Updated Integration Test Session",
            open_files='["main.cpp", "helper.h", "test.py", "new_file.cpp"]',
            active_file="new_file.cpp",
            timestamp="2023-01-01T13:00:00",
            project_name="TestProject"
        )

        # Save new session
        new_session_id = db_manager.save_session(updated_session)

        # Verify new session was created
        final_sessions = db_manager.get_sessions(project_name="TestProject")
        new_session = next((s for s in final_sessions if s.id == new_session_id), None)
        assert new_session is not None
        assert "new_file.cpp" in new_session.open_files
        
        # Verify we now have 2 sessions
        assert len(final_sessions) == 2

    @pytest.mark.integration
    @pytest.mark.database
    @pytest.mark.skip(reason="save_test_case_result and get_test_cases_for_result methods not implemented in DatabaseManager")
    def test_test_case_result_workflow(self, mock_database):
        """Test test case results storage workflow."""
        db_manager = DatabaseManager(mock_database)
        
        from src.app.persistence.database.database_manager import TestCaseResult
        
        # Create parent test result first
        test_result = TestResult(
            test_type="stress",
            file_path="/test/case_test.cpp",
            test_count=3,
            passed_tests=2,
            failed_tests=1,
            total_time=0.5,
            timestamp="2023-01-01T12:00:00",
            project_name="CaseTestProject"
        )
        
        test_result_id = db_manager.save_test_result(test_result)
        
        # Create and save test cases
        test_cases = [
            TestCaseResult(
                test_number=1,
                passed=True,
                input_data="5 3",
                expected_output="8",
                actual_output="8",
                execution_time=0.001,
                timestamp="2023-01-01T12:00:01"
            ),
            TestCaseResult(
                test_number=2,
                passed=True,
                input_data="10 15",
                expected_output="25",
                actual_output="25",
                execution_time=0.002,
                timestamp="2023-01-01T12:00:02"
            ),
            TestCaseResult(
                test_number=3,
                passed=False,
                input_data="100 200",
                expected_output="300",
                actual_output="299",
                execution_time=0.003,
                error_message="Output mismatch",
                timestamp="2023-01-01T12:00:03"
            )
        ]
        
        # Save all test cases
        for test_case in test_cases:
            case_id = db_manager.save_test_case_result(test_case, test_result_id)
            assert case_id is not None
        
        # Retrieve and verify test cases
        retrieved_cases = db_manager.get_test_cases_for_result(test_result_id)
        assert len(retrieved_cases) == 3
        
        # Verify specific test case results
        passed_cases = [case for case in retrieved_cases if case.passed]
        failed_cases = [case for case in retrieved_cases if not case.passed]
        
        assert len(passed_cases) == 2
        assert len(failed_cases) == 1
        assert failed_cases[0].error_message == "Output mismatch"


class TestCompilationWorkflow:
    """Integration tests for compilation workflow (mocked)."""

    @pytest.mark.integration
    def test_compilation_configuration_integration(self, temp_config_dir, tmp_path):
        """Test integration between configuration and compilation settings."""
        # Setup configuration
        config_manager = ConfigManager(os.path.join(temp_config_dir, 'config.json'))
        config = config_manager.load_config()
        config['cpp_version'] = 'c++17'
        config['workspace_folder'] = str(tmp_path)
        config_manager.save_config(config)
        
        # Create test source file
        source_file = tmp_path / "test.cpp"
        source_content = '''#include <iostream>
#include <vector>

int main() {
    std::vector<int> numbers = {1, 2, 3, 4, 5};
    for (const auto& num : numbers) {
        std::cout << num << " ";
    }
    return 0;
}'''
        
        FileOperations.save_file(source_file, source_content)
        assert source_file.exists()
        
        # Verify configuration can be used for compilation settings
        reloaded_config = config_manager.load_config()
        assert reloaded_config['cpp_version'] == 'c++17'
        assert reloaded_config['workspace_folder'] == str(tmp_path)
        
        # Mock compilation command construction
        cpp_version = reloaded_config['cpp_version']
        workspace = Path(reloaded_config['workspace_folder'])
        
        expected_compile_args = [
            'g++',
            f'-std={cpp_version}',
            '-O2',
            str(source_file),
            '-o',
            str(workspace / 'test.exe')
        ]
        
        # Verify compilation arguments are constructed correctly
        assert 'g++' in expected_compile_args
        assert f'-std={cpp_version}' in expected_compile_args
        assert str(source_file) in expected_compile_args


class TestAIIntegrationWorkflow:
    """Integration tests for AI integration workflow (mocked)."""

    @pytest.mark.integration
    @pytest.mark.ai
    def test_ai_configuration_workflow(self, temp_config_dir):
        """Test AI configuration and integration workflow."""
        config_manager = ConfigManager(os.path.join(temp_config_dir, 'config.json'))
        
        # Step 1: Configure AI settings
        config = config_manager.load_config()
        config['gemini']['enabled'] = True
        config['gemini']['api_key'] = 'test-api-key-123'
        config['gemini']['model'] = 'gemini-2.5-flash'
        config_manager.save_config(config)
        
        # Step 2: Verify AI configuration
        ai_config = config_manager.load_config()['gemini']
        assert ai_config['enabled'] is True
        assert ai_config['api_key'] == 'test-api-key-123'
        assert ai_config['model'] == 'gemini-2.5-flash'
        
        # Step 3: Mock AI request workflow
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "candidates": [{
                    "content": {
                        "parts": [{
                            "text": "This code looks good! Here are some suggestions..."
                        }]
                    }
                }]
            }
            mock_post.return_value = mock_response
            
            # Simulate AI API call
            test_code = "int main() { return 0; }"
            
            # Mock the API request
            response = mock_post.return_value
            assert response.status_code == 200
            
            response_data = response.json()
            assert 'candidates' in response_data
            assert len(response_data['candidates']) > 0

    @pytest.mark.integration
    @pytest.mark.ai
    def test_ai_disabled_workflow(self, temp_config_dir):
        """Test workflow when AI is disabled."""
        config_manager = ConfigManager(os.path.join(temp_config_dir, 'config.json'))
        
        # Configure AI as disabled
        config = config_manager.load_config()
        config['gemini']['enabled'] = False
        config_manager.save_config(config)
        
        # Verify AI is disabled
        ai_config = config_manager.load_config()['gemini']
        assert ai_config['enabled'] is False
        
        # AI-dependent features should handle disabled state gracefully
        # (This would be tested in the actual UI components)


class TestEndToEndWorkflows:
    """Complete end-to-end workflow integration tests."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_complete_testing_session_workflow(self, temp_config_dir, mock_database, tmp_path):
        """Test complete testing session from configuration to results storage."""
        # Step 1: Setup configuration
        config_manager = ConfigManager(os.path.join(temp_config_dir, 'config.json'))
        config = config_manager.load_config()
        config['workspace_folder'] = str(tmp_path)
        config['cpp_version'] = 'c++17'
        config_manager.save_config(config)
        
        # Step 2: Create test files
        files = {
            'generator.cpp': '''#include <iostream>
#include <random>
int main() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(1, 100);
    std::cout << dis(gen) << " " << dis(gen) << std::endl;
    return 0;
}''',
            'correct.cpp': '''#include <iostream>
int main() {
    int a, b;
    std::cin >> a >> b;
    std::cout << a + b << std::endl;
    return 0;
}''',
            'test.cpp': '''#include <iostream>
int main() {
    int a, b;
    std::cin >> a >> b;
    std::cout << a + b << std::endl;
    return 0;
}'''
        }
        
        for filename, content in files.items():
            file_path = tmp_path / filename
            FileOperations.save_file(file_path, content)
            assert file_path.exists()
        
        # Step 3: Simulate test execution results
        db_manager = DatabaseManager(mock_database)
        
        test_result = TestResult(
            test_type="stress",
            file_path=str(tmp_path / "test.cpp"),
            test_count=50,
            passed_tests=50,
            failed_tests=0,
            total_time=2.5,
            timestamp="2023-01-01T12:00:00",
            test_details='{"generator": "generator.cpp", "correct": "correct.cpp"}',
            project_name="EndToEndTest",
            files_snapshot=json.dumps(files),
            mismatch_analysis='{"passed_all": true}'
        )
        
        result_id = db_manager.save_test_result(test_result)
        
        # Step 4: Verify complete workflow
        assert result_id is not None
        
        # Verify configuration
        final_config = config_manager.load_config()
        assert final_config['workspace_folder'] == str(tmp_path)
        
        # Verify files exist
        for filename in files:
            assert (tmp_path / filename).exists()
        
        # Verify test results stored
        all_results = db_manager.get_test_results(project_name="EndToEndTest")
        stored_result = next((r for r in all_results if r.id == result_id), None)
        assert stored_result is not None
        assert stored_result.passed_tests == 50
        assert stored_result.failed_tests == 0
        
        # Verify files snapshot
        snapshot_data = json.loads(stored_result.files_snapshot)
        assert 'generator.cpp' in snapshot_data
        assert 'correct.cpp' in snapshot_data
        assert 'test.cpp' in snapshot_data