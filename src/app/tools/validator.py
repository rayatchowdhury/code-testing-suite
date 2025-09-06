# -*- coding: utf-8 -*-
import os
import re
import subprocess
import logging
from typing import List, Dict, Tuple, Optional
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)

class Validator(QObject):
    """Code validation tool with configurable rules and strictness levels"""
    
    validationProgress = Signal(int)  # Progress percentage
    validationComplete = Signal(dict)  # Results
    validationError = Signal(str)  # Error message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.strictness_level = 3  # Default medium strictness
        
    def set_strictness(self, level: int):
        """Set validation strictness level (1-5)"""
        self.strictness_level = max(1, min(5, level))
        
    def validate_code(self, file_path: str, style_rules_path: Optional[str] = None) -> Dict:
        """
        Validate code file against various rules
        Returns validation results dictionary
        """
        if not os.path.exists(file_path):
            self.validationError.emit(f"File not found: {file_path}")
            return {}
            
        try:
            results = {
                'file_path': file_path,
                'strictness_level': self.strictness_level,
                'syntax_valid': False,
                'style_issues': [],
                'code_quality_issues': [],
                'security_issues': [],
                'performance_warnings': [],
                'overall_score': 0,
                'total_issues': 0
            }
            
            self.validationProgress.emit(10)
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 1. Syntax validation
            results['syntax_valid'] = self._validate_syntax(file_path, content)
            self.validationProgress.emit(25)
            
            # 2. Style validation
            if style_rules_path and os.path.exists(style_rules_path):
                results['style_issues'] = self._validate_style(content, style_rules_path)
            else:
                results['style_issues'] = self._validate_default_style(content)
            self.validationProgress.emit(50)
            
            # 3. Code quality checks
            results['code_quality_issues'] = self._validate_code_quality(content)
            self.validationProgress.emit(75)
            
            # 4. Security and performance (for higher strictness)
            if self.strictness_level >= 3:
                results['security_issues'] = self._validate_security(content)
                results['performance_warnings'] = self._validate_performance(content)
                
            self.validationProgress.emit(90)
            
            # Calculate overall score
            results = self._calculate_score(results)
            self.validationProgress.emit(100)
            
            self.validationComplete.emit(results)
            return results
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            logger.error(error_msg)
            self.validationError.emit(error_msg)
            return {}
    
    def _validate_syntax(self, file_path: str, content: str) -> bool:
        """Validate syntax by attempting compilation"""
        if not file_path.endswith(('.cpp', '.c')):
            return True  # Skip syntax check for non-C++ files
            
        try:
            # Try to compile with g++ or clang++
            temp_file = file_path + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Try compilation
            for compiler in ['g++', 'clang++', 'gcc']:
                try:
                    result = subprocess.run([
                        compiler, '-fsyntax-only', temp_file
                    ], capture_output=True, text=True, timeout=10)
                    
                    # Clean up temp file
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        
                    return result.returncode == 0
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
                    
            # If no compiler found, assume syntax is valid
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return True
            
        except Exception as e:
            logger.error(f"Syntax validation error: {e}")
            return False
    
    def _validate_style(self, content: str, style_rules_path: str) -> List[Dict]:
        """Validate against custom style rules"""
        issues = []
        
        try:
            with open(style_rules_path, 'r', encoding='utf-8') as f:
                rules_content = f.read()
                
            # Parse style rules (basic implementation)
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # Check line length
                if 'Maximum line length:' in rules_content:
                    max_len_match = re.search(r'Maximum line length:\s*(\d+)', rules_content)
                    if max_len_match:
                        max_len = int(max_len_match.group(1))
                        if len(line) > max_len:
                            issues.append({
                                'type': 'style',
                                'line': i,
                                'message': f'Line exceeds maximum length of {max_len} characters',
                                'severity': 'warning' if self.strictness_level < 4 else 'error'
                            })
                
                # Check indentation
                if 'Indentation:' in rules_content and line.strip():
                    indent_match = re.search(r'Indentation:\s*(\d+)\s*spaces', rules_content)
                    if indent_match:
                        expected_indent = int(indent_match.group(1))
                        leading_spaces = len(line) - len(line.lstrip(' '))
                        if leading_spaces % expected_indent != 0 and leading_spaces > 0:
                            issues.append({
                                'type': 'style',
                                'line': i,
                                'message': f'Inconsistent indentation (expected multiples of {expected_indent})',
                                'severity': 'warning'
                            })
                            
        except Exception as e:
            logger.error(f"Style validation error: {e}")
            
        return issues
    
    def _validate_default_style(self, content: str) -> List[Dict]:
        """Validate against default style rules"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for tabs (prefer spaces)
            if '\t' in line and self.strictness_level >= 2:
                issues.append({
                    'type': 'style',
                    'line': i,
                    'message': 'Use spaces instead of tabs for indentation',
                    'severity': 'warning'
                })
            
            # Check line length (default 100 characters)
            max_len = 100 if self.strictness_level <= 3 else 80
            if len(line) > max_len:
                issues.append({
                    'type': 'style',
                    'line': i,
                    'message': f'Line exceeds {max_len} characters',
                    'severity': 'warning' if self.strictness_level < 4 else 'error'
                })
            
            # Check trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                issues.append({
                    'type': 'style',
                    'line': i,
                    'message': 'Trailing whitespace detected',
                    'severity': 'info'
                })
        
        return issues
    
    def _validate_code_quality(self, content: str) -> List[Dict]:
        """Validate code quality aspects"""
        issues = []
        lines = content.split('\n')
        
        # Check for common code quality issues
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Magic numbers (for strictness >= 3)
            if self.strictness_level >= 3:
                magic_numbers = re.findall(r'\b(\d{2,})\b', line_stripped)
                for num in magic_numbers:
                    if num not in ['10', '100', '1000']:  # Common acceptable numbers
                        issues.append({
                            'type': 'quality',
                            'line': i,
                            'message': f'Consider using a named constant instead of magic number {num}',
                            'severity': 'info'
                        })
            
            # TODO comments (for strictness >= 2)
            if self.strictness_level >= 2 and 'TODO' in line_stripped.upper():
                issues.append({
                    'type': 'quality',
                    'line': i,
                    'message': 'TODO comment found - consider completing or removing',
                    'severity': 'info'
                })
            
            # Empty catch blocks (for C++)
            if 'catch' in line_stripped and '{' in line_stripped and '}' in line_stripped:
                issues.append({
                    'type': 'quality',
                    'line': i,
                    'message': 'Empty catch block detected',
                    'severity': 'warning'
                })
        
        # Check for missing comments on complex functions (strictness >= 4)
        if self.strictness_level >= 4:
            function_pattern = r'^\s*(int|void|string|double|float|bool)\s+\w+\s*\([^)]*\)\s*{'
            for i, line in enumerate(lines, 1):
                if re.match(function_pattern, line):
                    # Check if previous line has a comment
                    if i > 1 and not lines[i-2].strip().startswith('//'):
                        issues.append({
                            'type': 'quality',
                            'line': i,
                            'message': 'Function lacks documentation comment',
                            'severity': 'warning'
                        })
        
        return issues
    
    def _validate_security(self, content: str) -> List[Dict]:
        """Validate security aspects (for higher strictness levels)"""
        issues = []
        
        if self.strictness_level < 3:
            return issues
            
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Unsafe functions in C++
            unsafe_functions = ['gets', 'sprintf', 'strcpy', 'strcat']
            for func in unsafe_functions:
                if f'{func}(' in line_stripped:
                    issues.append({
                        'type': 'security',
                        'line': i,
                        'message': f'Use of potentially unsafe function {func}()',
                        'severity': 'warning'
                    })
            
            # Buffer overflow risks
            if 'char ' in line_stripped and '[' in line_stripped and ']' in line_stripped:
                if 'scanf' in content or 'gets' in content:
                    issues.append({
                        'type': 'security',
                        'line': i,
                        'message': 'Fixed-size buffer with unsafe input functions detected',
                        'severity': 'error'
                    })
        
        return issues
    
    def _validate_performance(self, content: str) -> List[Dict]:
        """Validate performance aspects (for higher strictness levels)"""
        issues = []
        
        if self.strictness_level < 3:
            return issues
            
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Inefficient string concatenation in loops
            if ('for' in line_stripped or 'while' in line_stripped) and i < len(lines) - 1:
                next_line = lines[i].strip()
                if '+=' in next_line and 'string' in content:
                    issues.append({
                        'type': 'performance',
                        'line': i + 1,
                        'message': 'String concatenation in loop may be inefficient',
                        'severity': 'info'
                    })
            
            # Unnecessary includes (basic check)
            if line_stripped.startswith('#include') and self.strictness_level >= 4:
                include_name = line_stripped.replace('#include', '').strip(' <>"')
                if include_name in ['iostream'] and 'cout' not in content and 'cin' not in content:
                    issues.append({
                        'type': 'performance',
                        'line': i,
                        'message': f'Unused include: {include_name}',
                        'severity': 'info'
                    })
        
        return issues
    
    def _calculate_score(self, results: Dict) -> Dict:
        """Calculate overall validation score"""
        total_issues = 0
        severity_weights = {
            'error': 3,
            'warning': 2,
            'info': 1
        }
        
        score_deduction = 0
        
        for category in ['style_issues', 'code_quality_issues', 'security_issues', 'performance_warnings']:
            issues = results.get(category, [])
            total_issues += len(issues)
            
            for issue in issues:
                severity = issue.get('severity', 'info')
                score_deduction += severity_weights.get(severity, 1)
        
        # Start with 100 and deduct points
        base_score = 100
        if not results['syntax_valid']:
            base_score -= 50  # Major penalty for syntax errors
        
        final_score = max(0, base_score - score_deduction)
        
        results['total_issues'] = total_issues
        results['overall_score'] = final_score
        
        return results
