import pytest

from q2_safe_haven import (EMPTY, RED, GREEN, components, count_safe, neighbours,
                           safe_making_move, setup, standard_move, play)


def board_from_rows(*rows):
    colours = {".": EMPTY, "R": RED, "G": GREEN}
    return [EMPTY] + [colours[c] for row in rows for c in row]


def test_neighbours_do_not_wrap_or_include_diagonals():
    assert neighbours(1) == [[], []]
    assert neighbours(2) == [[], [2, 3], [1, 4], [1, 4], [2, 3]]
    nb = neighbours(3)
    assert nb[3] == [2, 6]
    assert nb[5] == [2, 4, 6, 8]
    assert nb[9] == [6, 8]


@pytest.mark.parametrize("r, g, expected", [
    (1, 1, [EMPTY, RED, GREEN, RED, GREEN]),
    (5, 2, [EMPTY, RED, GREEN, GREEN, RED]),
    (9, 10, [EMPTY, RED, GREEN, RED, GREEN]),
])
def test_setup_counts_empty_visits_and_wraps(r, g, expected):
    assert setup(2, r, g) == expected
    assert setup(1, r, g) == [EMPTY, RED]


def test_components_and_safe_counts_reject_a_changed_colour():
    nb = neighbours(4)
    board = board_from_rows("R.G.", ".G..", "....", "RR.G")
    assert components(board, nb, 16) == [[1], [3], [6], [13, 14], [16]]
    assert count_safe(board, nb, 16, RED) == 2
    assert count_safe(board, nb, 16, GREEN) == 3
    board[2] = RED  # Joins three previously separate havens into a mixed one.
    assert components(board, nb, 16) == [[1, 2, 3, 6], [13, 14], [16]]
    assert count_safe(board, nb, 16, RED) == 1
    assert count_safe(board, nb, 16, GREEN) == 1


@pytest.mark.parametrize("top, bottom, expected", [
    ("RRRGG", "RG...", (21, 22)),  # Fewest enemies wins over most own pieces.
    ("RRG..", "RG...", (2, 3)),    # Then most own pieces.
    ("RG...", "RG...", (21, 22)),  # Then highest square in the haven.
])
def test_standard_move_haven_priority(top, bottom, expected):
    board = board_from_rows(top, ".....", ".....", ".....", bottom)
    before = board[:]
    assert standard_move(board, neighbours(5), 25, RED) == expected
    assert board == before


def test_standard_move_uses_lowest_source_and_target():
    board = board_from_rows("RG", "GR")
    assert standard_move(board, neighbours(2), 4, RED) == (1, 2)
    assert standard_move(board, neighbours(2), 4, GREEN) == (2, 1)


@pytest.mark.parametrize("rows", [("..", ".."), ("RR", "RR"), ("GG", "GG"), ("R.", ".G")])
def test_single_colour_havens_cannot_be_captured(rows):
    board = board_from_rows(*rows)
    for player in (RED, GREEN):
        assert standard_move(board, neighbours(2), 4, player) is None


@pytest.mark.parametrize("player", [RED, GREEN])
def test_safe_making_move_creates_a_new_haven_and_restores_board(player):
    opponent = GREEN if player == RED else RED
    board = [EMPTY, player, opponent, opponent, EMPTY]
    before = board[:]
    assert safe_making_move(board, neighbours(2), 4, player) == (1, 2)
    assert board == before
    board[1], board[2] = EMPTY, player
    assert count_safe(board, neighbours(2), 4, player) == 1


def test_legal_capture_without_new_haven_is_not_a_safe_making_move():
    board = board_from_rows("RG", ".G")
    before = board[:]
    assert standard_move(board, neighbours(2), 4, RED) == (1, 2)
    assert safe_making_move(board, neighbours(2), 4, RED) is None
    assert board == before


@pytest.mark.parametrize("enhanced", [False, True])
def test_small_game_result(enhanced):
    assert play(1, 1, 1, enhanced=enhanced) == (1, 0)
    assert play(3, 5, 5, enhanced=enhanced) == (2, 1)
