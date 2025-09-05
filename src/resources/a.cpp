#include <algorithm>
#include <iostream>
#include <vector>

/**
 * @brief Sorts a vector using the Bubble Sort algorithm.
 * @param arr The vector of integers to be sorted.
 */
void bubbleSort(std::vector<int>& arr)
{
    int n = arr.size();
    for (int i = 0; i < n - 1; i++)
    {
        for (int j = 0; j < n - i - 1; j++)
        {
            if (arr[j] > arr[j + 1])
            {
                std::swap(arr[j], arr[j + 1]); // Swap elements
            }
        }
    }
}

int main()
{
    int n;
    std::cout << "Enter the size of the vector: ";
    std::cin >> n;

    std::vector<int> arr(n);
    std::cout << "Enter the elements of the vector: ";
    for (int i = 0; i < n; i++)
    {
        std::cin >> arr[i];
    }

    bubbleSort(arr); // Sort the vector

    std::cout << "Sorted vector: ";
    for (int i = 0; i < n; i++)
    {
        std::cout << arr[i] << " ";
    }
    std::cout << "\n";

    return 0;
}