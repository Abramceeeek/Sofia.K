"""m349 (Abram, 24 Nov: "Add regression tests for: incorrect final finish times; sunset activities scheduled after
sunset when sunset is essential to the experience; unsupported or misleading food prices; seasonal descriptions that
are inappropriate for the visit date; duplicated sentences and descriptions. Ensure the displayed plan, underlying
schedule and cost summary agree.")"""
import re
from datetime import date, timedelta

from test_api import client, install  # noqa: F401  (the client fixture)

from brain import dayplan, quality, sun
from brain.config import DATA_DIR
from brain.dayplan import parse_hhmm
from brain.moments import load_moments

CARDS = {m.id: m for m in load_moments(DATA_DIR / "moments")}


def _trip(client, **kw):
    h, _ = install(client)
    body = {"start_date": (date.today() + timedelta(days=5)).isoformat(), "nights": 2, "day_start": "10:00",
            "day_end": "20:00", "stops_per_day": 3, **kw}
    r = client.post("/v1/me/trips/days", headers=h, json=body)
    assert r.status_code == 201, r.text
    return [d for d in r.json()["days"] if d.get("plan")]


def test_the_plan_its_schedule_and_its_cost_summary_agree(client):
    for feel in ("relaxed", "full"):
        for d in _trip(client, day_feel=feel):
            pl, stops = d["plan"], d["plan"]["stops"]
            t = pl["totals"]
            assert t["finish"] == stops[-1]["depart"]                           # the finish is the last stop's end
            assert abs(t["cost_gbp"] - (sum(st["cost_gbp"] for st in stops) + t["transport_gbp"])) < 0.01
            prev = parse_hhmm(d["window"]["start"])
            for st in stops:                                                   # no stop before the journey to it
                assert parse_hhmm(st["arrive"]) >= prev + (st.get("travel_min") or 0) - 1, st["title"]
                assert parse_hhmm(st["depart"]) >= parse_hhmm(st["arrive"])
                prev = parse_hhmm(st["depart"])
            assert parse_hhmm(stops[-1]["depart"]) <= parse_hhmm(d["window"]["end"])
            if fa := pl.get("free_after"):                                     # the free time is the day's own
                assert fa["from"] == stops[-1]["depart"] and fa["until"] == d["window"]["end"]
                assert fa["min"] == parse_hhmm(fa["until"]) - parse_hhmm(fa["from"])


def _sentences(text: str) -> list[str]:
    return [x.strip().lower() for x in re.split(r"(?<=[.!?])\s+", text or "") if len(x.strip()) > 12]


def test_no_sentence_is_said_twice_in_a_day(client):
    """What the day view shows (the stop's words, why it's picked, its notes and price) and what the text view shows
    (its lines, the blind pair's format): no sentence twice in a stop, or on two stops of a day."""
    def shown(st):
        v = st.get("what") or ""
        day = _sentences(" ".join(map(str, v)) if isinstance(v, list) else str(v))
        for r in st.get("reasons") or []:
            day += _sentences(r.get("you") or "")
        for ln in st.get("notes") or []:
            day += _sentences(ln)
        text = [x for ln in st.get("lines") or [] for x in _sentences(ln)]
        return day, text
    for d in _trip(client, day_feel="balanced"):
        said: dict[str, str] = {}
        for st in d["plan"]["stops"]:
            day, text = shown(st)
            assert len(day) == len(set(day)), (st["title"], day)                   # within a stop, both views
            assert len(text) == len(set(text)), (st["title"], text)
            for x in set(day):
                assert x not in said, f"{x!r} on {st['title']} and {said[x]}"      # across the day
                said[x] = st["title"]


def test_no_two_ready_cards_share_their_words():
    """The cards' own text, which both views show: never the same description or way in on two cards (the test
    cards above share theirs, so the day check covers the Brain's own sentences)."""
    for field in ("what_happens", "why_it_works"):
        texts = [getattr(m.experience, field) for m in CARDS.values() if m.status == "ready" and getattr(m.experience, field)]
        assert len(texts) == len(set(texts)), field
    by_path: dict[str, set] = {}   # variants of one moment (a plan holds one of them) may share their way in
    for m in CARDS.values():
        if m.status == "ready" and m.approach and m.approach.path:
            by_path.setdefault(m.approach.path, set()).add(m.variant_of or m.id)
    assert {k: v for k, v in by_path.items() if len(v) > 1} == {}


def test_what_the_brain_says_about_a_stop_reaches_the_day_view(client):
    """m349: free time, a later start and estimates are on `notes`, which the apps show under the stop (the day view
    never showed `lines`), as well as on the text lines."""
    days = _trip(client, day_feel="relaxed")
    notes = [n for d in days for st in d["plan"]["stops"] for n in st.get("notes") or []]
    lines = [ln for d in days for st in d["plan"]["stops"] for ln in st.get("lines") or []]
    assert notes and all(n in lines for n in notes)


