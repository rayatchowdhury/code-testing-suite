"""
Codemod: QSS Path Fixup
Updates resource paths to design_system assets.
"""

import re
from pathlib import Path
from typing import List, Tuple

# Repo root
REPO_ROOT = Path(__file__).parent.parent.parent
PRESENTATION_ROOT = REPO_ROOT / "src" / "app" / "presentation"


def fix_qss_paths_in_file(file_path: Path) -> int:
    """
    Fix QSS resource paths in a Python file.
    Returns number of changes made.
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        changes = 0
        
        # Pattern 1: setStyleSheet with file paths
        # Example: widget.setStyleSheet("file:///path/to/styles/...")
        content = re.sub(
            r'(setStyleSheet\(["\'])file:///.*?/styles/',
            r'\1file:///design_system/styles/',
            content
        )
        
        # Pattern 2: QSS file loads
        # Example: QFile(":/styles/...")
        content = re.sub(
            r'(QFile\(["\']):/styles/',
            r'\1:/design_system/styles/',
            content
        )
        
        # Pattern 3: Resource paths in comments or strings
        content = re.sub(
            r'(["\'])src/app/presentation/styles/',
            r'\1src/app/presentation/design_system/styles/',
            content
        )
        
        # Pattern 4: Icon paths
        content = re.sub(
            r'(["\'])icons/',
            r'\1design_system/assets/icons/',
            content
        )
        
        # Pattern 5: Font paths
        content = re.sub(
            r'(["\'])fonts/',
            r'\1design_system/assets/fonts/',
            content
        )
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            changes = content.count('\n') - original_content.count('\n') + 1
        
        return changes
    
    except Exception as e:
        print(f"ERROR processing {file_path}: {e}")
        return 0


def fix_all_qss_paths(root: Path) -> Tuple[int, int]:
    """Fix QSS paths in all Python files."""
    total_files = 0
    total_changes = 0
    
    for py_file in root.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        total_files += 1
        changes = fix_qss_paths_in_file(py_file)
        
        if changes > 0:
            rel_path = py_file.relative_to(root)
            print(f"  ✓ {rel_path}: {changes} paths fixed")
            total_changes += 1
    
    return total_files, total_changes


def main():
    """Main QSS path fixer."""
    print("=" * 80)
    print("QSS PATH FIXUP")
    print("=" * 80)
    print()
    
    print("Fixing resource paths...")
    total_files, files_changed = fix_all_qss_paths(PRESENTATION_ROOT)
    
    print(f"\n✓ QSS path fixup complete")
    print(f"  Files processed: {total_files}")
    print(f"  Files changed: {files_changed}")
    print()


if __name__ == "__main__":
    main()
