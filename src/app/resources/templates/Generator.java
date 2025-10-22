import java.util.*;

public class Generator {
    public static void main(String[] args) {
        Random random = new Random();
        
        // Generate random test case
        // Example: generate random array
        int n = random.nextInt(10) + 1;
        
        System.out.println(n);
        for (int i = 0; i < n; i++) {
            System.out.print(random.nextInt(100) + 1);
            if (i < n - 1) System.out.print(" ");
        }
        System.out.println();
    }
}