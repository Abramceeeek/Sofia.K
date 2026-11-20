"""Regression tests for the audit of 11 Nov 2026 (decisions/security-audit.md). Each test names its finding."""

import base64
import json
import time

import pytest
from sqlalchemy import select

from brain import api, db, ops

from test_api import ADMIN, client, install  # noqa: F401  (the fixture)

PLAN = {"start": {"lat": 51.5081, "lon": -0.1281}, "start_time": "10:00", "end_time": "16:00", "stops": 4,
        "date": "2026-12-05"}


# ---- SEC-01: the rate limiter and made-up tokens ---------------------------------------------------------------

def test_sec01_the_limiter_holds_a_bounded_number_of_counters_and_stays_quick():
    lim = ops.Limiter(max_keys=500)
    t0 = time.perf_counter()
    for i in range(20_000):
        assert lim.hit(lim.key("any", "tok", f"made-up-{i}"), 180, 60) is None
    took = time.perf_counter() - t0
    assert len(lim._hits) == 500            # before: one counter per made-up token, for ever
    assert took < 5                         # before: every request swept the whole table once it passed 50,000


def test_sec01_a_flood_of_made_up_tokens_cannot_reset_an_overall_cap():
    lim = ops.Limiter(max_keys=10)
    assert [lim.hit("installs-all", 2, 3600) for _ in range(2)] == [None, None]
    for i in range(1000):
        lim.hit(lim.key("any", "tok", f"made-up-{i}"), 180, 60)
    assert lim.hit("installs-all", 2, 3600) is not None      # the named counter was never dropped


def test_sec01_made_up_tokens_from_one_address_are_limited_together(client, monkeypatch):
    monkeypatch.setitem(ops.LIMITS, "address", (5, 60))
    at = {"X-Forwarded-For": "198.51.100.7"}
    codes = [client.get("/v1/me/plans", headers={**at, "Authorization": f"Bearer made-up-{i}"}).status_code
             for i in range(8)]
    assert codes == [401] * 5 + [429] * 3   # before: 401 for ever, each with a database lookup
    other = {"X-Forwarded-For": "198.51.100.8", "Authorization": "Bearer made-up-x"}
    assert client.get("/v1/me/plans", headers=other).status_code == 401     # another address isn't held up


def test_sec01_the_edge_s_own_address_header_is_used_before_the_one_a_client_can_fake(client, monkeypatch):
    monkeypatch.setitem(ops.LIMITS, "install", (2, 3600))
    body = {"consent": {"version": "v", "research": True}}
    # the same real client (CF-Connecting-IP), pretending to be someone new each time in X-Forwarded-For
    at = lambda fake: client.post("/v1/installs", json=body, headers={"CF-Connecting-IP": "203.0.113.5",
                                                                     "X-Forwarded-For": fake}).status_code
    assert [at("10.1.1.1"), at("10.2.2.2"), at("10.3.3.3")] == [201, 201, 429]


# ---- SEC-02: nothing unbounded goes into the database -------------------------------------------------------------

def test_sec02_a_request_body_over_the_cap_is_turned_away(client):
    h, uid = install(client)
    big = {"items": [{"question": "best_hour", "text": "x" * 5000}] * 40}      # ~200 KB
    r = client.post("/v1/me/answers", headers=h, json=big)
    assert r.status_code == 413
    with client.app.state.Session() as s:
        assert s.scalar(select(db.Answer).where(db.Answer.user_id == uid)) is None


def test_sec02_a_body_with_no_declared_length_is_counted_as_it_arrives(client):
    h, _ = install(client)

    def chunks():
        yield b'{"name": "e", "props": {"a": "'
        for _ in range(40):
            yield b"y" * 8192
        yield b'"}}'

    r = client.post("/v1/me/events", headers={**h, "Content-Type": "application/json"}, content=chunks())
    assert r.status_code == 413


def test_sec02_lists_and_free_form_fields_have_a_size(client):
    h, uid = install(client)
    assert client.post("/v1/me/swipes", headers=h,
                       json={"items": [{"item": 1, "reaction": "loved"}] * 65}).status_code == 422
    assert client.post("/v1/me/answers", headers=h,
                       json={"items": [{"question": f"q{i}", "text": "x"} for i in range(21)]}).status_code == 422
    assert client.post("/v1/me/events", headers=h, json={"name": "e", "props": {"blob": "y" * 3000}}).status_code == 422
    assert client.post("/v1/me/plans", headers=h, json={**PLAN, "intent": {"blob": "z" * 3000}}).status_code == 422
    # what the apps really send still passes
    assert client.post("/v1/me/events", headers=h,
                       json={"name": "share_sheet", "props": {"moment": "m_x", "rating": "5", "reason": "1"}}).status_code == 204
    assert client.post("/v1/me/plans", headers=h, json={**PLAN, "intent": {"must_do": "t_view"}}).status_code == 201


