#include <iostream>
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
}