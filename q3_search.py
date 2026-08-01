"""BIO 2025 Q3(c) - wider search for the maxima.

The number of measurable periods depends only on the *ratios* of the burn
times (scaling every fuse scales every period), so the maximum is attained at
a 'generic' ratio inside the best chamber of the arrangement.  We therefore
(1) sweep all coprime tuples up to a bound, and (2) random-sample large tuples
up to 5000, and check the two agree.
"""
import random
import sys
import time
from math import gcd

from q3_short_fuse import count_periods

random.seed(20250101)


def sweep2(limit):
    best, arg = -1, None
    for a in range(1, limit + 1):
        for b in range(a, limit + 1):
            if gcd(a, b) != 1:
                continue
            k = count_periods([a, b])
            if k > best:
                best, arg = k, (a, b)
    return best, arg


def sweep3(limit):
    best, arg = -1, None
    for a in range(1, limit + 1):
        for b in range(a, limit + 1):
            for c in range(b, limit + 1):
                if gcd(gcd(a, b), c) != 1:
                    continue
                k = count_periods([a, b, c])
                if k > best:
                    best, arg = k, (a, b, c)
    return best, arg


def sample(f, trials, hi=5000):
    best, arg = -1, None
    for _ in range(trials):
        t = sorted(random.randint(1, hi) for _ in range(f))
        k = count_periods(t)
        if k > best:
            best, arg = k, tuple(t)
    return best, arg


def main():
    print("TWO FUSES")
    for lim in (40, 80, 160, 320):
        t0 = time.perf_counter()
        b, a = sweep2(lim)
        print("  sweep <=%4d : max %4d at %-14s (%.1fs)" % (lim, b, a, time.perf_counter() - t0))
    for n in (20000, 100000):
        t0 = time.perf_counter()
        b, a = sample(2, n)
        print("  random %6d : max %4d at %-20s (%.1fs)" % (n, b, a, time.perf_counter() - t0))

    print()
    print("THREE FUSES")
    for lim in (20, 30, 40, 50, 60):
        t0 = time.perf_counter()
        b, a = sweep3(lim)
        print("  sweep <=%4d : max %4d at %-16s (%.1fs)" % (lim, b, a, time.perf_counter() - t0))
        sys.stdout.flush()
    for n in (20000, 100000, 300000):
        t0 = time.perf_counter()
        b, a = sample(3, n)
        print("  random %6d : max %4d at %-24s (%.1fs)" % (n, b, a, time.perf_counter() - t0))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
