"""Test suite for Phase 2 storage optimization (Issues #38 and #39)"""
import pytest
import json
import tempfile
import os
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from src.app.persistence.database import FilesSnapshot


class TestFilesSnapshotOptimization:
    """Test files snapshot optimization (Issue #38)"""
    
    def test_files_snapshot_serialization(self):
        """Test FilesSnapshot to_json() and from_json() methods (Issue #4)"""
        snapshot = FilesSnapshot(
            generator_code="print('generator')",
            correct_code="print('correct')",
            test_code="print('test')",
            validator_code="print('validator')",
            additional_files={"utils.py": "def helper(): pass"}
        )
        
        # Serialize
        json_str = snapshot.to_json()
        assert json_str
        assert "generator" in json_str
        assert "validator" in json_str
        
        # Deserialize
        restored = FilesSnapshot.from_json(json_str)
        assert restored.generator_code == snapshot.generator_code
        assert restored.correct_code == snapshot.correct_code
        assert restored.test_code == snapshot.test_code
        assert restored.validator_code == snapshot.validator_code
        assert restored.additional_files == snapshot.additional_files
    
    def test_files_snapshot_from_empty_json(self):
        """Test FilesSnapshot.from_json() with empty string"""
        snapshot = FilesSnapshot.from_json("")
        assert snapshot.generator_code == ""
        assert snapshot.correct_code == ""
        assert snapshot.test_code == ""
        assert snapshot.validator_code == ""
        assert snapshot.additional_files == {}
    
    def test_files_snapshot_from_malformed_json(self):
        """Test FilesSnapshot.from_json() with malformed JSON"""
        snapshot = FilesSnapshot.from_json("not valid json {")
        # Should return empty snapshot on error
        assert snapshot.generator_code == ""
    
    def test_validator_code_field_exists(self):
        """Test that validator_code field was added to FilesSnapshot"""
        snapshot = FilesSnapshot(validator_code="validator content")
        assert hasattr(snapshot, 'validator_code')
        assert snapshot.validator_code == "validator content"


class TestOnDemandSaving:
    """Test on-demand saving (Issue #39)"""
    
    def test_base_runner_has_public_save_method(self):
        """Test that BaseRunner has public save_test_results_to_database() method"""
        from src.app.core.tools.base.base_runner import BaseRunner
        
        # Check method exists and is public
        assert hasattr(BaseRunner, 'save_test_results_to_database')
        method = getattr(BaseRunner, 'save_test_results_to_database')
        assert callable(method)
        # Public methods don't start with underscore
        assert not method.__name__.startswith('_')
    
    def test_save_method_returns_int(self):
        """Test that save_test_results_to_database() returns int"""
        from src.app.core.tools.base.base_runner import BaseRunner
        from datetime import datetime
        
        # Create mock runner
        with tempfile.TemporaryDirectory() as tmpdir:
            files = {'test': os.path.join(tmpdir, 'test.py')}
            
            # Create actual test file
            with open(files['test'], 'w') as f:
                f.write("print('test')")
            
            runner = BaseRunner(tmpdir, files, 'comparison')
            
            # Mock worker with results
            runner.worker = Mock()
            runner.worker.get_results = Mock(return_value=[
                {'passed': True, 'test_number': 1}
            ])
            runner.test_start_time = datetime.now()
            
            # Mock _create_test_result
            from src.app.persistence.database import TestResult
            runner._create_test_result = Mock(return_value=TestResult(
                test_type='comparison',
                file_path='test.py',
                test_count=1,
                passed_tests=1,
                failed_tests=0,
                total_time=1.0
            ))
            
            # Call should return int
            result = runner.save_test_results_to_database()
            assert isinstance(result, int)
            # -1 on error, positive on success
            assert result >= -1
    
    def test_save_without_worker_returns_minus_one(self):
        """Test that save without worker returns -1"""
        from src.app.core.tools.base.base_runner import BaseRunner
        
        with tempfile.TemporaryDirectory() as tmpdir:
            files = {'test': os.path.join(tmpdir, 'test.py')}
            with open(files['test'], 'w') as f:
                f.write("print('test')")
            
            runner = BaseRunner(tmpdir, files, 'comparison')
            runner.worker = None  # No worker
            
            result = runner.save_test_results_to_database()
            assert result == -1


