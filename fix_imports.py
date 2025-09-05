#!/usr/bin/env python3
"""
Script to fix all flat structure imports in src/app to relative imports
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix flat structure imports to relative imports in a single file"""
    if not file_path.suffix == '.py':
        return False
        
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Map of flat structure imports to relative imports
        # Calculate relative path based on file location
        src_app_path = Path("src/app")
        rel_path_to_src_app = os.path.relpath(src_app_path, file_path.parent)
        
        # Count dots needed for relative import based on depth
        file_relative_to_src_app = file_path.relative_to(src_app_path)
        depth = len(file_relative_to_src_app.parts) - 1  # -1 because file itself doesn't count
        dots = "." * (depth + 1) if depth >= 0 else ".."
        
        # Define replacement patterns - both top-level and indented imports
        replacements = [
            # Top-level imports (^from)
            (r'^from widgets\.', f'from {dots}widgets.'),
            (r'^from widgets import', f'from {dots}widgets import'),
            (r'^from views\.', f'from {dots}views.'),
            (r'^from views import', f'from {dots}views import'),
            (r'^from styles\.', f'from {dots}styles.'),
            (r'^from styles import', f'from {dots}styles import'),
            (r'^from utils\.', f'from {dots}utils.'),
            (r'^from utils import', f'from {dots}utils import'),
            (r'^from config\.', f'from {dots}config.'),
            (r'^from config import', f'from {dots}config import'),
            (r'^from constants\.', f'from {dots}constants.'),
            (r'^from constants import', f'from {dots}constants import'),
            (r'^from database\.', f'from {dots}database.'),
            (r'^from database import', f'from {dots}database import'),
            (r'^from ai\.', f'from {dots}ai.'),
            (r'^from ai import', f'from {dots}ai import'),
            (r'^from tools\.', f'from {dots}tools.'),
            (r'^from tools import', f'from {dots}tools import'),
            
            # Indented imports (local imports inside functions/methods)
            (r'^(\s+)from widgets\.', f'\\1from {dots}widgets.'),
            (r'^(\s+)from widgets import', f'\\1from {dots}widgets import'),
            (r'^(\s+)from views\.', f'\\1from {dots}views.'),
            (r'^(\s+)from views import', f'\\1from {dots}views import'),
            (r'^(\s+)from styles\.', f'\\1from {dots}styles.'),
            (r'^(\s+)from styles import', f'\\1from {dots}styles import'),
            (r'^(\s+)from utils\.', f'\\1from {dots}utils.'),
            (r'^(\s+)from utils import', f'\\1from {dots}utils import'),
            (r'^(\s+)from config\.', f'\\1from {dots}config.'),
            (r'^(\s+)from config import', f'\\1from {dots}config import'),
            (r'^(\s+)from constants\.', f'\\1from {dots}constants.'),
            (r'^(\s+)from constants import', f'\\1from {dots}constants import'),
            (r'^(\s+)from database\.', f'\\1from {dots}database.'),
            (r'^(\s+)from database import', f'\\1from {dots}database import'),
            (r'^(\s+)from ai\.', f'\\1from {dots}ai.'),
            (r'^(\s+)from ai import', f'\\1from {dots}ai import'),
            (r'^(\s+)from tools\.', f'\\1from {dots}tools.'),
            (r'^(\s+)from tools import', f'\\1from {dots}tools import'),
        ]
        
        # Apply replacements
        modified = False
        for pattern, replacement in replacements:
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            if new_content != content:
                content = new_content
                modified = True
        
        if modified:
            file_path.write_text(content, encoding='utf-8')
            print(f"✅ Fixed imports in: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix all imports in src/app"""
    src_app_dir = Path("src/app")
    if not src_app_dir.exists():
        print("❌ src/app directory not found!")
        return
    
    print("🔧 Fixing flat structure imports to relative imports...")
    
    files_processed = 0
    files_modified = 0
    
    # Process all Python files in src/app
    for py_file in src_app_dir.rglob("*.py"):
        files_processed += 1
        if fix_imports_in_file(py_file):
            files_modified += 1
    
    print(f"\n📊 Summary:")
    print(f"   Files processed: {files_processed}")
    print(f"   Files modified: {files_modified}")
    print(f"✅ Import fixing complete!")

if __name__ == "__main__":
    main()