def test_a_meal_with_no_named_place_says_its_price_is_an_estimate():
    st = {"key": "lunch@m_x", "moment_id": "lunch@m_x", "cost_gbp": 6.0, "cost_kind": "food"}
    assert dayplan._cost_line(st) == "Food: about £6, ODYS's estimate"
    named = {"key": "m_padella_borough#lunch", "moment_id": "m_padella_borough", "cost_gbp": 15.0, "cost_kind": "food"}
    assert dayplan._cost_line(named) == "Food: about £15"                    # its menu's price, checked
    two = [dict(st, lines=[]), dict(st, key="dinner@m_y", moment_id="dinner@m_y", lines=[])]
    dayplan.say_estimates(two)
    assert two[0]["lines"] == [dayplan.ESTIMATE_MEAL] and two[1]["lines"] == []   # said once a day


def test_no_ready_card_promises_something_out_of_season():
    """A winter visitor isn't promised summer flowers: a card's words name a season-bound thing only with its season."""
    bad = {m.id: hits for m in CARDS.values() if m.status == "ready"
           if (hits := quality.unseasonal(" ".join([m.title, m.experience.what_happens or "",
                                                    m.experience.why_it_works or ""])))}
    assert bad == {}


def test_unseasonal_words_are_found_and_qualified_ones_allowed():
    assert quality.unseasonal("A rooftop garden full of summer flowers.") == ["summer flowers"]
    assert quality.unseasonal("Cherry blossom over the path.") == ["blossom"]
    assert quality.unseasonal("In spring, cherry blossom over the path.") == []
    assert quality.unseasonal("Planted beds and trees, with flowers in summer.") == []
    assert quality.unseasonal("A calm walk among the trees.") == []


def test_sunset_is_worked_out_for_the_date_and_the_place():
    d = date(2026, 12, 4)
    assert "15:45" <= sun.sunset(d) <= "16:00"                                # central London (tests/test_sun.py)
    seville = sun.sunset(d, 37.3891, -5.9845, "Europe/Madrid")
    assert seville and parse_hhmm(seville) - parse_hhmm(sun.sunset(d)) > 120   # later, by its own clock
    assert sun.sunset(date(2026, 6, 21)) != sun.sunset(d)


def test_a_place_called_at_sunset_is_planned_at_sunset_on_every_day_it_comes(client):
    for d in _trip(client, day_feel="full", nights=3):
        set_at = parse_hhmm(sun.sunset(date.fromisoformat(d["date"])))
        for st in d["plan"]["stops"]:
            m = CARDS.get(st["moment_id"])
            if m and "sunset" in m.title.lower() and m.best_time.best_around_sunset:
                lo, hi = m.best_time.best_around_sunset
                assert set_at + lo <= parse_hhmm(st["arrive"]) <= set_at + hi, (d["date"], st["title"], st["arrive"])
                assert parse_hhmm(st["depart"]) >= set_at, (d["date"], st["title"], st["depart"])   # m352: there as it sets


def _food(mid, at, key=None):
    return {"moment_id": mid, "key": key or mid, "arrive": at, "cost_kind": "food"}


def test_two_substantial_lunches_141_minutes_apart_are_rejected():
    """m360 (Abram, 26 Nov: "A substantial restaurant lunch followed by another substantial lunch 141 minutes later
    should be rejected"): three hours between the starts of substantial meals; the later named one goes."""
    stops = [_food("m_wahaca_southbank", "12:00", "m_wahaca_southbank#lunch"), _food("m_padella_borough", "14:21")]
    assert dayplan.meals_close(stops) == ["m_padella_borough"]
    slot = [{"moment_id": "lunch@m_tate_modern", "key": "lunch@m_tate_modern", "arrive": "12:30", "lunch": True},
            _food("m_flat_iron_covent_garden", "14:45")]
    assert dayplan.meals_close(slot) == ["m_flat_iron_covent_garden"]   # a named restaurant after the lunch slot
    assert dayplan.meals_close([stops[0], _food("m_dishoom_covent_garden", "15:00")]) == []   # 180 min: allowed


def test_a_tasting_or_a_snack_is_never_held_apart_from_a_meal():
    """m360 (Abram: "Do not suppress genuine food discoveries simply because they are close together"): a market
    tasting, a bakery or a street-food snack doesn't count as a meal, before or after one."""
    stops = [_food("m_borough_market_graze", "12:07"), _food("m_padella_borough", "13:29", "m_padella_borough#lunch"),
             _food("m_beigel_bake_late", "15:15")]
    assert dayplan.meals_close(stops) == []
    assert not dayplan.substantial_meal(stops[0]) and not dayplan.substantial_meal(stops[2])
    assert dayplan.substantial_meal(stops[1])


