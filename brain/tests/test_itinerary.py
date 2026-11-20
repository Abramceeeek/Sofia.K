"""WS3 (m210): a trip through several places, planned segment by segment with the one planner. The journeys and
places below are ILLUSTRATIVE (made-up times, approximate centres), not timetables."""
from datetime import date, datetime

import pytest

from brain import itinerary as it
from brain.config import DATA_DIR
from brain.moments import Point
from brain.places import Destination, load_destinations


def _dest(key, name, country, tz, currency):
    return Destination(key, name, country, None, tz, currency, (), Point(lat=0, lon=0), None, "none", "estimate", None)


DESTS = {**load_destinations(DATA_DIR / "destinations.yaml"),
         "paris": _dest("paris", "Paris", "FR", "Europe/Paris", "EUR"),
         "amsterdam": _dest("amsterdam", "Amsterdam", "NL", "Europe/Amsterdam", "EUR"),
         "vienna": _dest("vienna", "Vienna", "AT", "Europe/Vienna", "EUR")}

T = lambda *a: datetime(2026, *a)
# 10 days, 9 nights, Thu 22 - Sat 31 Oct 2026: clocks go back on Sun 25 Oct in the UK and the EU alike
EUROPE = it.Trip(
    start=date(2026, 10, 22),
    segments=(it.DestinationSegment("london", date(2026, 10, 22), 3,
                                    it.AccommodationStay("A London hotel", date(2026, 10, 22), date(2026, 10, 25))),
              it.DestinationSegment("paris", date(2026, 10, 25), 3),
              it.DestinationSegment("amsterdam", date(2026, 10, 28), 1),
              it.DestinationSegment("vienna", date(2026, 10, 30), 1)),
    transfers=(it.TransferSegment("london", "paris", "train", T(10, 25, 11, 0), T(10, 25, 14, 20)),
               it.TransferSegment("paris", "amsterdam", "train", T(10, 28, 10, 0), T(10, 28, 13, 20)),
               it.TransferSegment("amsterdam", "vienna", "train", T(10, 29, 19, 0), T(10, 30, 9, 0))),
    inbound=it.TransferSegment("london", "london", "flight", T(10, 22, 7, 0), T(10, 22, 10, 0)),
    outbound=it.TransferSegment("vienna", "vienna", "flight", T(10, 31, 15, 0), T(10, 31, 17, 0)))


def test_ten_days_through_four_places_with_a_night_on_board():
    ds = it.days(EUROPE, DESTS)
    assert len(ds) == 10 and [d.day.day for d in ds] == list(range(22, 32))
    assert [d.kind for d in ds] == ["arrival", "full", "full", "transfer", "full", "full", "transfer", "transfer",
                                    "arrival", "departure"]
    assert [d.destination for d in ds] == ["london"] * 4 + ["paris"] * 3 + ["amsterdam", "vienna", "vienna"]
    on_board = ds[7]
    assert "You sleep on board tonight." in on_board.notes and on_board.notes[0].startswith(
        "Leave Amsterdam by train at 19:00 (Amsterdam time).")
    assert ds[8].notes == ["Arrive in Vienna at 09:00 (Vienna time), after 14 h 00 min."]


def test_time_zones_and_the_clock_change_never_bend_a_journey():
    london_paris = EUROPE.transfers[0]
    assert london_paris.minutes(DESTS) == 140                       # 11:00 London to 14:20 Paris: 2 h 20, not 3 h 20
    night = it.TransferSegment("london", "paris", "train", T(10, 24, 23, 0), T(10, 25, 7, 0))
    # 23:00 in London (BST, 22:00 UTC) to 07:00 in Paris after the change (CET, 06:00 UTC): 8 h, though the wall
    # clocks alone, an hour apart on any other night, would say 7
    assert night.minutes(DESTS) == 8 * 60
    assert it.TransferSegment("paris", "london", "train", T(10, 26, 9, 0), T(10, 26, 9, 30)).minutes(DESTS) == 90


def test_each_place_is_one_request_to_the_same_planner_and_unchecked_places_say_so():
    reqs = it.segment_requests(EUROPE, DESTS, used={"london": ["m_bm_great_court"], "paris": ["x"]})
    assert [r["destination"] for r in reqs] == ["london"]           # only checked coverage gets planned places
    r = reqs[0]
    assert (r["start_date"], r["nights"], r["stay_name"]) == ("2026-10-22", 3, "A London hotel")
    assert r["arrive"] == {"mode": "flight", "time": "10:00"} and r["leave"] == {"mode": "train", "time": "11:00"}
    assert r["exclude"] == ["x"]                                    # moments planned elsewhere in the trip
    one = it.Trip(date(2026, 11, 20), (it.DestinationSegment("london", date(2026, 11, 20), 3),))
    assert [d.kind for d in it.days(one, DESTS)] == ["arrival", "full", "full", "departure"]   # today's trip


def test_a_missing_journey_is_a_gap_day_not_an_invented_train():
    trip = it.Trip(EUROPE.start, EUROPE.segments, transfers=EUROPE.transfers[1:], inbound=EUROPE.inbound)
    gap = it.days(trip, DESTS)[3]
    assert gap.kind == "gap" and gap.notes[0].startswith("How you get from London to Paris isn't set yet")


def test_dates_that_dont_fit_together_are_said_in_plain_words():
    bad = it.Trip(EUROPE.start, (EUROPE.segments[0], it.DestinationSegment("paris", date(2026, 10, 26), 3)),
                  transfers=EUROPE.transfers[:1])
    with pytest.raises(it.TripError, match="Paris starts on Mon 26 Oct, but after London it would be Sun 25 Oct"):
        it.days(bad, DESTS)
    backwards = it.TransferSegment("london", "paris", "train", T(10, 25, 14, 0), T(10, 25, 14, 30))
    assert any("arrives before it leaves" in p for p in it.validate(
        it.Trip(EUROPE.start, EUROPE.segments[:2], transfers=(backwards,)), DESTS))
    assert it.validate(EUROPE, DESTS) == []


def test_changing_one_place_or_a_delayed_journey_touches_only_its_own_days():
    # Paris's leaving day (the train into Amsterdam), Amsterdam's own, and Vienna's arrival (the night train out of it)
    assert it.affected_days(EUROPE, DESTS, "amsterdam") == [6, 7, 8]
    assert it.affected_days(EUROPE, DESTS, "london") == [0, 1, 2, 3]
