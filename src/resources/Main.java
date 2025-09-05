// Purpose: This program calculates the sum of two integers entered by the user.

// Parameters/Returns:
// - Takes two integer inputs from the user.
// - Returns the sum of the two integers.

// Dependencies:
// - Scanner class from java.util package

// Usage examples:
// - Run the program and enter two integers when prompted.
// - The program will print the sum of the two integers.

import java.util.Scanner;

public class Main {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Read the first integer from the user
        System.out.println("Enter the first integer:");
        int num1 = scanner.nextInt();

        // Read the second integer from the user
        System.out.println("Enter the second integer:");
        int num2 = scanner.nextInt();

        // Calculate the sum of the two integers
        int sum = num1 + num2;

        // Print the sum of the two integers
        System.out.println("The sum of " + num1 + " and " + num2 + " is " + sum);

        scanner.close();
    }
}