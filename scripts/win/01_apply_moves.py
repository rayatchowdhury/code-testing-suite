"""
Script 1: Apply Moves
Physically moves files according to rename_map.csv.
Creates necessary directories and __init__.py files.
"""

import csv
import shutil
from pathlib import Path
from collections import defaultdict

# Repo root
REPO_ROOT = Path(__file__).parent.parent.parent
PRESENTATION_ROOT = REPO_ROOT / "src" / "app" / "presentation"
REFACTOR_DIR = REPO_ROOT / "refactor"
RENAME_MAP_FILE = REFACTOR_DIR / "rename_map.csv"


def load_moves(phase_filter=None):
    """Load moves from CSV, optionally filtered by phase."""
    moves = []
    
    if not RENAME_MAP_FILE.exists():
        print(f"ERROR: Rename map not found: {RENAME_MAP_FILE}")
        return moves
    
    with open(RENAME_MAP_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if phase_filter is None or row['phase'] == phase_filter:
                # Skip removal operations for now
                if row['dst_path'] != '_removed' and '*' not in row['src_path']:
                    moves.append(row)
    
    return moves


def apply_move(src_rel: str, dst_rel: str, dry_run=False):
    """
    Apply a single file move.
    
    Args:
        src_rel: Source path relative to presentation root
        dst_rel: Destination path relative to presentation root
        dry_run: If True, don't actually move files
    
    Returns:
        True if successful, False otherwise
    """
    src_path = PRESENTATION_ROOT / src_rel.replace("/", "\\")
    dst_path = PRESENTATION_ROOT / dst_rel.replace("/", "\\")
    
    # Check source exists
    if not src_path.exists():
        print(f"  ⚠ Source not found: {src_rel}")
        return False
    
    # Create destination directory
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    
    if dry_run:
        print(f"  [DRY RUN] Would move: {src_rel} → {dst_rel}")
        return True
    
    try:
        # Move file
        shutil.move(str(src_path), str(dst_path))
        print(f"  ✓ Moved: {src_rel} → {dst_rel}")
        return True
    except Exception as e:
        print(f"  ✗ ERROR moving {src_rel}: {e}")
        return False


def ensure_init_files(root: Path, dry_run=False):
    """Ensure all package directories have __init__.py files."""
    created = 0
    
    for dir_path in root.rglob("*"):
        if dir_path.is_dir() and dir_path.name != "__pycache__":
            init_file = dir_path / "__init__.py"
            
            if not init_file.exists():
                # Check if directory has Python files
                has_py_files = any(dir_path.glob("*.py"))
                
                if has_py_files:
                    if dry_run:
                        rel_path = dir_path.relative_to(root)
                        print(f"  [DRY RUN] Would create: {rel_path}/__init__.py")
                    else:
                        init_file.write_text('"""Package exports."""\n', encoding='utf-8')
                        rel_path = dir_path.relative_to(root)
                        print(f"  ✓ Created: {rel_path}/__init__.py")
                    created += 1
    
    return created


def cleanup_empty_dirs(root: Path, dry_run=False):
    """Remove empty directories after moves."""
    removed = 0
    
    # Walk bottom-up to handle nested empty dirs
    for dir_path in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if dir_path.is_dir() and dir_path.name != "__pycache__":
            # Check if empty (no files, only __pycache__ if any)
            contents = list(dir_path.iterdir())
            is_empty = len(contents) == 0 or (len(contents) == 1 and contents[0].name == "__pycache__")
            
            if is_empty:
                if dry_run:
                    rel_path = dir_path.relative_to(root)
                    print(f"  [DRY RUN] Would remove empty dir: {rel_path}")
                else:
                    try:
                        # Remove __pycache__ first if it exists
                        pycache = dir_path / "__pycache__"
                        if pycache.exists():
                            shutil.rmtree(pycache)
                        
                        # Remove directory
                        dir_path.rmdir()
                        rel_path = dir_path.relative_to(root)
                        print(f"  ✓ Removed empty dir: {rel_path}")
                        removed += 1
                    except Exception as e:
                        print(f"  ⚠ Could not remove {dir_path}: {e}")
    
    return removed


def main():
    """Main move application function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Apply file moves for presentation migration")
    parser.add_argument("--phase", help="Apply moves for specific phase only (P1, P2, P3, P4)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without making changes")
    args = parser.parse_args()
    
    print("=" * 80)
    print("APPLY FILE MOVES")
    print("=" * 80)
    print()
    
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified\n")
    
    # Load moves
    moves = load_moves(args.phase)
    
    if not moves:
        print("No moves to apply")
        return
    
    print(f"Loaded {len(moves)} moves{f' for phase {args.phase}' if args.phase else ''}\n")
    
    # Apply moves
    print("Applying moves...")
    successful = 0
    failed = 0
    
    for move in moves:
        src = move['src_path']
        dst = move['dst_path']
        
        if apply_move(src, dst, args.dry_run):
            successful += 1
        else:
            failed += 1
    
    print(f"\nMoves: {successful} successful, {failed} failed")
    
    # Ensure __init__.py files
    if not args.dry_run:
        print("\nEnsuring __init__.py files...")
        created = ensure_init_files(PRESENTATION_ROOT, args.dry_run)
        print(f"Created {created} __init__.py files")
    
    # Cleanup empty directories
    if not args.dry_run:
        print("\nCleaning up empty directories...")
        removed = cleanup_empty_dirs(PRESENTATION_ROOT, args.dry_run)
        print(f"Removed {removed} empty directories")
    
    print("\n" + "=" * 80)
    if args.dry_run:
        print("DRY RUN COMPLETE - No files were modified")
    else:
        print("MOVES APPLIED SUCCESSFULLY")
    print("=" * 80)
    print()
    
    if not args.dry_run:
        print("Next step:")
        print(f"  python scripts\\win\\02_run_codemods.py {f'--phase {args.phase}' if args.phase else ''}")
    print()


if __name__ == "__main__":
    main()
