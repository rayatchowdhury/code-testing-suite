import random
import sys


def main():
    # Generate random test case
    # Example: generate random array
    n = random.randint(1, 10)

    print(n)
    arr = [random.randint(1, 100) for _ in range(n)]
    print(" ".join(map(str, arr)))


if __name__ == "__main__":
    main()