def test_sec02_the_same_place_many_times_in_one_request_is_one_answer(client):
    h, uid = install(client)
    r = client.post("/v1/me/swipes", headers=h, json={"items": [{"item": 1, "reaction": "fine"}] * 30
                                                                 + [{"item": 1, "reaction": "loved"}]})
    assert r.status_code == 204
    with client.app.state.Session() as s:
        rows = list(s.scalars(select(db.Swipe).where(db.Swipe.user_id == uid)))
    assert [(x.item, x.reaction) for x in rows] == [(1, "loved")]     # before: 31 rows


# ---- SEC-03: values the patterns used to let through --------------------------------------------------------------

@pytest.mark.parametrize("change", [{"date": "2026-13-45"}, {"start_time": "99:99"}, {"end_time": "24:00"},
                                    {"start": {"lat": 999, "lon": 0}}, {"budget_gbp": 1e12}])
def test_sec03_impossible_dates_times_and_places_are_a_422_not_an_error(client, change):
    h, _ = install(client)
    assert client.post("/v1/me/plans", headers=h, json={**PLAN, **change}).status_code == 422


def test_sec03_trip_times_are_real_times(client):
    h, _ = install(client)
    assert client.post("/v1/me/trips/length", headers=h, json={"day_start": "00:00", "day_end": "99:99"}).status_code == 422
    assert client.post("/v1/me/trips/days", headers=h,
                       json={"start_date": "2026-12-05", "nights": 1, "day_start": "77:77"}).status_code == 422


# ---- SEC-04: one phone's number can't break the read-out for everyone -----------------------------------------------

@pytest.mark.parametrize("body", ['{"moment_id":"t_view","rating":5,"conditions":{"temp_c":Infinity}}',
                                  '{"moment_id":"t_view","rating":5,"travel_min":Infinity}',
                                  '{"moment_id":"t_view","rating":5,"conditions":{"temp_c":NaN}}',
                                  '{"moment_id":"t_view","rating":5,"travel_min":1e308}'])
def test_sec04_numbers_that_are_not_numbers_are_refused(client, body):
    h, _ = install(client)
    r = client.post("/v1/me/ratings", headers={**h, "Content-Type": "application/json"}, content=body)
    assert r.status_code == 422
    assert client.get("/v1/admin/export", headers=ADMIN).status_code == 200


def test_sec04_the_export_survives_a_bad_number_already_in_the_database(client):
    h, uid = install(client)
    assert client.post("/v1/me/ratings", headers=h, json={"moment_id": "t_view", "rating": 4}).status_code == 201
    with client.app.state.Session() as s:      # as an older server could have stored it
        row = s.scalar(select(db.Rating).where(db.Rating.user_id == uid))
        row.travel_min = float("inf")
        if s.get_bind().dialect.name == "sqlite":   # Postgres refuses an infinity inside JSON, so it can't be stored
            user = s.get(db.User, uid)
            user.delta = {**(user.delta or {}), "poison": [float("inf")]}
        s.commit()
    r = client.get("/v1/admin/export", headers=ADMIN)
    assert r.status_code == 200                # before: 500 for the whole export
    mine = next(x for x in r.json()["ratings"] if x["user_id"] == uid)
    assert mine["travel_min"] is None and mine["rating"] == 4


def test_finite_leaves_ordinary_values_alone():
    assert api._finite({"a": [1.5, float("nan"), "x", None, {"b": float("-inf")}]}) == {"a": [1.5, None, "x", None, {"b": None}]}


# ---- SEC-06: what a plan row keeps about where the person was --------------------------------------------------------

def _kept(client, uid) -> str:
    with client.app.state.Session() as s:
        return json.dumps([[p.stops, p.intent] for p in s.scalars(select(db.Plan).where(db.Plan.user_id == uid))])


@pytest.mark.parametrize("marker", [{"start_name": "where you are"}, {"start_name": "Somewhere", "start_is_here": True}])
def test_sec06_a_day_from_where_i_am_is_planned_with_the_point_and_kept_without_it(client, marker):
    h, uid = install(client)
    here = {"lat": 51.5081, "lon": -0.1281}
    sent = client.post("/v1/me/plans", headers=h, json={**PLAN, "start": here, **marker}).json()
    at_start = [st for st in sent["stops"] if st["moment_id"].endswith("@start")]
    assert at_start and all(st["pin"] == here for st in at_start)       # the person still sees lunch on the map
    assert "51.5081" not in _kept(client, uid)                           # before: kept as that stop's pin


def test_sec06_a_named_start_keeps_its_pin(client):
    h, uid = install(client)
    client.post("/v1/me/plans", headers=h, json={**PLAN, "start_name": "Charing Cross station"})
    assert "51.5081" in _kept(client, uid)      # a station isn't the person's position


