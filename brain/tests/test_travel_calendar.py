"""WS5 (m211): two calendars, never mixed; bank and school holidays kept apart; every entry with its source; what
isn't known is said, never read as "nothing on"."""
from datetime import date, datetime, timezone

from brain import travelcalendar as tc
from brain.config import DATA_DIR
from brain.moments import Point
from brain.places import Destination, load_destinations

DESTS = load_destinations(DATA_DIR / "destinations.yaml")
LONDON = DESTS["london"]
VIENNA = Destination("vienna", "Vienna", "AT", None, "Europe/Vienna", "EUR", (), Point(lat=0, lon=0), None, "none",
                     "estimate", None)
AREAS = tc.load_school_areas()


def _titles(v, kind=None):
    return [(e.start.isoformat(), e.title) for e in v.entries if kind is None or e.kind == kind]


def test_each_nation_has_its_own_bank_holidays_and_substitutes_are_said():
    span = (date(2026, 12, 20), date(2027, 1, 5))
    scot = tc.home_calendar("scotland", None, *span)
    eng = tc.home_calendar("england-and-wales", None, *span)
    assert ("2027-01-04", "2nd January (substitute day)") in _titles(scot)
    assert "2027-01-04" not in [d for d, _ in _titles(eng)]
    assert ("2026-12-28", "Boxing Day (substitute day)") in _titles(eng)
    ni = tc.home_calendar("northern-ireland", None, date(2027, 3, 15), date(2027, 3, 20))
    assert [t for _, t in _titles(ni)] == ["St Patrick’s Day"]
    assert all(e.applies_to.startswith("Everyone in ") for e in scot.entries)


def test_school_holidays_are_their_own_kind_with_the_council_the_source_and_the_exceptions():
    v = tc.home_calendar("england-and-wales", "cardiff", date(2026, 10, 24), date(2026, 10, 31), AREAS)
    school = [e for e in v.entries if e.kind == "school_holiday"]
    assert [(e.title, e.start, e.end) for e in school] == [("Autumn half term", date(2026, 10, 26),
                                                            date(2026, 10, 30))]
    e = school[0]
    assert e.authority == "Cardiff Council" and e.source.startswith("https://www.gov.wales/")
    assert e.applies_to == "Schools that follow Cardiff Council's dates" and "Independent schools" in e.exceptions
    assert e.last_verified == "2026-11-07"


def test_overlapping_bank_and_school_holidays_stay_separate():
    v = tc.home_calendar("scotland", "edinburgh", date(2026, 12, 20), date(2027, 1, 5), AREAS)
    kinds = [(e.kind, e.title) for e in v.entries]
    assert ("school_holiday", "Winter holiday") in kinds and ("bank_holiday", "Christmas Day") in kinds
    assert len([k for k, _ in kinds if k == "school_holiday"]) == 1      # one entry, never merged with the bank days


def test_the_destinations_calendar_never_holds_the_travellers_school_holidays():
    span = (date(2026, 10, 24), date(2026, 10, 31))
    home = tc.home_calendar("england-and-wales", "cardiff", *span, AREAS)
    dest = tc.destination_calendar(LONDON, "london", *span)
    assert any(e.kind == "school_holiday" for e in home.entries)
    assert not any(e.kind == "school_holiday" for e in dest.entries) and dest.side == "destination"
    assert "Festivals and major events aren't added yet." in dest.unknown


def test_an_unknown_destination_or_year_is_said_never_read_as_nothing_on():
    paris = tc.destination_calendar(None, "Paris", date(2026, 12, 24), date(2026, 12, 29))
    assert paris.entries == [] and paris.unknown == ["We don't have Paris's holidays yet."]
    later = tc.destination_calendar(LONDON, "london", date(2028, 12, 20), date(2029, 1, 5))
    assert any(u.startswith("Bank holidays are known from") and "26 Dec 2028 only" in u for u in later.unknown)
    next_year = tc.home_calendar("england-and-wales", "cardiff", date(2027, 8, 1), date(2027, 8, 10), AREAS)
    assert "Cardiff Council's school holidays are checked for 2026-27 only." in next_year.unknown
    nowhere = tc.home_calendar("england-and-wales", "camden", date(2026, 10, 24), date(2026, 10, 31), AREAS)
    assert "School holidays for your area aren't checked yet." in nowhere.unknown   # Camden: page not readable
    assert tc.stay_note(None, "Paris", date(2026, 12, 24), date(2026, 12, 29)) == "We don't have Paris's holidays yet."
    assert tc.stay_note(LONDON, "london", date(2026, 12, 24), date(2026, 12, 29)) is None


def test_date_boundaries_are_inclusive_and_exact():
    # Edinburgh's mid-term break is 12-19 Oct 2026: a stay ending on the 12th touches it, one starting the 20th doesn't
    touch = tc.home_calendar(None, "edinburgh", date(2026, 10, 10), date(2026, 10, 12), AREAS)
    miss = tc.home_calendar(None, "edinburgh", date(2026, 10, 20), date(2026, 10, 25), AREAS)
    assert [e.title for e in touch.entries] == ["Mid-term break"] and miss.entries == []
    assert "Bank holidays where you live aren't known." in touch.unknown
    one_day = tc.home_calendar(None, "edinburgh", date(2026, 9, 14), date(2026, 9, 14), AREAS)
    assert [e.line() for e in one_day.entries] == ["Mon 14 Sep: Autumn holiday"]


def test_the_date_is_the_places_own_not_the_servers():
    late = datetime(2026, 12, 24, 23, 30, tzinfo=timezone.utc)
    assert tc.local_day(late, LONDON) == date(2026, 12, 24)
    assert tc.local_day(late, VIENNA) == date(2026, 12, 25)               # already Christmas Day in Vienna
    summer = datetime(2026, 6, 30, 23, 30, tzinfo=timezone.utc)
    assert tc.local_day(summer, LONDON) == date(2026, 7, 1)               # British Summer Time


def test_every_school_entry_in_the_file_is_well_formed():
    for key, a in AREAS.items():
        assert a.source.startswith("https://") and a.last_verified and a.exceptions and a.years
        assert all(f <= t for _, f, t in a.holidays)
