from fractions import Fraction
from pathlib import Path
import runpy

import pytest

import q2_check
import q3_check
import q3_short_fuse


def small_q1_check(monkeypatch, checker, limit):
    monkeypatch.setattr(checker, "LIMIT", limit)
    # The million-value recount is independently run by the existing gate;
    # these tests exercise main's validation on small witnesses.
    monkeypatch.setattr(checker, "check_written", lambda: None)


def test_q1_checker_accepts_valid_answers(monkeypatch, q1_checker):
    small_q1_check(monkeypatch, q1_checker, 54)
    assert q1_checker.main() == 0


@pytest.mark.parametrize("corruption", [[2, 10], [1, 22], [11, 1], [1, 2, 9]])
def test_q1_checker_rejects_nonpalindrome_wrong_sum_order_and_length(monkeypatch, q1_checker, corruption):
    small_q1_check(monkeypatch, q1_checker, 12)
    original = q1_checker.solve
    monkeypatch.setattr(q1_checker, "solve", lambda n: corruption if n == 12 else original(n))
    with pytest.raises(AssertionError):
        q1_checker.main()


@pytest.mark.parametrize("number, corruption", [(12, None), (54, [2, 8, 44])])
def test_q1_checker_rejects_missing_answer_and_wrong_tiebreak(monkeypatch, q1_checker, number, corruption):
    small_q1_check(monkeypatch, q1_checker, number)
    original = q1_checker.solve
    monkeypatch.setattr(q1_checker, "solve", lambda n: corruption if n == number else original(n))
    assert q1_checker.main() == 1


def small_setup_check(monkeypatch):
    def small_range(*args):
        if args in ((1, 8), (1, 26), (1, 50)):
            return range(1, 3)
        return range(*args)
    monkeypatch.setattr(q2_check, "range", small_range, raising=False)


def test_q2_setup_checker_accepts_valid_boards(monkeypatch):
    small_setup_check(monkeypatch)
    q2_check.check_setup()


@pytest.mark.parametrize("corruption", ["colour", "truncated"])
def test_q2_setup_checker_rejects_changed_colour_and_truncation(monkeypatch, corruption):
    small_setup_check(monkeypatch)
    original = q2_check.setup

    def corrupt_setup(*args):
        board = original(*args)
        if corruption == "truncated":
            return board[:-1]
        board[1] = q2_check.GREEN
        return board

    monkeypatch.setattr(q2_check, "setup", corrupt_setup)
    with pytest.raises(AssertionError, match="set-ups disagree"):
        q2_check.check_setup()


def one_game(monkeypatch, board):
    # Stop after the first hand-built 2x2 game. If a corrupted move slips through
    # all assertions, the second setup raises RuntimeError and fails the test.
    monkeypatch.setattr(q2_check, "range", lambda *args: [2] if args == (1, 11) else range(*args), raising=False)
    boards = iter([board])

    def setup(*args):
        try:
            return next(boards)[:]
        except StopIteration:
            raise RuntimeError("checker accepted the corrupted game")

    monkeypatch.setattr(q2_check, "setup", setup)


def test_q2_game_checkers_accept_valid_games():
    q2_check.check_games()
    q2_check.check_enhanced_games()


@pytest.mark.parametrize("board, move", [
    ([0, 1, 2, 1, 2], (2, 1)),  # Adjacent, but colours are reversed.
    ([0, 1, 1, 1, 2], (1, 4)),  # Correct colours, but a diagonal capture.
])
def test_q2_game_checker_rejects_illegal_moves(monkeypatch, board, move):
    one_game(monkeypatch, board)
    # A second call means validation accepted the illegal first move. Raising
    # StopIteration there prevents a later invariant from masking that bug.
    moves = iter([move])
    monkeypatch.setattr(q2_check, "standard_move", lambda *args: next(moves))
    with pytest.raises(AssertionError):
        q2_check.check_games()


def test_q2_game_checker_rejects_premature_end_with_mixed_haven(monkeypatch):
    one_game(monkeypatch, [0, 1, 2, 1, 2])
    monkeypatch.setattr(q2_check, "standard_move", lambda *args: None)
    with pytest.raises(AssertionError):
        q2_check.check_games()


def test_q2_enhanced_checker_rejects_move_that_creates_no_haven(monkeypatch):
    one_game(monkeypatch, [0, 1, 2, 0, 2])
    moves = iter([(1, 2), None])
    monkeypatch.setattr(q2_check, "safe_making_move", lambda *args: next(moves))
    monkeypatch.setattr(q2_check, "standard_move", lambda *args: None)
    with pytest.raises(AssertionError) as caught:
        q2_check.check_enhanced_games()
    assert caught.value.args == ((2, 1, 1, (1, 2)),)


def test_q3_written_checker_accepts_valid_periods():
    q3_check.check_written()


def test_q3_written_checker_rejects_a_removed_period(monkeypatch):
    original = q3_check.brute

    def missing_period(times):
        periods = original(times)
        if times == [1, 2]:
            periods.remove(Fraction(3, 4))
        return periods

    monkeypatch.setattr(q3_check, "brute", missing_period)
    with pytest.raises(AssertionError):
        q3_check.check_written()


@pytest.mark.parametrize("corruption", ["value", "count"])
def test_q3_gate_rejects_changed_value_even_if_count_matches(monkeypatch, corruption):
    original = q3_short_fuse._scaled_periods

    def corrupt_periods(times):
        periods, scale = original(times)
        if times == [1]:
            periods = periods - {scale}
            if corruption == "value":
                periods.add(3 * scale)  # Same cardinality, impossible duration.
        return periods, scale

    monkeypatch.setattr(q3_short_fuse, "_scaled_periods", corrupt_periods)
    with pytest.raises(AssertionError):
        runpy.run_path(str(Path(q3_check.__file__)), run_name="__main__")
