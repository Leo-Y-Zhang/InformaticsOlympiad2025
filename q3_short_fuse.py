"""BIO 2025 Round One, Question 3(a): Short Fuse.

Input : f  (1 <= f <= 4) then f burn times, each 1..5000
Output: the number of distinct periods measurable with those fuses.

Model
-----
Decisions may only be taken at time 0 and at the instant a fuse finishes.
Each fuse has a mode: 0 unlit, 1 burning at one end, 2 burning at both ends.
Modes never decrease (a burning fuse cannot be paused or put out).
Remaining burn time r falls at `mode` per unit time; the fuse ends when r = 0.

A measurable period is t_j - t_i for two event instants of one schedule
(t = 0 counts as an event).  Because the future depends only on the current
state, the answer is the union, over every reachable decision state S, of
{0} together with the set of future event offsets from S -- and that set
memoises on the state, which keeps the search tiny.

All times are held as integers scaled by 2**(f+2); at most f halvings can
occur along any schedule, so the arithmetic stays exact.
"""
import sys
from fractions import Fraction
from itertools import product

NAME = "<your name>"
SCHOOL = "<your school/college>"

DONE = -1


def _scaled_periods(times):
    f = len(times)
    scale = 1 << (f + 2)
    init = tuple(t * scale for t in times)
    memo = {}

    def successors(rem, mode):
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
        out = []
        for combo in product(*opts):
            dt = None
            for i in range(f):
                if combo[i] > 0:
                    t = rem[i] // combo[i]
                    if dt is None or t < dt:
                        dt = t
            if dt is None:                  # nothing is burning: no further event
                continue
            rem2 = list(rem)
            mode2 = list(combo)
            for i in range(f):
                if combo[i] > 0:
                    rem2[i] -= combo[i] * dt
                    if rem2[i] == 0:
                        mode2[i] = DONE
            out.append((dt, tuple(rem2), tuple(mode2)))
        return out

    def future(state):
        got = memo.get(state)
        if got is not None:
            return got
        out = set()
        for dt, rem2, mode2 in successors(*state):
            out.add(dt)
            for x in future((rem2, mode2)):
                out.add(dt + x)
        memo[state] = out
        return out

    periods = {0}
    start = (init, (0,) * f)
    seen = set()
    stack = [start]
    while stack:
        state = stack.pop()
        if state in seen:
            continue
        seen.add(state)
        periods |= future(state)
        for dt, rem2, mode2 in successors(*state):
            stack.append((rem2, mode2))
    return periods, scale


def period_set(times):
    """Exact sorted list of every measurable period."""
    periods, scale = _scaled_periods(times)
    return sorted(Fraction(p, scale) for p in periods)


def count_periods(times):
    periods, _ = _scaled_periods(times)
    return len(periods)


def main():
    print("BIO 2025 Q3 Short Fuse - %s - %s" % (NAME, SCHOOL), file=sys.stderr)
    data = sys.stdin.read().split()
    f = int(data[0])
    times = [int(x) for x in data[1:1 + f]]
    print(count_periods(times))


if __name__ == "__main__":
    main()
