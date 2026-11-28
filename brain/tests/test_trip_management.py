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


def test_re_planning_the_rest_of_today_is_compared_with_what_was_still_ahead():
    """m341: "re-plan the rest of today" doesn't call the stops already done "left out"."""
    old = [{"key": "a", "moment_id": "a", "title": "The morning place", "rateable": True, "cost_gbp": 0,
            "travel_min": 5, "travel_mode": "walk", "arrive": "10:00", "depart": "11:00"},
           {"key": "b", "moment_id": "b", "title": "The closed place", "rateable": True, "cost_gbp": 0,
            "travel_min": 5, "travel_mode": "walk", "arrive": "14:00", "depart": "15:00"}]
    new = [{"key": "c", "moment_id": "c", "title": "The open place nearby", "rateable": True, "cost_gbp": 0,
            "travel_min": 5, "travel_mode": "walk", "arrive": "14:10", "depart": "15:10"}]
    ch = dayplan.plan_change(old, new, since="13:30")
    assert ch["out"] == ["The closed place"] and ch["text"].startswith("Instead of The closed place: The open place")


def test_a_stop_with_a_rain_option_names_it_for_the_one_tap_swap(client):
    h, _ = install(client)
    body, plan = _day(client, h)
    with_rain = [st for st in plan["stops"] if st.get("rain_swap")]
    assert with_rain and all(st.get("rain_swap_id") for st in with_rain)   # the card behind "If it rains"
    for st in with_rain[:1]:
        swap = {**_swap(body, plan, st), "intent": {"must_do": st["rain_swap_id"]}}
        new = client.post("/v1/me/plans", headers=h, json=swap).json()
        assert st["rain_swap_id"] in {s["moment_id"] for s in new["stops"]} and new["change"]["text"]


def test_estimates_are_said_as_estimates():
    """m343 (Abram: "clearly distinguish estimated costs, verified venue information, booking requirements")."""
    stops = [{"moment_id": "m_a", "key": "m_a", "cost_gbp": 22.0, "travel_min": 20, "travel_mode": "transit", "lines": []},
             {"moment_id": "lunch@m_a", "key": "lunch@m_a", "cost_gbp": 15.0, "travel_min": 0, "travel_mode": "walk",
              "lines": []}]
    dayplan.say_estimates(stops)
    assert stops[0]["lines"] == [dayplan.ESTIMATE_FARES] and "TfL charges the real fare" in dayplan.ESTIMATE_FARES
    assert stops[1]["lines"] == [dayplan.ESTIMATE_MEAL]
    named = [{"moment_id": "m_padella_borough", "key": "m_padella_borough#lunch", "cost_gbp": 15.0, "lines": []}]
    dayplan.say_estimates(named)
    assert named[0]["lines"] == []                                        # a named place's price is its menu's


def test_a_relaxed_day_feel_keeps_the_places_asked_and_adds_none(client):
    """m344, changed by m346 (Abram, 24 Nov: "Margaret and Alan request two places and choose Relaxed. Two excellent
    experiences finishing at 15:00 can be a successful day"; "The number of places requested should be respected"):
    Relaxed keeps the places they asked for, adds none and says the rest of the day is theirs. Separate from activity."""
    start = (date.today() + timedelta(days=3)).isoformat()
    trip = {"start_date": start, "nights": 1, "day_start": "10:00", "day_end": "18:00", "stops_per_day": 3}
    counts, frees = {}, {}
    for feel in (None, "relaxed"):
        h, _ = install(client)
        d = client.post("/v1/me/trips/days", headers=h, json={**trip, "day_feel": feel}).json()
        assert all(x["day_feel"] == (feel or "balanced") for x in d["days"])
        counts[feel] = [len([st for st in x["plan"]["stops"] if st["rateable"] and not st.get("lunch")])
                        for x in d["days"] if x["plan"]]
        frees[feel] = [x["plan"].get("free_after") for x in d["days"] if x["plan"]]
    assert all(n <= 3 for n in counts["relaxed"])                     # none beyond the three asked
    assert sum(counts["relaxed"]) <= sum(counts[None])
    for f in frees["relaxed"]:
        assert f is None or f["text"].startswith("A relaxed day, as you asked: the rest of it is yours from")


def test_the_trip_day_feel_wins_over_the_profile_default(client):
    """m346: "stored with the trip, editable": the trip's own answer is the one planned with."""
    h, _ = install(client)
    assert client.put("/v1/me/profile", headers=h, json={"day_feel": "full"}).status_code == 204
    start = (date.today() + timedelta(days=3)).isoformat()
    trip = {"start_date": start, "nights": 0, "day_start": "10:00", "day_end": "18:00", "stops_per_day": 2}
    assert client.post("/v1/me/trips/days", headers=h, json=trip).json()["day_feel"] == "full"
    assert client.post("/v1/me/trips/days", headers=h, json={**trip, "day_feel": "relaxed"}).json()["day_feel"] == "relaxed"


