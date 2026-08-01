"""BIO 2025 Q2 parts (b), (c) and (d) - helper."""
import sys

from q2_safe_haven import EMPTY, RED, GREEN, setup, neighbours, play

LETTER = {EMPTY: ".", RED: "R", GREEN: "G"}


def show(board, n):
    for row in range(n):
        print("   " + " ".join(LETTER[board[row * n + c + 1]] for c in range(n)))


def main():
    print("== 2(b) set-up grid for  3 123456789 987654321 ==")
    b = setup(3, 123456789, 987654321)
    show(b, 3)
    print("   Red  :", [p for p in range(1, 10) if b[p] == RED])
    print("   Green:", [p for p in range(1, 10) if b[p] == GREEN])

    print()
    print("== 2(c) 4x4 chequerboard, r and g both < 50 ==")
    nb4 = neighbours(4)
    hits = []
    for r in range(1, 50):
        for g in range(1, 50):
            b = setup(4, r, g)
            if all(b[p] != b[q] for p in range(1, 17) for q in nb4[p]):
                hits.append((r, g))
    print("   solutions found:", len(hits))
    for r, g in hits[:20]:
        print("   r = %d, g = %d" % (r, g))
    if hits:
        r, g = hits[0]
        print("   grid for r=%d g=%d:" % (r, g))
        show(setup(4, r, g), 4)

    print()
    print("== 2(d) input 10 810 2025, amended strategy ==")
    print("   standard strategy :", "%d %d" % play(10, 810, 2025, enhanced=False))
    print("   amended  strategy :", "%d %d" % play(10, 810, 2025, enhanced=True))
    print()
    print("   set-up grid for 10 810 2025:")
    show(setup(10, 810, 2025), 10)


if __name__ == "__main__":
    main()
