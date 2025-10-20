# Dead Code Finder

A comprehensive Python script using `vulture` to find unused code, functions, imports, and variables.

## Features

- 🔍 Scan any folder for dead code
- 📊 Detailed statistics and categorization
- 🎯 Configurable confidence levels
- 📋 Multiple sorting options (type, file, confidence, size)
- 💾 Save reports to file
- 🎨 Colored, formatted output
- ⚙️ Ignore patterns for false positives

## Installation

```bash
# Install vulture if not already installed
pip install vulture
```

## Usage

### Basic Usage

```bash
# Scan presentation layer (default)
python find_dead_code.py

# Scan a specific folder
python find_dead_code.py src/app/core

# Scan with higher confidence threshold
python find_dead_code.py src --min-confidence 80
```

### Advanced Usage

```bash
# Sort by estimated size (largest first)
python find_dead_code.py src/app/presentation --sort-by size

# Sort by file
python find_dead_code.py src --sort-by file

# Sort by confidence level
python find_dead_code.py src --sort-by confidence

# Save report to file
python find_dead_code.py src --output dead_code_report.txt

# Ignore specific patterns
python find_dead_code.py src --ignore-names test_* _private*
```

### Examples

```bash
# Find dead code in widgets with 90% confidence
python find_dead_code.py src/app/presentation/widgets --min-confidence 90

# Comprehensive scan with size sorting and report
python find_dead_code.py src --min-confidence 80 --sort-by size -o report.txt

# Quick scan of views
python find_dead_code.py src/app/presentation/views
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `path` | Path to scan | `src/app/presentation` |
| `--min-confidence` | Minimum confidence (0-100) | `60` |
| `--sort-by` | Sort results by: `type`, `file`, `confidence`, `size` | `type` |
| `--output` / `-o` | Save report to file | None |
| `--ignore-names` | Patterns to ignore | None |

## Understanding Results

### Confidence Levels
- **100%**: Definitely unused (e.g., unused variables in function)
- **90%**: Very likely unused (e.g., unused imports)
- **60-80%**: Possibly unused (may be used dynamically)

### False Positives
Some items flagged may be:
- Used dynamically (e.g., `getattr()`, signal connections)
- Qt framework callbacks (e.g., `paintEvent`, `sizeHint`)
- Protocol/abstract methods meant to be overridden
- Entry points or plugin hooks

### Categories
- **Imports**: Unused import statements
- **Functions**: Unused functions
- **Methods**: Unused class methods
- **Classes**: Unused class definitions
- **Properties**: Unused @property decorators
- **Variables**: Unused variables
- **Attributes**: Unused class attributes

## Output Format

```
🔍 DEAD CODE ANALYSIS (min confidence: 80%)
================================================================================

📊 SUMMARY:
   Total dead code items: 45
   Estimated lines: ~230
   
   Breakdown by type:
      - Imports: 12
      - Functions: 15
      - Methods: 10
      - Variables: 8

📋 DETAILED BREAKDOWN BY TYPE
--------------------------------------------------------------------------------

🔸 FUNCTIONS (15 items)
   path/to/file.py:42
      function: 'unused_helper' (90% confidence)
```

## Tips

1. **Start with high confidence**: Use `--min-confidence 90` to find obvious dead code
2. **Review carefully**: Always verify before deleting - some items may be used dynamically
3. **Use size sorting**: `--sort-by size` helps prioritize large cleanups
4. **Save reports**: Use `-o report.txt` to track progress over time
5. **Ignore test patterns**: Use `--ignore-names test_*` to exclude test files

## Integration with Workflow

```bash
# Regular cleanup workflow
python find_dead_code.py src --min-confidence 85 --sort-by size -o cleanup.txt
# Review cleanup.txt
# Delete confirmed dead code
# Run tests
# Commit changes
```

## Exit Codes

- `0`: No dead code found
- `1`: Dead code detected (or error occurred)

## Notes

- The script provides **estimated line counts** - actual LOC may vary
- Some unused code may be intentional (e.g., future features, API compatibility)
- Always run tests after removing dead code
- Consider using git to track and review changes
