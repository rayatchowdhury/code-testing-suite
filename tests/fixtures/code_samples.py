"""
Code sample fixtures for integration testing.

Provides reusable, working code samples for:
- Generators (produce test input)
- Test solutions (solution to be tested)
- Correct solutions (reference implementation)
- Validators (check solution correctness)

These samples are designed for real compilation and execution in integration tests.
"""

# ============================================================================
# C++ Code Samples
# ============================================================================

# Generator: produces simple array input
CPP_GENERATOR_SIMPLE = """
#include <iostream>
using namespace std;

int main() {
    cout << "5" << endl;
    cout << "3 1 4 5 2" << endl;
    return 0;
}
""".strip()

# Generator: produces random array input
CPP_GENERATOR_RANDOM = """
#include <iostream>
#include <cstdlib>
#include <ctime>
using namespace std;

int main() {
    srand(time(0));
    int n = 5 + rand() % 10;
    cout << n << endl;
    
    for (int i = 0; i < n; i++) {
        int value = rand() % 100;
        cout << value << " ";
    }
    cout << endl;
    
    return 0;
}
""".strip()

# Correct solution: sorts array ascending
CPP_CORRECT_SORT_ASC = """
#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    int n;
    cin >> n;
    
    int arr[1000];
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }
    
    sort(arr, arr + n);
    
    for (int i = 0; i < n; i++) {
        cout << arr[i];
        if (i < n - 1) cout << " ";
    }
    cout << endl;
    
    return 0;
}
""".strip()

# Test solution: sorts array ascending (MATCHING)
CPP_TEST_SORT_ASC = """
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    int n;
    cin >> n;
    
    vector<int> numbers(n);
    for (int i = 0; i < n; i++) {
        cin >> numbers[i];
    }
    
    sort(numbers.begin(), numbers.end());
    
    for (int i = 0; i < n; i++) {
        cout << numbers[i];
        if (i < n - 1) cout << " ";
    }
    cout << endl;
    
    return 0;
}
""".strip()

# Test solution: sorts array descending (MISMATCHED)
CPP_TEST_SORT_DESC = """
#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    int n;
    cin >> n;
    
    int arr[1000];
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }
    
    // WRONG: sorting descending instead of ascending
    sort(arr, arr + n, greater<int>());
    
    for (int i = 0; i < n; i++) {
        cout << arr[i];
        if (i < n - 1) cout << " ";
    }
    cout << endl;
    
    return 0;
}
""".strip()

# Test solution: doesn't sort (MISMATCHED)
CPP_TEST_NO_SORT = """
#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    
    int arr[1000];
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }
    
    // WRONG: not sorting at all
    for (int i = 0; i < n; i++) {
        cout << arr[i];
        if (i < n - 1) cout << " ";
    }
    cout << endl;
    
    return 0;
}
""".strip()

# Validator: checks if output is sorted
CPP_VALIDATOR_SORTED = """
#include <iostream>
#include <vector>
#include <sstream>
using namespace std;

int main() {
    string line;
    getline(cin, line);
    
    istringstream iss(line);
    vector<int> nums;
    int num;
    while (iss >> num) {
        nums.push_back(num);
    }
    
    // Check if sorted
    for (size_t i = 1; i < nums.size(); i++) {
        if (nums[i] < nums[i-1]) {
            return 1;  // Wrong Answer
        }
    }
    
    return 0;  // Accepted
}
""".strip()

# Test solution: benchmark test (simple computation)
CPP_BENCHMARK_SOLUTION = """
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    int n;
    cin >> n;
    
    vector<int> arr(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }
    
    // Perform some computation
    sort(arr.begin(), arr.end());
    
    long long sum = 0;
    for (int x : arr) {
        sum += x;
    }
    
    cout << sum << endl;
    
    return 0;
}
""".strip()

# ============================================================================
# Python Code Samples
# ============================================================================

# Generator: produces simple input
PYTHON_GENERATOR_SIMPLE = """
print("5")
print("10 20 30 40 50")
""".strip()

# Correct solution: sums numbers
PYTHON_CORRECT_SUM = """
n = int(input())
numbers = list(map(int, input().split()))
print(sum(numbers))
""".strip()

# Test solution: sums numbers (MATCHING)
PYTHON_TEST_SUM = """
n = int(input())
numbers = list(map(int, input().split()))
total = sum(numbers)
print(total)
""".strip()

# Test solution: multiplies instead of sum (MISMATCHED)
PYTHON_TEST_MULTIPLY = """
n = int(input())
numbers = list(map(int, input().split()))
result = 1
for num in numbers:
    result *= num
print(result)
""".strip()

# Validator: checks positive output
PYTHON_VALIDATOR_POSITIVE = """
output = int(input())
exit(0 if output > 0 else 1)
""".strip()

# ============================================================================
# Java Code Samples
# ============================================================================

# Generator: produces simple input
JAVA_GENERATOR_SIMPLE = """
public class Main {
    public static void main(String[] args) {
        System.out.println("5");
        System.out.println("1 2 3 4 5");
    }
}
""".strip()

# Correct solution: finds maximum
JAVA_CORRECT_MAX = """
import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        
        int max = Integer.MIN_VALUE;
        for (int i = 0; i < n; i++) {
            int num = sc.nextInt();
            max = Math.max(max, num);
        }
        
        System.out.println(max);
    }
}
""".strip()

# Test solution: finds maximum (MATCHING)
JAVA_TEST_MAX = """
import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }
        
        Arrays.sort(arr);
        System.out.println(arr[n-1]);
    }
}
""".strip()

# ============================================================================
# Code Sample Sets (for easy workspace setup)
# ============================================================================

CPP_COMPARATOR_MATCHING = {
    'generator': CPP_GENERATOR_SIMPLE,
    'correct': CPP_CORRECT_SORT_ASC,
    'test': CPP_TEST_SORT_ASC,
}

CPP_COMPARATOR_MISMATCHED = {
    'generator': CPP_GENERATOR_SIMPLE,
    'correct': CPP_CORRECT_SORT_ASC,
    'test': CPP_TEST_SORT_DESC,
}

CPP_VALIDATOR_SET = {
    'generator': CPP_GENERATOR_SIMPLE,
    'validator': CPP_VALIDATOR_SORTED,
    'test': CPP_TEST_SORT_ASC,
}

CPP_BENCHMARKER_SET = {
    'generator': CPP_GENERATOR_SIMPLE,  # Use simple generator for consistent benchmarking
    'test': CPP_BENCHMARK_SOLUTION,
}

PYTHON_COMPARATOR_MATCHING = {
    'generator': PYTHON_GENERATOR_SIMPLE,
    'correct': PYTHON_CORRECT_SUM,
    'test': PYTHON_TEST_SUM,
}

PYTHON_VALIDATOR_SET = {
    'generator': PYTHON_GENERATOR_SIMPLE,
    'validator': PYTHON_VALIDATOR_POSITIVE,
    'test': PYTHON_TEST_SUM,
}
