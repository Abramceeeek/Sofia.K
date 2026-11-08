"""m222: school holidays from official sources only, with a coverage matrix that says what is and isn't checked.
Two councils are never "UK-wide"; bank holidays and school holidays stay separate."""
from datetime import date

from brain import travelcalendar as tc

AREAS = tc.load_school_areas()
ROWS = tc.load_coverage()


def test_the_matrix_and_the_data_agree_both_ways():
    assert tc.check_coverage(ROWS, AREAS) == []
    england = [r for r in ROWS if r["nation"] == "England"]
    assert england and not any(r["status"] == "checked" for r in england)   # England: nothing checked, and said so
    assert tc.coverage_summary(ROWS)["England"]["blocked"] == 7
    assert any(r["nation"] == "Scotland" and r["status"] == "not checked" for r in ROWS)   # one council isn't Scotland
    # a made-up area with no "checked" row, or a checked row with no dates, is caught
    fake = {**AREAS, "glasgow": AREAS["edinburgh"]}
    assert tc.check_coverage(ROWS, fake) == ["glasgow: dates with no 'checked' row"]
    bad = ROWS + [{"nation": "Scotland", "name": "Glasgow", "status": "checked", "areas": ["glasgow"]}]
    assert "Glasgow: no dates for glasgow" in tc.check_coverage(bad, AREAS)


def test_wales_is_one_table_and_powys_differs():
    welsh = [k for k, a in AREAS.items() if a.source.startswith("https://www.gov.wales/")]
    assert len(welsh) == 22
    same = {k for k in welsh if AREAS[k].holidays == AREAS["cardiff"].holidays}
    assert same == set(welsh) - {"powys"}
    assert dict((t, (f, e)) for t, f, e in AREAS["powys"].holidays)["Christmas holiday"] == \
        (date(2026, 12, 23), date(2027, 1, 3))      # the autumn term ends Tue 22 Dec 2026 in Powys


def test_france_runs_from_the_first_day_off_to_the_day_before_classes_resume():
    for zone in ("france_zone_a", "france_zone_b", "france_zone_c"):
        for title, f, e in AREAS[zone].holidays:
            assert f.strftime("%a") == "Sat" and e.strftime("%a") in ("Sun", "Wed"), (zone, title)   # été: to Wed 1 Sep
    hiver = {z: dict((t, (f, e)) for t, f, e in AREAS[z].holidays)["Vacances d'hiver"]
             for z in ("france_zone_a", "france_zone_b", "france_zone_c")}
    assert len(set(hiver.values())) == 3                          # the zones' winter holidays differ
    noel = {dict((t, (f, e)) for t, f, e in AREAS[z].holidays)["Vacances de Noël"]
            for z in ("france_zone_a", "france_zone_b", "france_zone_c")}
    assert noel == {(date(2026, 12, 19), date(2027, 1, 3))}       # Christmas is the same everywhere


def test_dutch_advice_dates_say_so_and_compulsory_ones_dont():
    v = tc.home_calendar(None, "netherlands_midden", date(2026, 10, 1), date(2027, 1, 10))
    autumn, xmas = [e for e in v.entries if e.kind == "school_holiday"]
    assert (autumn.start, autumn.end) == (date(2026, 10, 17), date(2026, 10, 25))
    assert autumn.exceptions.startswith("Advice dates: schools may differ.")
    assert not xmas.exceptions.startswith("Advice dates")
    assert "Bank holidays where you live aren't known." in v.unknown   # no Dutch public holidays yet: said


def test_northern_ireland_keeps_bank_and_school_holidays_apart():
    v = tc.home_calendar("northern-ireland", "northern_ireland", date(2027, 3, 15), date(2027, 3, 20))
    kinds = sorted((e.kind, e.title) for e in v.entries if e.start == date(2027, 3, 17))
    assert [k for k, _ in kinds] == ["bank_holiday", "school_holiday"]   # St Patrick's Day: two entries, two sources
    school = next(e for e in v.entries if e.kind == "school_holiday")
    assert "at their own discretion" in school.exceptions and school.applies_to.startswith("Schools that follow")
    later = tc.home_calendar("northern-ireland", "northern_ireland", date(2027, 7, 1), date(2027, 8, 1))
    assert "Department of Education (Northern Ireland)'s school holidays are checked for 2026-27 only." in later.unknown
