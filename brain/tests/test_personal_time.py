"""m200-m202: regression tests for the person's own time in a day (Abram's six cases, 7 Nov).

The allowances either side of plans away from the day's places (30 min somewhere else, 45 min not decided) are GUESSES
the planner leaves room for, never promises about real journey times.
"""
from datetime import date, timedelta

from test_api import client, install  # noqa: F401  (the client fixture)

START = date.today() + timedelta(days=5)
STAY = {"lat": 51.5117, "lon": -0.1240}   # Covent Garden


def _day(client, h, personal, **kw):
    body = {"start_date": START.isoformat(), "nights": 2, "day_start": "10:00", "day_end": "18:00",
            "stops_per_day": 3, "personal": personal, **kw}
    r = client.post("/v1/me/trips/days", headers=h, json=body)
    assert r.status_code == 201, r.text
    return {d["index"]: d for d in r.json()["days"]}


def _mine(day):
    return [(st["arrive"], st["depart"], st["mine"]) for st in day["plan"]["stops"] if st["mine"]]


def _clear(day, gap_before=0, gap_after=0):
    """No place or lunch overlaps a block or the allowance either side of it."""
    m = lambda t: int(t[:2]) * 60 + int(t[3:])
    stops = day["plan"]["stops"]
    for b in (st for st in stops if st["mine"]):
        lo, hi = m(b["arrive"]) - gap_before, m(b["depart"]) + gap_after
        for st in stops:
            if not st["mine"]:
                assert m(st["depart"]) <= lo or m(st["arrive"]) >= hi, (st["title"], st["arrive"], b["arrive"])


def test_at_the_start_and_the_end_of_the_day(client):
    h, _ = install(client)
    days = _day(client, h, [{"day": 1, "mine": [{"kind": "plans", "start": "10:00", "end": "11:00"},
                                                {"kind": "free", "start": "17:00", "end": "18:00"}]}])
    one = days[1]
    assert _mine(one) == [("10:00", "11:00", "plans"), ("17:00", "18:00", "free")]
    assert all(b["planned"] for b in one["mine"])
    # plans not decided yet: no time before them (the day starts there), 45 min after them
    assert "45 min after to get back" in one["plan"]["stops"][0]["what"]
    _clear(one, gap_after=45)


def test_two_blocks_in_one_day(client):
    h, _ = install(client)
    one = _day(client, h, [{"day": 1, "mine": [
        {"kind": "plans", "start": "12:00", "end": "13:00", "location": "near"},
        {"kind": "free", "start": "15:30", "end": "16:30"}]}])[1]
    assert _mine(one) == [("12:00", "13:00", "plans"), ("15:30", "16:30", "free")]
    places = [st for st in one["plan"]["stops"] if st["rateable"] and not st["lunch"]]
    assert 1 <= len(places) <= 3
    _clear(one)


def test_plans_over_lunchtime(client):
    h, _ = install(client)
    days = _day(client, h, [
        {"day": 0, "mine": [{"kind": "plans", "start": "12:30", "end": "13:30", "location": "near"}]},
        {"day": 1, "mine": [{"kind": "plans", "start": "12:30", "end": "13:30", "location": "near", "meal": True}]},
        {"day": 2, "mine": [{"kind": "plans", "start": "12:00", "end": "14:00"}]}])
    assert any(st["lunch"] for st in days[0]["plan"]["stops"])           # near, no meal said: lunch fits beside
    assert not any(st["lunch"] for st in days[1]["plan"]["stops"])       # they eat during the plans
    two = days[2]                                                         # not decided: no room, and it says so
    assert not any(st["lunch"] for st in two["plan"]["stops"])
    assert "no room for a lunch stop" in next(st for st in two["plan"]["stops"] if st["mine"])["what"]
    assert len([st for st in two["plan"]["stops"] if st["rateable"] and not st["lunch"]]) <= 3
    _clear(two, 45, 45)


def test_replanning_after_a_place_is_cancelled_keeps_the_block(client):
    """"Re-plan the rest of today" (a place closed): later start, the cancelled place left out, the block kept."""
    h, _ = install(client)
    body = {"start": STAY, "start_name": "your stay", "start_time": "10:00", "end_time": "18:00", "stops": 4,
            "familiar": False, "mine": [{"kind": "plans", "start": "15:00", "end": "16:00", "location": "elsewhere"}]}
    first = client.post("/v1/me/plans", headers=h, json=body).json()["stops"]
    gone = next(st["moment_id"] for st in first if st["rateable"])
    rest = client.post("/v1/me/plans", headers=h, json={**body, "start_time": "12:00", "stops": 3,
                                                         "exclude": [gone]})
    assert rest.status_code == 201, rest.text
    stops = rest.json()["stops"]
    assert [(st["arrive"], st["depart"]) for st in stops if st["mine"]] == [("15:00", "16:00")]
    assert gone not in {st["moment_id"] for st in stops} and all(st["arrive"] >= "12:00" for st in stops)
    assert next(st for st in stops if st["mine"])["what"].startswith("Somewhere else: we've left 30 min")


def test_a_day_that_is_yours(client):
    h, _ = install(client)
    days = _day(client, h, [{"day": 1, "free_day": True}])
    assert days[1]["free_day"] and days[1]["plan"] is None and days[1]["title"] == "A day that's yours"
    assert days[0]["plan"] and days[2]["plan"]                            # the other days are planned as usual


def test_first_and_last_days_with_the_journeys(client):
    """Arriving by train at 12:00 and leaving by train at 17:00: blocks inside the planned part are planned; a block
    after the train home can't be, and says so; the journeys stay."""
    h, _ = install(client)
    days = _day(client, h, [
        {"day": 0, "mine": [{"kind": "free", "start": "16:00", "end": "17:00"}]},
        {"day": 2, "mine": [{"kind": "plans", "start": "11:00", "end": "12:00", "location": "near"},
                            {"kind": "free", "start": "17:00", "end": "18:00"}]}],
        stay=STAY, stay_name="Sample hotel",
        arrive={"mode": "train", "place": "KGX", "time": "12:00"}, leave={"mode": "train", "place": "KGX", "time": "17:00"})
    first, last = days[0], days[2]
    assert first["legs"][0]["slot"] == "arrive" and first["plan"]["stops"][0]["arrive"] >= "12:00"
    assert _mine(first) == [("16:00", "17:00", "free")]
    assert last["legs"][-1]["slot"] == "leave"
    assert [(b["start"], b["planned"]) for b in last["mine"]] == [("11:00", True), ("17:00", False)]
    assert _mine(last) == [("11:00", "12:00", "plans")]
    leave_by = last["legs"][-1]["depart"]
    assert all(st["depart"] <= leave_by for st in last["plan"]["stops"])
