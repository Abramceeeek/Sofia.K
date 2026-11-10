"""m219: every recommendation can say why, from the inputs it was really computed from. Each factor's value is the
algorithm's own number, its text is a template around that number, and what wasn't known is listed, never guessed.
Synthetic data only."""
from datetime import date, timedelta

from brain import explain, fx, trips

from test_api import client, install  # noqa: F401  (the client fixture)

DAY = {"start": {"lat": 51.5081, "lon": -0.1281}, "start_name": "Charing Cross station",
       "start_time": "10:00", "end_time": "18:00", "conditions": {"temp_c": 18, "rain_prob": 0.1}}


def _st(**kw):
    base = {"moment_id": "m1", "title": "A view", "why": [
        {"feature": "movement_views", "label": "views", "contribution": 0.42},
        {"feature": "crowds", "label": "crowds", "contribution": -0.21},
        {"feature": "aspiration_match", "label": "fields that inspire you", "contribution": 0.12},
        {"feature": "awe", "label": "awe", "contribution": 0.01}],
        "travel_min": 12, "travel_mode": "walk", "from": "Charing Cross station", "arrive": "11:20", "depart": "12:30",
        "best_windows": [(960, 1050)], "cost_gbp": 0.0, "familiar": False}
    return {**base, **kw}


def test_a_stop_says_why_from_the_planners_own_numbers():
    e = explain.stop(_st(), p=0.81, windows=[(600, 1050)], hours_text="10:00-17:30",
                     labels={"aspiration_match": "one of your interests"})
    f = {(x["kind"], x["value"]): x for x in e["factors"]}
    assert f[("preference", 0.81)]["text"] == ("A strong match for you: the rating model gives a 81% chance you'd "
                                               "rate it Good or better.")
    assert f[("preference", 0.42)]["effect"] == "for" and f[("preference", -0.21)]["effect"] == "against"
    assert f[("preference", 0.12)]["text"] == "One of your interests: counts for it, for you."   # the app's words
    assert ("preference", 0.01) not in f                       # too small to have mattered: not said
    assert f[("travel", 12)]["text"] == "12 min on foot from Charing Cross station." and f[("travel", 12)]["effect"] == "for"
    assert f[("hours", "10:00-17:30")]["text"] == ("You're there 11:20–12:30, inside the card's visiting window "
                                                    "(10:00–17:30).")
    assert f[("hours", "10:00-17:30")]["source"] == "the card's visiting window; opening hours: 10:00-17:30"
    assert f[("best_time", "16:00-17:30")]["effect"] == "neutral"   # not at its best time: said, not hidden
    assert f[("budget", 0.0)]["text"] == "Free." and e["unknown"] == []
    # the rules are the planner's: 15 and 30 min are where its transfer penalties start
    assert [explain.stop(_st(travel_min=t, travel_mode="transit"), p=None, windows=[])["factors"][0]["effect"]
            for t in (15, 16, 30, 31)] == ["for", "neutral", "neutral", "against"]
    # no card times known: said as unknown, never assumed open
    assert "opening times" in explain.stop(_st(), p=0.6, windows=[])["unknown"]


def test_a_stop_against_a_budget_and_a_weak_match():
    block = {"budget_gbp": 20.0, "total_gbp": 21.0, "status": "over"}
    e = explain.stop(_st(cost_gbp=6.0), p=0.4, windows=[(0, 1440)], budget=block)
    f = {x["kind"]: x for x in reversed(e["factors"])}       # the first factor of each kind
    assert f["preference"]["text"].startswith("Worth a try: the rating model gives a 40% chance")
    assert f["preference"]["effect"] == "neutral"
    assert f["budget"]["text"] == "£6 of your £20; the day comes to £21." and f["budget"]["effect"] == "against"
    assert f["hours"]["text"] == "Any time of day suits it."


def _stay(sid, total, rating, km, nights=4, pay_there=0.0, currency="GBP"):
    return trips.Stay(sid, sid, "hotel", 4, rating, 100, "London", 51.5, -0.12, None, total, currency, nights,
                      "Double room", "Room only", False, True, distance_km=km, pay_there=pay_there)


