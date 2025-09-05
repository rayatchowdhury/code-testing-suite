#!/usr/bin/env python3
"""
Phase 3 Cleanup Analysis Script
Analyzes the codebase to identify cleanup opportunities
"""

import os
import ast
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple

class CleanupAnalyzer:
    """Analyze codebase for cleanup opportunities"""
    
    def __init__(self, src_path: str = "src/app"):
        self.src_path = Path(src_path)
        self.issues = {
            'unused_imports': [],
            'duplicate_code': [],
            'long_functions': [],
            'complex_conditions': [],
            'dead_code': [],
            'import_issues': []
        }
    
    def analyze(self):
        """Run complete cleanup analysis"""
        print("[*] Starting Phase 3 Cleanup Analysis...")
        print("=" * 50)
        
        for py_file in self.src_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            print(f"[>] Analyzing: {py_file.relative_to(self.src_path)}")
            self.analyze_file(py_file)
        
        self.report_findings()
    
    def analyze_file(self, file_path: Path):
        """Analyze a single Python file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            # Analyze imports
            self.analyze_imports(file_path, content, tree)
            
            # Analyze functions
            self.analyze_functions(file_path, tree)
            
            # Look for potential issues
            self.analyze_code_quality(file_path, content)
            
        except Exception as e:
            print(f"  [!] Error analyzing {file_path}: {e}")
    
    def analyze_imports(self, file_path: Path, content: str, tree: ast.AST):
        """Analyze import statements"""
        imports = []
        used_names = set()
        
        # Extract all imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        imports.append(alias.name if alias.name != '*' else f"{node.module}.*")
        
        # Extract all used names (simplified)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)
        
        # Check for wildcard imports
        if '*' in content and 'import *' in content:
            self.issues['import_issues'].append({
                'file': file_path,
                'issue': 'wildcard_import',
                'line': self.find_line_with_text(content, 'import *')
            })
        
        # Check for duplicate imports (simplified)
        import_counts = {}
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'import ' in line and not line.strip().startswith('#'):
                import_counts[line.strip()] = import_counts.get(line.strip(), 0) + 1
                if import_counts[line.strip()] > 1:
                    self.issues['import_issues'].append({
                        'file': file_path,
                        'issue': 'duplicate_import', 
                        'line': i + 1,
                        'content': line.strip()
                    })
    
    def analyze_functions(self, file_path: Path, tree: ast.AST):
        """Analyze function definitions"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Count lines in function
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    func_lines = node.end_lineno - node.lineno
                    if func_lines > 50:
                        self.issues['long_functions'].append({
                            'file': file_path,
                            'function': node.name,
                            'lines': func_lines,
                            'start_line': node.lineno
                        })
                
                # Check for complex conditions (nested ifs)
                self.check_complexity(file_path, node)
    
    def check_complexity(self, file_path: Path, node: ast.AST):
        """Check for complex nested conditions"""
        nested_depth = 0
        
        def count_nested_ifs(node, depth=0):
            nonlocal nested_depth
            nested_depth = max(nested_depth, depth)
            
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.If):
                    count_nested_ifs(child, depth + 1)
                else:
                    count_nested_ifs(child, depth)
        
        count_nested_ifs(node)
        
        if nested_depth > 3:
            self.issues['complex_conditions'].append({
                'file': file_path,
                'function': getattr(node, 'name', 'unknown'),
                'nested_depth': nested_depth,
                'line': node.lineno
            })
    
    def analyze_code_quality(self, file_path: Path, content: str):
        """Analyze general code quality issues"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Look for debug prints
            if re.search(r'\bprint\s*\(.*debug.*\)', line.lower()):
                self.issues['dead_code'].append({
                    'file': file_path,
                    'issue': 'debug_print',
                    'line': i + 1,
                    'content': line.strip()
                })
            
            # Look for TODO/FIXME comments
            if re.search(r'#.*\b(TODO|FIXME|HACK)\b', line.upper()):
                self.issues['dead_code'].append({
                    'file': file_path,
                    'issue': 'todo_comment',
                    'line': i + 1,
                    'content': line.strip()
                })
    
    def find_line_with_text(self, content: str, text: str) -> int:
        """Find line number containing specific text"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if text in line:
                return i + 1
        return 0
    
    def report_findings(self):
        """Report all findings"""
        print("\n" + "=" * 50)
        print("[*] PHASE 3 CLEANUP ANALYSIS RESULTS")
        print("=" * 50)
        
        total_issues = sum(len(issues) for issues in self.issues.values())
        
        if total_issues == 0:
            print("[+] No major cleanup issues found! Codebase is in good shape.")
            return
        
        print(f"[*] Found {total_issues} potential cleanup opportunities:\n")
        
        # Import Issues
        if self.issues['import_issues']:
            print(f"[>] IMPORT ISSUES ({len(self.issues['import_issues'])} found):")
            for issue in self.issues['import_issues']:
                file_path = issue['file'].relative_to(self.src_path)
                print(f"  • {file_path}:{issue['line']} - {issue['issue']}")
                if 'content' in issue:
                    print(f"    Content: {issue['content']}")
            print()
        
        # Long Functions
        if self.issues['long_functions']:
            print(f"[>] LONG FUNCTIONS ({len(self.issues['long_functions'])} found):")
            for issue in self.issues['long_functions']:
                file_path = issue['file'].relative_to(self.src_path)
                print(f"  • {file_path}:{issue['start_line']} - {issue['function']}() ({issue['lines']} lines)")
            print()
        
        # Complex Conditions
        if self.issues['complex_conditions']:
            print(f"[>] COMPLEX CONDITIONS ({len(self.issues['complex_conditions'])} found):")
            for issue in self.issues['complex_conditions']:
                file_path = issue['file'].relative_to(self.src_path)
                print(f"  • {file_path}:{issue['line']} - {issue['function']}() (nesting depth: {issue['nested_depth']})")
            print()
        
        # Dead Code
        if self.issues['dead_code']:
            print(f"[>] POTENTIAL DEAD CODE ({len(self.issues['dead_code'])} found):")
            for issue in self.issues['dead_code']:
                file_path = issue['file'].relative_to(self.src_path)
                print(f"  • {file_path}:{issue['line']} - {issue['issue']}")
                print(f"    Content: {issue['content']}")
            print()
        
        print("[*] CLEANUP PRIORITY:")
        print("1. Fix import issues (wildcard imports, duplicates)")
        print("2. Simplify long functions (>50 lines)")
        print("3. Reduce complex conditions (>3 levels deep)")
        print("4. Remove dead code and debug prints")

if __name__ == "__main__":
    analyzer = CleanupAnalyzer()
    analyzer.analyze()
