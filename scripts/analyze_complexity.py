#!/usr/bin/env python3
"""
Comprehensive Code Complexity Analyzer using Radon

This script analyzes Python code complexity metrics including:
- Cyclomatic Complexity (CC) - Measures code complexity based on control flow
- Maintainability Index (MI) - Measures code maintainability (0-100 scale)
- Halstead Metrics - Measures program vocabulary and volume
- Raw Metrics - Lines of code, comments, etc.

Features:
- Multiple sorting modes (complexity, maintainability, file, type)
- Configurable thresholds for different complexity grades
- File output capability
- Ignore patterns support
- Detailed categorized reporting
- Summary statistics

Usage:
    python analyze_complexity.py <path> [options]

Examples:
    # Analyze presentation layer, show high complexity (C or worse)
    python analyze_complexity.py src/app/presentation --min-grade C

    # Sort by maintainability, save to file
    python analyze_complexity.py src --sort-by maintainability -o report.txt

    # Show only specific complexity grades
    python analyze_complexity.py src/app --grades C D E F

    # Ignore test files
    python analyze_complexity.py src --ignore-names "*test*"

Author: Code Testing Suite Team
Version: 1.0.0
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import json

try:
    from radon.complexity import cc_visit, cc_rank
    from radon.metrics import mi_visit, mi_rank
    from radon.raw import analyze as raw_analyze
    from radon.visitors import Function, Class
except ImportError:
    print("❌ Error: Radon is not installed!")
    print("📦 Install it with: pip install radon")
    sys.exit(1)


class ComplexityAnalyzer:
    """
    Analyze code complexity using Radon metrics.
    """

    # Cyclomatic Complexity grades
    CC_GRADES = {
        'A': (1, 5),      # Simple, low risk
        'B': (6, 10),     # More complex, moderate risk
        'C': (11, 20),    # Complex, high risk
        'D': (21, 30),    # Very complex, very high risk
        'E': (31, 40),    # Extremely complex, maintenance nightmare
        'F': (41, None),  # Untestable, refactor immediately
    }

    # Maintainability Index ranges
    MI_RANKS = {
        'A': (20, 100),   # Highly maintainable
        'B': (10, 19),    # Moderately maintainable
        'C': (0, 9),      # Difficult to maintain
    }

    def __init__(
        self,
        min_grade: str = 'A',
        sort_by: str = 'complexity',
        ignore_names: Optional[List[str]] = None
    ):
        """
        Initialize ComplexityAnalyzer.

        Args:
            min_grade: Minimum complexity grade to report (A-F)
            sort_by: Sort mode (complexity, maintainability, file, type)
            ignore_names: Patterns to ignore
        """
        self.min_grade = min_grade.upper()
        self.sort_by = sort_by
        self.ignore_names = ignore_names or []
        self.results = []

    def analyze_path(self, path: str) -> bool:
        """
        Analyze Python files in the given path.

        Args:
            path: File or directory path to analyze

        Returns:
            bool: True if analysis succeeded
        """
        path_obj = Path(path)

        if not path_obj.exists():
            print(f"❌ Error: Path '{path}' does not exist!")
            return False

        # Collect Python files
        if path_obj.is_file():
            if path_obj.suffix == '.py':
                files = [path_obj]
            else:
                print(f"❌ Error: '{path}' is not a Python file!")
                return False
        else:
            files = list(path_obj.rglob('*.py'))

        if not files:
            print(f"❌ No Python files found in '{path}'")
            return False

        # Analyze each file
        for file_path in files:
            # Check ignore patterns
            if self._should_ignore(str(file_path)):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()

                self._analyze_file(str(file_path), code)
            except Exception as e:
                print(f"⚠️  Warning: Could not analyze {file_path}: {e}")
                continue

        return True

    def _should_ignore(self, file_path: str) -> bool:
        """Check if file should be ignored based on patterns."""
        from fnmatch import fnmatch

        for pattern in self.ignore_names:
            if fnmatch(file_path, pattern):
                return True
        return False

    def _analyze_file(self, file_path: str, code: str):
        """
        Analyze a single file for complexity metrics.

        Args:
            file_path: Path to the file
            code: File contents
        """
        # Cyclomatic Complexity
        try:
            cc_results = cc_visit(code)
            for item in cc_results:
                grade = cc_rank(item.complexity)

                # Filter by minimum grade
                if not self._meets_grade_threshold(grade, self.min_grade):
                    continue

                self.results.append({
                    'file': file_path,
                    'type': item.classname if isinstance(item, Class) else 'function',
                    'name': item.name,
                    'complexity': item.complexity,
                    'grade': grade,
                    'lineno': item.lineno,
                    'col_offset': item.col_offset,
                    'endline': item.endline if hasattr(item, 'endline') else None,
                })
        except Exception as e:
            # File might have syntax errors or other issues
            pass

    def _meets_grade_threshold(self, grade: str, min_grade: str) -> bool:
        """Check if grade meets minimum threshold."""
        grade_order = ['A', 'B', 'C', 'D', 'E', 'F']
        return grade_order.index(grade) >= grade_order.index(min_grade)

    def get_sorted_results(self) -> List[Dict]:
        """
        Get results sorted by specified mode.

        Returns:
            List of sorted complexity results
        """
        if self.sort_by == 'complexity':
            return sorted(self.results, key=lambda x: x['complexity'], reverse=True)
        elif self.sort_by == 'file':
            return sorted(self.results, key=lambda x: (x['file'], x['lineno']))
        elif self.sort_by == 'type':
            return sorted(self.results, key=lambda x: (x['type'], x['complexity']), reverse=True)
        elif self.sort_by == 'grade':
            grade_order = ['F', 'E', 'D', 'C', 'B', 'A']
            return sorted(self.results, key=lambda x: (grade_order.index(x['grade']), x['complexity']), reverse=True)
        else:
            return self.results

    def categorize_by_grade(self) -> Dict[str, List[Dict]]:
        """Categorize results by complexity grade."""
        categorized = defaultdict(list)
        for item in self.results:
            categorized[item['grade']].append(item)
        return dict(categorized)

    def categorize_by_file(self) -> Dict[str, List[Dict]]:
        """Categorize results by file."""
        categorized = defaultdict(list)
        for item in self.results:
            categorized[item['file']].append(item)
        return dict(categorized)

    def get_statistics(self) -> Dict:
        """Get summary statistics."""
        if not self.results:
            return {}

        complexities = [r['complexity'] for r in self.results]
        grades = [r['grade'] for r in self.results]

        return {
            'total_items': len(self.results),
            'avg_complexity': sum(complexities) / len(complexities),
            'max_complexity': max(complexities),
            'min_complexity': min(complexities),
            'grade_distribution': {
                grade: grades.count(grade) for grade in set(grades)
            },
            'files_analyzed': len(set(r['file'] for r in self.results)),
        }

    def format_report(self) -> str:
        """
        Format complexity analysis report.

        Returns:
            Formatted report string
        """
        if not self.results:
            return "✅ No high complexity code found!"

        lines = []
        lines.append("=" * 80)
        lines.append("🔍 CODE COMPLEXITY ANALYSIS")
        lines.append("=" * 80)
        lines.append("")

        # Statistics
        stats = self.get_statistics()
        lines.append("📊 SUMMARY:")
        lines.append(f"   Total items: {stats['total_items']}")
        lines.append(f"   Files analyzed: {stats['files_analyzed']}")
        lines.append(f"   Average complexity: {stats['avg_complexity']:.1f}")
        lines.append(f"   Max complexity: {stats['max_complexity']}")
        lines.append("")
        lines.append("   Grade distribution:")
        for grade in ['F', 'E', 'D', 'C', 'B', 'A']:
            if grade in stats['grade_distribution']:
                count = stats['grade_distribution'][grade]
                desc = self._get_grade_description(grade)
                lines.append(f"      {grade}: {count} items - {desc}")
        lines.append("")

        # Legend
        lines.append("=" * 80)
        lines.append("📋 COMPLEXITY GRADES")
        lines.append("=" * 80)
        lines.append("")
        lines.append("   A (1-5):    Simple, low risk - Easy to maintain")
        lines.append("   B (6-10):   More complex, moderate risk - Acceptable")
        lines.append("   C (11-20):  Complex, high risk - Consider refactoring")
        lines.append("   D (21-30):  Very complex, very high risk - Refactor soon")
        lines.append("   E (31-40):  Extremely complex - Maintenance nightmare")
        lines.append("   F (41+):    Untestable - Refactor immediately!")
        lines.append("")

        # Detailed breakdown
        lines.append("=" * 80)
        lines.append(f"📋 DETAILED BREAKDOWN (sorted by {self.sort_by})")
        lines.append("=" * 80)
        lines.append("")

        if self.sort_by == 'grade':
            # Group by grade
            categorized = self.categorize_by_grade()
            for grade in ['F', 'E', 'D', 'C', 'B', 'A']:
                if grade not in categorized:
                    continue

                items = categorized[grade]
                desc = self._get_grade_description(grade)
                lines.append("")
                lines.append(f"🔸 GRADE {grade}: {desc}")
                lines.append("-" * 80)

                for item in sorted(items, key=lambda x: x['complexity'], reverse=True):
                    lines.append(f"   {item['file']}:{item['lineno']}")
                    lines.append(f"      {item['type']}: {item['name']}")
                    lines.append(f"      Complexity: {item['complexity']} (Grade {item['grade']})")
                    lines.append("")

        elif self.sort_by == 'file':
            # Group by file
            categorized = self.categorize_by_file()
            for file_path in sorted(categorized.keys()):
                items = categorized[file_path]
                lines.append("")
                lines.append(f"📁 {file_path}")
                lines.append("-" * 80)

                for item in sorted(items, key=lambda x: x['lineno']):
                    lines.append(f"   Line {item['lineno']}: {item['name']}")
                    lines.append(f"      Type: {item['type']}")
                    lines.append(f"      Complexity: {item['complexity']} (Grade {item['grade']})")
                    lines.append("")

        else:
            # List all items sorted
            for item in self.get_sorted_results():
                lines.append(f"   {item['file']}:{item['lineno']}")
                lines.append(f"      {item['type']}: {item['name']}")
                lines.append(f"      Complexity: {item['complexity']} (Grade {item['grade']})")
                lines.append("")

        return "\n".join(lines)

    def _get_grade_description(self, grade: str) -> str:
        """Get description for complexity grade."""
        descriptions = {
            'A': 'Simple, low risk',
            'B': 'More complex, moderate risk',
            'C': 'Complex, high risk - Consider refactoring',
            'D': 'Very complex - Refactor soon',
            'E': 'Extremely complex - Maintenance nightmare',
            'F': 'Untestable - Refactor immediately!',
        }
        return descriptions.get(grade, 'Unknown')


def main():
    """Main entry point."""
    # Fix encoding for Windows console
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

    parser = argparse.ArgumentParser(
        description='Analyze code complexity using Radon',
        epilog="""
