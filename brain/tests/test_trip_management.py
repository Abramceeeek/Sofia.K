"""m336 (Abram, 24 Nov: trip management): replace one stop and keep the rest, show alternatives when something is
unavailable, say what a change does to the day (time, travel, cost), and keep every other day as it was."""
from datetime import date, timedelta

from test_api import client, install  # noqa: F401  (the client fixture)

from brain import dayplan

START = {"lat": 51.5081, "lon": -0.1281}


def _day(client, h, **kw):
    body = {"start": START, "start_name": "Charing Cross", "start_time": "10:00", "end_time": "17:00",
            "date": (date.today() + timedelta(days=3)).isoformat(), "stops": 4, **kw}
    r = client.post("/v1/me/plans", headers=h, json=body)
    assert r.status_code == 201, r.text
    return body, r.json()


def _swap(body, plan, out):
    keep = [st["key"] for st in plan["stops"] if st["key"] != out["key"]]
    return {**body, "keep": keep, "exclude": [out["moment_id"]], "compare_to": plan["id"]}


def test_a_swap_keeps_the_rest_and_says_what_changed(client):
    h, _ = install(client)
    body, plan = _day(client, h)
    out = next(st for st in plan["stops"] if st["rateable"])
    r = client.post("/v1/me/plans", headers=h, json=_swap(body, plan, out))
    assert r.status_code == 201, r.text
    new = r.json()
    kept = {st["key"] for st in plan["stops"]} - {out["key"]}
    assert kept <= {st["key"] for st in new["stops"]}                    # the rest of the day stays
    assert out["moment_id"] not in {st["moment_id"] for st in new["stops"]}
    ch = new["change"]
    assert ch["out"] == [out["title"]] and ch["text"].startswith("Instead of")
    assert {"finish_before", "finish_after", "cost_before_gbp", "cost_after_gbp", "travel_before_min",
            "travel_after_min"} <= set(ch)


def test_alternatives_are_different_and_each_keeps_the_rest(client):
    h, _ = install(client)
    body, plan = _day(client, h)
    out = next(st for st in plan["stops"] if st["rateable"])
    r = client.post("/v1/me/plans/alternatives", headers=h, json={"request": _swap(body, plan, out), "count": 3})
    assert r.status_code == 201, r.text
    alts = r.json()["alternatives"]
    assert 1 <= len(alts) <= 3
    kept = {st["key"] for st in plan["stops"]} - {out["key"]}
    came = []
    for a in alts:
        assert kept <= {st["key"] for st in a["stops"]} and a["change"]["text"]
        came.append(frozenset(st["moment_id"] for st in a["stops"] if st["rateable"]) - {k.split("#")[0] for k in kept})
    assert len(set(came)) == len(came)                                    # each brings in something different


def test_no_alternatives_for_the_blind_comparison_and_no_change_from_someone_elses_plan(client):
    h, _ = install(client)
    other, _ = install(client)
    body, plan = _day(client, h)
    out = next(st for st in plan["stops"] if st["rateable"])
    blind = {**_swap(body, plan, out), "blind": True}
    assert client.post("/v1/me/plans/alternatives", headers=h, json={"request": blind}).status_code == 422
    theirs = client.post("/v1/me/plans", headers=other, json=_swap(body, plan, out)).json()
    assert "change" not in theirs                                         # never compared with another person's plan


def test_the_change_line_names_the_swap_the_finish_the_cost_and_the_travel():
    old = [{"key": "a", "moment_id": "a", "title": "Liberty's wooden galleries", "rateable": True, "cost_gbp": 0,
            "travel_min": 10, "travel_mode": "walk", "depart": "17:40"}]
    new = [{"key": "b", "moment_id": "b", "title": "Graze your way round Borough Market", "rateable": True,
            "cost_gbp": 15.0, "travel_min": 26, "travel_mode": "transit", "depart": "17:20"}]
    ch = dayplan.plan_change(old, new)
    assert ch["text"] == ("Instead of Liberty's wooden galleries: Graze your way round Borough Market. The day ends at "
                          "17:20 (was 17:40). It costs about £18 more. 16 min more getting around.")   # £15 and one £3 fare
