"""BIO 2025 Q3 parts (b) and (c) - helper."""
import sys
from fractions import Fraction
from math import gcd

from q3_short_fuse import period_set, count_periods


def fmt(x):
    return str(x.numerator) if x.denominator == 1 else "%d/%d" % (x.numerator, x.denominator)


def main():
    print("== 3(b) two fuses, burn times 1 and 2 ==")
    ps = period_set([1, 2])
    print("   count:", len(ps))
    print("   " + ", ".join(fmt(p) for p in ps))
    print("   decimal: " + ", ".join(str(float(p)) for p in ps))

    print()
    print("== 3(c) maximum with TWO fuses ==")
    best, arg = -1, None
    for a in range(1, 121):
        for b in range(a, 121):
            if gcd(a, b) != 1:
                continue
            c = count_periods([a, b])
            if c > best:
                best, arg = c, (a, b)
                print("   new best %d at %s" % (c, (a, b)))
    print("   MAX (2 fuses) =", best, "first at", arg)

    print()
    print("== 3(c) maximum with THREE fuses ==")
    LIM = 26
    best3, arg3 = -1, None
    for a in range(1, LIM + 1):
        for b in range(a, LIM + 1):
            for c in range(b, LIM + 1):
                if gcd(gcd(a, b), c) != 1:
                    continue
                k = count_periods([a, b, c])
                if k > best3:
                    best3, arg3 = k, (a, b, c)
                    print("   new best %d at %s" % (k, (a, b, c)))
    print("   MAX (3 fuses, values <= %d) = %d  first at %s" % (LIM, best3, arg3))


if __name__ == "__main__":
    main()
