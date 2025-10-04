import sys

def main():
    # Validator receives: sys.argv[1] = input file, sys.argv[2] = output file
    
    if len(sys.argv) != 3:
        print("Usage: validator.py <input_file> <output_file>", file=sys.stderr)
        sys.exit(3)
    
    try:
        # Read input - Example: one number
        with open(sys.argv[1], 'r') as f:
            n = int(f.readline().strip())
    except Exception as e:
        print(f"Cannot read input: {e}", file=sys.stderr)
        sys.exit(3)
    
    # Read output
    try:
        with open(sys.argv[2], 'r') as f:
            result = int(f.readline().strip())
    except Exception as e:
        print("No output", file=sys.stderr)
        sys.exit(2)  # Presentation Error
    
    # Validate: output should equal input (simple echo test)
    if result == n:
        sys.exit(0)  # Correct
    else:
        sys.exit(1)  # Wrong Answer
    
    # Exit codes: 0=Correct, 1=Wrong, 2=Format Error

if __name__ == "__main__":
    main()
