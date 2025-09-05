#include <bits/stdc++.h>
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>
using namespace std;
using namespace __gnu_pbds;

/**
 * @brief Ordered set for efficient order statistics operations.
 *
 * This template uses the GNU Policy-Based Data Structure library to create
 * a set that supports order statistics operations in logarithmic time.
 */
template <class T>
using ordered_set = tree<T, null_type, less<T>, rb_tree_tag, tree_order_statistics_node_update>;

/**
 * @brief Generate a random value of type T in the range [l, r].
 *
 * This function uses a static random device and Mersenne Twister engine
 * to generate random values. It supports integral types, floating-point types,
 * and characters.
 *
 * @tparam T The type of the random value to generate.
 * @param l The lower bound of the range (inclusive).
 * @param r The upper bound of the range (inclusive).
 * @return A random value of type T in the range [l, r].
 * @throw invalid_argument If an unsupported type is used.
 */
template <typename T>
T random(T l, T r)
{
  static random_device rd;
  static mt19937_64 gen(rd());
  if (l > r)
    swap(l, r);
  if constexpr (is_floating_point_v<T>)
  {
    uniform_real_distribution<T> dist(l, r);
    return dist(gen);
  }
  else if constexpr (is_integral_v<T> && !is_same_v<T, char>)
  {
    uniform_int_distribution<T> dist(l, r);
    return dist(gen);
  }
  else if constexpr (is_same_v<T, char>)
  {
    uniform_int_distribution<int> dist(static_cast<int>(l), static_cast<int>(r));
    return static_cast<char>(dist(gen));
  }
  else
    throw invalid_argument("Unsupported type for random generation");
}

/**
 * @brief Select a random element from a vector.
 *
 * @tparam T The type of elements in the vector.
 * @param a The vector to select from.
 * @return A random element from the vector.
 */
template <typename T>
T random(const vector<T> &a)
{
  return a[random(0, static_cast<int>(a.size()) - 1)];
}

/**
 * @brief Select a random character from a string.
 *
 * @param s The string to select from.
 * @return A random character from the string.
 */
char random(const string &s)
{
  return s[random(0, static_cast<int>(s.size()) - 1)];
}

/**
 * @brief A vector of random elements.
 *
 * This class extends the standard vector to create a container
 * filled with random elements of a specified type.
 *
 * @tparam T The type of elements in the vector.
 * 
 * 
 * 
 */
template <typename T>
class rvector : public vector<T>
{
public:
  /**
   * @brief Create a vector of random elements in a specified range.
   *
   * @param length The number of elements in the vector.
   * @param l The lower bound of the range for random values.
   * @param r The upper bound of the range for random values.
   */
  rvector(size_t length, T l, T r)
  {
    this->resize(length);
    generate(this->begin(), this->end(), [=]()
             { return random(l, r); });
  }

  /**
   * @brief Create a vector of random elements selected from a given set.
   *
   * @param length The number of elements in the vector.
   * @param a The vector to select random elements from.
   */
  rvector(size_t length, const vector<T> &a)
  {
    this->resize(length);
    generate(this->begin(), this->end(), [=]()
             { return random(a); });
  }

  /**
   * @brief Print the elements of the vector.
   *
   * Outputs the elements of the vector in a space-separated format.
   */
  void print() const
  {
    for (const auto &x : *this)
      cout << x << " ";
    cout << "\n";
  }
};

/**
 * @brief A random permutation of integers.
 *
 * This class generates a random permutation of integers starting from a specified value.
 */
class permutation : public vector<int>
{
public:
  /**
   * @brief Create a random permutation of n integers.
   *
   * @param n The number of integers in the permutation.
   * @param start The starting value for the permutation (default is 1).
   */
  permutation(int n, int start = 1)
  {
    this->resize(n);
    iota(this->begin(), this->end(), start);
    shuffle(this->begin(), this->end(), mt19937(random_device()()));
  }

  /**
   * @brief Print the permutation.
   *
   * Outputs the elements of the permutation in a space-separated format.
   */
  void print() const
  {
    for (const auto &x : *this)
      cout << x << " ";
    cout << "\n";
  }
};

/**
 * @brief A vector of unique random elements.
 *
 * This class extends the standard vector to create a container
 * filled with unique random elements of a specified type.
 *
 * @tparam T The type of elements in the vector.
 */
template <typename T>
class unique_vector : public vector<T>
{
public:
  /**
   * @brief Create a vector of unique random elements in a specified range.
   *
   * @param n The number of unique elements to generate.
   * @param l The lower bound of the range for random values.
   * @param r The upper bound of the range for random values.
   * @throw invalid_argument If the range is too small for the requested number of unique elements.
   */
  unique_vector(size_t n, T l, T r)
  {
    if (l > r)
      swap(l, r);
    if (n > static_cast<size_t>(r - l + 1))
      throw invalid_argument("Range too small for requested number of unique elements");

    if (static_cast<size_t>(r - l + 1) <= 10 * n)
    {
      vector<T> v(r - l + 1);
      iota(v.begin(), v.end(), l);
      shuffle(v.begin(), v.end(), mt19937(random_device()()));
      this->assign(v.begin(), v.begin() + n);
    }
    else
    {
      unordered_set<T> s;
      while (s.size() < n)
        s.insert(random(l, r));
      this->assign(s.begin(), s.end());
    }
  }

