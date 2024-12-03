import subprocess
import os

class CompilerRunner:
    def __init__(self, console_output):
        self.console = console_output

    def compile_code(self, filepath):
        """Compile the C++ code"""
        if not filepath:
            self.console.displayOutput("Error: No file to compile")
            return False

        try:
            compile_process = subprocess.run(
                ['g++', filepath, '-o', os.path.splitext(filepath)[0]],
                capture_output=True, text=True
            )
            
            if compile_process.returncode == 0:
                self.console.displayOutput("Compilation successful!")
                return True
            else:
                self.console.displayOutput(f"Compilation Error:\n{compile_process.stderr}")
                return False
        
        except Exception as e:
            self.console.displayOutput(f"Error: {str(e)}")
            return False

    def run_code(self, filepath):
        """Run the compiled executable"""
        if not filepath:
            self.console.displayOutput("Error: No file to run")
            return

        exe_path = os.path.splitext(filepath)[0]
        
        if not os.path.exists(exe_path):
            self.console.displayOutput("Error: Executable not found. Attempting to compile...")
            if not self.compile_code(filepath):
                return

        try:
            run_process = subprocess.run(
                [exe_path],
                capture_output=True, 
                text=True
            )
            
            self.console.displayOutput("Program Output:")
            self.console.displayOutput(run_process.stdout)
            
            if run_process.returncode != 0:
                self.console.displayOutput(f"Runtime Error:\n{run_process.stderr}")
        
        except Exception as e:
            self.console.displayOutput(f"Error: {str(e)}")
