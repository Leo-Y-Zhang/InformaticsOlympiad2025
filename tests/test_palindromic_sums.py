from itertools import combinations_with_replacement

import pytest

from q1_palindromic_sums import is_pal, palindromes_upto, solve
from q1_written import all_sums


@pytest.mark.parametrize("number, expected", [(1, True), (101, True), (1001, True), (10, False), (123, False)])
def test_palindrome_predicate(number, expected):
    assert is_pal(number) is expected


@pytest.mark.parametrize("limit", [0, 1, 9, 10, 11, 99, 100, 101, 111, 999, 1001])
def test_generation_includes_endpoint_without_gaps_or_duplicates(limit):
    expected = [n for n in range(1, limit + 1) if str(n) == str(n)[::-1]]
    assert palindromes_upto(limit) == expected


@pytest.mark.parametrize("number, expected", [
    (1, [1]), (11, [11]), (12, [1, 11]), (20, [9, 11]),
    (54, [1, 9, 44]), (201, [1, 9, 191]), (1031, [1, 101, 929]),
])
def test_minimal_sum_and_both_tiebreaks(number, expected):
    assert solve(number) == expected


@pytest.mark.parametrize("number", [1, 12, 20, 21, 54, 201])
def test_all_minimal_representations_include_repeated_terms(number, q1_checker):
    # Literal digit tests and combinations provide an independent small oracle.
    pals = [n for n in range(1, number + 1) if str(n) == str(n)[::-1]]
    for length in (1, 2, 3):
        expected = [terms for terms in combinations_with_replacement(pals, length)
                    if sum(terms) == number]
        if expected:
            break
    assert all_sums(number) == expected
    assert q1_checker.every_minimal(number, pals, set(pals)) == expected