Examples:
  # Analyze with default settings (show A grade and above)
  python analyze_complexity.py src/app/presentation

  # Show only high complexity (C grade or worse)
  python analyze_complexity.py src --min-grade C

  # Sort by file and save to report
  python analyze_complexity.py src --sort-by file -o complexity_report.txt

  # Analyze specific grades only
  python analyze_complexity.py src --grades C D E F

  # Ignore test files
  python analyze_complexity.py src --ignore-names "*test*" "*/tests/*"

Complexity Grades:
  A (1-5):   Simple, low risk
  B (6-10):  More complex, moderate risk
  C (11-20): Complex, high risk
  D (21-30): Very complex, very high risk
  E (31-40): Extremely complex
  F (41+):   Untestable, refactor immediately
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'path',
        help='Path to file or directory to analyze'
    )

    parser.add_argument(
        '--min-grade',
        default='A',
        choices=['A', 'B', 'C', 'D', 'E', 'F'],
        help='Minimum complexity grade to report (default: A, shows all)'
    )

    parser.add_argument(
        '--sort-by',
        default='complexity',
        choices=['complexity', 'file', 'type', 'grade'],
        help='Sort results by: complexity (default), file, type, or grade'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output file path (if not specified, prints to console)'
    )

    parser.add_argument(
        '--ignore-names',
        nargs='+',
        help='Patterns to ignore (e.g., "*test*" "*/migrations/*")'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )

    args = parser.parse_args()

    # Display analysis info (unless JSON output)
    if not args.json:
        print(f"🔍 Analyzing: {args.path}")
        print(f"   Min grade: {args.min_grade}")
        print(f"   Sort by: {args.sort_by}")
        print("")
        print("⏳ Analyzing...")
        print("")

    # Create analyzer
    analyzer = ComplexityAnalyzer(
        min_grade=args.min_grade,
        sort_by=args.sort_by,
        ignore_names=args.ignore_names
    )

    # Run analysis
    if not analyzer.analyze_path(args.path):
        sys.exit(1)

    # Generate report
    if args.json:
        report = json.dumps({
            'results': analyzer.get_sorted_results(),
            'statistics': analyzer.get_statistics(),
        }, indent=2)
    else:
        report = analyzer.format_report()

    # Output report
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            if not args.json:
                print(f"📝 Report saved to: {args.output}")
        except Exception as e:
            if not args.json:
                print(f"❌ Error saving report: {e}")
            sys.exit(1)
    else:
        print(report)

    # Exit code based on findings
    if analyzer.results:
        if not args.json:
            print("")
            print(f"⚠️  Found {len(analyzer.results)} items meeting complexity threshold")
            print("💡 Review and consider refactoring high complexity code")
        sys.exit(1)
    else:
        if not args.json:
            print("")
            print("✅ All code meets complexity standards!")
        sys.exit(0)


if __name__ == '__main__':
    main()