def test_a_stays_place_in_best_for_your_days_is_the_rankings_own_sum():
    stays = [_stay("a", 400.0, 8.0, 1.0), _stay("b", 600.0, 9.2, 0.4), _stay("c", 320.0, 6.5, 5.0, pay_there=80.0),
             _stay("d", 500.0, None, None)]
    px = trips.stay_pricing(stays)
    why = explain.stay_rank(stays, px, "Charing Cross")
    scores = trips.recommended_scores(stays, px)
    for s in stays:   # the parts add up to the very score the list is sorted by
        assert abs(why[s.id]["score"] - scores[s.id]) < 1e-3, s.id
    order = [s.id for s in trips.filter_stays(stays, trips.StayFilters())]
    assert order == sorted(why, key=lambda i: -why[i]["score"])
    b = {x["kind"]: x for x in why["b"]["factors"]}
    assert b["rating"]["text"] == "Guests rate it 9.2 out of 10 (these results: 6.5 to 9.2); 45% of the score."
    assert b["price"]["text"] == "£150 a night (these results: £100 to £150); 35% of the score."
    c = {x["kind"]: x for x in why["c"]["factors"]}
    assert c["price"]["text"].startswith("£100 a night, including £20 paid there")   # fees counted, and said
    assert why["d"]["unknown"] == ["guests' rating (counted as middling)", "where it is (counted as middling)"]


def test_a_stay_against_the_trip_and_a_trip_length():
    fit = {"days": [{"index": 1, "to_first": 14, "back": 18, "text": "Day 2: 14 min there, 18 back"}],
           "line": "About 14 min to your first place and 18 min back, on a typical day of this trip.",
           "to_first": 14, "back": 18, "missing": [2]}
    cost = {"whole": 840.0, "per_night": 210.0, "line": "£840 for 4 nights, taxes included, as the provider shows it.",
            "cancel": "Non-refundable, as found.", "board": None, "sample": True}
    e = explain.stay_for_trip(fit, cost, "GBP", False, ["Christmas Day"])
    f = [(x["kind"], x["effect"], x["value"]) for x in e["factors"]]
    assert ("location", "against", 18) not in f and ("location", "neutral", 18) in f   # 18 min: a fair way
    assert ("terms", "against", "non-refundable") in f and ("calendar", "neutral", "Christmas Day") in f
    assert e["unknown"] == ["days with no places yet: 3"]
    assert e["factors"][-3]["source"] == "the provider's price (a sample price)"
    r = {"place": "London", "strong_matches": 9, "good_matches": 14, "checked": 39, "best": 9, "capped": False,
         "places_per_day": 3, "suggested_days": 3, "your_days": 2, "spare_days": 0}
    t = explain.trip_length(r)["factors"]
    assert t[0]["text"] == ("9 strong matches for you in London (a 75% or better chance of Good), and 14 good ones, "
                            "of 39 checked places.")
    assert t[1]["text"] == "The suggestion is built on your 9 strong matches."
    assert t[2]["text"] == ("At 3 places a day, keeping the day's shape (at most two history stops a day, one wander), "
                            "those 9 take 3 exploring days.")
    assert (t[3]["effect"], t[3]["text"]) == ("against", "Your trip has 2 exploring days: fewer than they need.")
    # no strong matches yet: it never says "the strong matches take…", it says what it used instead
    t = explain.trip_length({**r, "strong_matches": 0, "best": 9})["factors"]
    assert t[1]["text"] == "Fewer strong matches than your places a day, so it uses your best 9 for now (strong and good ones)."


TASTE = {"movement_views", "crowds", "aspiration_match", "awe"}


def test_why_this_stop_is_at_most_three_reasons_with_no_score_or_percentage():
    """m230 (Abram, m224): a collapsed "Why this stop?", at most three reasons from the planner's own inputs, no raw
    model scores or percentages, and one trade-off when something counts against the stop."""
    e = explain.stop(_st(), p=0.81, windows=[(600, 1050)], hours_text="10:00-17:30",
                     labels={"aspiration_match": "one of your interests"}, taste=TASTE)
    assert [w["text"] for w in e["why"]] == [
        "From your answers, it has what you like: views, one of your interests.",   # the score's top two terms, named
        "It fits the card's visiting window, 10:00–17:30.",
        "The trade-off: it has crowds, which your answers count against."]       # never all upside
    assert [w["effect"] for w in e["why"]] == ["for", "for", "against"]
    for w in e["why"]:
        assert "%" not in w["text"] and "81" not in w["text"] and "0.4" not in w["text"] and "0.2" not in w["text"]
    # at its best time, a short walk, free, and nothing against it: three reasons, no trade-off
    ok = explain.stop(_st(arrive="16:10", depart="17:00", why=_st()["why"][:1]), p=0.81, windows=[(600, 1050)],
                      taste=TASTE)
    assert [w["text"] for w in ok["why"]] == ["From your answers, it has what you like: views.",
                                              "You're there at its best time, 16:00–17:30.",
                                              "12 min on foot from Charing Cross station."]


