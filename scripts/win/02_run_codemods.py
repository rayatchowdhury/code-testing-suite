"""
Script 2: Run Codemods
Executes all codemods in sequence to rewrite imports and fix paths.
"""

import subprocess
import sys
from pathlib import Path

# Repo root
REPO_ROOT = Path(__file__).parent.parent.parent
CODEMODS_DIR = REPO_ROOT / "refactor" / "codemods"


def run_codemod(script_name: str, args: list = None):
    """
    Run a codemod script.
    
    Args:
        script_name: Name of the codemod script
        args: Additional arguments to pass
    
    Returns:
        True if successful, False otherwise
    """
    script_path = CODEMODS_DIR / script_name
    
    if not script_path.exists():
        print(f"  ⚠ Codemod not found: {script_name}")
        return False
    
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    try:
        print(f"\n{'=' * 80}")
        print(f"Running: {script_name}")
        print('=' * 80)
        
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode == 0:
            print(f"✓ {script_name} completed successfully")
            return True
        else:
            print(f"✗ {script_name} failed with code {result.returncode}")
            return False
    
    except Exception as e:
        print(f"✗ Error running {script_name}: {e}")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    missing = []
    
    # Check for libcst (needed for import_rewrites.py)
    try:
        import libcst
        print("  ✓ libcst installed")
    except ImportError:
        print("  ✗ libcst not installed")
        missing.append("libcst")
    
    if missing:
        print("\nMissing dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nInstall with:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    return True


def main():
    """Main codemod runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run codemods for presentation migration")
    parser.add_argument("--phase", help="Run codemods for specific phase only (P1, P2, P3, P4)")
    parser.add_argument("--skip-import-check", action="store_true", help="Skip dependency check")
    args = parser.parse_args()
    
    print("=" * 80)
    print("RUN CODEMODS")
    print("=" * 80)
    print()
    
    # Check dependencies
    if not args.skip_import_check:
        if not check_dependencies():
            print("\nCannot proceed without required dependencies")
            return
        print()
    
    # Prepare arguments for codemods
    codemod_args = []
    if args.phase:
        codemod_args.extend(["--phase", args.phase])
    
    # Run codemods in sequence
    codemods = [
        "import_rewrites.py",
        "qss_path_fixup.py",
        "__init___exports_fixup.py",
    ]
    
    results = {}
    
    for codemod in codemods:
        success = run_codemod(codemod, codemod_args if codemod == "import_rewrites.py" else [])
        results[codemod] = success
    
    # Summary
    print("\n" + "=" * 80)
    print("CODEMODS SUMMARY")
    print("=" * 80)
    
    for codemod, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {codemod}")
    
    all_success = all(results.values())
    
    print("\n" + "=" * 80)
    if all_success:
        print("ALL CODEMODS COMPLETED SUCCESSFULLY")
    else:
        print("SOME CODEMODS FAILED")
    print("=" * 80)
    print()
    
    if all_success:
        print("Next step:")
        print(f"  python scripts\\win\\03_build_and_smoke.py {f'--phase {args.phase}' if args.phase else ''}")
    else:
        print("Review errors above and fix before proceeding")
    
    print()


if __name__ == "__main__":
    main()
