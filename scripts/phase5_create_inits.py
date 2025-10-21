"""
Phase 5: Create __init__.py files for all migrated windows
"""

import os

WINDOW_CONFIGS = [
    {
        "name": "editor",
        "class_name": "CodeEditorWindow",
        "description": "Code Editor Window with syntax highlighting and file management",
    },
    {
        "name": "benchmarker",
        "class_name": "BenchmarkerWindow",
        "description": "Benchmarker Window for performance testing",
    },
    {
        "name": "comparator",
        "class_name": "ComparatorWindow",
        "description": "Comparator Window for output comparison testing",
    },
    {
        "name": "validator",
        "class_name": "ValidatorWindow",
        "description": "Validator Window for solution validation",
    },
    {
        "name": "results",
        "class_name": "ResultsWindow",
        "description": "Results Window for test history and detailed views",
    },
    {
        "name": "help_center",
        "class_name": "HelpCenterWindow",
        "description": "Help Center Window with documentation and tutorials",
    },
]

def create_init_file(window_config):
    """Create __init__.py for a window."""
    name = window_config["name"]
    class_name = window_config["class_name"]
    description = window_config["description"]
    
    target_dir = f"src/app/presentation/windows/{name}"
    init_file = f"{target_dir}/__init__.py"
    
    content = f'''"""
{class_name.replace("Window", " Window")} Package

Phase 5: Per-Window Packaging
{description}
"""

from src.app.presentation.windows.{name}.view import {class_name}

__all__ = ["{class_name}"]
'''
    
    with open(init_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Created {init_file}")
    
    # Create widgets __init__.py if widgets directory exists
    widgets_dir = f"{target_dir}/widgets"
    if os.path.exists(widgets_dir):
        widgets_init = f"{widgets_dir}/__init__.py"
        with open(widgets_init, "w", encoding="utf-8") as f:
            f.write(f"# {class_name} widgets\n")
        print(f"Created {widgets_init}")

def main():
    """Create all __init__.py files."""
    print("Creating __init__.py files for all windows...")
    for config in WINDOW_CONFIGS:
        create_init_file(config)
    print("\nDone!")

if __name__ == "__main__":
    main()
