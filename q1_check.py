"""Question 1(a): an independent brute force, in the spirit of q2_check and q3_check.

`q1_palindromic_sums.solve` is clever -- it scans upwards and stops at the first
hit, which is only correct if that scan order happens to encode the tie-break the
paper asks for. This enumerates *every* minimal-length representation and applies
the tie-break directly, then compares. Agreement over a range is evidence; the
scan being clever is not.

It also pins something the solver assumes silently: `solve` returns None when no
sum of three or fewer palindromes exists, and `main` would fail on that. Every
positive integer is a sum of three palindromes (Cilleruelo, Luca and Baxter,
2018), so None should never happen -- but nothing here checked.
"""
import sys
from itertools import combinations_with_replacement

from q1_palindromic_sums import is_pal, palindromes_upto, solve

# 5000, not a few hundred: below about 450 only nine values need three
# palindromes at all, so a small range leaves the three-palindrome tie-break
# almost untouched and a mutation of it survives. At 5000 it is 1003 values.
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 5000


def every_minimal(n, pals, pset):
    """All minimal-length palindromic sums for n, each ascending."""
    if is_pal(n):
        return [(n,)]

    pairs = [(p, n - p) for p in pals if p <= n - p and (n - p) in pset]
    if pairs:
        return sorted(pairs)

    triples = []
    for a, b in combinations_with_replacement(pals, 2):
        c = n - a - b
        if c < b:
            continue
        if c in pset:
            triples.append((a, b, c))
    return sorted(triples)


def main() -> int:
    pals = palindromes_upto(LIMIT)
    pset = set(pals)
    checked = 0
    ties = 0

    for n in range(1, LIMIT + 1):
        got = solve(n)
        if got is None:
            print(f"  FAIL n={n}: solve returned None; no sum of <= 3 palindromes found")
            return 1

        # the answer must be an answer at all, before it is the right one
        assert all(is_pal(x) for x in got), (n, got)
        assert sum(got) == n, (n, got)
        assert list(got) == sorted(got), (n, got)

        options = every_minimal(n, [p for p in pals if p <= n], pset)
        assert options, (n, "brute force found no representation")
        assert len(got) == len(options[0]), (
            n, f"solver used {len(got)} palindromes, minimum is {len(options[0])}"
        )

        # "lowest palindrome used, then highest palindrome used" is a preference
        # for each in turn: minimise the smallest, then MAXIMISE the largest.
        # Reading (2) the other way round -- minimising the largest -- disagrees
        # first at n = 201, where it wants 1 + 99 + 101 over the solver's
        # 1 + 9 + 191. Both are valid minimal sums, so the reading is what
        # decides, and the solver's own "largest possible partner" says which.
        want = min(options, key=lambda rep: (rep[0], -rep[-1]))
        if tuple(got) != want:
            print(f"  FAIL n={n}: solver {got}, tie-break says {list(want)}")
            return 1
        if len(options) > 1:
            ties += 1
        checked += 1

    print(f"  n = 1..{LIMIT}: {checked} agree with the brute force, "
          f"{ties} had more than one minimal representation")
    print(f"  longest sum needed over the range: "
          f"{max(len(solve(n)) for n in range(1, LIMIT + 1))} palindromes")
    print("all cases agree exactly (the representation, not just its length)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
