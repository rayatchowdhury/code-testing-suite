"""
Codemod: Import Rewrite Engine
Rewrites import statements based on rename_map.csv.
Uses libcst for safe AST transformations.
"""

import csv
import libcst as cst
from pathlib import Path
from typing import Dict, List, Set, Tuple
import sys

# Repo root
REPO_ROOT = Path(__file__).parent.parent.parent
PRESENTATION_ROOT = REPO_ROOT / "src" / "app" / "presentation"
RENAME_MAP_FILE = REPO_ROOT / "refactor" / "rename_map.csv"


class ImportRewriter(cst.CSTTransformer):
    """CST transformer to rewrite import statements."""
    
    def __init__(self, path_mappings: Dict[str, str]):
        """
        Args:
            path_mappings: Dict mapping old module paths to new module paths
        """
        self.path_mappings = path_mappings
        self.changes_made = 0
    
    def _convert_path_to_module(self, path: str) -> str:
        """Convert file path to Python module path."""
        # Remove .py extension
        if path.endswith(".py"):
            path = path[:-3]
        
        # Convert Windows/Unix paths to module notation
        module = path.replace("\\", ".").replace("/", ".")
        
        # Add presentation prefix if not present
        if not module.startswith("src.app.presentation"):
            module = f"src.app.presentation.{module}"
        
        return module
    
    def _rewrite_module_name(self, module: str) -> Tuple[str, bool]:
        """
        Rewrite a module name if it matches path mappings.
        Returns (new_module, was_changed).
        """
        for old_path, new_path in self.path_mappings.items():
            old_module = self._convert_path_to_module(old_path)
            new_module = self._convert_path_to_module(new_path)
            
            # Exact match
            if module == old_module:
                return new_module, True
            
            # Prefix match (for submodule imports)
            if module.startswith(old_module + "."):
                suffix = module[len(old_module):]
                return new_module + suffix, True
        
        return module, False
    
    def leave_Import(self, original_node: cst.Import, updated_node: cst.Import) -> cst.Import:
        """Rewrite 'import module' statements."""
        new_names = []
        changed = False
        
        for name in updated_node.names:
            if isinstance(name, cst.ImportAlias):
                module_str = cst.helpers.get_full_name_for_node(name.name)
                if module_str:
                    new_module_str, was_changed = self._rewrite_module_name(module_str)
                    if was_changed:
                        changed = True
                        new_name = name.with_changes(
                            name=cst.helpers.parse_template_module("{}", config=None).body[0].body[0].names[0].name.with_deep_changes(
                                old_node=name.name,
                                value=new_module_str
                            ) if hasattr(name.name, 'value') else cst.parse_expression(new_module_str)
                        )
                        new_names.append(new_name)
                    else:
                        new_names.append(name)
                else:
                    new_names.append(name)
            else:
                new_names.append(name)
        
        if changed:
            self.changes_made += 1
            return updated_node.with_changes(names=new_names)
        
        return updated_node
    
    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.ImportFrom:
        """Rewrite 'from module import name' statements."""
        if updated_node.module is None:
            return updated_node
        
        module_str = cst.helpers.get_full_name_for_node(updated_node.module)
        if not module_str:
            return updated_node
        
        new_module_str, was_changed = self._rewrite_module_name(module_str)
        
        if was_changed:
            self.changes_made += 1
            # Parse new module path
            new_module = cst.parse_expression(new_module_str)
            return updated_node.with_changes(module=new_module)
        
        return updated_node


def load_rename_map(csv_file: Path) -> Dict[str, str]:
    """Load rename mappings from CSV."""
    mappings = {}
    
    if not csv_file.exists():
        print(f"ERROR: Rename map not found: {csv_file}")
        return mappings
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            src = row['src_path']
            dst = row['dst_path']
            mappings[src] = dst
    
    return mappings


def rewrite_file_imports(file_path: Path, path_mappings: Dict[str, str]) -> int:
    """
    Rewrite imports in a single file.
    Returns number of changes made.
    """
    try:
        # Read file
        content = file_path.read_text(encoding='utf-8')
        
        # Parse as CST
        tree = cst.parse_module(content)
        
        # Transform
        transformer = ImportRewriter(path_mappings)
        new_tree = tree.visit(transformer)
        
        # Write back if changed
        if transformer.changes_made > 0:
            file_path.write_text(new_tree.code, encoding='utf-8')
            return transformer.changes_made
        
        return 0
    
    except Exception as e:
        print(f"ERROR processing {file_path}: {e}")
        return 0


def rewrite_all_imports(root: Path, path_mappings: Dict[str, str], phase: str = None):
    """Rewrite imports in all Python files."""
    total_files = 0
    total_changes = 0
    
    for py_file in root.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        total_files += 1
        changes = rewrite_file_imports(py_file, path_mappings)
        
        if changes > 0:
            rel_path = py_file.relative_to(root)
            print(f"  ✓ {rel_path}: {changes} imports rewritten")
            total_changes += changes
    
    return total_files, total_changes


def main():
    """Main import rewriter."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Rewrite presentation layer imports")
    parser.add_argument("--phase", help="Only rewrite imports for specific phase (P1, P2, P3, P4)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without modifying files")
    args = parser.parse_args()
    
    print("=" * 80)
    print("IMPORT REWRITER")
    print("=" * 80)
    print()
    
    # Load rename map
    print("Loading rename map...")
    path_mappings = load_rename_map(RENAME_MAP_FILE)
    
    if not path_mappings:
        print("No mappings found. Exiting.")
        return
    
    # Filter by phase if specified
    if args.phase:
        print(f"Filtering for phase: {args.phase}")
        # Re-read CSV with phase filter
        filtered = {}
        with open(RENAME_MAP_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['phase'] == args.phase:
                    filtered[row['src_path']] = row['dst_path']
        path_mappings = filtered
    
    print(f"Loaded {len(path_mappings)} path mappings")
    
    if args.dry_run:
        print("\nDRY RUN MODE - No files will be modified")
        print("\nMappings to apply:")
        for old, new in list(path_mappings.items())[:10]:
            print(f"  {old} → {new}")
        if len(path_mappings) > 10:
            print(f"  ... and {len(path_mappings) - 10} more")
        return
    
    # Rewrite imports
    print("\nRewriting imports...")
    total_files, total_changes = rewrite_all_imports(PRESENTATION_ROOT, path_mappings, args.phase)
    
    print(f"\n✓ Import rewrite complete")
    print(f"  Files processed: {total_files}")
    print(f"  Imports rewritten: {total_changes}")
    print()


if __name__ == "__main__":
    # Check for libcst
    try:
        import libcst
    except ImportError:
        print("ERROR: libcst not installed")
        print("Install with: pip install libcst")
        sys.exit(1)
    
    main()
