"""
Codemod: __init__ Exports Fixup
Ensures new package __init__.py files export the expected symbols.
"""

import ast
from pathlib import Path
from typing import Dict, List, Set

# Repo root
REPO_ROOT = Path(__file__).parent.parent.parent
PRESENTATION_ROOT = REPO_ROOT / "src" / "app" / "presentation"


# Define expected exports for key packages
EXPECTED_EXPORTS = {
    "design_system/styles": [
        "get_style",
        "COMMON_STYLES",
        "apply_inline_style",
    ],
    "design_system/tokens": [
        "COLORS",
        "SPACING",
        "STATUS_COLORS",
    ],
    "navigation": [
        "NavigationRouter",
        "WindowManager",
        "Routes",
    ],
    "base": [
        "WindowBase",
        "ContentWindowBase",
        "TestWindowBase",
    ],
    "shared/components/editor": [
        "CodeEditor",
        "EditorWidget",
        "EditorTabWidget",
        "SyntaxHighlighter",
    ],
    "shared/components/console": [
        "ConsoleWidget",
    ],
    "shared/components/sidebar": [
        "Sidebar",
        "TestCountSlider",
        "LimitsInput",
    ],
    "shared/components/status_view": [
        "StatusView",
        "StatusViewModel",
    ],
}


def extract_exports_from_file(file_path: Path) -> Set[str]:
    """Extract exported symbols from a Python file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
        
        exports = set()
        
        # Look for class and function definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                exports.add(node.name)
            elif isinstance(node, ast.FunctionDef):
                if not node.name.startswith("_"):
                    exports.add(node.name)
            elif isinstance(node, ast.Assign):
                # Look for variable assignments
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id.isupper():  # Constants
                            exports.add(target.id)
        
        return exports
    
    except:
        return set()


def build_init_content(package_path: Path, expected: List[str]) -> str:
    """Build __init__.py content with proper exports."""
    
    # Find all Python files in the package
    py_files = [f for f in package_path.glob("*.py") if f.name != "__init__.py"]
    
    imports = []
    all_exports = []
    
    for py_file in py_files:
        module_name = py_file.stem
        file_exports = extract_exports_from_file(py_file)
        
        # Filter to expected exports
        exports_to_import = [e for e in expected if e in file_exports]
        
        if exports_to_import:
            imports.append(f"from .{module_name} import {', '.join(exports_to_import)}")
            all_exports.extend(exports_to_import)
    
    # Build content
    content = '"""Package exports."""\n\n'
    content += "\n".join(imports)
    content += "\n\n"
    content += f"__all__ = [\n"
    for export in sorted(all_exports):
        content += f'    "{export}",\n'
    content += "]\n"
    
    return content


def fix_init_exports(root: Path) -> int:
    """Fix __init__.py exports in key packages."""
    fixed_count = 0
    
    for package_rel, expected in EXPECTED_EXPORTS.items():
        package_path = root / package_rel.replace("/", "\\")
        init_file = package_path / "__init__.py"
        
        if not package_path.exists():
            print(f"  ⚠ Package not found: {package_rel}")
            continue
        
        # Build new content
        new_content = build_init_content(package_path, expected)
        
        # Write if different
        if init_file.exists():
            current_content = init_file.read_text(encoding='utf-8')
            if current_content != new_content:
                init_file.write_text(new_content, encoding='utf-8')
                print(f"  ✓ Updated: {package_rel}/__init__.py")
                fixed_count += 1
        else:
            # Create new __init__.py
            init_file.write_text(new_content, encoding='utf-8')
            print(f"  ✓ Created: {package_rel}/__init__.py")
            fixed_count += 1
    
    return fixed_count


def main():
    """Main __init__ exports fixer."""
    print("=" * 80)
    print("__init__ EXPORTS FIXUP")
    print("=" * 80)
    print()
    
    print("Fixing package exports...")
    fixed_count = fix_init_exports(PRESENTATION_ROOT)
    
    print(f"\n✓ __init__ exports fixup complete")
    print(f"  Packages updated: {fixed_count}")
    print()


if __name__ == "__main__":
    main()
