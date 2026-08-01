"""BIO 2025 Q1 parts (b) and (c) - helper.

(b) every palindromic sum representing 54
(c) how many n in 1..1000000 need three palindromes
"""
import sys

from q1_palindromic_sums import is_pal, palindromes_upto, solve

LIMIT = 1000000


def all_sums(n):
    """Every minimal-length palindromic sum for n (as sorted tuples)."""
    pals = palindromes_upto(n)
    pset = set(pals)
    if is_pal(n):
        return [(n,)]
    pairs = sorted({tuple(sorted((p, n - p))) for p in pals if (n - p) in pset})
    if pairs:
        return pairs
    out = set()
    for i, a in enumerate(pals):
        for b in pals[i:]:
            c = n - a - b
            if c >= b and c in pset:
                out.add((a, b, c))
    return sorted(out)


def main():
    print("== 1(b) palindromic sums for 54 ==")
    for s in all_sums(54):
        print("  54 = " + " + ".join(str(x) for x in s))
    print("  program would print:", " ".join(str(x) for x in solve(54)))

    print()
    print("== 1(c) counts over 1..%d ==" % LIMIT)
    pals = palindromes_upto(LIMIT)
    full = (1 << (LIMIT + 1)) - 2                      # bits 1..LIMIT set

    one = 0
    for p in pals:
        one |= 1 << p
    one &= full

    two = 0
    for p in pals:
        two |= one << p
    two &= full

    three = 0
    for p in pals:
        three |= two << p
    three &= full

    n1 = bin(one).count("1")
    n2 = bin(two & ~one).count("1")
    n3 = bin(three & ~two & ~one).count("1")
    missed = bin(full & ~three & ~two & ~one).count("1")

    print("  palindromes (need 1)      :", n1)
    print("  need exactly 2            :", n2)
    print("  need exactly 3  ->  ANSWER:", n3)
    print("  need 4 or more (expect 0) :", missed)
    print("  total check               :", n1 + n2 + n3 + missed, "==", LIMIT)


if __name__ == "__main__":
    main()
