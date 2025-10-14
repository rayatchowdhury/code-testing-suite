"""
Coverage Gap Analysis Script for Phase 8

Analyzes coverage.json to identify testing gaps and generate detailed reports.
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def load_coverage_data(coverage_file: str = "coverage.json") -> Dict:
    """Load coverage data from JSON file."""
    with open(coverage_file, "r") as f:
        return json.load(f)


def categorize_files(files: Dict) -> Dict[str, List[Tuple[str, float, int, int]]]:
    """Categorize files by layer and extract coverage metrics."""
    categories = defaultdict(list)

    for filepath, data in files.items():
        if "src\\app" not in filepath:
            continue

        summary = data["summary"]
        coverage_pct = summary["percent_covered"]
        missing_lines = summary["missing_lines"]
        total_lines = summary["num_statements"]

        # Determine category
        if "core\\tools" in filepath:
            category = "core_tools"
        elif "core\\config" in filepath:
            category = "core_config"
        elif "core\\ai" in filepath:
            category = "core_ai"
        elif "persistence\\database" in filepath:
            category = "database"
        elif "presentation\\views" in filepath:
            category = "presentation_views"
        elif "presentation\\widgets" in filepath:
            category = "presentation_widgets"
        elif "presentation\\styles" in filepath:
            category = "presentation_styles"
        elif "presentation\\window_controller" in filepath:
            category = "window_controller"
        elif "shared" in filepath:
            category = "shared"
        else:
            category = "other"

        categories[category].append(
            (
                filepath.replace("src\\app\\", ""),
                coverage_pct,
                missing_lines,
                total_lines,
            )
        )

    return dict(categories)


def generate_report(categories: Dict) -> str:
    """Generate markdown report of coverage gaps."""

    report = []
    report.append("# Phase 8 Coverage Gap Analysis")
    report.append("")
    report.append(f"**Generated**: {Path('coverage.json').stat().st_mtime}")
    report.append("")
    report.append("## Executive Summary")
    report.append("")

    # Calculate overall statistics
    total_files = sum(len(files) for files in categories.values())
    all_coverages = [cov for files in categories.values() for _, cov, _, _ in files]
    avg_coverage = sum(all_coverages) / len(all_coverages) if all_coverages else 0

    files_below_70 = sum(1 for cov in all_coverages if cov < 70)
    files_below_50 = sum(1 for cov in all_coverages if cov < 50)
    files_below_30 = sum(1 for cov in all_coverages if cov < 30)

    report.append(f"- **Total Files Analyzed**: {total_files}")
    report.append(f"- **Average Coverage**: {avg_coverage:.1f}%")
    report.append(
        f"- **Files <70% Coverage**: {files_below_70} ({files_below_70/total_files*100:.1f}%)"
    )
    report.append(
        f"- **Files <50% Coverage**: {files_below_50} ({files_below_50/total_files*100:.1f}%)"
    )
    report.append(
        f"- **Files <30% Coverage**: {files_below_30} ({files_below_30/total_files*100:.1f}%)"
    )
    report.append("")

    # Coverage by layer
    report.append("## Coverage by Layer")
    report.append("")
    report.append("| Layer | Avg Coverage | Files | <70% | <50% | <30% |")
    report.append("|-------|-------------|-------|------|------|------|")

    layer_stats = []
    for category, files in sorted(categories.items()):
        if not files:
            continue
        coverages = [cov for _, cov, _, _ in files]
        avg_cov = sum(coverages) / len(coverages)
        below_70 = sum(1 for cov in coverages if cov < 70)
        below_50 = sum(1 for cov in coverages if cov < 50)
        below_30 = sum(1 for cov in coverages if cov < 30)

        layer_stats.append(
            (category, avg_cov, len(files), below_70, below_50, below_30)
        )
        report.append(
            f"| {category.replace('_', ' ').title()} | {avg_cov:.1f}% | {len(files)} | {below_70} | {below_50} | {below_30} |"
        )

    report.append("")

    # Priority 1: Critical files with <50% coverage
    report.append("## 🔴 Priority 1: Critical Gaps (<50% Coverage)")
    report.append("")
    report.append("These files require immediate attention:")
    report.append("")

    critical_files = []
    for category, files in categories.items():
        for filepath, cov, missing, total in files:
            if cov < 50:
                critical_files.append((category, filepath, cov, missing, total))

    critical_files.sort(
        key=lambda x: (x[2], -x[4])
    )  # Sort by coverage (asc), then by size (desc)

    if critical_files:
        current_category = None
        for category, filepath, cov, missing, total in critical_files:
            if category != current_category:
                report.append(f"### {category.replace('_', ' ').title()}")
                report.append("")
                current_category = category

            report.append(f"- **`{filepath}`**")
            report.append(f"  - Coverage: {cov:.1f}%")
            report.append(f"  - Missing: {missing}/{total} lines")
            report.append(
                f"  - **Action**: Add {(total - (total * cov / 100)) / 10:.0f}-{(total - (total * cov / 100)) / 5:.0f} tests"
            )
            report.append("")
    else:
        report.append("✅ No critical gaps found!")
        report.append("")

    # Priority 2: Moderate gaps (50-70% coverage)
    report.append("## 🟡 Priority 2: Moderate Gaps (50-70% Coverage)")
    report.append("")

    moderate_files = []
    for category, files in categories.items():
        for filepath, cov, missing, total in files:
            if 50 <= cov < 70:
                moderate_files.append((category, filepath, cov, missing, total))

    moderate_files.sort(key=lambda x: (x[2], -x[4]))

    if moderate_files:
        report.append(f"Found {len(moderate_files)} files needing improvement:")
        report.append("")
        current_category = None
        for category, filepath, cov, missing, total in moderate_files:
            if category != current_category:
                report.append(f"### {category.replace('_', ' ').title()}")
                report.append("")
                current_category = category

            report.append(
                f"- **`{filepath}`** - {cov:.1f}% ({missing}/{total} missing)"
            )
            report.append(
                f"  - **Action**: Add {missing / 10:.0f}-{missing / 5:.0f} tests to reach 80%+"
            )
            report.append("")
    else:
        report.append("✅ No moderate gaps found!")
        report.append("")

    # Priority 3: Fine-tuning (70-90% coverage)
    report.append("## 🟢 Priority 3: Fine-Tuning (70-90% Coverage)")
    report.append("")
    report.append("These files are close to excellent coverage:")
    report.append("")

    good_files = []
    for category, files in categories.items():
        for filepath, cov, missing, total in files:
            if 70 <= cov < 90:
                good_files.append((category, filepath, cov, missing, total))

    good_files.sort(key=lambda x: x[2])

    if good_files[:10]:  # Show top 10
        report.append("**Top 10 candidates for 90%+ coverage:**")
        report.append("")
        for category, filepath, cov, missing, total in good_files[:10]:
            report.append(f"- **`{filepath}`** - {cov:.1f}% ({missing} lines missing)")
        report.append("")

    # Excellent coverage (90%+)
    report.append("## ✅ Excellent Coverage (90%+ Coverage)")
    report.append("")

    excellent_files = []
    for category, files in categories.items():
        for filepath, cov, missing, total in files:
            if cov >= 90:
                excellent_files.append((category, filepath, cov))

    report.append(f"**{len(excellent_files)} files** with excellent coverage:")
    report.append("")

    by_category = defaultdict(int)
    for category, filepath, cov in excellent_files:
        by_category[category] += 1

    for category, count in sorted(by_category.items(), key=lambda x: -x[1]):
        report.append(f"- {category.replace('_', ' ').title()}: {count} files")
    report.append("")

    # Recommendations
    report.append("## 📋 Recommendations")
    report.append("")

    report.append("### Immediate Actions (Next 2-3 days)")
    report.append("")
    report.append("1. **Focus on Presentation Layer**")
    report.append(
        f"   - Current avg: {sum(cov for _, cov, _, _ in categories.get('presentation_views', [])) / max(len(categories.get('presentation_views', [])), 1):.1f}%"
    )
    report.append("   - Target: 50%+ (add ~30-40 tests)")
    report.append(
        "   - Priority files: config_dialog.py, results windows, window controllers"
    )
    report.append("")

    report.append("2. **Fill Core Tools Gaps**")
    report.append(
        f"   - Current avg: {sum(cov for _, cov, _, _ in categories.get('core_tools', [])) / max(len(categories.get('core_tools', [])), 1):.1f}%"
    )
    report.append("   - Target: 90%+ (add ~20-25 tests)")
    report.append("   - Focus: Error handling, edge cases, timeout scenarios")
    report.append("")

    report.append("3. **Test Error Paths**")
    report.append("   - Add tests for file I/O errors")
    report.append("   - Add tests for compilation failures")
    report.append("   - Add tests for database connection issues")
    report.append("   - Estimated: +5-8% coverage gain")
    report.append("")

    report.append("### Long-term Actions")
    report.append("")
    report.append("1. Maintain 70%+ coverage for all new code")
    report.append("2. Add performance baseline tests")
    report.append("3. Set up coverage regression detection in CI/CD")
    report.append("4. Create test templates for common patterns")
    report.append("")

    # Estimated effort
    report.append("## ⏱️ Estimated Effort")
    report.append("")
    report.append("| Priority | Files | Tests Needed | Time Est. |")
    report.append("|----------|-------|--------------|-----------|")

    priority_1_count = len(critical_files)
    priority_2_count = len(moderate_files)
    priority_3_count = min(10, len(good_files))

    report.append(
        f"| Priority 1 (<50%) | {priority_1_count} | {priority_1_count * 10}-{priority_1_count * 15} | 6-8 hours |"
    )
    report.append(
        f"| Priority 2 (50-70%) | {priority_2_count} | {priority_2_count * 5}-{priority_2_count * 8} | 4-6 hours |"
    )
    report.append(
        f"| Priority 3 (70-90%) | {priority_3_count} | {priority_3_count * 3}-{priority_3_count * 5} | 2-3 hours |"
    )
    report.append(
        f"| **Total** | **{priority_1_count + priority_2_count + priority_3_count}** | **{priority_1_count * 10 + priority_2_count * 5 + priority_3_count * 3}-{priority_1_count * 15 + priority_2_count * 8 + priority_3_count * 5}** | **12-17 hours** |"
    )
    report.append("")

    report.append("---")
    report.append("")
    report.append("*Generated by scripts/analyze_coverage_gaps.py*")

    return "\n".join(report)


def main():
    """Main entry point."""
    print("Loading coverage data...")
    data = load_coverage_data()

    print("Categorizing files...")
    categories = categorize_files(data["files"])

    print("Generating report...")
    report = generate_report(categories)

    output_file = Path("PHASE_8_COVERAGE_GAPS.md")
    output_file.write_text(report, encoding="utf-8")

    print(f"✅ Report generated: {output_file}")
    print(
        f"   Total files analyzed: {sum(len(files) for files in categories.values())}"
    )
    print(f"   Layers: {len(categories)}")

    # Print summary to console
    all_coverages = [cov for files in categories.values() for _, cov, _, _ in files]
    avg_coverage = sum(all_coverages) / len(all_coverages) if all_coverages else 0
    files_below_70 = sum(1 for cov in all_coverages if cov < 70)

    print(f"\n📊 Quick Summary:")
    print(f"   Average Coverage: {avg_coverage:.1f}%")
    print(f"   Files <70%: {files_below_70}")
    print(
        f"   Goal Status: {'✅ ACHIEVED' if avg_coverage >= 70 else f'🔄 {70 - avg_coverage:.1f}% to go'}"
    )


if __name__ == "__main__":
    main()