  /**
   * @brief Print the unique elements of the vector.
   *
   * Outputs the elements of the vector in a space-separated format.
   */
  void print() const
  {
    for (const auto &x : *this)
      cout << x << " ";
    cout << "\n";
  }
};

/**
 * @brief A random string generator.
 *
 * This class extends the standard string to create a string
 * filled with random characters.
 */
class rstring : public string
{
public:
  /**
   * @brief Create a random string of specified length with characters in a given range.
   *
   * @param length The length of the string to generate.
   * @param l The lower bound of the character range.
   * @param r The upper bound of the character range.
   */
  rstring(size_t length, char l, char r)
  {
    this->resize(length);
    generate(this->begin(), this->end(), [=]()
             { return random(l, r); });
  }

  /**
   * @brief Create a random string of specified length with characters from a given set.
   *
   * @param length The length of the string to generate.
   * @param s The string containing the set of characters to choose from.
   */
  rstring(size_t length, const string &s)
  {
    this->resize(length);
    generate(this->begin(), this->end(), [=]()
             { return random(s); });
  }

  /**
   * @brief Print the random string.
   */
  void print() const
  {
    cout << *this << "\n";
  }
};

/**
 * @brief A random matrix generator.
 *
 * This class extends the standard vector of vectors to create a 2D matrix
 * filled with random elements of a specified type.
 *
 * @tparam T The type of elements in the matrix.
 */
template <typename T>
class rmatrix : public vector<vector<T>>
{
public:
  /**
   * @brief Create a random matrix with elements in a specified range.
   *
   * @param r The number of rows in the matrix.
   * @param c The number of columns in the matrix.
   * @param l The lower bound of the range for random values.
   * @param h The upper bound of the range for random values.
   */
  rmatrix(size_t r, size_t c, T l, T h)
  {
    this->resize(r, vector<T>(c));
    for (auto &row : *this)
    {
      for (auto &elem : row)
      {
        elem = random(l, h);
      }
    }
  }

  /**
   * @brief Create a random matrix with elements from a given set.
   *
   * @param r The number of rows in the matrix.
   * @param c The number of columns in the matrix.
   * @param values The vector containing the set of values to choose from.
   */
  rmatrix(size_t r, size_t c, const vector<T> &values)
  {
    this->resize(r, vector<T>(c));
    for (auto &row : *this)
    {
      for (auto &elem : row)
      {
        elem = random(values);
      }
    }
  }

  /**
   * @brief Create a random character matrix with elements from a given string.
   *
   * @param r The number of rows in the matrix.
   * @param c The number of columns in the matrix.
   * @param s The string containing the set of characters to choose from.
   */
  template <typename U = T, typename = enable_if_t<is_same_v<U, char>>>
  rmatrix(size_t r, size_t c, const string &s)
  {
    this->resize(r, vector<T>(c));
    for (auto &row : *this)
    {
      for (auto &elem : row)
      {
        elem = random(s);
      }
    }
  }

  /**
   * @brief Print the matrix.
   *
   * @param separator The separator to use between elements (default is space).
   */
  void print(const string &separator = " ") const
  {
    for (const auto &row : *this)
    {
      for (size_t i = 0; i < row.size(); ++i)
      {
        if (i > 0)
          cout << separator;
        cout << row[i];
      }
      cout << "\n";
    }
  }
};

/**
 * @brief Base class for graph generators.
 *
 * This class provides common functionality for various types of graph generators.
 *
 * @tparam WeightType The type of weights for weighted graphs.
 */
template <typename WeightType = long long>
class GraphBase
{
protected:
  vector<array<long long, 2>> edges;
  vector<WeightType> weights;
  bool isWeighted = false;

public:
  /**
   * @brief Print the edges and weights (if weighted) of the graph.
   */
  void print() const
  {
    for (size_t i = 0; i < edges.size(); ++i)
    {
      cout << edges[i][0] << " " << edges[i][1];
      if (isWeighted)
        cout << " " << weights[i];
      cout << "\n";
    }
  }
};

/**
 * @brief Random tree generator.
 *
 * This class generates random trees with a specified number of vertices.
 *
 * @tparam WeightType The type of weights for weighted trees.
 */
template <typename WeightType = long long>
class Tree : public GraphBase<WeightType>
{
private:
  void generateEdges(int n)
  {
    if (n <= 0)
    {
      throw invalid_argument("Number of vertices in a tree must be positive");
    }
    permutation perm(n);
    for (int i = 1; i < n; i++)
    {
      long long u = perm[i];
      long long v = perm[random(0, i - 1)];
      this->edges.push_back({u, v});
    }
  }

public:
  /**
   * @brief Create an unweighted tree with n vertices.
   *
   * @param n The number of vertices in the tree.
   */
  Tree(int n)
  {
    generateEdges(n);
  }

