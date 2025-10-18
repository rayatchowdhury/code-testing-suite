#!/usr/bin/env python3
"""
Style Linter for Code Testing Suite

Validates styling best practices across the codebase:
- No inline .setStyleSheet() calls in view/widget files
- No hardcoded hex colors (should use MATERIAL_COLORS)
- No oversized style files (>200 lines)
- Proper use of centralized styles and helpers

Usage:
    python scripts/lint_styles.py
"""

import ast
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


@dataclass
class StyleViolation:
    """Represents a style guideline violation"""

    file_path: str
    line_number: int
    violation_type: str
    message: str
    severity: str  # 'error', 'warning', 'info'


class StyleLinter:
    """Linter for styling best practices"""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.violations: List[StyleViolation] = []

        # Paths to check
        self.views_path = workspace_root / "src" / "app" / "presentation" / "views"
        self.widgets_path = (
            workspace_root / "src" / "app" / "presentation" / "widgets"
        )
        self.styles_path = workspace_root / "src" / "app" / "presentation" / "styles"

        # Patterns
        self.hex_color_pattern = re.compile(r"#[0-9A-Fa-f]{3,6}")
        self.setstylesheet_pattern = re.compile(
            r"\.setStyleSheet\s*\(\s*['\"](?!.*MATERIAL_COLORS)"
        )

    def check_inline_styles(self) -> List[StyleViolation]:
        """
        Check for inline .setStyleSheet() calls in view/widget files.

        Views and widgets should import styles from styles/components/ instead of
        defining styles inline.
        """
        violations = []

        for directory in [self.views_path, self.widgets_path]:
            if not directory.exists():
                continue

            for python_file in directory.rglob("*.py"):
                if python_file.name.startswith("__"):
                    continue

                with open(python_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                for line_num, line in enumerate(lines, 1):
                    # Skip if it's using a centralized style
                    if "MATERIAL_COLORS" in line or "from src.app.presentation.styles" in line:
                        continue

                    # Check for inline style definitions
                    if ".setStyleSheet(" in line and (
                        "f'" in line
                        or 'f"' in line
                        or '"font-' in line
                        or "'font-" in line
                        or '"color:' in line
                        or "'color:" in line
                        or '"background' in line
                        or "'background" in line
                    ):
                        # Allow specific helper imports
                        if any(
                            helper in line
                            for helper in [
                                "bold_label(",
                                "error_text(",
                                "success_text(",
                                "warning_text(",
                                "text_secondary(",
                            ]
                        ):
                            continue

                        violations.append(
                            StyleViolation(
                                file_path=str(python_file.relative_to(self.workspace_root)),
                                line_number=line_num,
                                violation_type="inline_style",
                                message=f"Inline style detected. Use centralized styles from styles/components/",
                                severity="warning",
                            )
                        )

        return violations

    def check_magic_colors(self) -> List[StyleViolation]:
        """
        Check for hardcoded hex colors in style strings.

        All colors should use MATERIAL_COLORS constants.
        """
        violations = []

        # Exempt files that legitimately need hex colors
        exempt_files = [
            "colors.py",  # Defines the colors
            "syntax_highlighting.py",  # Syntax highlighting needs specific colors
            "gradients.py",  # Gradients use specific color values
            "code_editor_display_area.py",  # Editor theme colors
            "ai_panel.py",  # AI panel has custom theme
        ]

        # Check presentation layer files
        presentation_root = self.workspace_root / "src" / "app" / "presentation"
        if not presentation_root.exists():
            return violations

        for python_file in presentation_root.rglob("*.py"):
            if python_file.name.startswith("__"):
                continue

            # Skip exempt files
            if any(exempt in str(python_file) for exempt in exempt_files):
                continue

            with open(python_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith("#"):
                    continue

                # Find hex colors
                hex_matches = self.hex_color_pattern.findall(line)
                if hex_matches:
                    # Allow some specific cases (like transparency alpha values)
                    if "40}" in line or "80}" in line:  # Transparency suffixes
                        continue

                    for hex_color in hex_matches:
                        violations.append(
                            StyleViolation(
                                file_path=str(python_file.relative_to(self.workspace_root)),
                                line_number=line_num,
                                violation_type="magic_color",
                                message=f"Hardcoded hex color '{hex_color}' found. Use MATERIAL_COLORS instead.",
                                severity="error",
                            )
                        )

        return violations

    def check_oversized_files(self, max_lines: int = 200) -> List[StyleViolation]:
        """
        Check for style files that exceed the line limit.

        Style component files should be <200 lines. If larger, they should be split
        into modular packages.
        """
        violations = []

        if not self.styles_path.exists():
            return violations

        # Only check files in styles/components/
        components_path = self.styles_path / "components"
        if not components_path.exists():
            return violations

        for python_file in components_path.rglob("*.py"):
            if python_file.name.startswith("__"):
                continue

            with open(python_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            line_count = len(lines)
            if line_count > max_lines:
                violations.append(
                    StyleViolation(
                        file_path=str(python_file.relative_to(self.workspace_root)),
                        line_number=1,
                        violation_type="oversized_file",
                        message=f"Style file has {line_count} lines (limit: {max_lines}). Consider splitting into a modular package.",
                        severity="warning",
                    )
                )

        return violations

    def run_all_checks(self) -> List[StyleViolation]:
        """Run all linting checks"""
        print("🔍 Running style linter...")
        print()

        all_violations = []

        # Check inline styles
        print("  ⚡ Checking for inline styles in views/widgets...")
        inline_violations = self.check_inline_styles()
        all_violations.extend(inline_violations)
        print(f"     Found {len(inline_violations)} inline style violations")

        # Check magic colors
        print("  🎨 Checking for hardcoded hex colors...")
        color_violations = self.check_magic_colors()
        all_violations.extend(color_violations)
        print(f"     Found {len(color_violations)} magic color violations")

        # Check oversized files
        print("  📏 Checking for oversized style files...")
        size_violations = self.check_oversized_files()
        all_violations.extend(size_violations)
        print(f"     Found {len(size_violations)} oversized file violations")

        print()
        return all_violations

    def print_report(self, violations: List[StyleViolation]):
        """Print formatted violation report"""
        if not violations:
            print("✅ No style violations found!")
            print()
            print("🎉 Your codebase follows all styling best practices!")
            return

        # Group by severity
        errors = [v for v in violations if v.severity == "error"]
        warnings = [v for v in violations if v.severity == "warning"]
        infos = [v for v in violations if v.severity == "info"]

        print(f"❌ Found {len(violations)} total violations")
        print()

        if errors:
            print(f"🔴 ERRORS ({len(errors)}):")
            print()
            for violation in errors:
                print(f"  {violation.file_path}:{violation.line_number}")
                print(f"    {violation.message}")
                print()

        if warnings:
            print(f"🟡 WARNINGS ({len(warnings)}):")
            print()
            for violation in warnings:
                print(f"  {violation.file_path}:{violation.line_number}")
                print(f"    {violation.message}")
                print()

        if infos:
            print(f"🔵 INFO ({len(infos)}):")
            print()
            for violation in infos:
                print(f"  {violation.file_path}:{violation.line_number}")
                print(f"    {violation.message}")
                print()

        # Summary
        print("=" * 70)
        print(f"SUMMARY: {len(errors)} errors, {len(warnings)} warnings, {len(infos)} info")
        print()

        if errors:
            print("❌ Please fix all errors before proceeding.")
        elif warnings:
            print("⚠️  Consider addressing warnings to improve code quality.")
        else:
            print("ℹ️  Informational issues noted.")


def main():
    """Main entry point"""
    workspace_root = Path(__file__).parent.parent
    linter = StyleLinter(workspace_root)

    violations = linter.run_all_checks()
    linter.print_report(violations)

    # Exit with error code if violations found
    if violations:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()
