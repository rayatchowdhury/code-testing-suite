"""
Discovery Script 1: Tree Analysis
Discovers current presentation layer structure and compares with target.
Windows-compatible Python script.
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

# Repo root
REPO_ROOT = Path(__file__).parent.parent.parent
PRESENTATION_ROOT = REPO_ROOT / "src" / "app" / "presentation"
TARGET_TREE_FILE = REPO_ROOT / "new_presentation.txt"
OUTPUT_DIR = REPO_ROOT / "refactor"
OUTPUT_FILE = OUTPUT_DIR / "current_tree.json"


def discover_files(root: Path) -> Dict[str, List[str]]:
    """Discover all files under presentation layer."""
    files_by_type = defaultdict(list)
    
    if not root.exists():
        print(f"ERROR: Presentation root not found: {root}")
        return {}
    
    for file_path in root.rglob("*"):
        if file_path.is_file():
            rel_path = file_path.relative_to(root)
            suffix = file_path.suffix.lower()
            
            if suffix == ".py":
                files_by_type["python"].append(str(rel_path))
            elif suffix == ".qss":
                files_by_type["styles"].append(str(rel_path))
            elif suffix in [".png", ".svg", ".jpg", ".jpeg", ".ico"]:
                files_by_type["assets"].append(str(rel_path))
            elif suffix in [".ttf", ".otf", ".woff", ".woff2"]:
                files_by_type["fonts"].append(str(rel_path))
            else:
                files_by_type["other"].append(str(rel_path))
    
    return dict(files_by_type)


def analyze_directory_structure(root: Path) -> Dict[str, int]:
    """Count files per top-level directory."""
    dir_counts = defaultdict(int)
    
    for file_path in root.rglob("*.py"):
        rel_path = file_path.relative_to(root)
        parts = rel_path.parts
        
        if len(parts) > 1:
            top_dir = parts[0]
            dir_counts[top_dir] += 1
        else:
            dir_counts["__root__"] += 1
    
    return dict(dir_counts)


def identify_legacy_locations(files: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Identify files in legacy locations that need migration."""
    legacy = defaultdict(list)
    
    for py_file in files.get("python", []):
        path_lower = py_file.lower()
        
        # Legacy window_controller
        if "window_controller" in path_lower:
            legacy["window_controller"].append(py_file)
        
        # Legacy styles directory (should move to design_system)
        if py_file.startswith("styles\\") or py_file.startswith("styles/"):
            legacy["styles_directory"].append(py_file)
        
        # Styles scattered in widgets
        if "widgets" in path_lower and "style" in path_lower:
            legacy["widgets_styles"].append(py_file)
        
        # Styles scattered in windows
        if "windows" in path_lower and "style" in path_lower:
            legacy["windows_styles"].append(py_file)
    
    return dict(legacy)


def load_target_structure() -> str:
    """Load the target structure from new_presentation.txt."""
    if TARGET_TREE_FILE.exists():
        try:
            return TARGET_TREE_FILE.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                return TARGET_TREE_FILE.read_text(encoding="utf-16")
            except:
                return TARGET_TREE_FILE.read_text(encoding="latin-1")
    return "TARGET STRUCTURE NOT FOUND"


def main():
    """Main discovery function."""
    print("=" * 80)
    print("PRESENTATION LAYER DISCOVERY")
    print("=" * 80)
    print()
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Discover current files
    print(f"Scanning: {PRESENTATION_ROOT}")
    files_by_type = discover_files(PRESENTATION_ROOT)
    
    # Count files
    total_files = sum(len(files) for files in files_by_type.values())
    print(f"\nTotal files found: {total_files}")
    print(f"  Python files: {len(files_by_type.get('python', []))}")
    print(f"  QSS files: {len(files_by_type.get('styles', []))}")
    print(f"  Asset files: {len(files_by_type.get('assets', []))}")
    print(f"  Font files: {len(files_by_type.get('fonts', []))}")
    print(f"  Other files: {len(files_by_type.get('other', []))}")
    
    # Directory structure
    print("\nFiles per top-level directory:")
    dir_counts = analyze_directory_structure(PRESENTATION_ROOT)
    for dir_name, count in sorted(dir_counts.items()):
        print(f"  {dir_name}: {count} files")
    
    # Legacy locations
    print("\nLegacy locations requiring migration:")
    legacy = identify_legacy_locations(files_by_type)
    for category, files in sorted(legacy.items()):
        print(f"  {category}: {len(files)} files")
    
    # Load target structure
    target_structure = load_target_structure()
    
    # Build output
    output = {
        "metadata": {
            "repo_root": str(REPO_ROOT),
            "presentation_root": str(PRESENTATION_ROOT),
            "total_files": total_files,
            "scan_date": "2025-10-21"
        },
        "files_by_type": files_by_type,
        "directory_counts": dir_counts,
        "legacy_locations": legacy,
        "target_structure": target_structure
    }
    
    # Save to JSON
    OUTPUT_FILE.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\n✓ Discovery complete. Output saved to: {OUTPUT_FILE}")
    print()


if __name__ == "__main__":
    main()
