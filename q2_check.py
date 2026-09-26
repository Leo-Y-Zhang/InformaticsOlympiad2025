"""Adversarial checks for the Question 2 solution."""
import time

from q2_safe_haven import (EMPTY, RED, GREEN, OTHER, setup, neighbours,
                           components, count_safe, standard_move,
                           safe_making_move, play)


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
    cases = 0
    for n in range(1, 8):
        for r in range(1, 26):
            for g in range(1, 26):
                cases += 1
                if setup(n, r, g) != naive_setup(n, r, g):
                    bad += 1
                    print("  MISMATCH", n, r, g)
    # The 4x4 board again with r and g up to 49. WRITTEN_ANSWERS.md said this
    # range was covered and it was not: the sweep in q2_written.py that goes to
    # 50 only asks whether the board came out chequered, and never calls
    # naive_setup. It is worth having, because a count of 49 on 16 squares
    # wraps the cyclic walk three times over, so an off-by-one in `setup`'s
    # modular shortcut has to survive more wraps than r <= 25 ever forces.
    for r in range(1, 50):
        for g in range(1, 50):
            cases += 1
            if setup(4, r, g) != naive_setup(4, r, g):
                bad += 1
                print("  MISMATCH", 4, r, g)
    print("  set-up: modular vs literal simulation over", cases,
          "cases, mismatches =", bad)
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


def check_enhanced_games():
    """2(d)'s amended strategy had no check beyond its running time. Every
    move it takes must be legal, every safe-haven-first move must really add a
    safe haven for the mover, and every game must still end with nothing but
    single-coloured havens."""
    games = 0
    for n in range(1, 11):
        for (r, g) in ((1, 1), (5, 5), (2, 3), (17, 23), (5000, 5000),
                       (4999, 5000), (810, 2025), (49, 50), (1, 5000)):
            board = setup(n, r, g)
            nb = neighbours(n)
            N = n * n
            player = RED
            moves = 0
            while True:
                before = count_safe(board, nb, N, player)
                mv = safe_making_move(board, nb, N, player)
                made = mv is not None
                if mv is None:
                    mv = standard_move(board, nb, N, player)
                if mv is None:
                    break
                q, t = mv
                assert board[q] == player and board[t] == OTHER[player], (n, r, g, mv)
                assert t in nb[q], (n, r, g, mv)
                board[q] = EMPTY
                board[t] = player
                if made:
                    assert count_safe(board, nb, N, player) > before, (n, r, g, mv)
                moves += 1
                assert moves <= N + 5, "game not terminating"
                player = OTHER[player]
            for comp in components(board, nb, N):
                assert len({board[x] for x in comp}) == 1, (n, r, g, comp)
            games += 1
    print("  amended games: %d terminate, every move legal, every safe-haven-first"
          " move adds one" % games)


def check_written():
    """The answers WRITTEN_ANSWERS.md gives for 2(b), 2(c) and 2(d).

    2(c) is taken from naive_setup, the literal simulation, not from the
    modular `setup` the program uses, so the claim that (25, 41) is the only
    pair is checked against the rules rather than against the code that
    produced it. 2(b) has to use `setup`: walking 987654321 squares one at a
    time is not a check anyone would wait for.
    """
    b = setup(3, 123456789, 987654321)
    assert [p for p in range(1, 10) if b[p] == RED] == [1, 3, 4, 8, 9], b
    assert [p for p in range(1, 10) if b[p] == GREEN] == [2, 5, 6, 7], b

    nb4 = neighbours(4)
    chequered = []
    for r in range(1, 50):
        for g in range(1, 50):
            b = naive_setup(4, r, g)
            if all(b[p] != b[q] for p in range(1, 17) for q in nb4[p]):
                chequered.append((r, g))
    assert chequered == [(25, 41)], chequered

    assert play(10, 810, 2025, enhanced=True) == (20, 17)
    assert play(10, 810, 2025) == (10, 5)
    print("  written answers: 2(b) grid, 2(c) only (25, 41), 2(d) 20 17 (unamended 10 5)")


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
    check_enhanced_games()
    check_written()
    check_timing_enhanced()
    print("  n=1 (single square):", "%d %d" % play(1, 1, 1))
    print("  sample 3 5 5       :", "%d %d" % play(3, 5, 5))