def test_a_food_focused_day_keeps_every_discovery():
    """m360: Sam, who loves food, can graze a market, have lunch, a salt beef bagel and dinner in one day."""
    day = [_food("m_borough_market_graze", "10:45"),
           {"moment_id": "lunch@m_tate_modern", "key": "lunch@m_tate_modern", "arrive": "13:00", "lunch": True},
           _food("m_beigel_bake_late", "15:30"),
           _food("m_dishoom_covent_garden", "18:45", "m_dishoom_covent_garden#dinner")]
    assert dayplan.meals_close(day) == []
    assert [dayplan.substantial_meal(st) for st in day] == [False, True, False, True]


def test_a_return_after_crossing_london_is_found_but_never_for_a_loved_place():
    """m353 (G12): back within 600 m of a place left earlier, after going more than 3 km away."""
    pin = lambda lat, lon: {"lat": lat, "lon": lon}
    stops = [{"moment_id": "m_a", "pin": pin(51.5055, -0.1166)}, {"moment_id": "m_b", "pin": pin(51.5100, -0.0800)},
             {"moment_id": "m_c", "pin": pin(51.5082, -0.0650)}, {"moment_id": "m_d", "pin": pin(51.5060, -0.1170)}]
    assert dayplan.backtracks(stops) == ["m_d"]
    assert dayplan.backtracks(stops, loved={"m_d"}) == []


def test_a_family_pays_each_persons_own_price_and_an_unknown_childs_price_is_named():
    """m353 (Abram: "Verify children's fares, party totals and activity eligibility")."""
    stops = [{"moment_id": "m_cutty_sark", "title": "Cutty Sark", "cost_gbp": 22.0, "cost_kind": "ticket",
              "travel_min": 0, "travel_mode": "walk"},
             {"moment_id": "m_national_maritime_museum", "title": "Maritime", "cost_gbp": 0.0, "travel_min": 0,
              "travel_mode": "walk"},
             {"moment_id": "m_horizon_22", "title": "Horizon 22", "cost_gbp": 5.0, "cost_kind": "ticket",
              "travel_min": 0, "travel_mode": "walk"}]
    pc = dayplan.party_cost(stops, CARDS, adults=2, children=2)
    child_h22 = CARDS["m_horizon_22"].child_cost_gbp
    assert child_h22 is None and pc["child_price_unknown"] == ["Horizon 22"]
    assert pc["total_gbp"] == 2 * 22 + 2 * 11 + 4 * 5               # the Cutty Sark's child ticket is £11


def test_open_until_gives_the_places_own_closing_time_not_the_travellers_end():
    """m355 (a review of d6c6ab6: "Tate Modern is open until 17:00" when it closes at 18:00 and the day ended at 17:00)."""
    tate = CARDS["m_tate_modern"]
    close = max(hi for lo, hi in tate.windows("mon", "2026-12-07"))
    stops = [{"moment_id": "m_tate_modern", "key": "m_tate_modern", "arrive": "13:00", "depart": "15:00"}]
    fa = dayplan.free_after(stops, "17:00", CARDS, "mon", "2026-12-07", "relaxed")
    assert fa and f"open until {dayplan.hhmm(close)}" in fa["text"] and close > parse_hhmm("17:00")


def test_walking_and_tube_are_measured_apart_and_the_whole_journey_kept():
    """m355 (Abram, 25 Nov: "A 25-minute walk and a 25-minute Tube journey are not necessarily equivalent… Keep the
    overall journey measurement")."""
    from brain.travel import LondonEstimate
    stops = [{"cost_gbp": 0, "travel_min": 25, "travel_mode": "walk", "depart": "11:00"},
             {"cost_gbp": 0, "travel_min": 25, "travel_mode": "transit", "depart": "12:00"},
             {"cost_gbp": 0, "travel_min": 0, "travel_mode": "walk", "depart": "13:00", "free_before_min": 30,
              "free_before_kind": "wait"}]
    t = dayplan.plan_totals(stops, LondonEstimate())
    assert (t["walk_min"], t["transit_min"], t["transit_legs"], t["wait_min"], t["journey_min"]) == (25, 25, 1, 30, 50)
    assert t["walk_km"] > 0


def test_journeys_stay_within_each_paces_walk_cap(client):
    """m355: regression cases for a gentle family, a gentle solo traveller and a full-on one: no single walk over the
    walking rule's 30 min, and no Tube or bus for a link walkable in about the same time."""
    from brain.travel import LondonEstimate
    est = LondonEstimate()
    for pace, company in (("gentle", "family"), ("gentle", "solo"), ("full_on", "friends")):
        h, _ = install(client)
        assert client.put("/v1/me/profile", headers=h, json={"activity": pace, "company": company}).status_code == 204
        body = {"start_date": (date.today() + timedelta(days=5)).isoformat(), "nights": 1, "day_start": "10:00",
                "day_end": "18:00", "stops_per_day": 3}
        for d in client.post("/v1/me/trips/days", headers=h, json=body).json()["days"]:
            for st in (d.get("plan") or {}).get("stops", []):
                if st.get("travel_mode") == "walk":
                    assert (st.get("travel_min") or 0) <= est.WALK_PREFER_MAX + 1, (pace, st["title"])