def test_the_trade_off_is_the_journey_or_the_budget_first():
    far = explain.stop(_st(travel_min=41, travel_mode="transit"), p=0.6, windows=[(600, 1050)], taste=TASTE)
    assert far["why"][-1] == {"kind": "travel", "effect": "against",
                              "text": "The trade-off: 41 min by Tube or bus from Charing Cross station."}
    block = {"budget_gbp": 20.0, "total_gbp": 21.0, "status": "over"}
    over = explain.stop(_st(cost_gbp=6.0), p=0.4, windows=[(0, 1440)], budget=block, taste=TASTE)
    assert over["why"][-1]["text"] == "The trade-off: £6 of your £20; the day comes to £21."
    assert len(over["why"]) <= explain.WHY_MAX
    # cost, travel and weather terms of the score aren't named as tastes: they have their own reasons
    cost = explain.stop(_st(why=[{"feature": "cost_per_10gbp", "label": "cost (per £10)", "contribution": -0.5}]),
                        p=0.6, windows=[], taste=TASTE)
    assert not [w for w in cost["why"] if "cost (per" in w["text"]]
    # no card (lunch, your own time): nothing to say why
    assert explain.stop(_st(), p=None, windows=[])["why"] == []


def test_a_lunch_slot_is_an_estimate_not_a_venue():
    block = {"budget_gbp": 12.0, "total_gbp": 12.0, "status": "tight",
             "lines": [{"label": "Lunch", "gbp": 6.0, "note": "A cheaper lunch: a supermarket, bakery or market stall"}]}
    e = explain.stop(_st(moment_id="lunch@m1", lunch=True, why=[], travel_min=0, cost_gbp=6.0, best_windows=[]),
                     p=None, windows=[],
                     budget=block)
    texts = [x["text"] for x in e["factors"]]
    assert texts == ["Right by Charing Cross station: no travel.",
                     "A cheaper lunch: a supermarket, bakery or market stall: about £6, an estimate. The day comes to "
                     "£12 of your £12."]


def test_explanations_come_with_plans_stays_and_lengths_and_never_with_the_blind_pair(client):
    h, _ = install(client)
    plan = client.post("/v1/me/plans", headers=h, json={**DAY, "budget_gbp": 30}).json()
    places = [st for st in plan["stops"] if st["rateable"]]
    assert places and all(st["explain"]["factors"] for st in places)
    for st in plan["stops"]:
        if st.get("explain"):
            f = {x["kind"]: x for x in st["explain"]["factors"]}
            assert f["travel"]["value"] == round(st["travel_min"])          # the plan's own travel time
        if st["rateable"]:
            pref = [x for x in st["explain"]["factors"] if x["kind"] == "preference"]
            word = st["match"].split(" for you")[0]
            assert pref[0]["text"].startswith(word)                        # the same number as the stop's words
            named = {round(w["contribution"], 3) for w in st["why"]}
            assert {x["value"] for x in pref[1:] if x["value"] != "familiar"} <= named   # the score's own terms
            f = {x["kind"]: x for x in st["explain"]["factors"]}
            total = explain._money(plan["budget"]["total_gbp"])                # the day's own total (m217)
            assert f"of your £30; the day comes to {total}." in f["budget"]["text"] or \
                f["budget"]["text"] == f"Free. The day comes to {total} of your £30."
    for st in places:                                                        # m230: "Why this stop?"
        why = st["explain"]["why"]
        assert 1 <= len(why) <= explain.WHY_MAX and not [w for w in why if "%" in w["text"]]
    blind = client.post("/v1/me/plans", headers=h, json={**DAY, "blind": True}).json()
    assert all("explain" not in st for st in blind["stops"])
    soon = date.today() + timedelta(days=30)
    s = client.post("/v1/trips/stays", headers=h, json={
        "checkin": soon.isoformat(), "checkout": (soon + timedelta(days=3)).isoformat()}).json()
    scores = [x["explain"]["score"] for x in s["results"]]
    assert scores == sorted(scores, reverse=True)                          # "Best for your days" is its own sum
    t = client.post("/v1/me/trips/length", headers=h, json={"destination": "london", "nights": 4}).json()
    assert t["explain"]["factors"][0]["value"] == t["strong_matches"]


