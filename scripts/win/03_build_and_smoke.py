"""
Script 3: Build and Smoke Test
Runs tests and optionally launches app for validation.
"""

import subprocess
import sys
from pathlib import Path

# Repo root
REPO_ROOT = Path(__file__).parent.parent.parent


def run_command(cmd: list, description: str, capture=False):
    """
    Run a shell command.
    
    Returns:
        (success: bool, output: str)
    """
    print(f"\n{'=' * 80}")
    print(description)
    print('=' * 80)
    
    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
        else:
            result = subprocess.run(cmd, cwd=REPO_ROOT)
        
        success = result.returncode == 0
        output = result.stdout if capture else ""
        
        if success:
            print(f"✓ {description} passed")
        else:
            print(f"✗ {description} failed with code {result.returncode}")
        
        return success, output
    
    except Exception as e:
        print(f"✗ Error running command: {e}")
        return False, ""


def run_unit_tests():
    """Run unit tests for presentation layer."""
    return run_command(
        [sys.executable, "-m", "pytest", "tests/unit/", "-v", "--tb=short"],
        "Running unit tests",
        capture=True
    )


def run_import_check():
    """Check for import errors by trying to import presentation package."""
    code = """
import sys
try:
    from src.app.presentation import *
    print("✓ Presentation package imports successfully")
    sys.exit(0)
except Exception as e:
    print(f"✗ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
    
    return run_command(
        [sys.executable, "-c", code],
        "Checking presentation imports",
        capture=True
    )


def run_syntax_check():
    """Run Python syntax check on all presentation files."""
    return run_command(
        [sys.executable, "-m", "py_compile"] + list((REPO_ROOT / "src" / "app" / "presentation").rglob("*.py")),
        "Checking Python syntax",
        capture=True
    )


def launch_app_smoke_test():
    """Launch the app for visual smoke test (manual)."""
    print(f"\n{'=' * 80}")
    print("Manual Smoke Test")
    print('=' * 80)
    print("\nThis will launch the application for manual testing.")
    print("Press Enter to launch, or Ctrl+C to skip...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nSkipping manual smoke test")
        return True, ""
    
    print("\nLaunching application...")
    print("Please test the following:")
    print("  1. Main window displays correctly")
    print("  2. All navigation works")
    print("  3. Windows render with proper styles")
    print("  4. StatusView displays in test windows")
    print("\nClose the app when testing is complete.\n")
    
    return run_command(
        [sys.executable, "-m", "src.app"],
        "Application smoke test"
    )


def main():
    """Main build and smoke test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build and smoke test presentation migration")
    parser.add_argument("--phase", help="Phase being tested (for documentation)")
    parser.add_argument("--skip-tests", action="store_true", help="Skip unit tests")
    parser.add_argument("--skip-app", action="store_true", help="Skip app launch")
    args = parser.parse_args()
    
    print("=" * 80)
    print("BUILD AND SMOKE TEST")
    if args.phase:
        print(f"Phase: {args.phase}")
    print("=" * 80)
    
    results = {}
    
    # Import check
    success, _ = run_import_check()
    results["Import Check"] = success
    
    if not success:
        print("\n⚠ Import errors detected. Fix before proceeding.")
        return
    
    # Unit tests (optional)
    if not args.skip_tests:
        success, _ = run_unit_tests()
        results["Unit Tests"] = success
    else:
        print("\nSkipping unit tests")
    
    # Manual app smoke test (optional)
    if not args.skip_app:
        success, _ = launch_app_smoke_test()
        results["App Smoke Test"] = success
    else:
        print("\nSkipping app smoke test")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {test_name}")
    
    all_success = all(results.values())
    
    print("\n" + "=" * 80)
    if all_success:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("=" * 80)
    print()
    
    if all_success:
        if args.phase:
            phases = {"P1": "P2", "P2": "P3", "P3": "P4", "P4": None}
            next_phase = phases.get(args.phase)
            
            if next_phase:
                print(f"Phase {args.phase} complete. Next phase:")
                print(f"  python scripts\\win\\00_dry_run.py --phase {next_phase}")
                print(f"  python scripts\\win\\01_apply_moves.py --phase {next_phase}")
            else:
                print("All phases complete! Final cleanup:")
                print("  - Remove refactor/aliases/presentation/legacy_aliases.py")
                print("  - Run full test suite")
                print("  - Update documentation")
        else:
            print("Migration complete!")
            print("Next steps:")
            print("  - Review all changes")
            print("  - Run full test suite")
            print("  - Update team documentation")
    else:
        print("Review errors above and fix before proceeding")
    
    print()


if __name__ == "__main__":
    main()