class TestCreateFilesSnapshot:
    """Test _create_files_snapshot() optimization (Issue #38)"""
    
    def test_snapshot_only_includes_self_files(self):
        """Test that snapshot only includes files from self.files, not entire workspace"""
        from src.app.core.tools.base.base_runner import BaseRunner
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple files in workspace
            workspace_files = [
                'generator.py',
                'correct.cpp',
                'test.java',
                'validator.py',
                'other_file.py',  # Should NOT be in snapshot
                'random.cpp',     # Should NOT be in snapshot
            ]
            
            for filename in workspace_files:
                filepath = os.path.join(tmpdir, filename)
                with open(filepath, 'w') as f:
                    f.write(f"// Content of {filename}\n")
            
            # Only specify 3 files in self.files (not all 6)
            runner_files = {
                'generator': os.path.join(tmpdir, 'generator.py'),
                'correct': os.path.join(tmpdir, 'correct.cpp'),
                'test': os.path.join(tmpdir, 'test.java'),
            }
            
            runner = BaseRunner(tmpdir, runner_files, 'comparison')
            
            # Get snapshot
            snapshot_dict = runner._create_files_snapshot()
            
            # Should contain the 3 specified files
            assert 'generator.py' in snapshot_dict['generator_code']
            assert 'correct.cpp' in snapshot_dict['correct_code']
            assert 'test.java' in snapshot_dict['test_code']
            
            # Should NOT contain the other files
            snapshot_str = str(snapshot_dict)
            assert 'other_file.py' not in snapshot_str
            assert 'random.cpp' not in snapshot_str
            
    def test_snapshot_with_validator_file(self):
        """Test that validator file is captured when present"""
        from src.app.core.tools.base.base_runner import BaseRunner
        
        with tempfile.TemporaryDirectory() as tmpdir:
            validator_path = os.path.join(tmpdir, 'validator.py')
            with open(validator_path, 'w') as f:
                f.write("# Validator code\nprint('validating')")
            
            runner_files = {
                'validator': validator_path
            }
            
            runner = BaseRunner(tmpdir, runner_files, 'validator')
            snapshot_dict = runner._create_files_snapshot()
            
            # Should contain validator code
            assert snapshot_dict['validator_code']
            assert 'validating' in snapshot_dict['validator_code']
    
    def test_snapshot_handles_missing_files(self):
        """Test that snapshot handles missing files gracefully"""
        from src.app.core.tools.base.base_runner import BaseRunner
        
        with tempfile.TemporaryDirectory() as tmpdir:
            runner_files = {
                'generator': os.path.join(tmpdir, 'nonexistent.py'),
                'test': os.path.join(tmpdir, 'also_missing.cpp'),
            }
            
            runner = BaseRunner(tmpdir, runner_files, 'comparison')
            
            # Should not raise exception
            snapshot_dict = runner._create_files_snapshot()
            
            # Should return empty strings for missing files
            assert snapshot_dict['generator_code'] == ""
            assert snapshot_dict['test_code'] == ""


class TestStatusViewSaveButton:
    """Test Save button in status views"""
    
    def test_sidebar_save_button_replacement(self):
        """Test that sidebar can replace Results button with Save button"""
        from src.app.presentation.widgets.sidebar import Sidebar
        from PySide6.QtWidgets import QApplication
        import sys
        
        # Ensure QApplication exists
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        try:
            sidebar = Sidebar("Test")
            sidebar.add_results_button()
            
            # Replace with save button
            sidebar.replace_results_with_save_button()
            
            # Should have save button
            assert hasattr(sidebar, 'save_button')
            assert sidebar.save_button.text() == "Tests Running..."
            assert not sidebar.save_button.isEnabled()
            
            # Should not have results button anymore
            assert not hasattr(sidebar, 'results_button') or sidebar.results_button is None or not sidebar.results_button.isVisible()
            
        finally:
            if app:
                app.quit()
    
    def test_sidebar_save_button_enable_and_restore(self):
        """Test that save button can be enabled and restored"""
        from src.app.presentation.widgets.sidebar import Sidebar
        from PySide6.QtWidgets import QApplication
        import sys
        
        app = None
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        try:
            sidebar = Sidebar("Test")
            sidebar.add_results_button()
            sidebar.replace_results_with_save_button()
            
            # Initially disabled
            assert not sidebar.save_button.isEnabled()
            assert sidebar.save_button.text() == "Tests Running..."
            
            # Enable save button
            sidebar.enable_save_button()
            assert sidebar.save_button.isEnabled()
            assert sidebar.save_button.text() == "💾 Save Results"
            
            # Mark as saved
            sidebar.mark_results_saved()
            assert not sidebar.save_button.isEnabled()
            assert sidebar.save_button.text() == "✓ Saved"
            
            # Restore results button (should remove save button and show results)
            sidebar.restore_results_button()
            assert hasattr(sidebar, 'results_button')
            # Can't verify isVisible() in test without showing the widget
            # Just verify the button exists and save button is removed
            assert not hasattr(sidebar, 'save_button') or sidebar.save_button is None
            
        finally:
            if app:
                app.quit()
    
    def test_status_view_has_set_runner_method(self):
        """Test that BaseStatusView has set_runner() method"""
        from src.app.presentation.widgets.unified_status_view import BaseStatusView
        
        assert hasattr(BaseStatusView, 'set_runner')
        method = getattr(BaseStatusView, 'set_runner')
        assert callable(method)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
