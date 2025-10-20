#!/usr/bin/env python3
"""
Dead Code Finder using Vulture

Usage:
    python find_dead_code.py [folder_path] [--min-confidence 60] [--sort-by size|confidence|type]

Examples:
    python find_dead_code.py src/app/presentation
    python find_dead_code.py src --min-confidence 80
    python find_dead_code.py src/app/core --sort-by size
"""

import sys
import argparse
from pathlib import Path
from collections import defaultdict
import vulture

class DeadCodeFinder:
    """Find dead code using vulture with enhanced reporting."""
    
    def __init__(self, min_confidence=60):
        self.min_confidence = min_confidence
        self.vulture = vulture.Vulture()
    
    def scan(self, paths):
        """Scan the given paths for dead code."""
        if isinstance(paths, str):
            paths = [paths]
        
        self.vulture.scavenge(paths)
        # Filter by confidence
        unused = [item for item in self.vulture.get_unused_code() 
                  if item.confidence >= self.min_confidence]
        return unused
    
    def categorize_by_type(self, unused_code):
        """Categorize unused code by type."""
        categorized = defaultdict(list)
        
        for item in unused_code:
            # Determine the type
            if 'import' in item.typ:
                category = 'imports'
            elif item.typ == 'function':
                category = 'functions'
            elif item.typ == 'method':
                category = 'methods'
            elif item.typ == 'property':
                category = 'properties'
            elif item.typ == 'class':
                category = 'classes'
            elif item.typ == 'variable':
                category = 'variables'
            elif item.typ == 'attribute':
                category = 'attributes'
            else:
                category = 'other'
            
            categorized[category].append(item)
        
        return categorized
    
    def group_by_file(self, unused_code):
        """Group unused code by file."""
        by_file = defaultdict(list)
        for item in unused_code:
            by_file[item.filename].append(item)
        return by_file
    
    def estimate_lines(self, item):
        """Estimate lines of code for an item."""
        # This is approximate - actual LOC would need file reading
        if 'import' in item.typ:
            return 1
        elif item.typ == 'variable':
            return 1
        elif item.typ == 'attribute':
            return 1
        elif item.typ == 'function':
            return 10  # Average function size
        elif item.typ == 'method':
            return 8   # Average method size
        elif item.typ == 'class':
            return 20  # Average class size
        elif item.typ == 'property':
            return 5
        else:
            return 3
    
    def format_report(self, unused_code, sort_by='type'):
        """Format a detailed report of unused code."""
        if not unused_code:
            return "✅ No dead code found!"
        
        lines = []
        lines.append(f"\n{'='*80}")
        lines.append(f"🔍 DEAD CODE ANALYSIS (min confidence: {self.min_confidence}%)")
        lines.append(f"{'='*80}\n")
        
        # Summary statistics
        total_items = len(unused_code)
        estimated_lines = sum(self.estimate_lines(item) for item in unused_code)
        
        categorized = self.categorize_by_type(unused_code)
        
        lines.append(f"📊 SUMMARY:")
        lines.append(f"   Total dead code items: {total_items}")
        lines.append(f"   Estimated lines: ~{estimated_lines}")
        lines.append(f"")
        lines.append(f"   Breakdown by type:")
        for category, items in sorted(categorized.items()):
            lines.append(f"      - {category.capitalize()}: {len(items)}")
        lines.append("")
        
        # Detailed breakdown
        if sort_by == 'type':
            self._format_by_type(lines, categorized)
        elif sort_by == 'file':
            by_file = self.group_by_file(unused_code)
            self._format_by_file(lines, by_file)
        elif sort_by == 'confidence':
            self._format_by_confidence(lines, unused_code)
        elif sort_by == 'size':
            self._format_by_size(lines, unused_code)
        
        return '\n'.join(lines)
    
    def _format_by_type(self, lines, categorized):
        """Format report grouped by type."""
        lines.append(f"{'='*80}")
        lines.append(f"📋 DETAILED BREAKDOWN BY TYPE")
        lines.append(f"{'='*80}\n")
        
        priority_order = ['imports', 'functions', 'methods', 'classes', 'properties', 'variables', 'attributes', 'other']
        
        for category in priority_order:
            if category not in categorized:
                continue
            
            items = categorized[category]
            if not items:
                continue
            
            lines.append(f"\n🔸 {category.upper()} ({len(items)} items)")
            lines.append(f"{'-'*80}")
            
            # Sort by filename and line number
            items.sort(key=lambda x: (x.filename, x.first_lineno))
            
            for item in items:
                rel_path = Path(item.filename).as_posix()
                lines.append(f"   {rel_path}:{item.first_lineno}")
                lines.append(f"      {item.typ}: '{item.name}' ({item.confidence}% confidence)")
                if hasattr(item, 'message') and item.message:
                    lines.append(f"      {item.message}")
                lines.append("")
    
    def _format_by_file(self, lines, by_file):
        """Format report grouped by file."""
        lines.append(f"{'='*80}")
        lines.append(f"📋 DETAILED BREAKDOWN BY FILE")
        lines.append(f"{'='*80}\n")
        
        for filename in sorted(by_file.keys()):
            items = by_file[filename]
            rel_path = Path(filename).as_posix()
            
            lines.append(f"\n📄 {rel_path} ({len(items)} items)")
            lines.append(f"{'-'*80}")
            
            items.sort(key=lambda x: x.first_lineno)
            
            for item in items:
                lines.append(f"   Line {item.first_lineno:4d}: {item.typ:12s} '{item.name}' ({item.confidence}%)")
    
    def _format_by_confidence(self, lines, unused_code):
        """Format report sorted by confidence."""
        lines.append(f"{'='*80}")
        lines.append(f"📋 DETAILED BREAKDOWN BY CONFIDENCE")
        lines.append(f"{'='*80}\n")
        
        sorted_items = sorted(unused_code, key=lambda x: x.confidence, reverse=True)
        
        current_confidence = None
        for item in sorted_items:
            if current_confidence != item.confidence:
                current_confidence = item.confidence
                lines.append(f"\n🔸 {current_confidence}% CONFIDENCE")
                lines.append(f"{'-'*80}")
            
            rel_path = Path(item.filename).as_posix()
            lines.append(f"   {rel_path}:{item.first_lineno}")
            lines.append(f"      {item.typ}: '{item.name}'")
    
    def _format_by_size(self, lines, unused_code):
        """Format report sorted by estimated size."""
        lines.append(f"{'='*80}")
        lines.append(f"📋 DETAILED BREAKDOWN BY ESTIMATED SIZE")
        lines.append(f"{'='*80}\n")
        
        sorted_items = sorted(unused_code, key=lambda x: self.estimate_lines(x), reverse=True)
        
        for item in sorted_items:
            estimated = self.estimate_lines(item)
            rel_path = Path(item.filename).as_posix()
            lines.append(f"   ~{estimated:3d} lines | {rel_path}:{item.first_lineno}")
            lines.append(f"              {item.typ}: '{item.name}' ({item.confidence}%)")
            lines.append("")
    
    def save_report(self, report, output_file):
        """Save report to file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📝 Report saved to: {output_file}")


def main():
    """Main entry point."""
    # Fix encoding for Windows console
    import sys
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    parser = argparse.ArgumentParser(
        description='Find dead code using vulture',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s src/app/presentation
  %(prog)s src --min-confidence 80
  %(prog)s src/app/core --sort-by size --output report.txt
  %(prog)s . --min-confidence 90 --sort-by confidence
        """
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        default='src/app/presentation',
        help='Path to scan for dead code (default: src/app/presentation)'
    )
    
    parser.add_argument(
        '--min-confidence',
        type=int,
        default=60,
        help='Minimum confidence level (0-100, default: 60)'
    )
    
    parser.add_argument(
        '--sort-by',
        choices=['type', 'file', 'confidence', 'size'],
        default='type',
        help='How to sort the results (default: type)'
    )
    
    parser.add_argument(
        '--output',
        '-o',
        help='Save report to file'
    )
    
    parser.add_argument(
        '--ignore-names',
        nargs='*',
        help='Patterns to ignore (e.g., test_* _private)'
    )
    
    args = parser.parse_args()
    
    # Validate path
    path = Path(args.path)
    if not path.exists():
        print(f"❌ Error: Path '{args.path}' does not exist!")
        sys.exit(1)
    
    # Run analysis
    print(f"🔍 Scanning: {path}")
    print(f"   Min confidence: {args.min_confidence}%")
    print(f"   Sort by: {args.sort_by}")
    print(f"\n⏳ Analyzing...")
    
    finder = DeadCodeFinder(min_confidence=args.min_confidence)
    unused_code = finder.scan(str(path))
    
    # Filter by ignore patterns if provided
    if args.ignore_names:
        import fnmatch
        filtered = []
        for item in unused_code:
            should_ignore = False
            for pattern in args.ignore_names:
                if fnmatch.fnmatch(item.name, pattern):
                    should_ignore = True
                    break
            if not should_ignore:
                filtered.append(item)
        unused_code = filtered
    
    # Generate report
    report = finder.format_report(unused_code, sort_by=args.sort_by)
    print(report)
    
    # Save to file if requested
    if args.output:
        finder.save_report(report, args.output)
    
    # Exit with appropriate code
    if unused_code:
        print(f"\n⚠️  Found {len(unused_code)} potentially unused items")
        print(f"💡 Review carefully - some may be used dynamically or be false positives")
        sys.exit(1)
    else:
        print(f"\n✅ No dead code found!")
        sys.exit(0)


if __name__ == '__main__':
    main()
