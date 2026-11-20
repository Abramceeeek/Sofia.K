"""m204: travel timing's first data: official UK bank holidays (GOV.UK), kept apart from school holidays."""
from datetime import date

from brain import traveltiming

from test_api import client, install  # noqa: F401  (the client fixture)


def test_the_official_file_is_kept_with_its_source():
    meta, days = traveltiming.load_bank_holidays()
    assert meta["source"] == "https://www.gov.uk/bank-holidays.json" and meta["fetched"] == "2026-11-07"
    assert set(meta["names"]) == {"england-and-wales", "scotland", "northern-ireland"}
    assert traveltiming.covered("england-and-wales") == (date(2019, 1, 1), date(2028, 12, 26))
    assert traveltiming.covered("nowhere") is None


def test_each_nation_has_its_own_days_and_substitutes_are_said():
    xmas = traveltiming.bank_holidays("england-and-wales", date(2026, 12, 20), date(2027, 1, 5))
    assert [(h.day, h.substitute) for h in xmas] == [(date(2026, 12, 25), False), (date(2026, 12, 28), True),
                                                     (date(2027, 1, 1), False)]
    andrew = lambda div: [h.title for h in traveltiming.bank_holidays(div, date(2026, 11, 28), date(2026, 12, 1))]
    assert any(t.startswith("St Andrew") for t in andrew("scotland")) and andrew("england-and-wales") == []


def test_a_stay_says_which_bank_holidays_it_includes_and_nothing_more():
    assert traveltiming.stay_holidays("london", date(2026, 12, 24), date(2026, 12, 29)) == [
        "Fri 25 Dec: Christmas Day", "Mon 28 Dec: Boxing Day (substitute day)"]
    assert traveltiming.stay_holidays("london", date(2026, 11, 10), date(2026, 11, 13)) == []
    assert traveltiming.stay_holidays("paris", date(2026, 12, 24), date(2026, 12, 29)) == []   # not known: silent


def test_the_bank_holidays_endpoint(client):
    r = client.get("/v1/travel-timing/bank-holidays", params={"division": "scotland", "from": "2026-11-01",
                                                               "to": "2026-12-31"})
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["kind"] == "bank_holidays" and out["source"].startswith("https://www.gov.uk/")
    assert [h["date"] for h in out["holidays"]][0] == "2026-11-30" and out["covers"]["to"] == "2028-12-26"
    assert client.get("/v1/travel-timing/bank-holidays", params={"division": "wales", "from": "2026-11-01",
                                                                 "to": "2026-12-31"}).status_code == 422
