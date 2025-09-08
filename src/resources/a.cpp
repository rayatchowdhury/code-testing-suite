/**
 * @file main.cpp
 * @brief This program demonstrates two fundamental algorithms: Bubble Sort and
 *        Longest Increasing Subsequence (LIS) using Dynamic Programming.
 *        It prompts the user to input a vector of integers, sorts this vector
 *        using the Bubble Sort algorithm, and then calculates the length of the
 *        Longest Increasing Subsequence within the *sorted* vector.
 *
 * The program is structured into three main parts:
 * 1. `bubbleSort`: An in-place sorting algorithm with O(N^2) time complexity.
 * 2. `findLongestIncreasingSubsequenceLength`: A Dynamic Programming approach
 *    to find the LIS length, also with O(N^2) time complexity.
 * 3. `main`: Handles user input, calls the sorting and LIS functions, and
 *    prints the results.
 *
 * @usage
 * To compile this program, use a C++ compiler (like g++):
 * `g++ -o vector_analysis main.cpp -std=c++11`
 *
 * To run the program:
 * `./vector_analysis`
 *
 * Follow the prompts in the console to enter the size and elements of your vector.
 */

#include <algorithm> // Required for std::max and std::swap
#include <iostream>  // Required for std::cout, std::cin
#include <vector>    // Required for std::vector

/**
 * @brief Sorts a vector of integers in ascending order using the Bubble Sort algorithm.
 *
 * Bubble Sort is a simple sorting algorithm that repeatedly steps through the list,
 * compares adjacent elements, and swaps them if they are in the wrong order.
 * This process continues until no swaps are needed in a pass, indicating the
 * list is sorted. This particular implementation performs a fixed number of passes.
 *
 * @param arr A reference to the vector of integers to be sorted. The vector will
 *            be modified in-place to contain the sorted elements.
 *
 * @complexity
 * - Time Complexity: O(N^2) in the worst and average case, where N is the number of
 *                    elements in the vector. This is due to the two nested loops,
 *                    each iterating up to N times.
 * - Space Complexity: O(1) as it sorts the array in-place without requiring additional
 *                     significant memory proportional to N.
 *
 * @edge_cases
 * - An empty vector: The loops will not execute, and the function will return
 *   without modification, which is the correct behavior.
 * - A vector with one element: The loops will not execute, and the function will
 *   return without modification, which is correct.
 * - A pre-sorted vector: The algorithm will still perform all comparisons,
 *   resulting in O(N^2) time complexity, but no swaps will occur. An optimized
 *   version might include a flag to detect if no swaps happened in a pass, allowing
 *   early termination. This implementation does not include that optimization.
 */
void bubbleSort(std::vector<int>& arr)
{
    // n: Stores the number of elements currently in the vector `arr`.
    // This value determines the bounds for the sorting loops.
    int n = arr.size();

    // Outer loop: Controls the number of passes.
    // In each pass, the largest unsorted element "bubbles" up to its correct position
    // at the end of the unsorted portion of the array.
    // After 'i' passes, the last 'i' elements are guaranteed to be sorted.
    // We need `n - 1` passes in the worst case.
    for (int i = 0; i < n - 1; i++)
    {
        // Inner loop: Iterates through the unsorted portion of the array.
        // It compares adjacent elements and swaps them if they are in the wrong order.
        // The upper bound `n - i - 1` ensures that we only iterate through the unsorted
        // part of the array, avoiding elements that have already been placed in their
        // final sorted position (i.e., the last 'i' elements).
        for (int j = 0; j < n - i - 1; j++)
        {
            // Compare adjacent elements. If the current element `arr[j]` is greater than
            // the next element `arr[j + 1]`, they are out of ascending order.
            if (arr[j] > arr[j + 1])
            {
                // Swap elements to put them in ascending order.
                std::swap(arr[j], arr[j + 1]);
            }
        }
    }
}

/**
 * @brief Finds the length of the Longest Increasing Subsequence (LIS) in a given vector.
 *
 * This function utilizes Dynamic Programming to solve the LIS problem. An increasing
 * subsequence is a subsequence in which the elements are in strictly increasing order.
 * The goal is to find the longest such subsequence within the input vector.
 * The approach has a time complexity of O(N^2).
 *
 * @param arr A constant reference to the vector of integers to analyze. The vector
 *            is not modified by this function.
 * @return The length of the Longest Increasing Subsequence found in the input vector.
 *
 * @complexity
 * - Time Complexity: O(N^2), where N is the number of elements in the vector.
 *                    This is due to the two nested loops iterating through the array.
 * - Space Complexity: O(N) for storing the `dp` array, which keeps track of LIS lengths.
 *
 * @edge_cases
 * - An empty vector: Returns 0, as an empty vector contains no subsequences.
 * - A vector with one element: Returns 1, as the element itself forms an LIS of length 1.
 * - A strictly decreasing vector (e.g., {5, 4, 3, 2, 1}): Returns 1, as each
 *   element can only form an LIS of length 1 by itself.
 * - A vector with duplicate elements (e.g., {1, 2, 2, 3}): Only strictly increasing
 *   subsequences are considered. The LIS here would be {1, 2, 3} with length 3.
 */
int findLongestIncreasingSubsequenceLength(const std::vector<int>& arr)
{
    // n: Stores the number of elements in the input vector `arr`.
    int n = arr.size();

    // Edge case: If the array is empty, there is no subsequence, so the LIS length is 0.
    if (n == 0)
    {
        return 0;
    }

    // dp: A vector used for dynamic programming.
    // dp[i] will store the length of the Longest Increasing Subsequence (LIS)
    // that ends with the element arr[i].
    // Initialization: Every element itself forms an LIS of length 1.
    std::vector<int> dp(n, 1);

    // maxLength: Stores the overall maximum LIS length found across all elements
    // in the vector. It is initialized to 1 because even a single-element array
    // has an LIS of length 1.
    int maxLength = 1;

    // Outer loop: Iterates through the array starting from the second element (index 1)
    // up to the last element. For each element `arr[i]`, we try to determine the
    // longest increasing subsequence that can *end* with `arr[i]`.
    for (int i = 1; i < n; i++)
    {
        // Inner loop: Compares `arr[i]` with all previous elements `arr[j]` (where `j < i`).
        // This is to check if `arr[i]` can extend any existing LIS that ends at `arr[j]`.
        for (int j = 0; j < i; j++)
        {
            // Condition for extending an LIS:
            // If `arr[i]` is strictly greater than `arr[j]`, it means `arr[i]` can be
            // appended to an increasing subsequence that ends at `arr[j]`.
            if (arr[i] > arr[j])
            {
                // Update `dp[i]`:
                // We compare the current length of LIS ending at `arr[i]` (`dp[i]`)
                // with a potential new length: `dp[j] + 1`.
                // `dp[j] + 1` represents the length of an LIS ending at `arr[j]`
                // plus `arr[i]` itself (hence +1).
                // We take the maximum of these two values to ensure `dp[i]` always stores
                // the true maximum LIS length that ends at `arr[i]`.
                dp[i] = std::max(dp[i], dp[j] + 1);
            }
        }
        // After checking all previous elements for `