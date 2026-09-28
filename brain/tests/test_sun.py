from datetime import date

import pytest

from brain.planner import parse_hhmm
from brain.sun import sunset

# sunrise-sunset.org API, central London (51.5074, -0.1278), read 2026-09-28 (research/sources.csv)
CHECKED = {date(2026, 10, 3): "18:36", date(2026, 10, 10): "18:20", date(2026, 10, 17): "18:05",
           date(2026, 10, 24): "17:50", date(2026, 10, 31): "16:37", date(2026, 11, 7): "16:25",
           date(2026, 11, 14): "16:14"}


@pytest.mark.parametrize("day,expected", CHECKED.items())
def test_sunset_matches_the_checked_times(day, expected):
    assert abs(parse_hhmm(sunset(day)) - parse_hhmm(expected)) <= 1


def test_clocks_going_back_moves_sunset_an_hour_earlier():
    before, after = parse_hhmm(sunset(date(2026, 10, 24))), parse_hhmm(sunset(date(2026, 10, 25)))
    assert 55 <= before - after <= 65


def test_no_sunset_in_the_arctic_summer():
    assert sunset(date(2026, 6, 21), lat=78.2, lon=15.6, tz="Arctic/Longyearbyen") is None
