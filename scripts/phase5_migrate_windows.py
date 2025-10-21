"""
Phase 5 Migration Script
Automates the migration of windows from views/ to windows/ structure.
"""

import subprocess
import os
from pathlib import Path

# Window migration mappings
WINDOWS_TO_MIGRATE = [
    {
        "name": "editor",
        "source_dir": "src/app/presentation/views/code_editor",
        "source_file": "code_editor_window.py",
        "has_widgets": True,
        "widget_files": []  # Will move all files except main window
    },
    {
        "name": "benchmarker",
        "source_dir": "src/app/presentation/views/benchmarker",
        "source_file": "benchmarker_window.py",
        "has_widgets": False,
    },
    {
        "name": "comparator",
        "source_dir": "src/app/presentation/views/comparator",
        "source_file": "comparator_window.py",
        "has_widgets": False,
    },
    {
        "name": "validator",
        "source_dir": "src/app/presentation/views/validator",
        "source_file": "validator_window.py",
        "has_widgets": False,
    },
    {
        "name": "results",
        "source_dir": "src/app/presentation/views/results",
        "source_file": "results_window.py",
        "has_widgets": True,
        "widget_files": ["results_widget.py"]
    },
    {
        "name": "help_center",
        "source_dir": "src/app/presentation/views/help_center",
        "source_file": "help_center_window.py",
        "has_widgets": False,
    },
]

def run_git_command(cmd):
    """Run a git command and return the result."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(f"Success: {result.stdout}")
    return result.returncode == 0

def migrate_window(window_info):
    """Migrate a single window to the new structure."""
    name = window_info["name"]
    source_dir = window_info["source_dir"]
    source_file = window_info["source_file"]
    
    print(f"\n{'='*60}")
    print(f"Migrating {name} window...")
    print(f"{'='*60}")
    
    # Create target directory
    target_dir = f"src/app/presentation/windows/{name}"
    
    # Move main window file
    source_path = f"{source_dir}/{source_file}"
    target_path = f"{target_dir}/view.py"
    
    print(f"Moving {source_file} -> view.py")
    if not run_git_command(f'git mv "{source_path}" "{target_path}"'):
        print(f"Failed to move {source_file}")
        return False
    
    # Handle widgets if present
    if window_info.get("has_widgets", False):
        widget_dir = f"{target_dir}/widgets"
        os.makedirs(widget_dir, exist_ok=True)
        
        # Get all Python files in source directory except __init__.py and the main window file
        source_path_obj = Path(source_dir)
        if source_path_obj.exists():
            for py_file in source_path_obj.glob("*.py"):
                if py_file.name not in ["__init__.py", source_file]:
                    print(f"Moving {py_file.name} to widgets/")
                    run_git_command(f'git mv "{py_file}" "{widget_dir}/{py_file.name}"')
    
    return True

def main():
    """Main migration script."""
    print("Phase 5: Windows Migration Script")
    print("=" * 60)
    
    for window in WINDOWS_TO_MIGRATE:
        migrate_window(window)
    
    print("\n" + "="*60)
    print("Migration complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Create __init__.py files for each window")
    print("2. Update imports using ruff")
    print("3. Run tests")

if __name__ == "__main__":
    main()
