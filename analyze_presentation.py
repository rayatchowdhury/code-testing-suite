#!/usr/bin/env python3
"""
Analyze src/app/presentation structure and generate comprehensive report.
"""

import os
import re
import ast
from pathlib import Path
from collections import defaultdict
from datetime import datetime

PRESENTATION_ROOT = Path("src/app/presentation")

def get_class_bases(node):
    """Extract base class names from a class node."""
    bases = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            bases.append(base.id)
        elif isinstance(base, ast.Attribute):
            # Handle qualified names like QMainWindow
            bases.append(base.attr)
    return bases

def analyze_file(filepath):
    """Analyze a single Python file and extract metadata."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=str(filepath))
        
        classes = []
        functions = []
        imports = []
        signals = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = get_class_bases(node)
                classes.append({
                    'name': node.name,
                    'line': node.lineno,
                    'bases': bases
                })
                
                # Check for Signal attributes in class
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                if isinstance(item.value, ast.Call):
                                    if hasattr(item.value.func, 'id') and 'Signal' in item.value.func.id:
                                        signals.append({
                                            'name': target.id,
                                            'line': item.lineno,
                                            'class': node.name
                                        })
                                    elif hasattr(item.value.func, 'attr') and 'Signal' in item.value.func.attr:
                                        signals.append({
                                            'name': target.id,
                                            'line': item.lineno,
                                            'class': node.name
                                        })
            
            elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                # Top-level functions only
                if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno
                    })
            
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append({
                            'module': module,
                            'name': alias.name,
                            'line': node.lineno
                        })
                else:
                    for alias in node.names:
                        imports.append({
                            'module': alias.name,
                            'name': alias.name,
                            'line': node.lineno
                        })
        
        return {
            'classes': classes,
            'functions': functions,
            'imports': imports,
            'signals': signals,
            'lines': len(content.splitlines())
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'classes': [],
            'functions': [],
            'imports': [],
            'signals': [],
            'lines': 0
        }

def analyze_presentation():
    """Analyze entire presentation directory."""
    files_data = {}
    
    for root, dirs, files in os.walk(PRESENTATION_ROOT):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                rel_path = filepath.relative_to(PRESENTATION_ROOT.parent.parent.parent)
                files_data[str(rel_path)] = analyze_file(filepath)
    
    return files_data

def generate_report(files_data):
    """Generate markdown report."""
    now = datetime.now()
    report = []
    
    report.append(f"# Presentation Structure Analysis ({now.strftime('%Y-%m-%d %H:%M %Z')})")
    report.append("")
    report.append("## Summary Statistics")
    report.append("")
    
    total_files = len(files_data)
    total_classes = sum(len(data['classes']) for data in files_data.values())
    total_functions = sum(len(data['functions']) for data in files_data.values())
    total_signals = sum(len(data['signals']) for data in files_data.values())
    total_lines = sum(data['lines'] for data in files_data.values())
    
    report.append(f"- **Total Python Files**: {total_files}")
    report.append(f"- **Total Classes**: {total_classes}")
    report.append(f"- **Total Functions**: {total_functions}")
    report.append(f"- **Total Signals**: {total_signals}")
    report.append(f"- **Total Lines of Code**: {total_lines:,}")
    report.append("")
    
    report.append("## Directory Structure")
    report.append("")
    report.append("```")
    report.append("presentation/")
    report.append("├── base/                     # Base classes and protocols")
    report.append("├── design_system/           # Design tokens and QSS")
    report.append("│   └── tokens/              # Color, spacing, status tokens")
    report.append("├── dialogs/                 # Dialog windows")
    report.append("│   └── result_detail/       # Test result detail dialog")
    report.append("├── navigation/              # Navigation router")
    report.append("├── services/                # Singleton services")
    report.append("├── styles/                  # Component styles")
    report.append("│   ├── components/          # Per-component QSS")
    report.append("│   ├── fonts/               # Font resources")
    report.append("│   └── helpers/             # Style utilities")
    report.append("├── views/                   # Legacy window views (deprecated)")
    report.append("├── widgets/                 # Reusable widgets")
    report.append("│   ├── display_area/        # Editor, console, AI panel")
    report.append("│   ├── sidebar/             # Sidebar components")
    report.append("│   └── status_view/         # Status display widgets")
    report.append("├── windows/                 # Per-window packages (MVVM)")
    report.append("│   ├── benchmarker/")
    report.append("│   ├── comparator/")
    report.append("│   ├── editor/")
    report.append("│   ├── help_center/")
    report.append("│   ├── main/")
    report.append("│   ├── results/")
    report.append("│   └── validator/")
    report.append("└── window_controller/       # Window management")
    report.append("```")
    report.append("")
    
    report.append("## Per-File Inventory")
    report.append("")
    
    # Sort files by path
    sorted_files = sorted(files_data.items())
    
    for filepath, data in sorted_files:
        report.append(f"### `{filepath}`")
        report.append("")
        
        if 'error' in data:
            report.append(f"**Error**: {data['error']}")
            report.append("")
            continue
        
        if data['classes']:
            report.append("**Classes:**")
            for cls in data['classes']:
                bases_str = f" extends {', '.join(cls['bases'])}" if cls['bases'] else ""
                report.append(f"- `{cls['name']}`{bases_str} (line {cls['line']})")
            report.append("")
        
        if data['functions']:
            report.append("**Functions:**")
            for func in data['functions'][:10]:  # Limit to first 10
                report.append(f"- `{func['name']}()` (line {func['line']})")
            if len(data['functions']) > 10:
                report.append(f"- *(+{len(data['functions']) - 10} more functions)*")
            report.append("")
        
        if data['signals']:
            report.append("**Signals:**")
            for sig in data['signals']:
                report.append(f"- `{sig['name']}` in `{sig['class']}` (line {sig['line']})")
            report.append("")
        
        # Add brief summary
        summary_parts = []
        if data['classes']:
            summary_parts.append(f"{len(data['classes'])} class{'es' if len(data['classes']) > 1 else ''}")
        if data['functions']:
            summary_parts.append(f"{len(data['functions'])} function{'s' if len(data['functions']) > 1 else ''}")
        if data['signals']:
            summary_parts.append(f"{len(data['signals'])} signal{'s' if len(data['signals']) > 1 else ''}")
        
        if summary_parts:
            report.append(f"*Summary: {', '.join(summary_parts)}, {data['lines']} lines*")
        else:
            report.append(f"*Summary: Module file, {data['lines']} lines*")
        report.append("")
    
    return "\n".join(report)

if __name__ == "__main__":
    print("Analyzing presentation structure...")
    files_data = analyze_presentation()
    report = generate_report(files_data)
    
    with open("temp_presentation_analysis.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"Analysis complete. {len(files_data)} files analyzed.")
    print("Report saved to temp_presentation_analysis.txt")
