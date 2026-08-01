"""BIO 2025 Round One, Question 1(a): Palindromic Sums.

Input : one integer n, 1 <= n <= 1000000
Output: the minimal-length palindromic sum for n, ascending, space separated.
        Ties broken by (1) lowest palindrome used, then (2) highest palindrome used.

The identifying banner is written to stderr so that stdout matches the sample
run exactly; change `file=sys.stderr` to print it on stdout if preferred.
"""
import sys
from bisect import bisect_right

NAME = "<your name>"
SCHOOL = "<your school/college>"


def is_pal(x):
    s = str(x)
    return s == s[::-1]


def palindromes_upto(limit):
    """All palindromic numbers 1..limit, ascending."""
    out = []
    h = 1
    while True:
        s = str(h)
        odd = int(s + s[-2::-1])
        even = int(s + s[::-1])
        if odd > limit and even > limit:
            break
        if odd <= limit:
            out.append(odd)
        if even <= limit:
            out.append(even)
        h += 1
    out.sort()
    return out


def solve(n):
    if is_pal(n):
        return [n]

    pals = palindromes_upto(n)
    pset = set(pals)

    # two palindromes: scanning upwards finds the smallest palindrome in any pair
    for p in pals:
        if (n - p) in pset:
            return sorted((p, n - p))

    # three palindromes: smallest first, then largest possible partner
    for a in pals:
        rest = n - a
        i = bisect_right(pals, rest - 1) - 1
        while i >= 0:
            c = pals[i]
            if (rest - c) in pset:
                return sorted((a, rest - c, c))
            i -= 1
    return None


def main():
    print("BIO 2025 Q1 Palindromic Sums - %s - %s" % (NAME, SCHOOL), file=sys.stderr)
    data = sys.stdin.read().split()
    n = int(data[0])
    print(" ".join(str(x) for x in solve(n)))


if __name__ == "__main__":
    main()
