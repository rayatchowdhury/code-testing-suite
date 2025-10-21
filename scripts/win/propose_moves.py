"""
Discovery Script 4: Move Planner
Generates rename_map.csv with all planned file moves.
Windows-compatible Python script.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Repo root
REPO_ROOT = Path(__file__).parent.parent.parent
PRESENTATION_ROOT = REPO_ROOT / "src" / "app" / "presentation"
OUTPUT_DIR = REPO_ROOT / "refactor"
TREE_FILE = OUTPUT_DIR / "current_tree.json"
STYLES_FILE = OUTPUT_DIR / "styles_widgets_analysis.json"
OUTPUT_CSV = OUTPUT_DIR / "rename_map.csv"


def load_discovery_data() -> Tuple[Dict, Dict]:
    """Load previously generated discovery data."""
    tree_data = {}
    styles_data = {}
    
    if TREE_FILE.exists():
        tree_data = json.loads(TREE_FILE.read_text(encoding="utf-8"))
    
    if STYLES_FILE.exists():
        styles_data = json.loads(STYLES_FILE.read_text(encoding="utf-8"))
    
    return tree_data, styles_data


def plan_style_moves(tree_data: Dict, styles_data: Dict) -> List[Dict]:
    """Plan Phase 1: Move all styles to design_system."""
    moves = []
    
    # Get legacy style files
    legacy_files = tree_data.get("legacy_locations", {})
    
    # Move files from styles/ directory
    for file_path in legacy_files.get("styles_directory", []):
        # Determine target path
        file_name = Path(file_path).name
        
        if "helper" in file_path.lower() or "inline" in file_path.lower():
            target = f"design_system\\styles\\{file_name}"
        elif "common" in file_path.lower():
            target = f"design_system\\styles\\{file_name}"
        elif "components" in file_path:
            # Extract component name
            parts = file_path.replace("/", "\\").split("\\")
            if "components" in parts:
                idx = parts.index("components")
                component_path = "\\".join(parts[idx+1:])
                target = f"design_system\\styles\\components\\{component_path}"
            else:
                target = f"design_system\\styles\\{file_name}"
        else:
            target = f"design_system\\styles\\{file_name}"
        
        moves.append({
            "src_path": file_path.replace("/", "\\"),
            "dst_path": target,
            "reason": "Consolidate styles to design_system",
            "phase": "P1",
            "risk": "medium"
        })
    
    return moves


def plan_navigation_moves(tree_data: Dict) -> List[Dict]:
    """Plan Phase 2: Move window_controller to navigation."""
    moves = []
    
    legacy_files = tree_data.get("legacy_locations", {})
    
    for file_path in legacy_files.get("window_controller", []):
        file_name = Path(file_path).name
        
        if file_name == "window_management.py":
            target = "navigation\\window_manager.py"
            reason = "Move WindowManager to navigation package"
        elif file_name == "base_window.py":
            # This will be deprecated in favor of ContentWindowBase
            target = f"_deprecated\\{file_name}"
            reason = "Deprecate in favor of ContentWindowBase"
        else:
            target = f"navigation\\{file_name}"
            reason = "Move to navigation package"
        
        moves.append({
            "src_path": file_path.replace("/", "\\"),
            "dst_path": target,
            "reason": reason,
            "phase": "P2",
            "risk": "high"
        })
    
    return moves


def plan_feature_pod_moves(styles_data: Dict) -> List[Dict]:
    """Plan Phase 3: Reorganize into feature pods."""
    moves = []
    
    # Get feature-local widgets
    feature_widgets = styles_data.get("widgets", {}).get("feature_local_widgets", [])
    
    for widget in feature_widgets:
        src_path = widget["file"].replace("/", "\\")
        widget_name = widget["name"]
        
        # Determine target feature based on location
        if "windows" in src_path:
            parts = src_path.split("\\")
            if "windows" in parts:
                idx = parts.index("windows")
                if idx + 1 < len(parts):
                    feature = parts[idx + 1]
                    target = f"windows\\{feature}\\widgets\\{Path(src_path).name}"
                    
                    moves.append({
                        "src_path": src_path,
                        "dst_path": target,
                        "reason": f"Move feature-local widget to {feature} pod",
                        "phase": "P3",
                        "risk": "low"
                    })
    
    return moves


def plan_cleanup_moves(tree_data: Dict) -> List[Dict]:
    """Plan Phase 4: Final cleanup and removals."""
    moves = []
    
    # Mark legacy directories for removal
    legacy_dirs = ["window_controller", "styles"]
    
    for dir_name in legacy_dirs:
        moves.append({
            "src_path": f"{dir_name}\\*",
            "dst_path": "_removed",
            "reason": f"Remove legacy {dir_name} directory",
            "phase": "P4",
            "risk": "low"
        })
    
    return moves


def main():
    """Main move planner."""
    print("=" * 80)
    print("MOVE PLANNER")
    print("=" * 80)
    print()
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load discovery data
    print("Loading discovery data...")
    tree_data, styles_data = load_discovery_data()
    
    # Plan moves for each phase
    print("Planning moves...")
    all_moves = []
    
    print("  Phase 1: Style consolidation...")
    p1_moves = plan_style_moves(tree_data, styles_data)
    all_moves.extend(p1_moves)
    print(f"    {len(p1_moves)} moves planned")
    
    print("  Phase 2: Navigation unification...")
    p2_moves = plan_navigation_moves(tree_data)
    all_moves.extend(p2_moves)
    print(f"    {len(p2_moves)} moves planned")
    
    print("  Phase 3: Feature pods...")
    p3_moves = plan_feature_pod_moves(styles_data)
    all_moves.extend(p3_moves)
    print(f"    {len(p3_moves)} moves planned")
    
    print("  Phase 4: Cleanup...")
    p4_moves = plan_cleanup_moves(tree_data)
    all_moves.extend(p4_moves)
    print(f"    {len(p4_moves)} moves planned")
    
    # Write CSV
    print(f"\nWriting {len(all_moves)} moves to CSV...")
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["src_path", "dst_path", "reason", "phase", "risk"])
        writer.writeheader()
        writer.writerows(all_moves)
    
    print(f"✓ Move plan complete. Output saved to: {OUTPUT_CSV}")
    
    # Summary by phase
    print("\nSummary by phase:")
    for phase in ["P1", "P2", "P3", "P4"]:
        count = sum(1 for m in all_moves if m["phase"] == phase)
        print(f"  {phase}: {count} moves")
    
    print()


if __name__ == "__main__":
    main()
