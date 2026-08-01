"""BIO 2025 Round One, Question 2(a): Safe Haven.

Input : n r g   (1 <= n <= 10, 1 <= r,g <= 5000)
Output: <red safe havens> <green safe havens>

`play(n, r, g, enhanced=True)` implements the amended strategy of part 2(d).
"""
import sys

NAME = "<your name>"
SCHOOL = "<your school/college>"

EMPTY, RED, GREEN = 0, 1, 2
OTHER = {RED: GREEN, GREEN: RED}


def neighbours(n):
    N = n * n
    nb = [[] for _ in range(N + 1)]
    for p in range(1, N + 1):
        row, col = (p - 1) // n, (p - 1) % n
        if row > 0:
            nb[p].append(p - n)
        if col > 0:
            nb[p].append(p - 1)
        if col < n - 1:
            nb[p].append(p + 1)
        if row < n - 1:
            nb[p].append(p + n)
        nb[p].sort()
    return nb


def setup(n, r, g):
    """Alternate claiming of squares until the grid is full."""
    N = n * n
    board = [EMPTY] * (N + 1)
    board[1] = RED
    last = 1
    turn = GREEN
    remaining = N - 1
    while remaining:
        step = r if turn == RED else g
        start = last % N + 1
        # empty squares in the cyclic order they will be visited
        empties = [q for q in
                   (((start - 1 + k) % N) + 1 for k in range(N))
                   if board[q] == EMPTY]
        pos = empties[(step - 1) % len(empties)]
        board[pos] = turn
        last = pos
        remaining -= 1
        turn = OTHER[turn]
    return board


def components(board, nb, N):
    """Havens: maximal connected groups of non-empty squares."""
    seen = [False] * (N + 1)
    comps = []
    for p in range(1, N + 1):
        if board[p] != EMPTY and not seen[p]:
            seen[p] = True
            stack = [p]
            comp = []
            while stack:
                q = stack.pop()
                comp.append(q)
                for x in nb[q]:
                    if board[x] != EMPTY and not seen[x]:
                        seen[x] = True
                        stack.append(x)
            comp.sort()
            comps.append(comp)
    return comps


def count_safe(board, nb, N, player):
    total = 0
    for comp in components(board, nb, N):
        if all(board[q] == player for q in comp):
            total += 1
    return total


def standard_move(board, nb, N, player):
    opp = OTHER[player]
    best_key = None
    best_comp = None
    for comp in components(board, nb, N):
        mine = sum(1 for q in comp if board[q] == player)
        theirs = len(comp) - mine
        if mine == 0 or theirs == 0:        # safe haven
            continue
        key = (-theirs, mine, comp[-1])      # fewest theirs, most mine, highest position
        if best_key is None or key > best_key:
            best_key = key
            best_comp = comp
    if best_comp is None:
        return None
    for q in best_comp:
        if board[q] == player:
            targets = [x for x in nb[q] if board[x] == opp]
            if targets:
                return (q, min(targets))
    return None


def safe_making_move(board, nb, N, player):
    """2(d): lowest move that creates at least one new safe haven for `player`."""
    opp = OTHER[player]
    base = count_safe(board, nb, N, player)
    for q in range(1, N + 1):
        if board[q] != player:
            continue
        for t in nb[q]:
            if board[t] != opp:
                continue
            board[q], board[t] = EMPTY, player
            made = count_safe(board, nb, N, player) > base
            board[q], board[t] = player, opp
            if made:
                return (q, t)
    return None


def play(n, r, g, enhanced=False):
    N = n * n
    board = setup(n, r, g)
    nb = neighbours(n)
    player = RED
    while True:
        move = safe_making_move(board, nb, N, player) if enhanced else None
        if move is None:
            move = standard_move(board, nb, N, player)
        if move is None:
            break
        q, t = move
        board[q] = EMPTY
        board[t] = player
        player = OTHER[player]
    red = count_safe(board, nb, N, RED)
    green = count_safe(board, nb, N, GREEN)
    return red, green


def main():
    print("BIO 2025 Q2 Safe Haven - %s - %s" % (NAME, SCHOOL), file=sys.stderr)
    data = sys.stdin.read().split()
    n, r, g = int(data[0]), int(data[1]), int(data[2])
    red, green = play(n, r, g)
    print("%d %d" % (red, green))


if __name__ == "__main__":
    main()
