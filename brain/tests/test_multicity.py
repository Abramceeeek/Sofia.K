"""m237 (WS3, Global Destination Intelligence): London -> Paris -> Amsterdam -> Brussels, as Abram asked, through the
hard cases: the clocks going forward on the travel day, different clocks either side of the Channel, a night bus, a
missed train (later the same day, or the next day), and one place's nights changing with or without moving the trip's
end. **The journeys are SAMPLE times, made up for testing, not timetables.** City centres are approximate. Nothing is
planned outside London (only London has checked coverage), and today's single-city trips are unchanged."""
from datetime import date, datetime

import pytest

from brain import itinerary as it
from brain.config import DATA_DIR
from brain.moments import Point
from brain.places import Destination, load_destinations


def _dest(key, name, country, tz, lat, lon):
    return Destination(key, name, country, None, tz, "EUR", (), Point(lat=lat, lon=lon), None, "none", "estimate", None)


DESTS = {**load_destinations(DATA_DIR / "destinations.yaml"),
         "paris": _dest("paris", "Paris", "FR", "Europe/Paris", 48.857, 2.352),
         "amsterdam": _dest("amsterdam", "Amsterdam", "NL", "Europe/Amsterdam", 52.368, 4.904),
         "brussels": _dest("brussels", "Brussels", "BE", "Europe/Brussels", 50.850, 4.352)}
T = lambda m, d, h, mi: datetime(2027, m, d, h, mi)
S = it.AccommodationStay

# Thu 25 Mar - Sat 3 Apr 2027, 9 nights. The clocks go forward in the UK and the EU on Sun 28 Mar 2027, the day of
# the train to Paris.
TOUR = it.Trip(
    start=date(2027, 3, 25),
    segments=(it.DestinationSegment("london", date(2027, 3, 25), 3, S("A London hotel", date(2027, 3, 25), date(2027, 3, 28))),
              it.DestinationSegment("paris", date(2027, 3, 28), 2, S("A Paris hotel", date(2027, 3, 28), date(2027, 3, 30))),
              it.DestinationSegment("amsterdam", date(2027, 3, 30), 2, S("An Amsterdam flat", date(2027, 3, 30), date(2027, 4, 1))),
              it.DestinationSegment("brussels", date(2027, 4, 1), 2, S("A Brussels hotel", date(2027, 4, 1), date(2027, 4, 3)))),
    transfers=(it.TransferSegment("london", "paris", "train", T(3, 28, 9, 1), T(3, 28, 12, 20), booked=True),
               it.TransferSegment("paris", "amsterdam", "train", T(3, 30, 10, 25), T(3, 30, 13, 45), booked=True),
               it.TransferSegment("amsterdam", "brussels", "train", T(4, 1, 11, 0), T(4, 1, 12, 52))),
    inbound=it.TransferSegment("london", "london", "flight", T(3, 25, 7, 0), T(3, 25, 10, 0)),
    outbound=it.TransferSegment("brussels", "london", "train", T(4, 3, 15, 56), T(4, 3, 16, 57), booked=True))


def test_one_continuous_itinerary_through_four_cities():
    days = it.summary(TOUR, DESTS)
    assert len(days) == 10 and days[0]["date"] == "2027-03-25" and days[-1]["date"] == "2027-04-03"
    assert [d["where"] for d in days] == ["London"] * 4 + ["Paris"] * 2 + ["Amsterdam"] * 2 + ["Brussels"] * 2
    assert [d["kind"] for d in days] == ["arrival", "full", "full", "transfer", "full", "transfer", "full",
                                         "transfer", "full", "departure"]
    assert [d["currency"] for d in days] == ["GBP"] * 4 + ["EUR"] * 6        # each city its own currency
    assert [r["destination"] for r in it.segment_requests(TOUR, DESTS)] == ["london"]   # only checked coverage


def test_the_clocks_going_forward_on_the_travel_day_and_the_channel_between_them():
    paris_day = it.days(TOUR, DESTS)[3]
    # 09:01 London (BST since 01:00 UTC that morning) to 12:20 Paris (CEST): 2 h 19, not 3 h 19
    assert TOUR.transfers[0].minutes(DESTS) == 139
    assert paris_day.notes == ["Leave London by train at 09:01 (London time).",
                               "Arrive in Paris at 12:20 (Paris time), after 2 h 19 min.",
                               "Paris is 1 hour ahead of London: your phone changes its clock."]
    home = it.days(TOUR, DESTS)[-1]
    assert "London is 1 hour behind Brussels: your phone changes its clock." in home.notes
    assert not any("clock" in n for n in it.days(TOUR, DESTS)[5].notes)  # Paris and Amsterdam share a clock


