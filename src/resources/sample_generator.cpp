#include <iostream>
#include <random>
#include <vector>
using namespace std;

int main() {
    // Simple test case generator that uses some memory
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<> dist(1, 1000);
    
    int n = dist(gen) % 100 + 10;  // Array size between 10-110
    cout << n << endl;
    
    // Generate array
    for (int i = 0; i < n; i++) {
        cout << dist(gen) << " ";
    }
    cout << endl;
    
    return 0;
}
