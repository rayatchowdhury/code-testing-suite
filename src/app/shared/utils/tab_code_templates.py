"""
Code templates for different tab types and programming languages.
Provides centralized template generation for test code files.
"""

class TabCodeTemplates:
    """
    Centralized code template generator for different tab types and languages.
    Supports C++, Python, and Java templates for Generator, Test Code, Correct Code, and Validator Code.
    """
    
    @staticmethod
    def get_template(tab_name, language='cpp'):
        """
        Get code template for specific tab and language.
        
        Args:
            tab_name (str): Name of the tab ('Generator', 'Test Code', 'Correct Code', 'Validator Code')
            language (str): Programming language ('cpp', 'py', 'java')
            
        Returns:
            str: Code template content
        """
        if language == 'cpp':
            return TabCodeTemplates._get_cpp_template(tab_name)
        elif language == 'py':
            return TabCodeTemplates._get_python_template(tab_name)
        elif language == 'java':
            return TabCodeTemplates._get_java_template(tab_name)
        else:
            # Default fallback to C++
            return TabCodeTemplates._get_cpp_template(tab_name)
    
    @staticmethod
    def _get_cpp_template(tab_name):
        """Get C++ template for specific tab."""
        if tab_name == 'Generator':
            return '''#include <iostream>
#include <random>
#include <chrono>
using namespace std;

int main() {
    // Seed random number generator
    mt19937 rng(chrono::steady_clock::now().time_since_epoch().count());
    
    // Generate random test case
    // Example: generate random array
    int n = uniform_int_distribution<int>(1, 10)(rng);
    
    cout << n << endl;
    for (int i = 0; i < n; i++) {
        cout << uniform_int_distribution<int>(1, 100)(rng);
        if (i < n - 1) cout << " ";
    }
    cout << endl;
    
    return 0;
}'''
        elif tab_name in ['Test Code', 'Correct Code']:
            return '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    // Read input
    int n;
    cin >> n;
    
    vector<int> arr(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }
    
    // Your algorithm here
    
    // Output result
    for (int i = 0; i < n; i++) {
        cout << arr[i];
        if (i < n - 1) cout << " ";
    }
    cout << endl;
    
    return 0;
}'''
        elif tab_name == 'Validator Code':
            return '''#include <iostream>
#include <vector>
#include <cassert>
using namespace std;

int main() {
    // Read input
    int n;
    cin >> n;
    
    // Validate input constraints
    assert(n >= 1 && n <= 1000000);
    
    vector<int> arr(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
        assert(arr[i] >= 1 && arr[i] <= 1000000);
    }
    
    // Additional validation logic here
    
    cout << "Input is valid" << endl;
    
    return 0;
}'''
        else:
            return '''#include <iostream>
using namespace std;

int main() {
    // Your code here
    return 0;
}'''

    @staticmethod
    def _get_python_template(tab_name):
        """Get Python template for specific tab."""
        if tab_name == 'Generator':
            return '''import random
import sys

def main():
    # Generate random test case
    # Example: generate random array
    n = random.randint(1, 10)
    
    print(n)
    arr = [random.randint(1, 100) for _ in range(n)]
    print(' '.join(map(str, arr)))

if __name__ == "__main__":
    main()
'''
        elif tab_name in ['Test Code', 'Correct Code']:
            return '''def main():
    # Read input
    n = int(input())
    arr = list(map(int, input().split()))
    
    # Your algorithm here
    
    # Output result
    print(' '.join(map(str, arr)))

if __name__ == "__main__":
    main()
'''
        elif tab_name == 'Validator Code':
            return '''import sys

def main():
    # Read input
    n = int(input())
    
    # Validate input constraints
    assert 1 <= n <= 1000000, f"Invalid n: {n}"
    
    arr = list(map(int, input().split()))
    assert len(arr) == n, f"Expected {n} elements, got {len(arr)}"
    
    for x in arr:
        assert 1 <= x <= 1000000, f"Invalid array element: {x}"
    
    # Additional validation logic here
    
    print("Input is valid")

if __name__ == "__main__":
    main()
'''
        else:
            return '''def main():
    # Your code here
    pass

if __name__ == "__main__":
    main()
'''

    @staticmethod
    def _get_java_template(tab_name):
        """Get Java template for specific tab."""
        if tab_name == 'Generator':
            class_name = 'Generator'
            return f'''import java.util.*;

public class {class_name} {{
    public static void main(String[] args) {{
        Random random = new Random();
        
        // Generate random test case
        // Example: generate random array
        int n = random.nextInt(10) + 1;
        
        System.out.println(n);
        for (int i = 0; i < n; i++) {{
            System.out.print(random.nextInt(100) + 1);
            if (i < n - 1) System.out.print(" ");
        }}
        System.out.println();
    }}
}}'''
        elif tab_name in ['Test Code', 'Correct Code']:
            class_name = tab_name.replace(' ', '')
            return f'''import java.util.*;

public class {class_name} {{
    public static void main(String[] args) {{
        Scanner scanner = new Scanner(System.in);
        
        // Read input
        int n = scanner.nextInt();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {{
            arr[i] = scanner.nextInt();
        }}
        
        // Your algorithm here
        
        // Output result
        for (int i = 0; i < n; i++) {{
            System.out.print(arr[i]);
            if (i < n - 1) System.out.print(" ");
        }}
        System.out.println();
        
        scanner.close();
    }}
}}'''
        elif tab_name == 'Validator Code':
            return '''import java.util.*;

public class ValidatorCode {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        // Read input
        int n = scanner.nextInt();
        
        // Validate input constraints
        assert n >= 1 && n <= 1000000 : "Invalid n: " + n;
        
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = scanner.nextInt();
            assert arr[i] >= 1 && arr[i] <= 1000000 : "Invalid array element: " + arr[i];
        }
        
        // Additional validation logic here
        
        System.out.println("Input is valid");
        scanner.close();
    }
}'''
        else:
            class_name = tab_name.replace(' ', '')
            return f'''public class {class_name} {{
    public static void main(String[] args) {{
        // Your code here
    }}
}}'''

    @staticmethod
    def get_available_languages():
        """Get list of supported programming languages."""
        return ['cpp', 'py', 'java']
    
    @staticmethod
    def get_supported_tabs():
        """Get list of supported tab types."""
        return ['Generator', 'Test Code', 'Correct Code', 'Validator Code']
    
    @staticmethod
    def is_supported_language(language):
        """Check if language is supported."""
        return language in TabCodeTemplates.get_available_languages()
    
    @staticmethod
    def is_supported_tab(tab_name):
        """Check if tab type is supported."""
        return tab_name in TabCodeTemplates.get_supported_tabs()


# Convenience functions for backward compatibility
def get_template(tab_name, language='cpp'):
    """Convenience function to get template."""
    return TabCodeTemplates.get_template(tab_name, language)

def get_cpp_template(tab_name):
    """Get C++ template for specific tab."""
    return TabCodeTemplates.get_template(tab_name, 'cpp')

def get_python_template(tab_name):
    """Get Python template for specific tab."""
    return TabCodeTemplates.get_template(tab_name, 'py')

def get_java_template(tab_name):
    """Get Java template for specific tab."""
    return TabCodeTemplates.get_template(tab_name, 'java')
