#!/usr/bin/env python3
"""
Import Rule Checker for Presentation Layer MVVM Architecture.

Enforces architectural rules:
1. No windows/** → windows/** imports (prevents window-to-window dependencies)
2. Windows may import: widgets/*, base/*, navigation/*, dialogs/*, design_system/*
3. Widgets may NOT import: windows/*
4. Detect circular dependencies

Usage:
    python scripts/check_import_rules.py [--strict] [--cycles] [--rule RULE_NAME]
"""

import argparse
import ast
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


class ImportRuleChecker:
    """Check import rules for presentation layer architecture."""

    def __init__(self, root_path: Path, strict: bool = False):
        self.root_path = root_path
        self.presentation_path = root_path / "src" / "app" / "presentation"
        self.strict = strict
        self.violations: List[Tuple[str, str, str]] = []
        self.import_graph: Dict[str, Set[str]] = defaultdict(set)

    def check_file(self, file_path: Path) -> List[Tuple[str, str, str]]:
        """
        Check a single Python file for import rule violations.

        Returns list of (file, rule, details) tuples.
        """
        violations = []

        try:
            with open(file_path, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"⚠️  Warning: Could not parse {file_path}: {e}")
            return violations

        relative_path = file_path.relative_to(self.root_path)
        module_name = self._path_to_module(relative_path)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported = alias.name
                    self._check_import(module_name, imported, file_path, violations)
                    self.import_graph[module_name].add(imported)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported = node.module
                    self._check_import(module_name, imported, file_path, violations)
                    self.import_graph[module_name].add(imported)

        return violations

    def _path_to_module(self, relative_path: Path) -> str:
        """Convert file path to module name."""
        parts = list(relative_path.parts)
        if parts[-1] == "__init__.py":
            parts = parts[:-1]
        elif parts[-1].endswith(".py"):
            parts[-1] = parts[-1][:-3]
        return ".".join(parts)

    def _check_import(
        self,
        importer: str,
        imported: str,
        file_path: Path,
        violations: List[Tuple[str, str, str]],
    ):
        """Check if an import violates architectural rules."""
        # Rule 1: No windows/** → windows/** imports
        if "presentation.windows" in importer and "presentation.windows" in imported:
            # Extract window names
            importer_window = self._extract_window_name(importer)
            imported_window = self._extract_window_name(imported)

            if importer_window and imported_window and importer_window != imported_window:
                violations.append(
                    (
                        str(file_path),
                        "no-windows-to-windows",
                        f"Window '{importer_window}' imports window '{imported_window}': {imported}",
                    )
                )

        # Rule 2: Components may NOT import windows/*
        if "presentation.shared.components" in importer and "presentation.windows" in imported:
            violations.append(
                (
                    str(file_path),
                    "no-components-to-windows",
                    f"Component imports window: {imported}",
                )
            )

        # Rule 3 (Strict mode): Windows should only import allowed modules
        if self.strict and "presentation.windows" in importer:
            # Allow windows to import from their own package (e.g., main/view.py → main/widgets/*)
            importer_window = self._extract_window_name(importer)
            imported_window = self._extract_window_name(imported)
            
            # If importing from same window package, allow it
            if importer_window and imported_window and importer_window == imported_window:
                return  # Same window package - allowed
            
            allowed_prefixes = [
                "src.app.presentation.shared.components",
                "src.app.presentation.shared.dialogs",
                "src.app.presentation.base",
                "src.app.presentation.navigation",
                "src.app.presentation.shared.design_system",
                "src.app.presentation.services",
                "src.app.core",
                "src.app.database",
                "src.app.shared",
                "PySide6",
                "typing",
                "dataclasses",
                "abc",
                "enum",
                "pathlib",
            ]

            if imported.startswith("src.app.presentation"):
                if not any(imported.startswith(prefix) for prefix in allowed_prefixes):
                    violations.append(
                        (
                            str(file_path),
                            "windows-forbidden-import",
                            f"Window imports disallowed module: {imported}",
                        )
                    )

    def _extract_window_name(self, module: str) -> str | None:
        """Extract window name from module path."""
        parts = module.split(".")
        try:
            windows_idx = parts.index("windows")
            if windows_idx + 1 < len(parts):
                return parts[windows_idx + 1]
        except ValueError:
            pass
        return None

    def check_all_files(self) -> List[Tuple[str, str, str]]:
        """Check all Python files in presentation layer."""
        all_violations = []

        if not self.presentation_path.exists():
            print(f"❌ Error: Presentation path not found: {self.presentation_path}")
            return all_violations

        for py_file in self.presentation_path.rglob("*.py"):
            # Skip __pycache__ and test files
            if "__pycache__" in str(py_file) or "test_" in py_file.name:
                continue

            violations = self.check_file(py_file)
            all_violations.extend(violations)

        return all_violations

    def find_cycles(self) -> List[List[str]]:
        """Find circular dependencies in import graph using DFS."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.import_graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path[:])
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            rec_stack.remove(node)

        for node in self.import_graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def print_report(self, violations: List[Tuple[str, str, str]], cycles: List[List[str]]):
        """Print formatted report of violations and cycles."""
        print("\n" + "=" * 80)
        print("📊 PRESENTATION LAYER IMPORT RULES CHECK")
        print("=" * 80 + "\n")

        if not violations and not cycles:
            print("✅ All import rules passed! No violations found.\n")
            return 0

        # Print violations by rule
        if violations:
            print(f"❌ Found {len(violations)} import rule violation(s):\n")

            violations_by_rule = defaultdict(list)
            for file, rule, details in violations:
                violations_by_rule[rule].append((file, details))

            for rule, rule_violations in sorted(violations_by_rule.items()):
                print(f"  🚫 Rule: {rule} ({len(rule_violations)} violations)")
                for file, details in rule_violations:
                    print(f"     File: {file}")
                    print(f"     Issue: {details}\n")

        # Print cycles
        if cycles:
            print(f"\n🔄 Found {len(cycles)} circular dependency cycle(s):\n")
            for i, cycle in enumerate(cycles, 1):
                print(f"  Cycle {i}:")
                for module in cycle:
                    print(f"    → {module}")
                print()

        print("=" * 80)
        print(f"Total Issues: {len(violations) + len(cycles)}")
        print("=" * 80 + "\n")

        return 1  # Exit code 1 for failures


def main():
    parser = argparse.ArgumentParser(
        description="Check import rules for presentation layer architecture"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict mode (enforce allowed imports for windows)",
    )
    parser.add_argument(
        "--cycles", action="store_true", help="Check for circular dependencies"
    )
    parser.add_argument(
        "--rule",
        choices=["no-windows-to-windows", "no-widgets-to-windows", "all"],
        default="all",
        help="Check specific rule only",
    )

    args = parser.parse_args()

    # Determine root path (assume script is in scripts/ dir)
    script_path = Path(__file__).resolve()
    root_path = script_path.parent.parent

    checker = ImportRuleChecker(root_path, strict=args.strict)

    # Collect all violations
    all_violations = checker.check_all_files()

    # Filter by rule if specified
    if args.rule != "all":
        all_violations = [(f, r, d) for f, r, d in all_violations if r == args.rule]

    # Find cycles if requested
    cycles = []
    if args.cycles:
        cycles = checker.find_cycles()

    # Print report
    exit_code = checker.print_report(all_violations, cycles)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
