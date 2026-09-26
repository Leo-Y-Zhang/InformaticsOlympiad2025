"""Adversarial check for Question 3.

Independent brute force: walk every schedule explicitly with exact Fractions,
collect the event times of each individual schedule and take all pairwise
differences.  No memoisation, no integer scaling -- so it shares no machinery
with the submitted solver beyond the rules themselves.
"""
from fractions import Fraction
from itertools import product

from q3_short_fuse import count_periods, _scaled_periods

DONE = -1


def brute(times):
    f = len(times)
    periods = {Fraction(0)}

    def walk(rem, mode, now, events):
        opts = []
        for i in range(f):
            m = mode[i]
            if m == DONE:
                opts.append((DONE,))
            elif m == 0:
                opts.append((0, 1, 2))
            elif m == 1:
                opts.append((1, 2))
            else:
                opts.append((2,))
        for combo in product(*opts):
            burning = [i for i in range(f) if combo[i] > 0]
            if not burning:
                continue
            dt = min(Fraction(rem[i], combo[i]) for i in burning)
            now2 = now + dt
            for e in events:
                periods.add(now2 - e)
            rem2 = list(rem)
            mode2 = list(combo)
            for i in burning:
                rem2[i] -= combo[i] * dt
                if rem2[i] == 0:
                    mode2[i] = DONE
            walk(tuple(rem2), tuple(mode2), now2, events + [now2])

    walk(tuple(Fraction(t) for t in times), (0,) * f, Fraction(0), [Fraction(0)])
    return periods


def exact_set(times):
    per, scale = _scaled_periods(times)
    return {Fraction(p, scale) for p in per}


CASES = [
    [1], [5], [1, 1], [1, 2], [3, 5], [2, 3], [5000, 1], [7, 11],
    [1, 1, 1], [1, 2, 3], [3, 5, 7], [41, 52, 55], [19, 23, 24],
    [1, 1, 1, 1], [1, 2, 3, 4], [3, 5, 7, 11], [13, 19, 23, 29],
]


def check_written():
    """The answers WRITTEN_ANSWERS.md gives for 3(b) and 3(c), taken from the
    brute force rather than the solver. The maxima themselves need the long
    sweep in q3_search.py; what is pinned here is that the tuples named as
    reaching them do, and that the small cases quoted beside them are right."""
    F = Fraction
    assert sorted(brute([1, 2])) == [F(0), F(1, 2), F(3, 4), F(1), F(5, 4), F(3, 2),
                                     F(2), F(5, 2), F(3)], sorted(brute([1, 2]))
    assert sorted(brute([3, 5])) == [F(x, 4) for x in (0, 1, 2, 4, 6, 7, 8, 10, 11, 12,
                                                        13, 14, 16, 20, 22, 26, 32)]
    for times, want in (([7, 11], 17), ([2522, 4808], 17), ([41, 52, 55], 163),
                        ([3901, 3975, 4015], 163), ([1, 1], 7), ([1, 1, 1], 16)):
        assert len(brute(times)) == want, (times, len(brute(times)), want)
    print("written answers: 3(b) nine periods, 3(c) 17 and 163 where claimed")


if __name__ == "__main__":
    check_written()
    for c in CASES:
        a = brute(c)
        b = exact_set(c)
        status = "OK " if a == b else "DIFF"
        print("%-18s brute %5d   solver %5d   %s" % (c, len(a), len(b), status))
        assert a == b, (c, sorted(a ^ b)[:10])
    print("all cases agree exactly (values, not just counts)")
