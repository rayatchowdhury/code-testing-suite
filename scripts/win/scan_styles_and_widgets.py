"""
Discovery Script 3: Styles and Widgets Scanner
Finds all style files, style imports, and classifies widgets as shared vs feature-local.
Windows-compatible Python script.
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

# Repo root
REPO_ROOT = Path(__file__).parent.parent.parent
PRESENTATION_ROOT = REPO_ROOT / "src" / "app" / "presentation"
OUTPUT_DIR = REPO_ROOT / "refactor"
OUTPUT_FILE = OUTPUT_DIR / "styles_widgets_analysis.json"


class ClassVisitor(ast.NodeVisitor):
    """AST visitor to extract class definitions and their bases."""
    
    def __init__(self):
        self.classes = []
    
    def visit_ClassDef(self, node):
        """Extract class name and base classes."""
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                # Handle module.ClassName
                bases.append(f"{ast.unparse(base.value)}.{base.attr}")
        
        self.classes.append({
            "name": node.name,
            "bases": bases,
            "line": node.lineno
        })
        self.generic_visit(node)


def extract_classes(file_path: Path) -> List[Dict]:
    """Extract class definitions from a Python file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))
        
        visitor = ClassVisitor()
        visitor.visit(tree)
        
        return visitor.classes
    except:
        return []


def find_style_files(root: Path) -> Dict[str, List[str]]:
    """Find all .qss files and Python files containing styles."""
    styles = {
        "qss_files": [],
        "style_py_files": [],
        "inline_style_usage": []
    }
    
    # Find .qss files
    for qss_file in root.rglob("*.qss"):
        rel_path = str(qss_file.relative_to(root))
        styles["qss_files"].append(rel_path)
    
    # Find Python files with "style" in name or path
    for py_file in root.rglob("*.py"):
        rel_path = str(py_file.relative_to(root))
        
        if "style" in rel_path.lower():
            styles["style_py_files"].append(rel_path)
        
        # Check for setStyleSheet usage
        try:
            content = py_file.read_text(encoding="utf-8")
            if "setStyleSheet" in content or "QSS" in content:
                styles["inline_style_usage"].append(rel_path)
        except:
            pass
    
    return styles


def classify_widgets(root: Path) -> Dict[str, List[Dict]]:
    """Classify widgets as shared (≥2 features) or feature-local."""
    
    # Widget base classes that indicate a widget
    WIDGET_BASES = {
        "QWidget", "QMainWindow", "QDialog", "QFrame",
        "QPushButton", "QLabel", "QLineEdit", "QTextEdit",
        "QPlainTextEdit", "QTabWidget", "QSplitter",
        "QScrollArea", "QGroupBox", "QListWidget", "QTreeWidget"
    }
    
    widgets = []
    
    for py_file in root.rglob("*.py"):
        # Skip __pycache__
        if "__pycache__" in str(py_file):
            continue
        
        rel_path = str(py_file.relative_to(root))
        classes = extract_classes(py_file)
        
        for cls in classes:
            # Check if it's a widget
            is_widget = any(base in str(cls["bases"]) for base in WIDGET_BASES)
            is_widget = is_widget or "Widget" in cls["name"] or "Window" in cls["name"]
            
            if is_widget:
                # Determine location
                location = "unknown"
                if "widgets" in rel_path:
                    location = "widgets"
                elif "windows" in rel_path:
                    location = "windows"
                elif "shared" in rel_path:
                    location = "shared"
                elif "dialogs" in rel_path:
                    location = "dialogs"
                
                widgets.append({
                    "name": cls["name"],
                    "file": rel_path,
                    "location": location,
                    "bases": cls["bases"]
                })
    
    # Classify by usage
    widget_usage = defaultdict(set)
    
    # Simple heuristic: widgets in shared/ or widgets/ are potentially shared
    shared_widgets = []
    feature_local_widgets = []
    
    for widget in widgets:
        if widget["location"] in ["shared", "widgets"]:
            shared_widgets.append(widget)
        elif widget["location"] in ["windows", "dialogs"]:
            # These are likely feature-local
            feature_local_widgets.append(widget)
        else:
            # Need more analysis
            shared_widgets.append(widget)
    
    return {
        "all_widgets": widgets,
        "shared_widgets": shared_widgets,
        "feature_local_widgets": feature_local_widgets,
        "widget_count": len(widgets)
    }


def map_style_imports(root: Path) -> Dict[str, List[str]]:
    """Map which files import styles from where."""
    style_imports = defaultdict(list)
    
    for py_file in root.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        rel_path = str(py_file.relative_to(root))
        
        try:
            content = py_file.read_text(encoding="utf-8")
            
            # Look for style imports
            if "from" in content and "style" in content.lower():
                lines = content.split("\n")
                for line in lines:
                    line_stripped = line.strip()
                    if line_stripped.startswith("from") and "style" in line_stripped.lower():
                        style_imports[rel_path].append(line_stripped)
        except:
            pass
    
    return dict(style_imports)


def main():
    """Main styles and widgets scanner."""
    print("=" * 80)
    print("STYLES AND WIDGETS SCANNER")
    print("=" * 80)
    print()
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Find style files
    print("Scanning for style files...")
    styles = find_style_files(PRESENTATION_ROOT)
    print(f"  QSS files: {len(styles['qss_files'])}")
    print(f"  Python style files: {len(styles['style_py_files'])}")
    print(f"  Files using inline styles: {len(styles['inline_style_usage'])}")
    
    # Classify widgets
    print("\nClassifying widgets...")
    widgets = classify_widgets(PRESENTATION_ROOT)
    print(f"  Total widgets found: {widgets['widget_count']}")
    print(f"  Shared widgets: {len(widgets['shared_widgets'])}")
    print(f"  Feature-local widgets: {len(widgets['feature_local_widgets'])}")
    
    # Map style imports
    print("\nMapping style imports...")
    style_imports = map_style_imports(PRESENTATION_ROOT)
    print(f"  Files importing styles: {len(style_imports)}")
    
    # Build output
    output = {
        "metadata": {
            "scan_date": "2025-10-21"
        },
        "styles": styles,
        "widgets": widgets,
        "style_imports": style_imports
    }
    
    # Save to JSON
    OUTPUT_FILE.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\n✓ Styles and widgets analysis complete. Output saved to: {OUTPUT_FILE}")
    
    # Print widget details
    print("\nShared widgets (sample):")
    for widget in widgets['shared_widgets'][:10]:
        print(f"  {widget['name']} in {widget['file']}")
    
    print()


if __name__ == "__main__":
    main()
