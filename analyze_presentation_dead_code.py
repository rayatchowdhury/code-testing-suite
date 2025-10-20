"""
Analyze presentation layer for dead code - unused functions, methods, and classes.
"""
import ast
import os
from pathlib import Path
from collections import defaultdict

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.definitions = defaultdict(list)  # {name: [(file, line, type)]}
        self.calls = defaultdict(list)  # {name: [(file, line)]}
        self.current_file = None
        self.current_class = None
        
    def visit_FunctionDef(self, node):
        func_type = "method" if self.current_class else "function"
        full_name = f"{self.current_class}.{node.name}" if self.current_class else node.name
        
        # Skip special methods and abstract methods
        if not node.name.startswith('__'):
            self.definitions[full_name].append((self.current_file, node.lineno, func_type))
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node.name
        self.definitions[node.name].append((self.current_file, node.lineno, "class"))
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_Call(self, node):
        # Track function/method calls
        if isinstance(node.func, ast.Name):
            self.calls[node.func.id].append((self.current_file, node.lineno))
        elif isinstance(node.func, ast.Attribute):
            self.calls[node.func.attr].append((self.current_file, node.lineno))
        self.generic_visit(node)
    
    def visit_Attribute(self, node):
        # Track attribute access (method/property access)
        if isinstance(node.attr, str):
            self.calls[node.attr].append((self.current_file, node.lineno))
        self.generic_visit(node)

def analyze_directory(directory):
    analyzer = CodeAnalyzer()
    
    for root, dirs, files in os.walk(directory):
        # Skip __pycache__ and test directories
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'tests', '.pytest_cache']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    tree = ast.parse(content, filename=filepath)
                    analyzer.current_file = filepath
                    analyzer.visit(tree)
                except (SyntaxError, UnicodeDecodeError) as e:
                    print(f"Error parsing {filepath}: {e}")
    
    return analyzer

def find_unused_code(analyzer):
    """Find definitions that are never called/used."""
    unused = []
    
    for name, definitions in analyzer.definitions.items():
        # Skip special cases
        if name.startswith('_') and not name.endswith('_'):  # Private but not special
            continue
        if name in ['main', 'setup', 'teardown']:  # Common entry points
            continue
        
        # Check if this name is ever called
        calls = analyzer.calls.get(name, [])
        
        # For methods, also check base name (without class prefix)
        if '.' in name:
            base_name = name.split('.')[-1]
            calls.extend(analyzer.calls.get(base_name, []))
        
        # If defined but never called (excluding files where it's defined)
        if len(calls) == 0:
            for file, line, def_type in definitions:
                unused.append({
                    'name': name,
                    'type': def_type,
                    'file': file,
                    'line': line,
                    'calls': len(calls)
                })
        elif len(calls) < 2:  # Called only once or twice - potentially unused
            for file, line, def_type in definitions:
                # Check if calls are only in the same file (self-contained)
                external_calls = [c for c in calls if c[0] != file]
                if len(external_calls) == 0:
                    unused.append({
                        'name': name,
                        'type': def_type,
                        'file': file,
                        'line': line,
                        'calls': len(calls),
                        'note': 'Only called internally'
                    })
    
    return unused

def main():
    presentation_dir = r"src\app\presentation"
    
    print("🔍 Analyzing presentation layer for dead code...\n")
    print("=" * 80)
    
    analyzer = analyze_directory(presentation_dir)
    unused = find_unused_code(analyzer)
    
    # Group by file
    by_file = defaultdict(list)
    for item in unused:
        rel_path = item['file'].replace(presentation_dir, '').replace('\\', '/').lstrip('/')
        by_file[rel_path].append(item)
    
    # Sort and display
    total_unused = 0
    for filepath in sorted(by_file.keys()):
        items = by_file[filepath]
        print(f"\n📄 {filepath}")
        print("-" * 80)
        
        for item in sorted(items, key=lambda x: x['line']):
            total_unused += 1
            note = f" ({item.get('note', '')})" if 'note' in item else ""
            print(f"  Line {item['line']:4d}: {item['type']:8s} '{item['name']}' - {item['calls']} calls{note}")
    
    print("\n" + "=" * 80)
    print(f"📊 Total potentially unused items: {total_unused}")
    print("\n💡 Note: This is a heuristic analysis. Some items may be:")
    print("   - Used dynamically (getattr, signals, etc.)")
    print("   - Template methods meant to be overridden")
    print("   - Qt framework callbacks (slots, event handlers)")
    print("   - Entry points or hooks")

if __name__ == "__main__":
    main()
