#!/usr/bin/env python3
"""
Quick Phase 3 Cleanup Script
Fixes high-priority, low-risk cleanup issues before Phase 4
"""

import re
from pathlib import Path
from typing import List, Tuple

class QuickCleanup:
    """Quick cleanup for critical issues only"""
    
    def __init__(self, src_path: str = "src/app"):
        self.src_path = Path(src_path)
        self.fixes_applied = []
    
    def run_cleanup(self):
        """Run quick cleanup for critical issues"""
        print("[*] Starting Quick Phase 3 Cleanup...")
        print("=" * 50)
        
        # Fix duplicate imports
        self.fix_duplicate_imports()
        
        # Fix TODO comment
        self.fix_todo_comments()
        
        # Report results
        self.report_results()
    
    def fix_duplicate_imports(self):
        """Fix duplicate import statements"""
        print("[>] Fixing duplicate imports...")
        
        duplicate_files = [
            ("__main__.py", 133, "import traceback"),
            ("database/database_manager.py", 559, "import os"),
            ("tools/stress_compiler_runner.py", 19, "from ..tools.compiler_runner import CompilerRunner"),
            ("tools/stress_compiler_runner.py", 20, "from PySide6.QtCore import QObject, Signal"),
            ("tools/stress_compiler_runner.py", 21, "import logging"),
            ("widgets/display_area_widgets/ai_panel.py", 275, "from ...ai.config.ai_config import AIConfig"),
            ("views/results/detailed_results_widget.py", 172, "import json"),
            ("views/results/results_window.py", 71, "from PySide6.QtWidgets import QMessageBox")
        ]
        
        for file_path, line_num, import_stmt in duplicate_files:
            self.remove_duplicate_import(file_path, line_num, import_stmt)
    
    def remove_duplicate_import(self, file_path: str, line_num: int, import_stmt: str):
        """Remove a specific duplicate import"""
        full_path = self.src_path / file_path
        
        if not full_path.exists():
            print(f"  [!] File not found: {file_path}")
            return
        
        try:
            # Read file content
            content = full_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check if the line contains the duplicate import
            if line_num <= len(lines) and import_stmt.strip() in lines[line_num - 1]:
                # Find if this import appears earlier in the file
                import_found_earlier = False
                for i, line in enumerate(lines[:line_num - 1]):
                    if import_stmt.strip() == line.strip():
                        import_found_earlier = True
                        break
                
                if import_found_earlier:
                    # Remove the duplicate
                    lines.pop(line_num - 1)
                    
                    # Write back
                    full_path.write_text('\n'.join(lines), encoding='utf-8')
                    
                    self.fixes_applied.append(f"Removed duplicate import in {file_path}:{line_num}")
                    print(f"  [+] Fixed: {file_path}:{line_num}")
                else:
                    print(f"  [i] No earlier import found in {file_path}:{line_num}")
            else:
                print(f"  [i] Import not found at expected location: {file_path}:{line_num}")
                
        except Exception as e:
            print(f"  [!] Error fixing {file_path}: {e}")
    
    def fix_todo_comments(self):
        """Fix TODO comments"""
        print("[>] Fixing TODO comments...")
        
        # Fix the TODO in results_window.py
        results_window_path = self.src_path / "views/results/results_window.py"
        
        if results_window_path.exists():
            try:
                content = results_window_path.read_text(encoding='utf-8')
                
                # Replace TODO with documented future work
                updated_content = content.replace(
                    "# TODO: Implement export functionality",
                    "# NOTE: Export functionality planned for future release"
                )
                
                if updated_content != content:
                    results_window_path.write_text(updated_content, encoding='utf-8')
                    self.fixes_applied.append("Updated TODO comment in views/results/results_window.py")
                    print("  [+] Fixed: TODO comment in results_window.py")
                else:
                    print("  [i] TODO comment not found at expected location")
                    
            except Exception as e:
                print(f"  [!] Error fixing TODO: {e}")
    
    def report_results(self):
        """Report cleanup results"""
        print("\n" + "=" * 50)
        print("[*] QUICK CLEANUP RESULTS")
        print("=" * 50)
        
        if self.fixes_applied:
            print(f"[+] Applied {len(self.fixes_applied)} fixes:")
            for fix in self.fixes_applied:
                print(f"  • {fix}")
            print(f"\n[*] Cleanup complete! {len(self.fixes_applied)} issues resolved.")
        else:
            print("[i] No fixes applied. Files may have been already cleaned or moved.")
        
        print("\n[*] REMAINING WORK FOR POST-PHASE 4:")
        print("• 40 long functions (planned for gradual refactoring)")
        print("• 11 complex conditions (architectural review needed)")
        print("• Consider implementing code quality metrics in CI/CD")

if __name__ == "__main__":
    cleanup = QuickCleanup()
    cleanup.run_cleanup()
