"""Adversarial checks for the Question 2 solution."""
import time

from q2_safe_haven import (EMPTY, RED, GREEN, OTHER, setup, neighbours,
                           components, standard_move, play)


def naive_setup(n, r, g):
    """Literal simulation: walk one square at a time, counting empty visits."""
    N = n * n
    board = [EMPTY] * (N + 1)
    board[1] = RED
    last = 1
    turn = GREEN
    while any(board[i] == EMPTY for i in range(1, N + 1)):
        need = r if turn == RED else g
        seen = 0
        pos = last
        while True:
            pos = pos % N + 1
            if board[pos] == EMPTY:
                seen += 1
                if seen == need:
                    break
        board[pos] = turn
        last = pos
        turn = OTHER[turn]
    return board


def check_setup():
    bad = 0
    for n in range(1, 8):
        for r in range(1, 26):
            for g in range(1, 26):
                if setup(n, r, g) != naive_setup(n, r, g):
                    bad += 1
                    print("  MISMATCH", n, r, g)
    print("  set-up: modular vs literal simulation, mismatches =", bad)
    assert bad == 0, "%d set-ups disagree with the literal simulation" % bad


def check_tiebreak():
    """The worked example in the paper: havens 1R/0G, 2R/3G, 4R/3G, 9R/4G."""
    havens = [(1, 0), (2, 3), (4, 3), (9, 4)]
    best = max(((-t, m, i) for i, (m, t) in enumerate(havens) if m and t))
    print("  tie-break picks haven index", best[2], "=", havens[best[2]],
          "(paper says the 4 Red / 3 Green one)")
    assert havens[best[2]] == (4, 3)


def check_games():
    worst = 0.0
    for n in range(1, 11):
        for (r, g) in ((1, 1), (5, 5), (2, 3), (17, 23), (5000, 5000),
                       (4999, 5000), (810, 2025), (49, 50), (1, 5000)):
            t0 = time.perf_counter()
            board = setup(n, r, g)
            nb = neighbours(n)
            N = n * n
            filled = sum(1 for p in range(1, N + 1) if board[p] != EMPTY)
            assert filled == N, (n, r, g)
            player = RED
            moves = 0
            while True:
                mv = standard_move(board, nb, N, player)
                if mv is None:
                    break
                q, t = mv
                assert board[q] == player and board[t] == OTHER[player]
                assert t in nb[q]
                board[q] = EMPTY
                board[t] = player
                moves += 1
                assert moves <= N + 5, "game not terminating"
                player = OTHER[player]
            # every surviving haven must be single-coloured
            for comp in components(board, nb, N):
                assert len({board[x] for x in comp}) == 1, (n, r, g, comp)
            dt = time.perf_counter() - t0
            worst = max(worst, dt)
    print("  games: all terminate with only safe havens; worst case %.3fs" % worst)


def check_timing_enhanced():
    t0 = time.perf_counter()
    res = play(10, 810, 2025, enhanced=True)
    print("  amended strategy 10 810 2025 -> %d %d  (%.3fs)" % (res[0], res[1],
                                                                time.perf_counter() - t0))


if __name__ == "__main__":
    print("Question 2 checks")
    check_setup()
    check_tiebreak()
    check_games()
    check_timing_enhanced()
    print("  n=1 (single square):", "%d %d" % play(1, 1, 1))
    print("  sample 3 5 5       :", "%d %d" % play(3, 5, 5))
