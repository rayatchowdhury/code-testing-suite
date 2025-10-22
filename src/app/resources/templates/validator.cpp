#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main(int argc, char* argv[]) {
    // Validator receives: argv[1] = input file, argv[2] = output file
    
    if (argc != 3) {
        cerr << "Usage: validator <input_file> <output_file>" << endl;
        return 3;
    }
    
    // Open files
    ifstream input_file(argv[1]);
    ifstream output_file(argv[2]);
    
    if (!input_file.is_open() || !output_file.is_open()) {
        cerr << "Cannot open files" << endl;
        return 3;
    }
    
    // Read input - Example: one number
    int n;
    if (!(input_file >> n)) {
        cerr << "Cannot read input" << endl;
        return 3;
    }
    
    // Read output
    int result;
    if (!(output_file >> result)) {
        cout << "No output" << endl;
        return 2;  // Presentation Error
    }
    
    // Validate: output should equal input (simple echo test)
    if (result == n) {
        return 0;  // Correct
    } else {
        return 1;  // Wrong Answer
    }
    
    // Exit codes: 0=Correct, 1=Wrong, 2=Format Error
}