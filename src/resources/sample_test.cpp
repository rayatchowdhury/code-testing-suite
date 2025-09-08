#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    int n;
    cin >> n;
    
    // Read array - this will consume memory based on input size
    vector<int> arr(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }
    
    // Simulate some processing that takes time and memory
    vector<int> result;
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            result.push_back(arr[i] + arr[j]);
        }
    }
    
    // Sort the result (additional memory usage)
    sort(result.begin(), result.end());
    
    // Output the sum of first 10 elements (or all if less than 10)
    int sum = 0;
    int count = min(10, (int)result.size());
    for (int i = 0; i < count; i++) {
        sum += result[i];
    }
    
    cout << sum << endl;
    
    return 0;
}
