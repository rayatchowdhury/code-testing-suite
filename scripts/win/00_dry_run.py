"""
Script 0: Dry Run
Shows what would happen without making changes.
"""

import csv
import json
from pathlib import Path
from collections import defaultdict

# Repo root
REPO_ROOT = Path(__file__).parent.parent.parent
REFACTOR_DIR = REPO_ROOT / "refactor"
RENAME_MAP_FILE = REFACTOR_DIR / "rename_map.csv"
TREE_FILE = REFACTOR_DIR / "current_tree.json"
IMPORT_GRAPH_FILE = REFACTOR_DIR / "import_graph.json"


def load_rename_map(phase_filter=None):
    """Load rename map, optionally filtered by phase."""
    moves = []
    
    if not RENAME_MAP_FILE.exists():
        print(f"ERROR: Rename map not found: {RENAME_MAP_FILE}")
        return moves
    
    with open(RENAME_MAP_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if phase_filter is None or row['phase'] == phase_filter:
                moves.append(row)
    
    return moves


def print_target_tree():
    """Print the target tree structure."""
    print("TARGET STRUCTURE")
    print("=" * 80)
    
    if not TREE_FILE.exists():
        print("Tree file not found")
        return
    
    data = json.loads(TREE_FILE.read_text(encoding='utf-8'))
    target = data.get('target_structure', '')
    
    print(target[:2000])  # Print first 2000 chars
    if len(target) > 2000:
        print("... (truncated)")
    print()


def print_move_summary(moves):
    """Print summary of planned moves."""
    print("PLANNED MOVES")
    print("=" * 80)
    
    # Group by phase
    by_phase = defaultdict(list)
    for move in moves:
        by_phase[move['phase']].append(move)
    
    for phase in sorted(by_phase.keys()):
        phase_moves = by_phase[phase]
        print(f"\n{phase}: {len(phase_moves)} moves")
        
        # Show first 5 from each phase
        for move in phase_moves[:5]:
            print(f"  {move['src_path']} → {move['dst_path']}")
        
        if len(phase_moves) > 5:
            print(f"  ... and {len(phase_moves) - 5} more")
    
    print()


def print_import_graph_delta(moves):
    """Print how imports will change."""
    print("IMPORT GRAPH IMPACT")
    print("=" * 80)
    
    if not IMPORT_GRAPH_FILE.exists():
        print("Import graph not found")
        return
    
    data = json.loads(IMPORT_GRAPH_FILE.read_text(encoding='utf-8'))
    metadata = data.get('metadata', {})
    
    print(f"Current state:")
    print(f"  Total Python files: {metadata.get('total_files', 'unknown')}")
    print(f"  Internal imports: {metadata.get('total_internal_imports', 'unknown')}")
    print(f"  External imports: {metadata.get('total_external_imports', 'unknown')}")
    
    print(f"\nFiles affected by moves: {len(moves)}")
    print(f"Estimated imports to rewrite: ~{len(moves) * 3}")  # Rough estimate
    print()


def print_risk_assessment(moves):
    """Print risk assessment."""
    print("RISK ASSESSMENT")
    print("=" * 80)
    
    risk_counts = defaultdict(int)
    for move in moves:
        risk_counts[move.get('risk', 'unknown')] += 1
    
    print("Moves by risk level:")
    for risk, count in sorted(risk_counts.items()):
        print(f"  {risk}: {count} moves")
    
    print("\nRecommendations:")
    print("  - Create git branch before starting")
    print("  - Run phases sequentially (P1 → P2 → P3 → P4)")
    print("  - Test after each phase")
    print("  - Keep legacy_aliases.py until Phase 4")
    print()


def main():
    """Main dry run function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dry run of presentation migration")
    parser.add_argument("--phase", help="Show specific phase only (P1, P2, P3, P4)")
    args = parser.parse_args()
    
    print("=" * 80)
    print("PRESENTATION LAYER MIGRATION - DRY RUN")
    print("=" * 80)
    print()
    
    # Print target tree
    print_target_tree()
    
    # Load moves
    moves = load_rename_map(args.phase)
    
    if not moves:
        print("No moves to display")
        return
    
    # Print summaries
    print_move_summary(moves)
    print_import_graph_delta(moves)
    print_risk_assessment(moves)
    
    print("=" * 80)
    print("DRY RUN COMPLETE - No files were modified")
    print("=" * 80)
    print()
    print("To proceed with migration:")
    print(f"  python scripts\\win\\01_apply_moves.py {f'--phase {args.phase}' if args.phase else ''}")
    print()


if __name__ == "__main__":
    main()
