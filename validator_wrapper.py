
#!/usr/bin/env python3
"""
Validator wrapper that converts file-based validators to stdin/stdout based.
Usage: python validator_wrapper.py <original_validator.exe>
Reads: input_data\noutput_data from stdin
Calls: original_validator.exe input_temp.txt output_temp.txt
Returns: same exit code as original validator
"""

import sys
import tempfile
import subprocess
import os

def main():
    if len(sys.argv) != 2:
        print("Usage: validator_wrapper.py <validator_executable>", file=sys.stderr)
        sys.exit(2)
    
    validator_exe = sys.argv[1]
    
    try:
        # Read input and output data from stdin
        lines = sys.stdin.read().strip().split('\n\n', 1)
        if len(lines) != 2:
            print("Expected input format: input_data\n\noutput_data", file=sys.stderr)
            sys.exit(2)
        
        input_data, output_data = lines
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as input_temp:
            input_temp.write(input_data)
            input_temp.flush()
            input_path = input_temp.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as output_temp:
            output_temp.write(output_data)
            output_temp.flush()
            output_path = output_temp.name
        
        try:
            # Call original validator
            result = subprocess.run(
                [validator_exe, input_path, output_path],
                capture_output=True,
                text=True
            )
            
            # Forward stdout/stderr
            if result.stdout:
                print(result.stdout, end='')
            if result.stderr:
                print(result.stderr, end='', file=sys.stderr)
            
            # Exit with same code as validator
            sys.exit(result.returncode)
            
        finally:
            # Cleanup temp files
            try:
                os.unlink(input_path)
                os.unlink(output_path)
            except OSError:
                pass
                
    except Exception as e:
        print(f"Wrapper error: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