def test_sec06_a_trip_s_plans_never_keep_the_name_of_the_stay(client):
    h, uid = install(client)
    r = client.post("/v1/me/trips/days", headers=h, json={
        "start_date": "2026-12-05", "nights": 1, "days": [1], "stay": {"lat": 51.5123, "lon": -0.1357},
        "stay_name": "The Private Stay Name", "day_start": "10:00", "day_end": "17:00"})
    assert r.status_code == 201
    day = r.json()["days"][0]
    assert day["plan"] is not None
    assert "The Private Stay Name" in json.dumps(day["plan"]["stops"])     # the person sees it
    kept = _kept(client, uid)
    assert "The Private Stay Name" not in kept and "your stay" in kept    # before: kept in "from …" and "Lunch near …"


def test_kept_stops_changes_only_what_it_says():
    stops = [{"moment_id": "t_boat", "pin": {"lat": 1, "lon": 2}, "lines": ["from Hotel X."]},
             {"moment_id": "lunch@start", "pin": {"lat": 3, "lon": 4}, "title": "Lunch near Hotel X"}]
    kept = api.kept_stops(stops, drop_start_pin=True, hide="Hotel X")
    assert kept == [{"moment_id": "t_boat", "pin": {"lat": 1, "lon": 2}, "lines": ["from your stay."]},
                    {"moment_id": "lunch@start", "pin": None, "title": "Lunch near your stay"}]
    assert stops[1]["pin"] == {"lat": 3, "lon": 4}     # the person's own copy is untouched


# ---- SEC-07: what anyone can read without a token -------------------------------------------------------------------

def test_sec07_the_api_pages_that_list_the_admin_routes_are_off(client):
    assert [client.get(p).status_code for p in ("/docs", "/redoc", "/openapi.json")] == [404, 404, 404]


def test_sec07_every_answer_carries_safe_browser_headers(client):
    h, _ = install(client)
    page = client.get("/privacy").headers
    assert page["x-content-type-options"] == "nosniff" and page["x-frame-options"] == "DENY"
    assert "frame-ancestors 'none'" in page["content-security-policy"]
    mine = client.get("/v1/me/plans", headers=h).headers
    assert mine["cache-control"] == "no-store" and mine["referrer-policy"] == "no-referrer"
    assert "content-security-policy" not in mine        # JSON: nothing for a browser to run


# ---- SEC-08: a malformed identity token is a "no", not an error ----------------------------------------------------

@pytest.mark.parametrize("header", [[1, 2], "x", 7, None])
def test_sec08_a_token_whose_header_is_not_an_object_is_refused_quietly(client, header):
    enc = lambda o: base64.urlsafe_b64encode(json.dumps(o).encode()).rstrip(b"=").decode()
    client.app.state.oidc.fetch = lambda url: {"keys": []}
    r = client.get("/v1/admin/backup", headers={"Authorization": f"Bearer {enc(header)}.{enc({})}.AAAA"})
    assert r.status_code == 403                 # before: 500, and an error alert to a person
    assert client.app.state.alerts.sent == []


def test_sec04_a_refused_request_is_never_echoed_back(client):
    h, _ = install(client)
    r = client.post("/v1/me/safety", headers=h, json={"message": "PRIVATE WORDS " * 400})
    assert r.status_code == 422 and "PRIVATE WORDS" not in r.text
    assert r.json()["detail"][0]["loc"] == ["body", "message"]


def test_sec05_one_ipv6_subscriber_is_one_address_however_many_addresses_it_uses():
    assert ops._network("2001:db8:1:2:aaaa::1") == ops._network("2001:db8:1:2:bbbb::9") == "2001:db8:1:2::/64"
    assert ops._network("2001:db8:1:3::1") != ops._network("2001:db8:1:2::1")
    assert ops._network("203.0.113.7") == "203.0.113.7" and ops._network("::ffff:203.0.113.7") == "203.0.113.7"
    assert ops._network("not an address") == "not an address"


def test_a_fit_that_gives_a_non_number_keeps_the_last_good_fit(client, monkeypatch):
    """Found running the tests on Postgres: a NaN in the person's fit can't be stored there and failed the request."""
    import numpy as np
    from brain import api as api_mod
    from brain.personal import DeltaPosterior
    h, uid = install(client)
    assert client.post("/v1/me/ratings", headers=h, json={"moment_id": "t_view", "rating": 4}).status_code == 201
    with client.app.state.Session() as s:
        good = s.get(db.User, uid).delta
    bad = lambda pop, obs: DeltaPosterior(np.full(len(pop.delta_prior_sd), np.nan), np.eye(len(pop.delta_prior_sd)), 1, 1)
    monkeypatch.setattr(api_mod, "update_person", bad)
    assert client.post("/v1/me/ratings", headers=h, json={"moment_id": "t_park", "rating": 2}).status_code == 201
    with client.app.state.Session() as s:
        assert s.get(db.User, uid).delta == good
