"""Service for FilesSnapshot operations."""

import difflib
import logging
import os
from typing import Any, Dict

from ..constants import TEST_TYPE_COMPARISON
from ..models import FilesSnapshot

logger = logging.getLogger(__name__)


class FilesSnapshotService:
    """Service for creating and managing files snapshots."""

    @staticmethod
    def create_snapshot(workspace_dir: str, test_type: str = TEST_TYPE_COMPARISON) -> FilesSnapshot:
        """
        Create a snapshot of relevant files for the specified test type.

        NEW BEHAVIOR: Only saves files needed for the test type with full filenames and extensions.
        - Comparison/Comparator: generator, correct, test (3 files)
        - Validation/Validator: generator, validator, test (3 files)
        - Benchmark/Benchmarker: generator, test (2 files)

        Args:
            workspace_dir: Root workspace directory (~/.code_testing_suite/workspace)
            test_type: Test type ('comparison', 'validation', 'benchmark', or 'comparator', 'validator', 'benchmarker')

        Returns:
            FilesSnapshot: Snapshot with only relevant files, full filenames, and per-file metadata
        """
        # Normalize test type names
        test_type_map = {
            "comparison": "comparator",
            "comparator": "comparator",
            "validation": "validator",
            "validator": "validator",
            "benchmark": "benchmarker",
            "benchmarker": "benchmarker",
            "stress": "comparator",  # Legacy support
        }

        test_subdir = test_type_map.get(test_type.lower(), "comparator")
        normalized_test_type = {
            "comparator": "comparison",
            "validator": "validation",
            "benchmarker": "benchmark",
        }[test_subdir]

        snapshot = FilesSnapshot(test_type=normalized_test_type)

        # Define required files per test type
        required_roles = {
            "comparator": ["generator", "correct", "test"],
            "validator": ["generator", "validator", "test"],
            "benchmarker": ["generator", "test"],
        }

        required = required_roles.get(test_subdir, ["generator", "test"])
        test_type_dir = os.path.join(workspace_dir, test_subdir)

        try:
            if not os.path.exists(test_type_dir):
                logger.warning(f"Test type directory not found: {test_type_dir}")
                return snapshot

            # Track languages to determine primary
            language_counts = {"cpp": 0, "py": 0, "java": 0}

            # Track which roles have been filled (only one file per role)
            roles_found = set()

            # Read all source files in test type directory
            for filename in os.listdir(test_type_dir):
                filepath = os.path.join(test_type_dir, filename)

                # Skip directories (inputs/outputs)
                if os.path.isdir(filepath):
                    continue

                # Only process source code files
                if not filename.endswith((".cpp", ".h", ".py", ".java")):
                    continue

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Detect language from extension
                    if filename.endswith(".py"):
                        language = "py"
                    elif filename.endswith(".java"):
                        language = "java"
                    else:
                        language = "cpp"

                    # Determine file role
                    base_name = filename.split(".")[0].lower()
                    role = None

                    # Check if this is a required file (only if role not already found)
                    for req_role in required:
                        if req_role in base_name and req_role not in roles_found:
                            role = req_role
                            roles_found.add(req_role)
                            break

                    # Only add files that match required roles
                    if role is not None:
                        snapshot.files[filename] = {
                            "content": content,
                            "language": language,
                            "role": role,
                        }
                        language_counts[language] += 1

                except Exception as e:
                    logger.warning(f"Error reading file {filename}: {e}")

            # Determine primary language (most common)
            if language_counts:
                snapshot.primary_language = max(language_counts, key=language_counts.get)

            logger.info(
                f"Created snapshot for {test_type} ({test_subdir}): {len(snapshot.files)} files, primary language: {snapshot.primary_language}"
            )

            return snapshot

        except Exception as e:
            logger.error(f"Error creating files snapshot: {e}", exc_info=True)
            return snapshot

    @staticmethod
    def analyze_output_mismatch(expected: str, actual: str) -> Dict[str, Any]:
        """
        Analyze differences between expected and actual output.

        Args:
            expected: Expected output string
            actual: Actual output string

        Returns:
            Dict containing:
                - unified_diff: List of unified diff lines
                - character_differences: List of char-level diffs
                - line_differences: List of line-level diffs
                - summary: Statistics about the differences
        """
        expected_lines = expected.strip().split("\n")
        actual_lines = actual.strip().split("\n")

        # Generate unified diff
        diff = list(
            difflib.unified_diff(
                expected_lines,
                actual_lines,
                fromfile="Expected Output",
                tofile="Actual Output",
                lineterm="",
                n=3,
            )
        )

        # Character-by-character diff for precise analysis
        char_diff = []
        for i, (exp_char, act_char) in enumerate(zip(expected, actual)):
            if exp_char != act_char:
                char_diff.append({"position": i, "expected": exp_char, "actual": act_char})

        # Line-by-line analysis
        line_analysis = []
        max_lines = max(len(expected_lines), len(actual_lines))

        for i in range(max_lines):
            exp_line = expected_lines[i] if i < len(expected_lines) else ""
            act_line = actual_lines[i] if i < len(actual_lines) else ""

            if exp_line != act_line:
                line_analysis.append(
                    {
                        "line_number": i + 1,
                        "expected": exp_line,
                        "actual": act_line,
                        "type": (
                            "modified"
                            if exp_line and act_line
                            else ("missing" if exp_line else "extra")
                        ),
                    }
                )

        return {
            "unified_diff": diff,
            "character_differences": char_diff,
            "line_differences": line_analysis,
            "summary": {
                "total_char_differences": len(char_diff),
                "total_line_differences": len(line_analysis),
                "expected_length": len(expected),
                "actual_length": len(actual),
                "expected_lines": len(expected_lines),
                "actual_lines": len(actual_lines),
            },
        }
