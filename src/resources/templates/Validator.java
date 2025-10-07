import java.io.*;
import java.util.*;

public class Validator {
    public static void main(String[] args) {
        // Validator receives: args[0] = input file, args[1] = output file
        
        if (args.length != 2) {
            System.err.println("Usage: Validator <input_file> <output_file>");
            System.exit(3);
        }
        
        try {
            // Read input - Example: one number
            Scanner inputFile = new Scanner(new File(args[0]));
            if (!inputFile.hasNextInt()) {
                System.err.println("Cannot read input");
                System.exit(3);
            }
            int n = inputFile.nextInt();
            inputFile.close();
            
            // Read output
            Scanner outputFile = new Scanner(new File(args[1]));
            if (!outputFile.hasNextInt()) {
                System.out.println("No output");
                System.exit(2);  // Presentation Error
            }
            int result = outputFile.nextInt();
            outputFile.close();
            
            // Validate: output should equal input (simple echo test)
            if (result == n) {
                System.exit(0);  // Correct
            } else {
                System.exit(1);  // Wrong Answer
            }
            
        } catch (FileNotFoundException e) {
            System.err.println("File not found: " + e.getMessage());
            System.exit(3);
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            System.exit(3);
        }
        
        // Exit codes: 0=Correct, 1=Wrong, 2=Format Error
    }
}