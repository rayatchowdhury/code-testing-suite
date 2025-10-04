import java.util.*;

public class Correct {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        // Read input
        int n = scanner.nextInt();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = scanner.nextInt();
        }
        
        // Your algorithm here
        
        // Output result
        for (int i = 0; i < n; i++) {
            System.out.print(arr[i]);
            if (i < n - 1) System.out.print(" ");
        }
        System.out.println();
        
        scanner.close();
    }
}