def test_a_night_bus_is_a_night_on_board_not_a_night_in_a_bed():
    bus = it.TransferSegment("amsterdam", "brussels", "bus", T(3, 31, 23, 0), T(4, 1, 6, 30))
    segs = (TOUR.segments[0], TOUR.segments[1],
            it.DestinationSegment("amsterdam", date(2027, 3, 30), 1, S("An Amsterdam flat", date(2027, 3, 30), date(2027, 3, 31))),
            TOUR.segments[3])
    trip = it.Trip(TOUR.start, segs, (TOUR.transfers[0], TOUR.transfers[1], bus), TOUR.inbound, TOUR.outbound)
    days = it.days(trip, DESTS)
    assert days[6].kind == "transfer" and "You sleep on board tonight." in days[6].notes
    assert days[7].kind == "arrival" and days[7].destination == "brussels" and days[7].day == date(2027, 4, 1)
    assert it.segment_requests(trip, DESTS) and it.validate(trip, DESTS) == []


def test_a_missed_train_later_the_same_day_changes_only_its_times():
    new, notes = it.missed_transfer(TOUR, DESTS, "paris", T(3, 30, 12, 25), T(3, 30, 15, 45))
    assert notes[0] == ("New train: leave Paris at Tue 12:25, arrive in Amsterdam at Tue 15:45 (local times), after "
                        "3 h 20 min.")
    assert "The missed train was booked: ask whoever sold it about the next one." in notes
    assert new.segments == TOUR.segments and new.outbound == TOUR.outbound
    assert it.affected_days(new, DESTS, "amsterdam") == it.affected_days(TOUR, DESTS, "amsterdam")


def test_a_missed_last_train_means_a_bed_tonight_and_an_unused_night_and_the_trip_keeps_its_end():
    new, notes = it.missed_transfer(TOUR, DESTS, "paris", T(3, 31, 8, 25), T(3, 31, 11, 45))
    paris, amsterdam = new.segments[1], new.segments[2]
    assert (paris.nights, amsterdam.arrive, amsterdam.nights) == (3, date(2027, 3, 31), 1)
    assert "You need a bed in Paris tonight: ask A Paris hotel for another night, or find one." in notes
    assert ("Your first night at An Amsterdam flat in Amsterdam won't be used: tell the stay as soon as you can."
            in notes)
    assert new.segments[3] == TOUR.segments[3] and new.outbound == TOUR.outbound   # Brussels and home unchanged
    assert it.validate(new, DESTS) == []
    # with one night in Amsterdam there is none to give, so the rest of the trip moves a day
    short = it.change_nights(TOUR, DESTS, "amsterdam", 1, keep_end=True)[0]
    moved, notes2 = it.missed_transfer(short, DESTS, "paris", T(3, 31, 8, 25), T(3, 31, 11, 45))
    assert moved.segments[3].arrive == date(2027, 4, 1) and moved.outbound.depart.date() == date(2027, 4, 4)
    assert any("no night to give" in n for n in notes2)
    assert any("Your train from Brussels is booked for Sat 3 Apr: it needs changing to Sun 4 Apr" in n for n in notes2)


def test_changing_one_citys_nights_moves_the_rest_or_keeps_the_end():
    longer, notes = it.change_nights(TOUR, DESTS, "paris", 3)
    assert [s.arrive for s in longer.segments] == [date(2027, 3, 25), date(2027, 3, 28), date(2027, 3, 31),
                                                   date(2027, 4, 2)]
    assert longer.outbound.depart.date() == date(2027, 4, 4) and "The trip now ends on Sun 4 Apr." in notes
    assert any("train from Paris is booked for Tue 30 Mar: it needs changing to Wed 31 Mar" in n for n in notes)
    assert any(n.startswith("The stay in Amsterdam (An Amsterdam flat) needs new dates") for n in notes)
    same_end, notes = it.change_nights(TOUR, DESTS, "paris", 3, keep_end=True)
    assert same_end.segments[2].nights == 1 and same_end.outbound == TOUR.outbound   # Amsterdam gives a night
    assert it.validate(same_end, DESTS) == []
    with pytest.raises(it.TripError, match="Amsterdam would have no nights left"):
        it.change_nights(TOUR, DESTS, "paris", 4, keep_end=True)
    with pytest.raises(it.TripError, match="needs at least one night"):
        it.change_nights(TOUR, DESTS, "paris", 0)


def test_todays_single_city_trip_is_unchanged():
    one = it.Trip(date(2026, 12, 4), (it.DestinationSegment("london", date(2026, 12, 4), 3),),
                  outbound=it.TransferSegment("london", "london", "flight", datetime(2026, 12, 7, 15, 0),
                                              datetime(2026, 12, 7, 17, 0)))
    assert [d.kind for d in it.days(one, DESTS)] == ["arrival", "full", "full", "departure"]
    longer, notes = it.change_nights(one, DESTS, "london", 4)
    assert [d.kind for d in it.days(longer, DESTS)] == ["arrival", "full", "full", "full", "departure"]
    assert longer.outbound.depart == datetime(2026, 12, 8, 15, 0) and notes[-1] == "The trip now ends on Tue 8 Dec."
