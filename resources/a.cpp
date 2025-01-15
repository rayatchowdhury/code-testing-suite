// C++ program to sort an array using Bubble Sort

#include <algorithm>
#include <iostream>

// Function to sort an array using Bubble Sort
void bubbleSort(int arr[], int n)
{
    // Iterate over the array n-1 times
    for (int i = 0; i < n - 1; i++)
    {
        // Iterate over the unsorted part of the array
        for (int j = 0; j < n - i - 1; j++)
        {
            // If the current element is greater than the next element, swap them
            if (arr[j] > arr[j + 1])
            {
                std::swap(arr[j], arr[j + 1]);
            }
        }
    }
}

int main()
{
    int n;
    std::cout << "Enter the size of the array: ";
    std::cin >> n;

    int arr[n];
    std::cout << "Enter the elements of the array: ";
    for (int i = 0; i < n; i++)
    {
        std::cin >> arr[i];
    }

    // Sort the array using Bubble Sort
    bubbleSort(arr, n);

    std::cout << "Sorted array: ";
    for (int i = 0; i < n; i++)
    {
        std::cout << arr[i] << " ";
    }
    std::cout << "\n";

    return 0;
}