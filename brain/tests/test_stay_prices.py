"""m203: a stay judged against the person's trip: nearby dates like for like, the whole cost, the days from here.
Sample prices only until Nuitée confirms its terms; the live path is tested on LiteAPI's documented response shape."""
from datetime import date, timedelta

from brain import stayprices, trips
from brain.moments import Point
from brain.travel import LondonEstimate

from test_api import client, install  # noqa: F401  (the client fixture)

STAY = stayprices.StayTerms("lp1", "Sample hotel", 51.5117, -0.1240, 600.0, 3, room="Double room",
                            board="Room only", refundable=True)


def test_nearby_dates_keep_the_nights_and_never_go_back_in_time():
    today = date(2026, 11, 7)
    opts = stayprices.nearby(date(2026, 11, 20), 3, today)
    assert len(opts) == 7 and all((co - ci).days == 3 for ci, co in opts)
    assert opts[3] == (date(2026, 11, 20), date(2026, 11, 23))
    assert [ci for ci, _ in stayprices.nearby(date(2026, 11, 8), 2, today)][0] == today   # not before today


def test_sample_prices_are_labelled_by_the_caller_and_match_the_persons_own_price():
    own = (date(2026, 11, 20), date(2026, 11, 23))                      # Fri, Sat, Sun nights
    opts = stayprices.nearby(own[0], 3, date(2026, 11, 7))
    dates = stayprices.sample_dates(STAY, own, opts)
    mine = next(d for d in dates if d.yours)
    assert mine.total == 600.0 and (mine.checkin, mine.checkout) == own
    week = next(d for d in dates if d.checkin == date(2026, 11, 23))     # Mon, Tue, Wed nights: no weekend
    assert week.total < mine.total
    assert dates == stayprices.sample_dates(STAY, own, opts)              # the same every time


def _rates(*rates):
    """LiteAPI's documented shape (docs.liteapi.travel/reference/post_hotels-rates, read 7 Nov 2026)."""
    return {"data": [{"hotelId": "lp1", "roomTypes": [{"rates": list(rates)}]}]}


def _rate(name, amount, board="RO", tag="RFN", fees=()):
    return {"name": name, "boardType": board, "boardName": "Room only" if board == "RO" else "Breakfast included",
            "cancellationPolicies": {"refundableTag": tag},
            "retailRate": {"total": [{"amount": amount, "currency": "GBP"}],
                           "taxesAndFees": [{"included": inc, "amount": a, "description": "Tax"} for inc, a in fees]}}


def test_the_same_room_on_the_same_terms_is_found_again_or_the_difference_is_said():
    resp = _rates(_rate("Double room", 650, fees=[(True, 50), (False, 12.5)]),
                  _rate("Double room", 590, tag="NRFN"), _rate("Twin room", 560, board="BB"))
    total, there, differs = stayprices.match_rate(resp, STAY)
    assert (total, there, differs) == (650.0, 12.5, [])                   # dearer, but the same room and terms
    only_other = _rates(_rate("Double room", 590, tag="NRFN"))
    assert stayprices.match_rate(only_other, STAY) == (590.0, 0.0, ["non-refundable"])
    assert stayprices.match_rate({"data": []}, STAY) == (None, 0.0, [])


def test_the_lowest_is_only_ever_like_for_like():
    d = lambda day, total, same=True: stayprices.DateOption(date(2026, 11, day), date(2026, 11, day + 3), total,
                                                            same_terms=same, differs=[] if same else ["non-refundable"])
    opts = [d(20, 600), d(21, 480, same=False), d(22, 520), d(23, None)]
    stayprices.mark_lowest(opts)
    assert [o.lowest for o in opts] == [False, False, True, False]


def test_the_stay_against_the_days():
    est = LondonEstimate()
    near, far = Point(lat=51.511, lon=-0.12), Point(lat=51.47, lon=-0.20)
    fit = stayprices.trip_fit(Point(lat=51.5117, lon=-0.1240), [
        stayprices.DayEnds(0, near, near), stayprices.DayEnds(1, near, near), stayprices.DayEnds(2, far, far)], est)
    assert [r["index"] for r in fit["days"]] == [0, 1, 2] and fit["to_first"] <= fit["days"][2]["to_first"]
    assert fit["line"].startswith("About ") and "Day 3 is the furthest" in fit["line"]
    assert stayprices.trip_fit(Point(lat=51.5, lon=-0.1), [], est)["days"] == []


def test_the_whole_cost_says_what_is_paid_at_the_property():
    c = stayprices.cost_lines(stayprices.StayTerms("x", "X", None, None, 600.0, 3, pay_there=12.5,
                                                   refundable=False), sample=False)
    assert c["whole"] == 612.5 and "including £12.50 paid at the property" in c["line"]
    assert c["cancel"] == "Non-refundable, as found."


def test_parse_liteapi_keeps_what_is_paid_at_the_property():
    q = trips.StayQuery("London", "GB", 51.5, -0.12, date(2026, 11, 20), date(2026, 11, 23))
    resp = {"data": [{"hotelId": "lp1", "roomTypes": [{"offerRetailRate": {"amount": 650, "currency": "GBP"},
                                                       "rates": [_rate("Double room", 650, fees=[(False, 12.5)])]}]}],
            "hotels": [{"id": "lp1", "name": "A hotel"}]}
    assert trips.parse_liteapi(resp, q)[0].pay_there == 12.5


def test_the_endpoint_uses_labelled_sample_prices_and_stores_nothing_about_the_stay(client):
    h, _ = install(client)
    ci = date.today() + timedelta(days=10)
    body = {"checkin": ci.isoformat(), "checkout": (ci + timedelta(days=3)).isoformat(), "adults": 2,
            "stay": {"id": "lp1", "name": "Sample hotel", "lat": 51.5117, "lon": -0.1240, "price_total": 600,
                     "nights": 3, "room": "Double room", "board": "Room only", "refundable": True},
            "days": [{"index": 0, "first": {"lat": 51.508, "lon": -0.128}, "last": {"lat": 51.505, "lon": -0.09}},
                     {"index": 1, "first": {"lat": 51.501, "lon": -0.142}, "last": {"lat": 51.507, "lon": -0.076}}]}
    r = client.post("/v1/trips/stays/compare", headers=h, json=body)
    assert r.status_code == 201 or r.status_code == 200, r.text
    out = r.json()
    assert out["source"] == "sample" and out["note"].startswith("Sample prices")
    assert len(out["dates"]) == 7 and sum(d["yours"] for d in out["dates"]) == 1
    assert next(d for d in out["dates"] if d["yours"])["whole"] == 600
    assert out["fit"]["line"].startswith("About ") and len(out["fit"]["days"]) == 2
    assert out["cost"]["cancel"].startswith("Free cancellation")
    with client.app.state.Session() as s:
        from brain import db
        ev = s.query(db.Event).filter_by(name="stay_compare").one()
        assert set(ev.props) == {"nights", "days", "live"}                 # never the stay, its price or the dates
    bad = {**body, "checkin": (date.today() - timedelta(days=1)).isoformat()}
    assert client.post("/v1/trips/stays/compare", headers=h, json=bad).status_code == 422