def test_why_this_stay_is_about_the_itinerary_not_the_score():
    """m241 (Abram, m234): where the stay is against the planned days first, then the whole cost, then the terms;
    one trade-off when there is one; never a score or a percentage."""
    fit = {"days": [{"index": 1, "to_first": 14, "back": 18, "text": "Day 2: 14 min there, 18 back"},
                    {"index": 2, "to_first": 38, "back": 35, "text": "Day 3: 38 min there, 35 back"}],
           "line": "About 14 min to your first place and 18 min back, on a typical day of this trip.",
           "to_first": 14, "back": 18, "missing": []}
    cost = {"whole": 840.0, "per_night": 210.0, "line": "£840 for 4 nights, taxes included, as the provider shows it.",
            "cancel": "Non-refundable, as found.", "board": None, "sample": True}
    why = explain.stay_for_trip(fit, cost, "GBP", False, [])["why"]
    assert [w["text"] for w in why] == [
        "About 14 min to your first place and 18 min back, on a typical day.",
        "£840 for 4 nights, taxes included, as the provider shows it.",
        "The trade-off: day 3: 38 min there, 35 back, the farthest of your days."]
    near = {**fit, "days": fit["days"][:1]}
    why = explain.stay_for_trip(near, cost, "GBP", False, ["Christmas Day"])["why"]
    assert why[-1] == {"kind": "terms", "effect": "against", "text": "The trade-off: non-refundable, as found."}
    assert len(why) == 3                                                # the trade-off takes the last place
    unknown_terms = explain.stay_for_trip(near, cost, "GBP", None, ["Christmas Day"])["why"]
    assert unknown_terms[-1]["text"] == "Your dates include a bank holiday: Christmas Day."   # a spare place
    free = explain.stay_for_trip(near, {**cost, "cancel": "Free cancellation until 1 Dec, as found."}, "GBP", True, [])
    assert [w["effect"] for w in free["why"]] == ["for", "for", "for"]
    for w in why + free["why"]:
        assert "%" not in w["text"]
    none = explain.stay_for_trip({"days": [], "line": "", "to_first": None, "back": None, "missing": [0]}, cost,
                                 "GBP", None, [])
    assert none["why"][0]["text"] == "Plan your days to see how far they are from here."


def test_why_this_length_says_what_more_days_add_and_fewer_leave_out():
    r = {"place": "London", "strong_matches": 9, "good_matches": 14, "checked": 39, "best": 9, "capped": False,
         "places_per_day": 3, "suggested_days": 3, "your_days": None, "spare_days": None,
         "options": [{"days": 1, "line": "Your 3 best, at about 3 places a day. You'd leave out 6: A, B, C and 3 more."},
                     {"days": 3, "line": "All 9 of your best, at about 3 places a day."},
                     {"days": 5, "line": "All 9 of your best, plus 4 more you'd likely enjoy, such as D and E."}]}
    why = explain.trip_length(r)["why"]
    assert [w["text"] for w in why] == [
        "9 strong matches for you in London: at 3 a day they take 3 days.",
        "In 1 day: Your 3 best, at about 3 places a day. You'd leave out 6: A, B, C and 3 more.",
        "In 5 days: All 9 of your best, plus 4 more you'd likely enjoy, such as D and E."]
    assert [w["effect"] for w in why] == ["for", "against", "for"] and not any("%" in w["text"] for w in why)
    weak = explain.trip_length({**r, "strong_matches": 1, "best": 6})["why"]
    assert weak[0]["text"] == "Your best 6 places in London for now take 3 days at 3 a day."


def test_the_trip_length_endpoint_carries_its_reasons(client):
    h, _ = install(client)
    d = client.post("/v1/me/trips/length", headers=h, json={"destination": "london", "nights": 4}).json()
    why = d["explain"]["why"]
    assert 1 <= len(why) <= explain.WHY_MAX and why[0]["text"].endswith(" a day.")
    assert any(w["text"].startswith("In ") for w in why[1:]) and not any("%" in w["text"] for w in why)