def test_pace_and_day_feel_are_separate(client):
    """m346 (Abram: "Test these combinations: Gentle + Full. Gentle + Relaxed. Medium + Balanced. Full-on + Full.
    Active + Relaxed. Do not assume that a gentle traveller wants fewer experiences"): the day feel sets how many
    places, the pace sets how strenuous they are, and neither changes the other."""
    from brain.config import DATA_DIR
    from brain.moments import load_moments
    active = {m.id for m in load_moments(DATA_DIR / "moments") if (m.features.place.get("active") or 0) >= 2}
    start = (date.today() + timedelta(days=3)).isoformat()
    trip = {"start_date": start, "nights": 1, "day_start": "10:00", "day_end": "19:00", "stops_per_day": 2}
    got = {}
    for pace, feel in (("gentle", "full"), ("gentle", "relaxed"), ("medium", "balanced"), ("full_on", "full"),
                       ("full_on", "relaxed")):
        h, _ = install(client)
        assert client.put("/v1/me/profile", headers=h, json={"activity": pace}).status_code == 204
        d = client.post("/v1/me/trips/days", headers=h, json={**trip, "day_feel": feel}).json()
        places = [[st for st in x["plan"]["stops"] if st["rateable"] and not st.get("lunch")
                   and not str(st.get("key") or "").endswith(("#lunch", "#dinner"))] for x in d["days"] if x["plan"]]
        got[(pace, feel)] = sum(len(p) for p in places)
        if feel == "relaxed":
            assert all(len(p) <= 2 for p in places)                      # the places asked for, none added
        if pace == "gentle":
            assert not {st["moment_id"] for p in places for st in p} & active   # never strenuous at a gentle pace
    assert got[("gentle", "full")] >= got[("gentle", "relaxed")]          # a gentle traveller can still have full days
    assert got[("full_on", "full")] >= got[("full_on", "relaxed")]


def test_a_paid_rain_option_says_its_price_budget_booking_and_a_free_one(client):
    """m353 (Abram, 25 Nov: "Don't describe a paid alternative as a simple replacement without explaining the extra
    expenditure"): the price, whether it fits the day's budget, any booking, and a free alternative where there is one."""
    from brain.config import DATA_DIR
    from brain.moments import load_moments
    cards = {m.id: m for m in load_moments(DATA_DIR / "moments")}
    h, _ = install(client)
    body, plan = _day(client, h)
    for st in plan["stops"]:
        rid = st.get("rain_swap_id")
        if not rid or rid not in cards:
            continue
        m = cards[rid]
        if (m.cost_gbp or 0) > 0:
            assert "It costs £" in st["rain_swap"] and ("fits your day's budget" in st["rain_swap"]
                                                         or "isn't in the day's cost" in st["rain_swap"])
            if m.best_time.book_ahead:
                assert "Book ahead:" in st["rain_swap"]
        else:
            assert st["rain_swap"].endswith("Free.")


def test_a_party_sees_each_travellers_cost_the_total_and_what_is_estimated(client):
    """m356 (Abram, 25 Nov: "The default budget is per person… show individual estimated spending, total estimated group
    spending, shared-cost allocation assumptions, children's applicable prices, clear estimated versus verified")."""
    h, _ = install(client)
    start = (date.today() + timedelta(days=3)).isoformat()
    body = {"start_date": start, "nights": 0, "day_start": "10:00", "day_end": "17:00", "stops_per_day": 3,
            "party": {"adults": 2, "children": [8, 11], "adult_budgets_gbp": [60, 40], "group_budget_gbp": 50}}
    d = next(x for x in client.post("/v1/me/trips/days", headers=h, json=body).json()["days"] if x["plan"])
    party = d["plan"]["party"]
    labels = [x["label"] for x in party["travellers"]]
    assert labels == ["Adult 1", "Adult 2", "Child 1 (8)", "Child 2 (11)"]
    assert abs(party["total_gbp"] - sum(x["cost_gbp"] for x in party["travellers"])) < 0.01
    assert party["verified"] and party["estimated"] and party["notes"][0].startswith("Each person pays")
    adult = party["travellers"][0]["cost_gbp"]
    assert all(x["cost_gbp"] <= adult + 0.01 for x in party["travellers"] if x["kind"] == "child")   # never more than an adult
    assert (party["over_group_gbp"] is not None) == (party["total_gbp"] > 50.5)
    one = client.post("/v1/me/trips/days", headers=h, json={**body, "party": None}).json()
    assert all("party" not in (x["plan"] or {}) for x in one["days"])   # one adult: the usual per-person line only


def test_a_trips_children_set_the_age_rules_whatever_the_profile_says():
    """m358: the bike loop (riders 14+) was kept out only when the profile said "family", so a couple's trip with an
    8-year-old on "Who's going" could plan it. The trip's children now count: an age rule keeps a card out when any
    child is under it, and the playground (children up to 12, with their adults) needs a child that young."""
    from brain.config import DATA_DIR
    from brain.moments import load_moments
    ready = [m for m in load_moments(DATA_DIR / "moments") if m.status == "ready"]
    ids = {m.id for m in ready}
    assert {"m_park_bike_loop_hyde", "m_diana_playground"} <= ids

    def out(company, children=None):
        return {i for _, xs in dayplan.kept_out(ready, [], {}, {}, company, None, children) for i in xs}

    assert "m_park_bike_loop_hyde" in out("partner", (8, 11))       # an 8-year-old can't ride
    assert "m_diana_playground" not in out("partner", (8, 11))      # and the playground is for them
    assert "m_park_bike_loop_hyde" not in out("partner", (15,))     # a 15-year-old can
    assert "m_diana_playground" in out("partner", (15,))            # who is too old for the playground
    assert "m_diana_playground" in out("partner")                   # no children: never the playground
    assert "m_park_bike_loop_hyde" in out("family")                 # a family whose ages we don't know: never the bike
