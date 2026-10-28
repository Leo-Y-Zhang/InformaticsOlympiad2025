from fractions import Fraction

import pytest

from q3_short_fuse import _scaled_periods, count_periods, period_set
from q3_search import sweep2, sweep3
from q3_written import fmt


@pytest.mark.parametrize("times, expected", [
    ([1], [Fraction(0), Fraction(1, 2), Fraction(1)]),
    ([1, 2], [Fraction(0), Fraction(1, 2), Fraction(3, 4), Fraction(1),
              Fraction(5, 4), Fraction(3, 2), Fraction(2), Fraction(5, 2), Fraction(3)]),
])
def test_exact_periods_include_zero_and_fractional_event_differences(times, expected):
    assert period_set(times) == expected
    assert count_periods(times) == len(expected)
    scaled, scale = _scaled_periods(times)
    assert {Fraction(p, scale) for p in scaled} == set(expected)


def test_fuse_order_and_common_time_scaling():
    original = period_set([1, 2, 3])
    assert period_set([3, 1, 2]) == original
    assert period_set([2, 4, 6]) == [2 * p for p in original]
    assert count_periods([1, 1]) == 7
    assert count_periods([1, 1, 1]) == 16


@pytest.mark.parametrize("value, expected", [
    (Fraction(0), "0"), (Fraction(2), "2"), (Fraction(3, 2), "3/2"),
])
def test_fraction_output(value, expected):
    assert fmt(value) == expected


def test_small_searches_include_the_upper_bound():
    assert sweep2(1) == (7, (1, 1))
    assert sweep2(2) == (9, (1, 2))
    assert sweep3(1) == (16, (1, 1, 1))