  /**
   * @brief Create a weighted tree with n vertices and weights in a specified range.
   *
   * @tparam T The type of the weight range bounds.
   * @param n The number of vertices in the tree.
   * @param l The lower bound of the weight range.
   * @param r The upper bound of the weight range.
   */
  template <typename T>
  Tree(int n, T l, T r) : Tree(n)
  {
    for (int i = 0; i < n - 1; i++)
      this->weights.push_back(random(l, r));
    this->isWeighted = true;
  }
};

/**
 * @brief Random binary tree generator.
 *
 * This class generates random binary trees with a specified number of nodes.
 *
 * @tparam WeightType The type of weights for weighted binary trees.
 */
template <typename WeightType = long long>
class BinaryTree : public GraphBase<WeightType>
{
private:
  // Generate random binary tree with n nodes
  void generateEdges(int n)
  {
    if (n <= 0)
    {
      throw invalid_argument("Number of nodes must be positive");
    }
    permutation perm(n);
    vector<int> children_count(n, 0);
    for (int i = 1; i < n; ++i)
    {
      long long u = perm[i];
      long long v = -1;
      while (true)
      {
        v = perm[random(0, i - 1)];
        if (children_count[v] < 2)
          break;
      }
      this->edges.push_back({u, v});
      children_count[v]++;
    }
  }

public:
  /**
   * @brief Create an unweighted binary tree with n nodes.
   *
   * @param n The number of nodes in the binary tree.
   */
  BinaryTree(int n)
  {
    generateEdges(n);
  }

  /**
   * @brief Create a weighted binary tree with n nodes and weights in a specified range.
   *
   * @tparam T The type of the weight range bounds.
   * @param n The number of nodes in the binary tree.
   * @param l The lower bound of the weight range.
   * @param r The upper bound of the weight range.
   */
  template <typename T>
  BinaryTree(int n, T l, T r) : BinaryTree(n)
  {
    for (int i = 0; i < n - 1; ++i)
      this->weights.push_back(random(l, r));
    this->isWeighted = true;
  }
};

/**
 * @brief Random graph generator.
 *
 * This class generates random graphs with a specified number of vertices and edges.
 *
 * @tparam WeightType The type of weights for weighted graphs.
 */
template <typename WeightType = long long>
class Graph : public GraphBase<WeightType>
{
private:
  // Generate random graph with n vertices and m edges
  void generateEdges(int n, int m)
  {
    if (n < 0 || m < 0)
      throw invalid_argument("Number of vertices and edges in a graph must be non-negative");
    set<array<long long, 2>> edgeSet;
    permutation perm(n);
    for (int i = 1; i < n && edgeSet.size() < m; i++)
    {
      long long u = perm[i];
      long long v = perm[random(0, i - 1)];
      if (edgeSet.find({u, v}) == edgeSet.end())
        edgeSet.insert({u, v});
    }
    while (edgeSet.size() < m)
    {
      long long u = random(1, n);
      long long v = random(1, n);
      if (u != v && edgeSet.find({u, v}) == edgeSet.end())
        edgeSet.insert({u, v});
    }
    this->edges.assign(edgeSet.begin(), edgeSet.end());
  }

public:
  /**
   * @brief Create an unweighted graph with n vertices and m edges.
   *
   * @param n The number of vertices in the graph.
   * @param m The number of edges in the graph.
   */
  Graph(int n, int m)
  {
    generateEdges(n, m);
  }

  /**
   * @brief Create a weighted graph with n vertices, m edges, and weights in a specified range.
   *
   * @tparam T The type of the weight range bounds.
   * @param n The number of vertices in the graph.
   * @param m The number of edges in the graph.
   * @param l The lower bound of the weight range.
   * @param r The upper bound of the weight range.
   */
  template <typename T>
  Graph(int n, int m, T l, T r) : Graph(n, m)
  {
    for (int i = 0; i < m; i++)
      this->weights.push_back(random(l, r));
    this->isWeighted = true;
  }
};

/**
 * @brief Random 2D points generator.
 *
 * This class generates a vector of random 2D points.
 */
class points : public vector<pair<int, int>>
{
public:
  /**
   * @brief Create n random points with x and y coordinates in a specified range.
   *
   * @param n The number of points to generate.
   * @param l The lower bound for both x and y coordinates.
   * @param r The upper bound for both x and y coordinates.
   */
  points(int n, int l, int r)
  {
    this->resize(n);
    for (auto &p : *this)
    {
      p = {random(l, r), random(l, r)};
    }
  }
  /**
   * @brief Create n random points with x and y coordinates in separate specified ranges.
   *
   * @param n The number of points to generate.
   * @param lx The lower bound for x coordinates.
   * @param rx The upper bound for x coordinates.
   * @param ly The lower bound for y coordinates.
   * @param ry The upper bound for y coordinates.
   */
  points(int n, int lx, int rx, int ly, int ry)
  {
    this->resize(n);
    for (auto &p : *this)
      p = {random(lx, rx), random(ly, ry)};
  }
  /**
   * @brief Print the generated points.
   *
   * Outputs each point as a pair of x and y coordinates.
   */
  void print() const
  {
    for (const auto &p : *this)
    {
      cout << p.first << " " << p.second << "\n";
    }
  }
};